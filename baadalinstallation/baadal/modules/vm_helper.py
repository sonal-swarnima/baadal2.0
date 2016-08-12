# -*- coding: utf-8 -*-
###################################################################################

from gluon import current
from helper import get_constant, execute_remote_cmd, config, get_datetime, \
    log_exception, is_pingable, get_context_path
from libvirt import * # @UnusedWildImport
from log_handler import logger
from nat_mapper import create_mapping, remove_mapping
import sys, math, shutil, libvirt, os, time, random
import xml.etree.ElementTree as etree


def _choose_datastore():
    """
    Chooses datastore from a list of available datastores
    """
    # datastore_capacity = current.db(current.db.datastore.id >= 0).select(orderby = current.db.datastore.used
    datastores = current.db(current.db.datastore.id >= 0).select()
    datastore_length = len(datastores)
    logger.debug("datastore_lengtn" + str(datastore_length))
    if(datastore_length == 0):
        raise Exception("No datastore found.")
    else:
        count = datastore_length
        available_datastores = {}
        while count != 0:
            available = datastores[datastore_length-count].capacity - datastores[datastore_length-count].used
            available_datastores[datastores[datastore_length-count]] = available
            count = count-1
        z = [(i,available_datastores[i]) for i in available_datastores] 
        z.sort(key=lambda x: x[1])
        available_datastores = z
        logger.debug("available d" + str(available_datastores[-1]))
        first_elts = available_datastores[-1]
        first_elts = first_elts[0]

        logger.debug("selected database" + str(first_elts))
        return first_elts

def host_resources_used(host_id):
    """
    Returns resources utilization of a host in MB, Count
    """
    RAM = 0.0
    CPU = 0.0
    vms = current.db((current.db.vm_data.host_id == host_id) & (current.db.vm_data.status != current.VM_STATUS_UNKNOWN) &  (current.db.vm_data.status != current.VM_STATUS_IN_QUEUE)).select()
    logger.debug("vms selected are: " + str(vms))
    for vm_data in vms:
        RAM += vm_data.RAM
        CPU += vm_data.vCPU
    
    return (math.ceil(RAM),math.ceil(CPU))

def getVirshDomainConn(vm_details, host_ip=None, domain_name=None):
    """
    Generic method to establish libvirt connection
    """    
    if vm_details != None:
        host_ip = vm_details.host_id.host_ip.private_ip
        domain_name = vm_details.vm_identity

    connection_object = libvirt.open("qemu+ssh://root@" + host_ip + "/system")

    domain = connection_object.lookupByName(domain_name)

    return (connection_object, domain)

def getVirshDomain(vm_details):
    """
    Generic method to establish libvirt connection
    """
    (connection_object, domain) = getVirshDomainConn(vm_details)
    connection_object.close()
    return domain
    
def _set_portgroup_in_vm(domain_name, portgroup, host_ip, vlan_tag):
    """
    Set the vlan tag in network configuration of VM
    This is required to ensure that VM fetches IP of its vlan from DHCP
    """
    (connection_object, domain) = getVirshDomainConn(None, host_ip, domain_name)
    xml = etree.fromstring(domain.XMLDesc(0))
    source_network_element = xml.find('.//interface/source') 
   
    source_network_string=etree.tostring(source_network_element) 
    logger.debug("Source network is " + source_network_string)

    if source_network_string.find(" network=") != -1:
        logger.debug("Source is set to network adding portgroup to the source tag ")
        source_network_element.set('portgroup', portgroup)  
        logger.debug("Changed source network is " + etree.tostring(source_network_element)) 
    elif source_network_string.find(" bridge=") != -1:
        logger.debug("Source is set to bridge adding <vlan><tag_id> to the interface tag ")
        root_new  = xml.find('.//interface')  
        root_new_vlan= etree.SubElement(root_new, 'vlan') 
        root_new_tag=  etree.SubElement(root_new_vlan, 'tag')
        root_new_tag.set('id',vlan_tag) 
        logger.debug("After append root_new_vlan is " + etree.tostring(root_new_vlan))  
    else:
        logger.debug("Neither VM nor vlan tagId is added in the xml" )  

    domain = connection_object.defineXML(etree.tostring(xml))
    domain.destroy()
    domain.create()
    domain.isActive()
    connection_object.close()
    
def _get_private_ip_mac(security_domain_id):
    """
    Chooses a random Private IP from the pool, such that:
        - It is not assigned to any VM or host
        - It belongs to VLAN of given security domain
    """
    vlans = current.db(current.db.security_domain.id == security_domain_id)._select(current.db.security_domain.vlan)
    private_ip_pool = current.db((~current.db.private_ip_pool.id.belongs(current.db(current.db.vm_data.private_ip != None)._select(current.db.vm_data.private_ip))) 
                                 & (~current.db.private_ip_pool.id.belongs(current.db(current.db.host.host_ip != None)._select(current.db.host.host_ip))) 
                                 & (current.db.private_ip_pool.vlan.belongs(vlans))).select(current.db.private_ip_pool.ALL, orderby='<random>').first()

    if private_ip_pool:
        return private_ip_pool 
    else:
        sd = current.db.security_domain[security_domain_id]
        raise Exception(("Available MACs are exhausted for security domain '%s'." % sd.name))


def _choose_random_public_ip():
    """
    Chooses a random Public IP from the pool, such that:
        - It is not assigned to any VM
        - It is not assigned to any host
        - IP is marked active.
    """
    public_ip_pool = current.db((~current.db.public_ip_pool.id.belongs(current.db(current.db.vm_data.public_ip != None)._select(current.db.vm_data.public_ip))) 
                              & (~current.db.public_ip_pool.id.belongs(current.db(current.db.host.public_ip != None)._select(current.db.host.public_ip)))
                              & (current.db.public_ip_pool.is_active == True)) \
                            .select(current.db.public_ip_pool.ALL, orderby='<random>').first()

    return public_ip_pool


def _choose_mac_ip(vm_properties):
    """
    Chooses mac address and ip address for a vm to be installed.
    It also chooses a random public IP if requested
    """
    if not 'private_ip' in vm_properties:
        private_ip_info = _get_private_ip_mac(vm_properties['security_domain'])
        vm_properties['private_ip'] = private_ip_info.private_ip
        vm_properties['mac_addr']   = private_ip_info.mac_addr
        vm_properties['vlan_name']  = private_ip_info.vlan.name
        vm_properties['vlan_tag']   = private_ip_info.vlan.vlan_tag

    if vm_properties['public_ip_req']:
        if 'public_ip' not in vm_properties:
            public_ip_pool = _choose_random_public_ip()

            if public_ip_pool:
                vm_properties['public_ip'] = public_ip_pool.public_ip
            else:
                raise Exception("Available Public IPs are exhausted.")
    else:
        vm_properties['public_ip'] = None


def _choose_mac_ip_vncport(vm_properties):
    """
    Chooses mac address, ip address and vncport for a vm to be installed
    """
    _choose_mac_ip(vm_properties)

    start_range = int(get_constant('vncport_start_range')) 
    end_range = int(get_constant('vncport_end_range'))
    vnc_ports_taken = current.db().select(current.db.vm_data.vnc_port)
    while True:
        random_vnc_port = random.randrange(start_range, end_range, 1)
        if not random_vnc_port in vnc_ports_taken:
            break;
    vm_properties['vnc_port'] = str(random_vnc_port)


def find_new_host(RAM, vCPU):
    """
    Select a random host from list of 3 hosts with available RAM and CPU
    Availability is checked with 200 percent over-commitment.
    """
    hosts = current.db(current.db.host.status == 1).select()
    hosts = hosts.as_list(True,False) 
    count = 3 
    selected_hosts = []
    while count != 0 and hosts:
        host = random.choice(hosts)
        logger.debug("Checking host =" + host['host_name'])
        (used_ram, used_cpu) = host_resources_used(host['id'])
        logger.debug("used ram: " + str(used_ram) + " used cpu: " + str(used_cpu) + " host ram: " + str(host['RAM']) + " host cpu "+ str(host['CPUs']))
        host_ram_after_200_percent_overcommitment = math.floor((host['RAM'] * 1024) * 2)
        host_cpu_after_200_percent_overcommitment = math.floor(host['CPUs'] * 2)

        logger.debug("ram available: %s cpu available: %s cpu < max cpu: %s" % ((( host_ram_after_200_percent_overcommitment - used_ram) >= RAM), ((host_cpu_after_200_percent_overcommitment - used_cpu) >= vCPU), (vCPU <= host['CPUs']) ))

        if((( host_ram_after_200_percent_overcommitment - used_ram) >= RAM) and ((host_cpu_after_200_percent_overcommitment - used_cpu) >= vCPU) and (vCPU <= host['CPUs'])):
            selected_hosts.append(host)
            count = count -1

        hosts.remove(host)
    
    if selected_hosts:
        #Sort selected host list by Ram first then Cpu
        selected_host = sorted(selected_hosts,key=lambda k: k['RAM'])[0]
        return selected_host['id'] 
    #If no suitable host found
    raise Exception("No active host is available for a new vm.")
    

def allocate_vm_properties(vm_details):
    """
    Allocates vm properties ( datastore, host, ip address, mac address, vnc port, ram, vcpus)
    """
    logger.debug("Inside allocate_vm_properties()...")
    vm_properties = {}

    vm_properties['datastore'] = _choose_datastore()
    logger.debug("Datastore selected is: " + str(vm_properties['datastore']))

    vm_properties['host'] = find_new_host(vm_details.RAM, vm_details.vCPU)
    logger.debug("Host selected is: " + str(vm_properties['host']))

    vm_properties['public_ip_req'] = False if (vm_details.public_ip == None) else True
    vm_properties['security_domain'] = vm_details.security_domain
    _choose_mac_ip_vncport(vm_properties)

    logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + " VNCPORT is : "  \
                          + str(vm_properties['vnc_port']) + " Vlan tag is " + str(vm_properties['vlan_tag']) )
    
    vm_properties['ram'] = vm_details.RAM
    vm_properties['vcpus'] = vm_details.vCPU

    return vm_properties


def create_vm_image(vm_details, datastore):
    """
    Create a VM image
        - Creates a directory for the new VM using vm_identity
        - Find the location of template image requested for
        - Copy the template image from its location to new vm directory
    """
    # Creates a directory for the new vm
    vm_directory_path = datastore.system_mount_point + '/' + get_constant('vms') + '/' + vm_details.vm_identity
    logger.debug("Creating vm directory...")
    if not os.path.exists (vm_directory_path):
        os.makedirs(vm_directory_path)
    else:
        raise Exception("Directory with same name as vmname already exists.")

    # Finds the location of template image that the user has requested for its vm.               
    template = current.db.template[vm_details.template_id]
    vm_image_name = vm_directory_path + '/' + vm_details.vm_identity + '.qcow2'

   
    # Copies the template image from its location to new vm directory
    storage_type = config.get("GENERAL_CONF","storage_type")

    copy_command = 'ndmpcopy ' if storage_type == current.STORAGE_NETAPP_NFS else 'cp '
    #template_dir = get_constant('vm_templates_datastore')
    if copy_command == 'cp ':
        template_location = datastore.system_mount_point + '/' + get_constant('templates_dir') + '/' + template.hdfile
        logger.debug("cp %s %s" % (template_location, vm_image_name))
        rc = os.system("cp %s %s" % (template_location, vm_image_name))

        if rc != 0:
            logger.error("Copy not successful")
            raise Exception("Copy not successful")
        else:
            logger.debug("Copied successfully")

    elif copy_command == 'ndmpcopy ':
        template_dir = template.datastore_id.path
        logger.debug(template_dir)
        
        logger.debug("Copy in progress when storage type is " + str(storage_type))
        command_to_execute = copy_command + template_dir + '/' + get_constant("templates_dir") + '/' +  \
                             template.hdfile + ' ' + datastore.path + '/' + get_constant('vms') + '/' + \
                             vm_details.vm_identity
        logger.debug("ndmpcopy command: " + str(command_to_execute))
        command_output = execute_remote_cmd(datastore.ds_ip, datastore.username, command_to_execute, datastore.password)
        logger.debug(command_output)
        logger.debug("Copied successfully.")
        
        try:
            vm_template_name = datastore.system_mount_point + '/' + get_constant('vms') + '/' + vm_details.vm_identity + '/' + template.hdfile
            os.rename(vm_template_name, vm_image_name)
            logger.debug("Template renamed successfully")
        except:
            logger.debug("Template rename not successful")
            raise Exception("Template rename not successful")

    return (template, vm_image_name)


def _get_install_command(vm_details, vm_image_location, vm_properties):
    """
    Generates install command for vm
    """
    template = vm_properties['template']
    bus = ',bus=virtio'     
    optional = ' --import --os-type=' + template.os
    model = ',model=virtio'
    if (template.arch != 'amd64' and template.os == 'Linux'):
        optional = optional + ' --arch=' + template.arch + ' '
   
    format_command = ''
    if (template.type == 'QCOW2'):
        format_command = ',format=qcow2'
    
    if (template.os == 'Windows'):
        bus = ''
        model = ''
    
    install_command = 'virt-install \
                     --name=' + vm_details.vm_identity + ' \
                     --ram=' + str(vm_properties['ram']) + ' \
                     --vcpus=' + str(vm_properties['vcpus']) + optional + ' \
                     --disk path=' + vm_image_location + format_command + bus + ',cache=none' + ' \
                     --network network='+current.LIBVIRT_NETWORK + model + ',mac=' + vm_properties['mac_addr'] + ' \
                     --graphics vnc,port=' + vm_properties['vnc_port'] + ',listen=0.0.0.0,password=duolc \
                     --noautoconsole \
                     --description \
                     --autostart \
                     --force' 

    return install_command 


def _generate_disk_xml(diskpath,target_disk):
    """
    Generates xml for defining new disk
    """
    root_element = etree.Element('disk',attrib = {'type':'block','device':'disk'})
    etree.SubElement(root_element, 'driver',attrib = {'name':'qemu','cache':'none', 'type':'qcow2'})
    etree.SubElement(root_element, 'source', attrib = {'dev':diskpath})
    etree.SubElement(root_element, 'target', attrib = {'dev': target_disk})

    return (etree.tostring(root_element))
      

def create_extra_disk_image(vm_details, disk_name, size, datastore):
    """
    Create extra disk image
    """
    vm_extra_disks_directory_path = datastore.system_mount_point + '/' + get_constant('extra_disks_dir') + '/' + \
                                    datastore.ds_name + '/' + vm_details.vm_identity

    if not os.path.exists (vm_extra_disks_directory_path):
        logger.debug("Making Directory")          
        os.makedirs(vm_extra_disks_directory_path)

    diskpath = vm_extra_disks_directory_path + '/' + disk_name

    command= "qemu-img create -f qcow2 "+ diskpath + " " + str(size) + "G"
    output = os.system(command)

    return False if output != 0 else True


def attach_disk(vm_details, disk_name, hostip, already_attached_disks, new_vm):
    """
    Attach given disk to the VM
    """
    try:
        (connection_object, domain) = getVirshDomainConn(None, hostip, vm_details.vm_identity)

        #already_attached_disks = len(current.db(current.db.attached_disks.vm_id == vm.id).select()) 
        logger.debug("Value of alreadyattached is : " + str(already_attached_disks))
        
        (diskpath, device_present, disk_size) = get_extra_disk_location(vm_details.datastore_id, vm_details.vm_identity, disk_name, True)

        if not device_present:
            raise Exception("Device to be attached %s missing" %(diskpath))
        
        # Attaching disk to vm using libvirt API
        target_disk = "vd" + chr(97 + already_attached_disks + 1)
        logger.debug(target_disk)
        logger.debug("...................")
        xmlDescription = _generate_disk_xml(diskpath, target_disk)
        logger.debug(xmlDescription)
        logger.debug("new vm is %s " % new_vm)

        if new_vm:
            logger.debug("Starting to attach disk on new vm request.")
            domain.destroy()
            logger.debug("VM destroyed")
            domain.attachDeviceFlags(xmlDescription, VIR_DOMAIN_AFFECT_CONFIG)
            logger.debug("Disk attached")
            
            logger.debug("Turn on vm")
            domain.create()
            logger.debug("VM started")
            domain.isActive()

        elif vm_details.status == current.VM_STATUS_SHUTDOWN:
            logger.debug("Starting to attach disk while vm is shutdown.")
            domain.attachDeviceFlags(xmlDescription, VIR_DOMAIN_AFFECT_CONFIG) 
            logger.debug("Disk attached")

        else:
            raise Exception("VM is not in shutdown state. Check its status on host")        
        
        xmlfile = domain.XMLDesc(0)
        domain = connection_object.defineXML(xmlfile)
        logger.debug("VM XML redefined")

        connection_object.close()
        return disk_size
    except:
        logger.exception('Exception: ') 
        return 0


def serve_extra_disk_request(vm_details, disk_size, host_ip, new_vm = False):
    """
    Serves extra disk request and updates db
    """
    logger.debug("Starting to serve extra disk request...")
    logger.debug("new vm is %s " % new_vm)
    datastore = _choose_datastore()
    already_attached_disks = len(current.db(current.db.attached_disks.vm_id == vm_details.id).select()) 
    disk_name = vm_details.vm_identity + "_disk" + str(already_attached_disks + 1) + ".qcow2"  

    disk_created = create_extra_disk_image(vm_details, disk_name, disk_size, datastore) 
    vm_details.datastore_id = datastore.id
    
    if disk_created:
        if (attach_disk(vm_details, disk_name, host_ip, already_attached_disks, new_vm)):
            current.db.attached_disks.insert(vm_id = vm_details.id, datastore_id = datastore.id , attached_disk_name = disk_name, capacity = disk_size)
            current.db(current.db.datastore.id == datastore.id).update(used = int(datastore.used) + int(disk_size)) 
            return True

    return False


def launch_vm_on_host(vm_details, vm_image_location, vm_properties):
    """
    Launches a vm image on host
    """
    attach_disk_status_message = ''
    install_command = _get_install_command(vm_details, vm_image_location, vm_properties)  
    # Starts installing a vm
    host_ip = current.db.host[vm_properties['host']].host_ip.private_ip
    logger.debug("Installation started...")
    logger.debug("Host is "+ host_ip)
    logger.debug("Installation command : " + install_command)
    command_output = execute_remote_cmd(host_ip, 'root', install_command)
    logger.debug(command_output)
    logger.debug("Starting to set portgroup in vm...")
    _set_portgroup_in_vm(vm_details['vm_identity'], vm_properties['vlan_name'], host_ip, vm_properties['vlan_tag'])
    logger.debug("Portgroup set in vm")

    # Serving HDD request
    if (int(vm_details.extra_HDD) != 0):
        if (serve_extra_disk_request(vm_details, vm_details.extra_HDD, host_ip, new_vm = True)):
            message = "Attached extra disk successfully."
            attach_disk_status_message += message
            logger.debug(message)
        else:
            attach_disk_status_message += "Attached extra disk failed."
    return attach_disk_status_message


def check_if_vm_defined(hostip, vmname):
    """
    Checks if a newly created vm is successfully defined
    """
    vm_defined = False
    try:
        connection_object = libvirt.openReadOnly('qemu+ssh://root@'+ hostip +'/system')
        domain = connection_object.lookupByName(vmname)
        if domain.ID() in connection_object.listDomainsID():
            vm_defined = True
            connection_object.close()
            return vm_defined
    except:
        return False


def _free_vm_properties(vm_details, vm_properties):
    """
    Frees vm properties in-case installation has failed mid-way
    """
    logger.debug("VM installation fails..Starting to free vm properties")

    if vm_properties:
        host_ip_of_vm = current.db.host[vm_properties['host']].host_ip.private_ip
        logger.debug("Host IP of vm is " + str(host_ip_of_vm))
        if check_if_vm_defined(host_ip_of_vm, vm_details.vm_identity):
            connection_object = libvirt.open('qemu+ssh://root@'+ host_ip_of_vm +'/system')
            domain = connection_object.lookupByName(vm_details.vm_identity)
            logger.debug("Starting to delete vm from host..")
            domain.destroy()
            domain.undefine()
            connection_object.close()
            logger.debug("VM deleted.")

    current.db(current.db.attached_disks.vm_id == vm_details.id).delete() 

    vm_directory_path = vm_properties['datastore'].system_mount_point + '/' + get_constant('vms') + '/' + vm_details.vm_identity

    vm_extra_disk_dir_path = vm_properties['datastore'].system_mount_point + '/' + get_constant('extra_disks_dir') + '/' + vm_properties['datastore'].ds_name + '/' + vm_details.vm_identity
    if os.path.exists (vm_directory_path):
        logger.debug("Starting to delete vm directory.")
        shutil.rmtree(vm_directory_path)
    if os.path.exists (vm_extra_disk_dir_path):
        logger.debug("Starting to delete vm extra disk directory.")
        shutil.rmtree(vm_extra_disk_dir_path)
    return
    

def update_db_after_vm_installation(vm_details, vm_properties, parent_id = None):
    """
    Updates db after a vm is installed successfully
    """
    logger.debug("Starting to update db after vm installation..")
    hostid = vm_properties['host']
    datastore = vm_properties['datastore']
    template_hdd = vm_properties['template'].hdd
    logger.debug("Inside update db after installation")
    logger.debug(vm_properties)

    # Updating the used entry of datastore
    current.db(current.db.datastore.id == datastore.id).update(used = int(datastore.used) + int(vm_details.extra_HDD) +        
                                                                int(template_hdd))

    private_ip_id = current.db.private_ip_pool(private_ip=vm_properties['private_ip']).id
    public_ip_id = None
    if vm_properties['public_ip'] != None:
        public_ip_id = current.db.public_ip_pool(public_ip=vm_properties['public_ip']).id
        
    if parent_id:
        vm_status = current.VM_STATUS_SHUTDOWN
    else:
        vm_status = current.VM_STATUS_RUNNING

    # Update vm_data table
    current.db(current.db.vm_data.id == vm_details.id).update( host_id = hostid, 
                                                               extra_HDD = vm_details.extra_HDD,
                                                               datastore_id = datastore.id, 
                                                               vnc_port = vm_properties['vnc_port'],
                                                               private_ip = private_ip_id, 
                                                               public_ip = public_ip_id, 
                                                               start_time = get_datetime(), 
                                                               parent_id = parent_id,
                                                               status = vm_status)

    logger.debug("Updated db")    
    return


def create_object_store(parameters,object_data):
    try:
        logger.debug("In create_object_store() function...")
        object_name=object_data['object_store_name']
        size_limit=object_data['object_store_size']
        sh_path = os.path.join(get_context_path(), 'private/object_storage.sh')
        command = 'sh %s %s %s' %(sh_path, object_name, str(size_limit))
        logger.debug("command :%s" %command)
        file_name=  object_data['object_store_name'] + "_key.txt" 
        file_path = os.path.join(get_context_path(), 'private/Object_keys/' + file_name)
        cp = os.open(file_path,os.O_RDWR|os.O_CREAT)
        co = os.fdopen(cp,"rw+")
        fd = os.open('/home/key.txt',os.O_RDWR|os.O_CREAT)
        fo = os.fdopen(fd,"r+")
        key_s3_secret= fo.readline();
        co.write(key_s3_secret);
        key_s3_access= fo.readline();
        co.write(key_s3_access);
        key_swift_secret= fo.readline();
        co.write(key_swift_secret); 
        swift_user= 'Swift_user: ' + object_name + ':swift'
        co.write(swift_user)
        co.close()
        a,b,key_swift_secret= key_swift_secret.partition(' ')
        a,b,key_s3_secret= key_s3_secret.partition(' ')
        a,b,key_s3_access= key_s3_access.partition(' ')
        #print key_s3_secret, key_s3_access , key_swift_secret
        object_data.update_record(swift_access_key= key_swift_secret.strip() , s3_secret_key= key_s3_secret.strip(), s3_access_key= key_s3_access.strip(), status=3)
        fo.close()
        message = "Object Store is created successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
        
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())

# Installs a vm
def install(parameters):
    """
    Installs a vm
    """
    vmid = parameters['vm_id']
    logger.debug("In install() function...")
    vm_details = current.db.vm_data[vmid]
    vm_properties = None

    try:
        # Fetches vm details from vm_data table
        logger.debug("VM details are: " + str(vm_details))

        # Calling allocate_vm_properties function
        vm_properties = allocate_vm_properties(vm_details)

        # Calling create_vm_image function
        (vm_properties['template'], vm_image_location) = create_vm_image(vm_details, vm_properties['datastore'])
     
        # Calling launch_vm_on_host
        attach_disk_status_message = launch_vm_on_host(vm_details, vm_image_location, vm_properties)       

        # Checking if vm has been installed successfully
        assert(check_if_vm_defined(current.db.host[vm_properties['host']].host_ip.private_ip, vm_details.vm_identity)), "VM is not installed. Check logs."

        if vm_properties['public_ip_req']:
            create_mapping(vm_properties['public_ip'], vm_properties['private_ip'])

        # Update database after vm installation
        update_db_after_vm_installation(vm_details, vm_properties) 

        message = "VM is installed successfully." + attach_disk_status_message
        logger.debug("Task Status: SUCCESS Message: %s " % message)

        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    

    except:
        if vm_properties != None:         
            _free_vm_properties(vm_details, vm_properties)
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def start(parameters):
    """
    Starts a vm
    """
    logger.debug("Inside start() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] == VIR_DOMAIN_RUNNING:
            raise Exception("VM is already running. Check vm status on host.")
        domain.create()
        
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_RUNNING)
        message = vm_details.vm_identity + " is started successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def suspend(parameters):
    """
    Suspends a vm
    """
    logger.debug("Inside suspend() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] == VIR_DOMAIN_PAUSED:
            raise Exception("VM is already paused. Check vm status on host.")
        domain.suspend()
        
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_SUSPENDED)       
        message = vm_details.vm_identity + " is suspended successfully." 
        logger.debug("Task Status: SUCCESS Message: %s " % message)     
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def resume(parameters):
    """
    Resumes a vm
    """
    logger.debug("Inside resume() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] == VIR_DOMAIN_RUNNING:
            raise Exception("VM is already running. Check vm status on host.")
        domain.resume()
        
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_RUNNING) 
        message = vm_details.vm_identity + " is resumed successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def destroy(parameters):
    """
    Destroys a vm forcefully
    """
    logger.debug("Inside destroy() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] == VIR_DOMAIN_SHUTOFF:
            raise Exception("VM is already shutoff. Check vm status on host.")
        domain.destroy()

        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_SHUTDOWN) 
        message = vm_details.vm_identity + " is destroyed successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def shutdown(parameters):
    """
    Destroys a vm gracefully
    """
    logger.debug("Inside shutdown() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] == VIR_DOMAIN_SHUTOFF:
            raise Exception("VM is already shutoff. Check vm status on host.")
        domain.managedSave()

        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_SHUTDOWN)
        message = vm_details.vm_identity + " is shutdown successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def _clean_up_database_after_vm_deletion(vm_details):
    """
    Cleans up database after vm deletion
    """
    logger.debug("Inside clean up database after vm deletion () function...")

    # moving vm image folder to archives folder
    archive_directory_path = vm_details.datastore_id.system_mount_point + '/' + get_constant('archives_dir')
    if not os.path.exists(archive_directory_path):
            os.makedirs(archive_directory_path)
    source_file = vm_details.datastore_id.system_mount_point + '/' + get_constant('vms') + '/' + vm_details.vm_identity
    archive_filename = vm_details.vm_identity + str(get_datetime())
    logger.debug(archive_filename)
    destination_file = archive_directory_path  + '/' + archive_filename
    shutil.move(source_file, destination_file)

    # removing hdd 
    vm_extra_disks_directory_path =  vm_details.datastore_id.system_mount_point + '/' + get_constant('extra_disks_dir') + '/' + \
                                    vm_details.datastore_id.ds_name + "/" + vm_details.vm_identity      
    if os.path.exists(vm_extra_disks_directory_path):
        shutil.rmtree(vm_extra_disks_directory_path)

    # updating the used entry of database
    current.db(current.db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                          (int(vm_details.extra_HDD) + int(vm_details.template_id.hdd)))

    # updating task_queue_event entry to remove reference of VM
    current.db(current.db.task_queue_event.vm_id == vm_details.id).update(vm_id = None)

    # deleting entry of extra disk of vm
    current.db(current.db.attached_disks.vm_id == vm_details.id).delete()

    logger.debug("Database cleaned")


def vm_has_snapshots(vm_id):
    """
    Checks if a vm has snapshot(s)
    """
    if (current.db(current.db.snapshot.vm_id == vm_id).select()):
        return True
    else:
        return False

        
def delete(parameters):
    """
    Deletes a vm
    """
    logger.debug("Inside delete() function")
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        domain = getVirshDomain(vm_details)
        logger.debug(str(vm_details.status))
        if (vm_details.status == current.VM_STATUS_RUNNING or vm_details.status == current.VM_STATUS_SUSPENDED):
            logger.debug("Vm is not shutoff. Shutting it off first.")
            domain.destroy()
        logger.debug("Starting to delete it...")
        domain.undefineFlags(VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA )

        if vm_details.public_ip:
            remove_mapping(vm_details.public_ip.public_ip, vm_details.private_ip.private_ip)
        message = vm_details.vm_identity + " is deleted successfully."
        logger.debug(message)
        _clean_up_database_after_vm_deletion(vm_details)
        current.db(current.db.vm_data.id == vm_id).delete()
        current.db.commit()
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def migrate_domain_with_snapshots(vm_details, destination_host_ip, domain, domain_snapshots_list, current_snapshot_name, flags, vm_backup_during_migration):
    """
    Migrate domain with snapshots
    """
    # XML dump of snapshot(s) of the vm
    logger.debug("Starting to take xml dump of the snapshot(s) of the vm... ")

    if not os.path.exists(vm_backup_during_migration):
            os.makedirs(vm_backup_during_migration)

    for domain_snapshot in domain_snapshots_list:
        logger.debug("snapshot name is " + str(domain_snapshot))
        dump_xml_path = vm_backup_during_migration + '/' + 'dump_' + domain_snapshot
        snapshot_dumpxml_command = 'virsh snapshot-dumpxml %s %s > %s' % ( vm_details.vm_identity, domain_snapshot, dump_xml_path)
        logger.debug("Taking xml dump of" + str(domain_snapshot))
        command_output = execute_remote_cmd(vm_details.host_id.host_ip.private_ip, 'root', snapshot_dumpxml_command)
        logger.debug(command_output)
        logger.debug("XML dump of " + str(domain_snapshot) + "succeeded.")

    # Delete snapshot(s) of the vm and migrate it to destination host
    logger.debug("Starting to delete snapshots of the vm....")
    for domain_snapshot in domain_snapshots_list:
        snapshot = domain.snapshotLookupByName(domain_snapshot, 0)
        snapshot.delete(0)
    logger.debug("Migrating the vm to destination host...")
    domain.migrateToURI("qemu+ssh://root@" + destination_host_ip + "/system", flags , None, 0)

    # Redefine all the snapshot(s) of the vm on the destination host and set current snapshot
    logger.debug("Starting to redefine all the snapshot(s) of the domain...")
    for domain_snapshot in domain_snapshots_list:
        redefine_xml_path =  vm_backup_during_migration + '/' + 'dump_' + domain_snapshot
        snapshot_redefine_command = 'virsh snapshot-create --redefine %s %s ' % (vm_details.vm_identity, redefine_xml_path)
        command_output = execute_remote_cmd(destination_host_ip, 'root', snapshot_redefine_command)
        logger.debug(command_output)

    snapshot_current_command = 'virsh snapshot-current %s %s' % (vm_details.vm_identity, current_snapshot_name)
    command_output = execute_remote_cmd(destination_host_ip, 'root', snapshot_current_command)
    logger.debug(command_output)

    return


def _clean_migration_directory(vm_backup_during_migration):
    """
    Delete directory created for storing dumpxml of vm snapshots
    """
    if os.path.exists(vm_backup_during_migration):
        shutil.rmtree(vm_backup_during_migration)

    return

 
def undo_migration(vm_details, domain_snapshots_list, current_snapshot_name, vm_backup_during_migration):
    """
    Undo the migration
    """
    if domain_snapshots_list:
        # Redefine the snapshots of the vm on the source host
        logger.debug("Starting to redefine all the snapshot(s) of the vm on the source host...")
        for domain_snapshot in domain_snapshots_list:
            redefine_xml_path =  vm_backup_during_migration + '/' + 'dump_' + domain_snapshot
            snapshot_redefine_command = 'virsh snapshot-create --redefine %s %s ' % (vm_details.vm_identity, redefine_xml_path)
            command_output = execute_remote_cmd(vm_details.host_id.host_ip.private_ip, 'root', snapshot_redefine_command, None, True)
            logger.debug(command_output)
        snapshot_current_command = 'virsh snapshot-current %s %s' % (vm_details.vm_identity, current_snapshot_name)
        command_output = execute_remote_cmd(vm_details.host_id.host_ip.private_ip, 'root', snapshot_current_command, None, True)
        logger.debug(command_output)
    # Delete directory created for storing dumpxml of vm snapshots
    _clean_migration_directory(vm_backup_during_migration)

    return


def migrate_domain(vm_id, destination_host_id=None, live_migration=False):
    """
    Migrate domain
    """
    vm_details = current.db.vm_data[vm_id]
    domain_snapshots_list = []
    current_snapshot_name = ''
    vm_migration_directory = get_constant('vm_migration_data')
    vm_backup_during_migration = vm_details.datastore_id.system_mount_point + '/' + vm_migration_directory + '/' + \
                                 vm_details.vm_identity

    if destination_host_id == None:
        destination_host_id = find_new_host(vm_details.RAM, vm_details.vCPU)

    destination_host_ip = current.db.host[destination_host_id].host_ip.private_ip

    flags = VIR_MIGRATE_PEER2PEER|VIR_MIGRATE_PERSIST_DEST|VIR_MIGRATE_UNDEFINE_SOURCE|VIR_MIGRATE_UNSAFE
    if live_migration:
        flags |= VIR_MIGRATE_TUNNELLED|VIR_MIGRATE_LIVE
        
    if vm_details.status == current.VM_STATUS_SUSPENDED:
        logger.debug("Vm is suspended")
        flags |= VIR_MIGRATE_TUNNELLED|VIR_MIGRATE_PAUSED
    elif vm_details.status == current.VM_STATUS_SHUTDOWN:
        logger.debug("Vm is shut off")
        flags |= VIR_MIGRATE_OFFLINE   
    logger.debug("Flags: " + str(flags))   

    try:    
        domain = getVirshDomain(vm_details)
        dom_snapshot_names = domain.snapshotListNames(0)
        
        for snapshot in current.db(current.db.snapshot.vm_id == vm_id).select():
            logger.debug("snapshot:" + str(snapshot.snapshot_name))
            domain_snapshots_list.append(snapshot.snapshot_name)
            dom_snapshot_names.remove(snapshot.snapshot_name)
        logger.debug("domain snapshot list is " + str(domain_snapshots_list))
        
        for dom_snapshot in dom_snapshot_names:
            logger.debug("Deleting orphan snapshot %s" %(dom_snapshot))
            snapshot = domain.snapshotLookupByName(dom_snapshot, 0)        
            snapshot.delete(0)
    
        if domain_snapshots_list:
            current_snapshot = domain.snapshotCurrent(0)
            current_snapshot_name = current_snapshot.getName()
            migrate_domain_with_snapshots(vm_details, destination_host_ip, domain, domain_snapshots_list, current_snapshot_name, flags, vm_backup_during_migration)
        else:
            domain.migrateToURI("qemu+ssh://root@" + destination_host_ip + "/system", flags , None, 0)

        vm_details.update_record(host_id = destination_host_id)
        current.db.commit()
        
        # Delete directory created for storing dumpxml of vm snapshot
        _clean_migration_directory(vm_backup_during_migration)

        message = vm_details.vm_identity + " is migrated successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        undo_migration(vm_details, domain_snapshots_list, current_snapshot_name, vm_backup_during_migration)
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def migrate_domain_datastore(vmid, destination_datastore_id, live_migration=False): 
    """
    Migrate VM domain from one datastore to another.
        - Copy VM Image to new datastore
        - Update VM XML definition
        - Update database
    """
    logger.debug(sys.path)
    vm_details = current.db.vm_data[vmid]
    datastore_id = vm_details["datastore_id"]
    logger.debug("Inside live disk migration block")

    try:
        (connection_object, domain) = getVirshDomainConn(vm_details)
        
        datastore = current.db.datastore[destination_datastore_id]
        vm_directory_path = datastore.system_mount_point + get_constant('vms') + '/' + vm_details.vm_identity
        logger.debug("Creating vm directory on other datastore...")
        if not os.path.exists (vm_directory_path):
            os.makedirs(vm_directory_path)
        diskpath = vm_directory_path + '/' + vm_details.vm_identity + '.qcow2'

        current_disk_path = vm_details.datastore_id.system_mount_point + get_constant('vms') + '/' + vm_details.vm_identity
        current_disk_file = current_disk_path + '/' + vm_details.vm_identity + '.qcow2'
        logger.debug(current_disk_file)

        xmlfile = domain.XMLDesc(0)

        if(live_migration==False):
            rc = os.system("cp %s %s" % (current_disk_file, diskpath))

            if rc != 0:
                logger.error("Copy not successful")
                raise Exception("Copy not successful")
            else:
                logger.debug("Copied successfully")

        else:
            if domain.isActive:
                domain.undefine()
                
                root = etree.fromstring(xmlfile)
                target_elem = root.find("devices/disk/target")
                target_disk = target_elem.get('dev')
                #
                #           destxml = generate_blockcopy_xml(diskpath,target_disk)
                flag = VIR_DOMAIN_BLOCK_REBASE_SHALLOW | VIR_DOMAIN_BLOCK_REBASE_COPY
                domain.blockRebase(target_disk, diskpath, 0, flag)
                
                block_info_list = domain.blockJobInfo(current_disk_file,0)
                
                while(block_info_list['end'] != block_info_list['cur']):
                    logger.debug("time to sleep")
                    time.sleep(60)
                    block_info_list = domain.blockJobInfo(current_disk_file,0)
                
                domain.blockJobAbort(current_disk_file, VIR_DOMAIN_BLOCK_JOB_ABORT_PIVOT)

        source_elem = root.find("devices/disk/source")
        source_elem.set('file',diskpath)
        newxml_file = etree.tostring(root)
        domain = connection_object.defineXML(newxml_file)
        
        vm_details.update_record(datastore_id=destination_datastore_id)

        if os.path.exists (diskpath):
            os.remove(current_disk_file)
            os.rmdir(current_disk_path)
        connection_object.close()

        message = vm_details.vm_identity + " is migrated successfully to new datastore."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        undo_datastore_migration(vm_details, domain, diskpath, current_disk_file, vm_directory_path, datastore_id)
        connection_object.close()
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def undo_datastore_migration(vm_details, domain, diskpath, current_disk_file, vm_directory_path, datastore_id):
    """
    Undo migration in case of any issue
    """
    # undo databse changes
    vm_details.update_record(datastore_id=datastore_id)
    
    block_info_list = domain.blockJobInfo(current_disk_file,0)
    if(bool(block_info_list) == True):
        while(block_info_list['end'] != block_info_list['cur']):
            logger.debug("time to sleep")
            time.sleep(60)
            block_info_list = domain.blockJobInfo(current_disk_file,0)
        if(block_info_list['end'] == block_info_list['cur']):
            domain.blockJobAbort(current_disk_file)
    if os.path.exists (diskpath):
        os.remove(diskpath)
        os.rmdir(vm_directory_path)


def migrate(parameters):
    """
    Migrates VM to new host
    """
    vmid = parameters['vm_id']
    logger.debug("Inside migrate() function for vm_id: "+str(vmid))
    destination_host_id = parameters['destination_host']
    if parameters['live_migration'] == 'on':
        live_migration = True
    else:
        live_migration = False
    return migrate_domain(vmid, destination_host_id, live_migration)
  

def migrate_datastore(parameters):
    """
    Migrates VM to new datastore
    """
    logger.debug("Inside migrate_datastore() function")
    vmid = parameters['vm_id']
    destination_ds_id = parameters['destination_ds']
    if parameters['live_migration'] == 'on':
        live_migration = True
    else:
        live_migration = False
    
    return migrate_domain_datastore(vmid, destination_ds_id, live_migration)
  

def snapshot(parameters):
    """
    Snapshots a vm
    """
    logger.debug("Inside snapshot() function")
    vm_id = parameters['vm_id']
    snapshot_type = parameters['snapshot_type']
    try:

        vm_details = current.db.vm_data[vm_id]

        if is_pingable(str(vm_details.private_ip.private_ip)):

            logger.debug("VM is pingable. Starting to start with snapshotting...")
            if snapshot_type != current.SNAPSHOT_USER:
                snapshots = current.db((current.db.snapshot.vm_id == vm_id) & (current.db.snapshot.type == snapshot_type)).select()
                #Delete the existing Daily/Monthly/Yearly snapshot
                for snapshot_cron in snapshots:
                    logger.debug(snapshot_cron)
                    delete_snapshot({'vm_id':vm_id, 'snapshot_id':snapshot_cron.id})

            snapshot_name = get_datetime().strftime("%I:%M%p_%B%d,%Y")
            domain = getVirshDomain(vm_details)
            xmlDesc = "<domainsnapshot><name>%s</name></domainsnapshot>" % (snapshot_name)
            domain.snapshotCreateXML(xmlDesc, 0)
            message = "Snapshotted successfully."
            current.db.snapshot.insert(vm_id = vm_id, datastore_id = vm_details.datastore_id, snapshot_name = snapshot_name, type = snapshot_type)
            logger.debug("Task Status: SUCCESS Message: %s " % message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message)

        else:
                
            message = "Unable to ping VM before snapshoting: %s" % (vm_details.private_ip.private_ip)
            raise Exception("Unable to ping VM before snapshoting: %s" % (vm_details.private_ip.private_ip))

    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def revert(parameters):
    """
    Reverts to snapshot
    """
    logger.debug("Inside revert snapshot() function")
    vm_id = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db.vm_data[vm_id]

    try:
        domain = getVirshDomain(vm_details)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        domain.revertToSnapshot(snapshot, 0)

        message = "Reverted to snapshot successfully."
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def delete_snapshot(parameters):
    """
    Deletes a snapshot
    """
    logger.debug("Inside delete snapshot() function")
    vm_id = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))
    try:
        domain = getVirshDomain(vm_details)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        
        snapshot = None
        try:
            snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        except libvirtError:
            logger.debug("Snapshot %s not found" %(snapshot_name))
        
        if snapshot != None:
            snapshot.delete(0)        

        message = "Deleted snapshot successfully."
        logger.debug(message)
        current.db(current.db.snapshot.id == snapshotid).delete()
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def update_security_domain(vm_details, security_domain_id, xmlDesc=None):
    """
    Get new IP for given security domain.
    Update the VM XML with new mac_address and update the information in DB
    """
    # fetch new private IP from db from given security domain
    private_ip_info = _get_private_ip_mac(security_domain_id)
    
    # update vm config to add new mac address.
    root = etree.fromstring(xmlDesc)
    mac_elem = root.find("devices/interface[@type='bridge']/mac")
    mac_elem.set('address', private_ip_info.mac_addr)
    vlan_tag_elem = root.find("devices/interface[@type='bridge']/vlan/tag")
    vlan_tag_elem.set('id', private_ip_info.vlan.vlan_tag)
    
    # update NAT IP mapping, if public IP present
    if vm_details.public_ip:
        remove_mapping(vm_details.public_ip.public_ip, vm_details.private_ip.private_ip)
        create_mapping(vm_details.public_ip.public_ip, private_ip_info.private_ip)
    
    # update vm_data
    current.db(current.db.vm_data.id == vm_details.id).update(security_domain = security_domain_id, 
                                                              private_ip = private_ip_info.id)
    
    return etree.tostring(root)

def edit_vm_config(parameters):
    """
    Edits vm configuration
    """
    logger.debug("Inside edit vm config() function")
    vm_id = parameters['vm_id']    
    vm_details = current.db.vm_data[vm_id]
    message = ""
    try:
        connection_object, domain = getVirshDomainConn(vm_details) 

        if 'vcpus' in parameters:
            new_vcpus = int(parameters['vcpus'])
            domain.setVcpusFlags(new_vcpus, VIR_DOMAIN_VCPU_MAXIMUM)
            domain.setVcpusFlags(new_vcpus, VIR_DOMAIN_AFFECT_CONFIG)
            message += "Edited vCPU successfully."
            current.db(current.db.vm_data.id == vm_id).update(vCPU = new_vcpus)

        if 'ram' in parameters:
            new_ram = int(parameters['ram']) * 1024
            logger.debug(str(new_ram))
            domain.setMemoryFlags(new_ram, VIR_DOMAIN_MEM_MAXIMUM)
            domain.setMemoryFlags(new_ram, VIR_DOMAIN_AFFECT_CONFIG)
            message +=  " And edited RAM successfully."
            current.db(current.db.vm_data.id == vm_id).update(RAM = int(parameters['ram']))
            
        if 'public_ip' in parameters:
            enable_public_ip = parameters['public_ip']
            if enable_public_ip:
                public_ip_pool = _choose_random_public_ip()

                if public_ip_pool:
                    create_mapping(public_ip_pool.public_ip, vm_details.private_ip.private_ip)
                    current.db.vm_data[vm_id] = dict(public_ip=public_ip_pool.id)
                    message += "Edited Public IP successfully."
                    
                else:
                    raise Exception("Available Public IPs are exhausted.")
            else:
                remove_mapping(vm_details.public_ip.public_ip, vm_details.private_ip.private_ip)
                current.db.vm_data[vm_id] = dict(public_ip = None)
        
        if 'security_domain' in parameters:
            logger.debug('Updating security domain')
            xmlfile = update_security_domain(vm_details, parameters['security_domain'], domain.XMLDesc(0))
            domain = connection_object.defineXML(xmlfile)
            if domain.isActive():
                domain.reboot(0)
            message += "Edited security domain successfully"

        connection_object.close()
        logger.debug("Task Status: SUCCESS Message: %s " % message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def _get_clone_properties(vm_details, cloned_vm_details, vm_properties):
    """
    Get properties for Cloned VM.
    """
    datastore = _choose_datastore()
    vm_properties['datastore'] = datastore
    logger.debug("Datastore selected is: " + str(datastore))

    vm_properties['security_domain'] = vm_details.security_domain
    vm_properties['public_ip_req'] = False
    # Finds mac address, ip address and vnc port for the cloned vm
    _choose_mac_ip_vncport(vm_properties)
    logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + \
                         " VNCPORT is : " + str(vm_properties['vnc_port']))
  
    # Template and host of parent vm
    vm_properties['template'] = current.db(current.db.template.id == vm_details.template_id).select()[0]
    vm_properties['vm_host_details'] = current.db.host[vm_details.host_id]
    
    vm_properties['host'] = vm_properties['vm_host_details'].id
    # Creates a directory for the cloned vm
    logger.debug("Creating directory for cloned vm...")
    cloned_vm_directory_path = datastore.system_mount_point + '/' + get_constant('vms') + '/' + cloned_vm_details.vm_identity
    if not os.path.exists (cloned_vm_directory_path):
        os.makedirs(cloned_vm_directory_path)
        clone_file_parameters = ' --file ' + cloned_vm_directory_path + '/' + cloned_vm_details.vm_identity + '.qcow2'
    else:
        raise Exception("Directory with same name as vmname already exists.")

    # Creates a folder for additional disks of the cloned vm
    vm = current.db(current.db.vm_data.vm_identity == vm_details.vm_identity).select().first()
    disk_details_of_cloning_vm = current.db(current.db.attached_disks.vm_id == vm.id).select(orderby=current.db.attached_disks.attached_disk_name)
    logger.debug(disk_details_of_cloning_vm)
    already_attached_disks = len(disk_details_of_cloning_vm) 
    
    cloned_vm_extra_disks_directory = datastore.system_mount_point + '/' + get_constant('extra_disks_dir') + '/' + \
                                      datastore.ds_name +  '/' + cloned_vm_details.vm_identity
    if already_attached_disks > 0:
        if not os.path.exists (cloned_vm_extra_disks_directory):
            logger.debug("Making Directory")          
            os.makedirs(cloned_vm_extra_disks_directory)
    count = already_attached_disks
    while already_attached_disks > 0:
        
        disk_name = cloned_vm_details.vm_identity + '_disk' + str(count - already_attached_disks + 1) + '.qcow2'
        clone_file_parameters += ' --file ' + cloned_vm_extra_disks_directory + '/' + disk_name
        current.db.attached_disks.insert(vm_id = cloned_vm_details.id, 
                                          datastore_id = datastore.id , 
                                          attached_disk_name = disk_name, 
                                          capacity = disk_details_of_cloning_vm[count - already_attached_disks].capacity)
        already_attached_disks -= 1

    return (clone_file_parameters)
                

def migrate_clone_to_new_host(vm_details, cloned_vm_details, new_host_id_for_cloned_vm,vm_properties):
    """
    Migrates cloned vm to new host
    """
    try:
        new_host_ip_for_cloned_vm = current.db.host[new_host_id_for_cloned_vm].host_ip.private_ip
        logger.debug("New host ip for cloned vm is: " + str(new_host_ip_for_cloned_vm))
        flags = VIR_MIGRATE_PEER2PEER|VIR_MIGRATE_PERSIST_DEST|VIR_MIGRATE_UNDEFINE_SOURCE|VIR_MIGRATE_OFFLINE|VIR_MIGRATE_UNSAFE
        logger.debug("Clone currently on: " + str(vm_details.host_id.host_ip))
        (current_host_connection_object, domain) = getVirshDomainConn(None, vm_details.host_id.host_ip, cloned_vm_details.vm_identity)
        logger.debug("Starting to migrate cloned vm to host " + str(new_host_ip_for_cloned_vm))

        domain.migrateToURI("qemu+ssh://root@" + new_host_ip_for_cloned_vm + "/system", flags , None, 0)
        current_host_connection_object.close()
        logger.debug("Successfully migrated cloned vm to host " + str(new_host_ip_for_cloned_vm))
        cloned_vm_details.update_record(host_id = new_host_id_for_cloned_vm)
        vm_properties['host'] = new_host_id_for_cloned_vm
        return True
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        logger.debug("Error: " + message)
        return False
        

def clone(vmid):
    """
    Clones vm
    """
    vm_properties = {}
    logger.debug("Inside clone() function")
    cloned_vm_details = current.db.vm_data[vmid]
    vm_details = current.db(current.db.vm_data.id == cloned_vm_details.parent_id).select().first()
    try:
        domain = getVirshDomain(vm_details)
        if domain.info()[0] != VIR_DOMAIN_SHUTOFF:
            raise Exception("VM is not shutoff. Check vm status.")

        clone_file_parameters = _get_clone_properties(vm_details, cloned_vm_details, vm_properties)
        logger.debug("cloned vm properties after clone_file_parameters" + str(vm_properties))
        host = vm_properties['vm_host_details']
        logger.debug("host is: " + str(host))
        logger.debug("host details are: " + str(host))
        (used_ram, used_cpu) = host_resources_used(host.id)
        logger.debug("uram: " + str(used_ram) + " used_cpu: " + str(used_cpu) + " host ram: " + str(host.RAM) +" host cpu: " + str(host.CPUs))
        host_ram_after_200_percent_overcommitment = math.floor((host.RAM * 1024) * 2)
        host_cpu_after_200_percent_overcommitment = math.floor(host.CPUs * 2)
        logger.debug("host_ram_after_200_percent_overcommitment in MB " + str(host_ram_after_200_percent_overcommitment))
        logger.debug("host_cpu_after_200_percent_overcommitment " + str(host_cpu_after_200_percent_overcommitment))
        logger.debug("Available RAM on host: %s, Requested RAM: %s" % ((host_ram_after_200_percent_overcommitment - used_ram), vm_details.RAM))
        logger.debug("Available CPUs on host: %s, Requested CPU: %s " % ((host_cpu_after_200_percent_overcommitment - used_cpu), vm_details.vCPU))
        

        if((( host_ram_after_200_percent_overcommitment - used_ram) >= vm_details.RAM) and ((host_cpu_after_200_percent_overcommitment - used_cpu) >= vm_details.vCPU) and (vm_details.vCPU <= host.CPUs)):
            clone_command = "virt-clone --original " + vm_details.vm_identity + " --name " + cloned_vm_details.vm_identity + \
                        clone_file_parameters + " --mac " + vm_properties['mac_addr']
            command_output = execute_remote_cmd(vm_details.host_id.host_ip.private_ip, 'root', clone_command, None, True)
            logger.debug(command_output)
            logger.debug("Updating db after cloning")
            update_db_after_vm_installation(cloned_vm_details, vm_properties, parent_id = vm_details.id)
            message = "Cloned successfully. "

            try:
                new_host_id_for_cloned_vm = find_new_host(cloned_vm_details.RAM, cloned_vm_details.vCPU)
                if new_host_id_for_cloned_vm != host.id:
                    if migrate_clone_to_new_host(vm_details, cloned_vm_details, new_host_id_for_cloned_vm,vm_properties):
                        message += "Found new host and migrated successfully."
                    else:
                        message += "Found new host but not migrated successfully."
                else:
                    message += "New host selected to migrate cloned vm is same as the host on which it currently resides."
            except:
                message += "Could not find host to migrate cloned vm."
        
            logger.debug("Task Status: SUCCESS Message: %s " % message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message)

        else:
            raise Exception("Host resources exhausted. Migrate the host vms and then try.")        
    except:
        _free_vm_properties(cloned_vm_details, vm_properties)
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def attach_extra_disk(parameters):
    """
    Attaches extra disk to VM
    """
    logger.debug("Inside attach extra disk() function")
    vmid = parameters['vm_id']
    disk_size = parameters['disk_size']
    vm_details = current.db.vm_data[vmid]
    logger.debug(str(vm_details))

    try:
        if (serve_extra_disk_request(vm_details, disk_size, vm_details.host_id.host_ip.private_ip)):
            current.db(current.db.vm_data.id == vmid).update(extra_HDD = vm_details.extra_HDD + disk_size)
            message = "Attached extra disk successfully"
            logger.debug(message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message) 
        else:
            message = " Your request for additional HDD could not be completed at this moment. Check logs."
            logger.debug("Task Status: SUCCESS Message: %s " % message)
            return (current.TASK_QUEUE_STATUS_FAILED, message) 
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def get_vm_image_location(datastore_id, vm_identity):
    """
    Get the file path for qcow2 image of a VM
    """
    datastore = current.db.datastore[datastore_id]
    vm_directory_path = datastore.system_mount_point + '/' + get_constant('vms') + '/' + vm_identity
    vm_image_name = vm_directory_path + '/' + vm_identity + '.qcow2'
    
    image_present = True if os.path.exists(vm_image_name) else False
    
    return (vm_image_name, image_present)

def get_extra_disk_location(datastore_id, vm_identity, disk_name, get_disk_size=False):
    """
    Get the file path for qcow2 image of teh extra disk
    """
    datastore = current.db.datastore[datastore_id]
    if datastore:
        vm_extra_disks_directory_path = datastore.system_mount_point + '/' + get_constant('extra_disks_dir') + '/' + \
                                        datastore.ds_name + '/' + vm_identity
        ext = '' if disk_name.endswith('.qcow2') else '.qcow2'
        disk_image_path = vm_extra_disks_directory_path + '/' + disk_name + ext
        image_present = True if os.path.exists(disk_image_path) else False
    
        disk_size = 0
        if image_present & get_disk_size:
            command = "qemu-img info " + disk_image_path + " | grep 'virtual size'"
            ret = os.popen(command).read() # Returns e.g. virtual size: 40G (42949672960 bytes)
            disk_size = int(ret[ret.index(':')+1:ret.index('G ')].strip())
            
        return (disk_image_path, image_present, disk_size)
    else:
        return (None, False, 0)


def launch_existing_vm_image(vm_details):
    """
    Launch existing VM image
        - Choose new private_ip & mac_addr if not provided
        - Get location for VM image
        - Launch VM on given host
        - Attach extra disk to VM if defined
        - Create mapping between public IP and private IP if required
    """
    logger.debug('Launch existing VM image')
    vm_properties = {}
    vm_properties['ram'] = vm_details.RAM
    vm_properties['vcpus'] = vm_details.vCPU
    vm_properties['security_domain'] = vm_details.security_domain
    
    #If Private IP was already chosen previously and DHCP entry is done
    if vm_details.private_ip != None:
        private_ip_info = current.db.private_ip_pool[vm_details.private_ip]
        if private_ip_info:
            vm_properties['private_ip'] = private_ip_info.private_ip
            vm_properties['mac_addr'] = private_ip_info.mac_addr
            vm_properties['vlan_name']  = private_ip_info.vlan.name
            vm_properties['vlan_tag'] = private_ip_info.vlan.vlan_tag
    
    if vm_details.public_ip == None:
        vm_properties['public_ip_req'] = False
    else:
        vm_properties['public_ip_req'] = True
        if vm_details.public_ip.is_active:
            vm_properties['public_ip'] = vm_details.public_ip.public_ip

    _choose_mac_ip_vncport(vm_properties)

    vm_properties['template'] = current.db.template[vm_details.template_id]
    vm_properties['datastore'] = current.db.datastore[vm_details.datastore_id]
    vm_properties['host'] = find_new_host(vm_details.RAM, vm_details.vCPU)
    
    (vm_image_name, image_present) = get_vm_image_location(vm_details.datastore_id, vm_details.vm_identity)
    if image_present:
        launch_vm_on_host(vm_details, vm_image_name, vm_properties)
        
        #Check if extra disk needs to be attached
        attached_disks = current.db((current.db.attached_disks.vm_id == vm_details.id)).select()
        if attached_disks:
            #Extra disk to be attached to the VM
            host_ip = current.db.host[vm_properties['host']].host_ip.private_ip
            disk_counter = 1
            for attached_disk in attached_disks:
                disk_size = attach_disk(vm_details, attached_disk.attached_disk_name, host_ip, disk_counter, True)
                current.db(current.db.attached_disks.vm_id == attached_disk.vm_id and 
                           current.db.attached_disks.attached_disk_name==attached_disk.attached_disk_name
                           ).update(capacity = disk_size)
                vm_details.extra_HDD += disk_size
                disk_counter += 1
                
        #Create mapping of Private_IP and Public_IP
        if vm_properties['public_ip_req']:
            create_mapping(vm_properties['public_ip'], vm_properties['private_ip'])

        update_db_after_vm_installation(vm_details, vm_properties)
        
def save_vm_as_template(parameters):
    """
    Save VM as template
    If template for given VM already exists, replace with new template.
    """
    logger.debug("Inside save_as_template() function")
    vm_id = parameters['vm_id']
    vm_data = current.db.vm_data[vm_id]
    user_list = []
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))

    try:
        (is_templated_created, new_template, old_template) = create_new_template(vm_details)
        if (is_templated_created):
            #remove old template
            if os.path.exists (old_template):
                os.remove(old_template)
            else:
                for user in current.db(current.db.user_vm_map.vm_id == vm_id).select(current.db.user_vm_map.user_id):
                    user_list.append(user.user_id)
            
                new_template_id = current.db.template.insert(name = vm_data.vm_name + "_template" ,
                                   os = vm_data.template_id.os ,
                                   os_name = vm_data.template_id.os_name ,
                                   os_version = vm_data.template_id.os_version ,
                                   os_type = vm_data.template_id.os_type ,
                                   arch = vm_data.template_id.arch ,
                                   hdd = vm_data.template_id.hdd ,
                                   hdfile = new_template ,
                                   type = vm_data.template_id.type ,
                                   tag = vm_data.vm_name + "_template" ,
                                   datastore_id = vm_data.template_id.datastore_id,
                                   owner = user_list)

            current.db.vm_data[vm_id] = dict(saved_template = new_template_id)
            message = "User Template saved successfully"
            logger.debug(message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message)
        else:
            message = " Vm Template not saved "
            logger.debug("Task Status: %s " % message)
            return (current.TASK_QUEUE_STATUS_FAILED, message)
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())

def delete_template(parameters):
    """
    Delete template
    """
    logger.debug("Inside delete_template() function")
    template_id = parameters['template_id']
    template_details = current.db.template[template_id]
    template_path = template_details["hdfile"]
    if os.path.exists(template_path):
        os.remove(template_path)

    # set value in db also
    parent_vm = current.db.vm_data(saved_template = template_id)
    if parent_vm:
        parent_vm.update_record(saved_template = None)
    del current.db.template[template_id]
        
    return (current.TASK_QUEUE_STATUS_SUCCESS, "")
   
def create_new_template(vm_details):
    """
    Create a new template from the VM image
        - Create template directory
        - Copy VM Image to directory(Live copy if VM is running)
        - Update database to define new template
    """
    try:
        (connection_object, domain) = getVirshDomainConn(vm_details)
        xmlfile = domain.XMLDesc(0)
        logger.debug("connection object created")
        datastore = _choose_datastore()
        logger.debug(datastore)
        new_template_dir = datastore.system_mount_point + '/' +get_constant('templates_dir') + '/' + vm_details.requester_id.first_name
        logger.debug("Creating user template directory...")
        if not os.path.exists (new_template_dir):
            os.makedirs(new_template_dir)
        template = new_template_dir + '/' + vm_details.vm_identity + '_template.qcow2'
        template_location =  '/' + vm_details.requester_id.first_name + '/' + vm_details.vm_identity + '_template.qcow2'
        old_template = new_template_dir + '/' + vm_details.vm_identity + '_template_old.qcow2'
        if os.path.exists (template):
            # move template to some other path
            logger.debug("move template to some other file")
            shutil.move(template, old_template)       
        logger.debug("template " + template)

        current_disk_path = vm_details.datastore_id.system_mount_point + get_constant('vms') + '/' + vm_details.vm_identity
        current_disk_file = current_disk_path + '/' + vm_details.vm_identity + '.qcow2'
        
        if (vm_details.status == current.VM_STATUS_RUNNING or vm_details.status == current.VM_STATUS_SUSPENDED):
            logger.debug("vm is active in db")
            if domain.isActive():
              
                domain.undefine()
                
                root = etree.fromstring(xmlfile)
                target_elem = root.find("devices/disk/target")
                target_disk = target_elem.get('dev')
                
                flag = VIR_DOMAIN_BLOCK_REBASE_SHALLOW | VIR_DOMAIN_BLOCK_REBASE_COPY
                domain.blockRebase(target_disk, template, 0, flag)
                block_info_list = domain.blockJobInfo(current_disk_file,0)
                
                while(block_info_list['end'] != block_info_list['cur']):
                    logger.debug("time to sleep")
                    time.sleep(60)
                    block_info_list = domain.blockJobInfo(current_disk_file,0)

                domain.blockJobAbort(current_disk_file)
                domain = connection_object.defineXML(xmlfile)

                connection_object.close()
                return (True, template_location, old_template)
            else:
                logger.debug("domain is not running on host")
                return (False, template_location, old_template)

        elif(vm_details.status == current.VM_STATUS_SHUTDOWN):
            if domain.isActive():
                logger.debug("Domain is still active...Please try again after some time!!!")
                return (False, template_location, old_template)
            else:
                logger.debug("copying")
                copy_command = "cp "+current_disk_file+" "+template
                logger.debug("copy_command"+copy_command)
                #rc = os.system("cp %s %s" % (current_disk_file, template))
                logger.debug("copy command running on " + vm_details.host_id.host_ip.private_ip + " host")
                command_output = execute_remote_cmd(vm_details.host_id.host_ip.private_ip, 'root', copy_command)
                logger.debug(command_output)

                #if rc != 0:
                #    logger.error("Copy not successful")
                #    raise Exception("Copy not successful")
                #    return (False, template, old_template)
                #else:
                #    logger.debug("Copied successfully")
                #    return (True, template, old_template)
                return (True, template_location, old_template)

    except:
        if not domain.isPersistent():
            domain = connection_object.defineXML(xmlfile)
        connection_object.close()
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (False, template_location, old_template)
