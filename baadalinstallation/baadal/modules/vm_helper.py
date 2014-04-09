# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
###################################################################################

import sys, math, shutil, paramiko, traceback, libvirt
import xml.etree.ElementTree as etree
from libvirt import *  # @UnusedWildImport
from helper import *  # @UnusedWildImport

# Chooses datastore from a list of available datastores
def choose_datastore():

    datastores = current.db(current.db.datastore.id >= 0).select(orderby = current.db.datastore.used)
 
    if(len(datastores) == 0):
        raise Exception("No datastore found.")
    else:
        return datastores[0]

#Returns resources utilization of a host in MB,Count
def host_resources_used(host_id):
    RAM = 0.0
    CPU = 0.0
    vms = current.db((current.db.vm_data.host_id == host_id) & (current.db.vm_data.status != current.VM_STATUS_UNKNOWN) &  (current.db.vm_data.status != current.VM_STATUS_IN_QUEUE)).select()
    logger.debug("vms selected are: " + str(vms))
    for vm_data in vms:
        RAM += vm_data.RAM
        CPU += vm_data.vCPU
    
    return (math.ceil(RAM),math.ceil(CPU))

def set_portgroup_in_vm(domain, portgroup, host_ip):
    connection_object = libvirt.open("qemu+ssh://root@" + host_ip + "/system")
    dom = connection_object.lookupByName(domain)
    xml = etree.fromstring(dom.XMLDesc(0))
    source_network_element = xml.find('.//interface/source')
    logger.debug("source network is " + etree.tostring(source_network_element))
    source_network_element.set('portgroup', portgroup)
    logger.debug("source network is " + etree.tostring(source_network_element))
    domain = connection_object.defineXML(etree.tostring(xml))
    domain.destroy()
    domain.create()
    domain.isActive()
    connection_object.close()
    
def get_private_ip_mac(security_domain_id):
    vlans = current.db(current.db.security_domain.id == security_domain_id)._select(current.db.security_domain.vlan)
    private_ip_pool = current.db((current.db.private_ip_pool.vm_id == None) & 
                         (current.db.private_ip_pool.vlan.belongs(vlans))).select(orderby='<random>').first()

    if private_ip_pool:
        return(private_ip_pool.private_ip, private_ip_pool.mac_addr, private_ip_pool.vlan.name)
    else:
        sd = current.db.security_domain[security_domain_id]
        raise Exception(("Available MACs are exhausted for security domain '%s'." % sd.name))

# Chooses mac address, ip address and vncport for a vm to be installed
def choose_mac_ip(vm_properties):

    private_ip_info = get_private_ip_mac(vm_properties['security_domain'])
    vm_properties['private_ip'] = private_ip_info[0]
    vm_properties['mac_addr']   = private_ip_info[1]
    vm_properties['vlan_name']  = private_ip_info[2]

    if vm_properties['public_ip_req']:
        public_ip_pool = current.db(current.db.public_ip_pool.vm_id == None).select(orderby='<random>').first()
        if public_ip_pool:
            vm_properties['public_ip'] = public_ip_pool.public_ip
        else:
            raise Exception("Available Public IPs are exhausted.")
    else:
        vm_properties['public_ip'] = current.PUBLIC_IP_NOT_ASSIGNED


def choose_mac_ip_vncport(vm_properties):
    
    choose_mac_ip(vm_properties)

    start_range = int(get_constant('vncport_start_range')) 
    end_range = int(get_constant('vncport_end_range'))
    vnc_ports_taken = current.db().select(current.db.vm_data.vnc_port)
    while True:
        random_vnc_port = random.randrange(start_range, end_range, 1)
        if not random_vnc_port in vnc_ports_taken:
            break;
    vm_properties['vnc_port'] = str(random_vnc_port)

#Returns all the host running vms of particular run level
def find_new_host(RAM, vCPU):
    hosts = current.db(current.db.host.status == 1).select() 
    for host in hosts:
        logger.debug("checking host="+host.host_name)
        (uram, ucpu)=host_resources_used(host.id)
        logger.debug("uram "+str(uram)+" ucpu "+str(ucpu)+" hram "+ str(host.RAM)+" hcpu "+ str(host.CPUs))
        if(((host.RAM*1024 - uram) >= RAM) & ((host.CPUs - ucpu) >= vCPU)):
            return host.id

    #If no suitable host found
    raise Exception("No active host is available for a new vm.")
    

# Allocates vm properties ( datastore, host, ip address, mac address, vnc port, ram, vcpus)
def allocate_vm_properties(vm_details):
    
    logger.debug("Inside allocate_vm_properties()...")
    vm_properties = {}

    vm_properties['datastore'] = choose_datastore()
    logger.debug("Datastore selected is: " + str(vm_properties['datastore']))

    vm_properties['host'] = find_new_host(vm_details.RAM, vm_details.vCPU)
    logger.debug("Host selected is: " + str(vm_properties['host']))

    vm_properties['public_ip_req'] = False if (vm_details.public_ip == current.PUBLIC_IP_NOT_ASSIGNED) else True
    vm_properties['security_domain'] = vm_details.security_domain
    choose_mac_ip_vncport(vm_properties)

    logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + " VNCPORT is : "  \
                          + str(vm_properties['vnc_port']))
    
    vm_properties['ram'] = vm_details.RAM
    vm_properties['vcpus'] = vm_details.vCPU

    return vm_properties


# Executes command on host machine using paramiko module
def exec_command_on_host(machine_ip, user_name, command, password=None):

    try:
        logger.debug("Starting to establish SSH connection with host " + str(machine_ip))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username = user_name, password = password)
        stdin,stdout,stderr = ssh.exec_command(command)
        logger.debug(stdout.readlines())
        install_error_message = stderr.readlines()
        if (stdout.channel.recv_exit_status()) == 1:
            logger.error(install_error_message)
            raise Exception(install_error_message)
    except paramiko.SSHException:
        message = log_exception('Exception: ')
        raise Exception(message)
    finally:
        if ssh:
            ssh.close()
    return
    
# Creates a vm image
def create_vm_image(vm_details, datastore):

    # Creates a directory for the new vm
    logger.debug("Creating vm directory...")
    if not os.path.exists (get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity):
        os.makedirs(get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity)
    else:
        raise Exception("Directory with same name as vmname already exists.")

    # Finds the location of template image that the user has requested for its vm.               
    template = current.db.template[vm_details.template_id]
    vm_image_location = get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity + '/' + \
                        vm_details.vm_identity + '.qcow2'
            
    # Copies the template image from its location to new vm directory
    storage_type = config.get("GENERAL_CONF","storage_type")

    copy_command = 'ndmpcopy ' if storage_type == current.STORAGE_NETAPP_NFS else 'cp '
        
    logger.debug("Copy in progress when storage type is " + str(storage_type))
    command_to_execute = copy_command + datastore.path + '/' + get_constant("templates_dir") + '/' +  \
                         template.hdfile + ' ' + datastore.path + '/' + get_constant('vms') + '/' + \
                         vm_details.vm_identity + '/' + vm_details.vm_identity + '.qcow2'
    exec_command_on_host(datastore.ds_ip, datastore.username, command_to_execute, datastore.password)
    logger.debug("Copied successfully.")

    return (template, vm_image_location)

# Determines an install command for vm
def get_install_command(vm_details, vm_image_location, vm_properties):

    template = vm_properties['template']
    bus = ',bus=virtio'     
    optional = ' --import --os-type=' + template.os_type
    if (template.arch != 'amd64' and template.os_type == 'Linux'):
        optional = optional + ' --arch=' + template.arch + ' '
        
    
    format_command = ''
    if (template.type == 'QCOW2'):
        format_command = ',format=qcow2'
    
    variant_command = ''
    if (template.os_type == 'Windows'):
        variant_command = ' --os-variant=' + template.arch 
        bus = ''
    
    install_command = 'virt-install \
                     --name=' + vm_details.vm_identity + ' \
                     --ram=' + str(vm_properties['ram']) + ' \
                     --vcpus=' + str(vm_properties['vcpus']) + optional + variant_command + ' \
                     --disk path=' + vm_image_location + format_command + bus + ',cache=none' + ' \
                     --network network='+current.LIBVIRT_NETWORK+',model=virtio,mac=' + vm_properties['mac_addr'] + ' \
                     --graphics vnc,port=' + vm_properties['vnc_port'] + ',listen=0.0.0.0,password=duolc \
                     --noautoconsole \
                     --description \
                     --autostart \
                     --force' 

    return install_command 

# Generates xml
def generate_xml(diskpath,target_disk):

    root_element = etree.Element('disk',attrib = {'type':'block','device':'disk'})
    etree.SubElement(root_element, 'driver',attrib = {'name':'qemu','cache':'none', 'type':'qcow2'})
    etree.SubElement(root_element, 'source', attrib = {'dev':diskpath})
    etree.SubElement(root_element, 'target', attrib = {'dev': target_disk})

    return (etree.tostring(root_element))
      
# Attaches a disk with vm
def attach_disk(vmname, disk_name, size, hostip, datastore, already_attached_disks):
   
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + hostip + "/system")
        domain = connection_object.lookupByName(vmname)
        #already_attached_disks = len(current.db(current.db.attached_disks.vm_id == vm.id).select()) 
        logger.debug("Value of alreadyattached is : " + str(already_attached_disks))

        if not os.path.exists (get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name \
                               +  '/' +vmname):
            logger.debug("Making Directory")          
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + '/'  \
                         + vmname)

        diskpath = get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + "/" + vmname \
                   + "/" + disk_name

        # Create a new image for the new disk to be attached
        command= "qemu-img create -f qcow2 "+ diskpath + " " + str(size) + "G"
        output = os.system(command)
        if output != 0:
            return False
            
        # Attaching disk to vm using libvirt API
        target_disk = "vd" + chr(97 + already_attached_disks + 1)
        xmlDescription = generate_xml(diskpath, target_disk)
        domain.attachDevice(xmlDescription)
        xmlfile = domain.XMLDesc(0)
        domain = connection_object.defineXML(xmlfile)
        domain.reboot(0)
        domain.isActive()
        logger.debug("The disk has been attached successfully.")
        connection_object.close()
        return True
    except:
        logger.exception('Exception: ') 
        return False

# Serves extra disk request and updates db
def serve_extra_disk_request(vm_details, disk_size, host_ip):

    logger.debug("Starting to serve extra disk request...")
    datastore = choose_datastore()
    already_attached_disks = len(current.db(current.db.attached_disks.vm_id == vm_details.id).select()) 
    disk_name = vm_details.vm_identity + "_disk" + str(already_attached_disks + 1) + ".qcow2"  

    if (attach_disk(vm_details.vm_identity, disk_name, disk_size, host_ip, datastore, already_attached_disks)):
        current.db.attached_disks.insert(vm_id = vm_details.id, datastore_id = datastore.id , attached_disk_name = disk_name, capacity = disk_size) 
        return True
    else:
        return False

# Launches a vm on host
def launch_vm_on_host(vm_details, vm_image_location, vm_properties):

    attach_disk_status_message = ''
    install_command = get_install_command(vm_details, vm_image_location, vm_properties)  
    # Starts installing a vm
    host_ip = current.db.host[vm_properties['host']].host_ip
    logger.debug("Installation started...")
    logger.debug("Host is "+ host_ip)
    logger.debug("Installation command : " + install_command)
    exec_command_on_host(host_ip, 'root', install_command)
    set_portgroup_in_vm(vm_details['vm_identity'],vm_properties['vlan_name'],host_ip)

    # Serving HDD request
    if (int(vm_details.extra_HDD) != 0):
        if (serve_extra_disk_request(vm_details, vm_details.extra_HDD, host_ip)):
            message = "Attached extra disk successfully."
            attach_disk_status_message += message
            logger.debug(message)
        else:
            attach_disk_status_message += "Attached extra disk failed."
    return attach_disk_status_message

# Checks if a newly created vm is defined
def check_if_vm_defined(hostip, vmname):

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

# Frees vm properties
def free_vm_properties(vm_details):

    if vm_details.host_id:
        if check_if_vm_defined(vm_details.host_id.host_ip, vm_details.vm_name):
            connection_object = libvirt.openReadOnly('qemu+ssh://root@'+ vm_details.host_id.host_ip +'/system')
            domain = connection_object.lookupByName(vm_details.vm_name)
            domain.undefine()
            connection_object.close()

    if os.path.exists (get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity):
        shutil.rmtree(get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity)
    return
    

# Updates db after a vm is installed successfully
def update_db_after_vm_installation(vm_details, vm_properties, parent_id = None):

    hostid = vm_properties['host']
    datastore = vm_properties['datastore']
    template_hdd = vm_properties['template'].hdd
    logger.debug("Inside update db after installation")
    logger.debug(str(hostid))

    # Updating the used entry of datastore
    current.db(current.db.datastore.id == datastore.id).update(used = int(datastore.used) + int(vm_details.extra_HDD) +        
                                                                int(template_hdd))

    current.db(current.db.private_ip_pool.private_ip == vm_properties['private_ip']).update(vm_id = vm_details.id)
    if vm_properties['public_ip_req']:
        current.db(current.db.public_ip_pool.public_ip == vm_properties['public_ip']).update(vm_id = vm_details.id)
    # vm_status (function : status) :- (install : running) ; (clone : shutdown)
    if parent_id:
        vm_status = current.VM_STATUS_SHUTDOWN
    else:
        vm_status = current.VM_STATUS_RUNNING

    # Update vm_data table
    current.db(current.db.vm_data.id == vm_details.id).update( host_id = hostid, 
                                                               datastore_id = datastore.id, 
                                                               private_ip = vm_properties['private_ip'], 
                                                               vnc_port = vm_properties['vnc_port'],
                                                               mac_addr = vm_properties['mac_addr'],
                                                               public_ip = vm_properties['public_ip'], 
                                                               start_time = get_datetime(), 
                                                               parent_id = parent_id,
                                                               status = vm_status)

    logger.debug("Updated db")    
    return


def create_NAT_IP_mapping(action, public_ip, private_ip):
    nat_ip = config.get("GENERAL_CONF","nat_ip")
    nat_user = config.get("GENERAL_CONF","nat_user")
    nat_script = config.get("GENERAL_CONF","nat_script_path")
    
    command = "bash %s %s %s %s"%(nat_script, action, public_ip, private_ip)
    
    exec_command_on_host(nat_ip, nat_user, command)
    
    
# Installs a vm
def install(parameters):
 
        vmid = parameters['vm_id']
        logger.debug("In install function...")
        vm_details = current.db.vm_data[vmid]

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
            assert(check_if_vm_defined(current.db.host[vm_properties['host']].host_ip, vm_details.vm_identity)), "VM is not installed. Check logs."

            if vm_properties['public_ip_req']:
                create_NAT_IP_mapping('add', vm_properties['public_ip'], vm_properties['private_ip'])

            # Update database after vm installation
            update_db_after_vm_installation(vm_details, vm_properties) 

            message = "VM is installed successfully." + attach_disk_status_message

            return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    

        except:            
            etype, value, tb = sys.exc_info()
            message = ''.join(traceback.format_exception(etype, value, tb, 10))
            logger.error("Exception " + message)
            free_vm_properties(vm_details)
            return (current.TASK_QUEUE_STATUS_FAILED, str(value))

# Starts a vm
def start(parameters):
    
    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.create()
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_RUNNING)
        connection_object.close()  
        message = vm_details.vm_identity + " is started successfully."
        logger.debug(message) 
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Suspends a vm
def suspend(parameters):

    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.suspend()
        connection_object.close()
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_SUSPENDED)       
        message = vm_details.vm_identity + " is suspended successfully." 
        logger.debug(message)       
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Resumes a vm
def resume(parameters):

    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.resume()
        connection_object.close()
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_RUNNING) 
        message = vm_details.vm_identity + " is resumed successfully."
        logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Destroys a vm forcefully
def destroy(parameters):

    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.destroy()
        connection_object.close()
        current.db(current.db.vm_data.id == vm_id).update(status = current.VM_STATUS_SHUTDOWN) 
        message = vm_details.vm_identity + " is destroyed successfully."
        logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Function to clean up database after vm deletion
def clean_up_database_after_vm_deletion(vm_details):
    
    logger.debug("Inside clean up function...")

    # moving vm image folder to archives folder
    if not os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('archives_dir')):
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('archives_dir'))
    source_file = get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity
    archive_filename = vm_details.vm_identity + str(get_datetime())
    logger.debug(archive_filename)
    destination_file = get_constant('vmfiles_path') + '/' + get_constant('archives_dir') + '/' + archive_filename
    shutil.move(source_file, destination_file)

    # removing hdd        
    if os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_identity):
        shutil.rmtree(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_identity)

    # updating the used entry of database
    current.db(current.db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                          (int(vm_details.extra_HDD) + int(vm_details.template_id.hdd)))
    # deleting entry of extra disk of vm
    current.db(current.db.attached_disks.vm_id == vm_details.id).delete()
    
def vm_has_snapshots(vm_id):
    if (current.db(current.db.snapshot.vm_id == vm_id).select()):
        return True
    else:
        return False

        
# Deletes a vm
def delete(parameters):

    vm_id = parameters['vm_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        logger.debug(str(vm_details.status))
        if (vm_details.status == current.VM_STATUS_RUNNING or vm_details.status == current.VM_STATUS_SUSPENDED):
            logger.debug("Vm is not shutoff. Shutting it off first.")
            domain.destroy()
        logger.debug("Starting to delete it...")
        domain.undefineFlags(VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA )
        connection_object.close()
        message = vm_details.vm_identity + " is deleted successfully."
        logger.debug(message)
        clean_up_database_after_vm_deletion(vm_details)
        current.db(current.db.vm_data.id == vm_id).delete()
        current.db.commit()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Migrate domain with snapshots
def migrate_domain_with_snapshots(vm_details, destination_host_ip, domain, domain_snapshots_list, current_snapshot_name, flags):

    # XML dump of snapshot(s) of the vm
    logger.debug("Starting to take xml dump of the snapshot(s) of the vm... ")
    if not os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity):
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity)
    for domain_snapshot in domain_snapshots_list:
        logger.debug("snapshot name is " + str(domain_snapshot))
        dump_xml_path = get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity + '/' + 'dump_' + domain_snapshot
        snapshot_dumpxml_command = 'virsh snapshot-dumpxml %s %s > %s' % ( vm_details.vm_identity, domain_snapshot, dump_xml_path)
        logger.debug("Taking xml dump of" + str(domain_snapshot))
        exec_command_on_host(vm_details.host_id.host_ip, 'root', snapshot_dumpxml_command)
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
        redefine_xml_path =  get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity + '/' + 'dump_' + domain_snapshot
        snapshot_redefine_command = 'virsh snapshot-create --redefine %s %s ' % (vm_details.vm_identity, redefine_xml_path)
        exec_command_on_host(destination_host_ip, 'root', snapshot_redefine_command)

    snapshot_current_command = 'virsh snapshot-current %s %s' % (vm_details.vm_identity, current_snapshot_name)
    exec_command_on_host(destination_host_ip, 'root', snapshot_current_command)

    return

# Delete directory created for storing dumpxml of vm snapshots
def clean_migration_directory(vm_details):

    if os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity):
        shutil.rmtree(get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity)

    return

# Undo the migration 
def undo_migration(vm_details, domain_snapshots_list, current_snapshot_name):

    if domain_snapshots_list:
        # Redefine the snapshots of the vm on the source host
        logger.debug("Starting to redefine all the snapshot(s) of the vm on the source host...")
        for domain_snapshot in domain_snapshots_list:
            redefine_xml_path =  get_constant('vmfiles_path') + '/' + get_constant('vm_migration_data') + '/' + vm_details.vm_identity + '/' + 'dump_' + domain_snapshot
            snapshot_redefine_command = 'virsh snapshot-create --redefine %s %s ' % (vm_details.vm_identity, redefine_xml_path)
            exec_command_on_host(vm_details.host_id.host_ip, 'root', snapshot_redefine_command)
        snapshot_current_command = 'virsh snapshot-current %s %s' % (vm_details.vm_identity, current_snapshot_name)
        exec_command_on_host(vm_details.host_id.host_ip, 'root', snapshot_current_command)
    # Delete directory created for storing dumpxml of vm snapshots
    clean_migration_directory(vm_details)

    return


# Migrate domain
def migrate_domain(vm_id, destination_host_id=None, live_migration=False):

    vm_details = current.db.vm_data[vm_id]
    domain_snapshots_list = []
    current_snapshot_name = ''
    if destination_host_id == None:
        destination_host_id = find_new_host(vm_details.RAM, vm_details.vCPU)

    destination_host_ip = current.db.host[destination_host_id]['host_ip']

    flags = VIR_MIGRATE_PEER2PEER|VIR_MIGRATE_PERSIST_DEST|VIR_MIGRATE_UNDEFINE_SOURCE
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
        current_host_connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = current_host_connection_object.lookupByName(vm_details.vm_identity)
        for snapshot in current.db(current.db.snapshot.vm_id == vm_id).select():
            logger.debug("snapshot:" + str(snapshot.snapshot_name))
            domain_snapshots_list.append(snapshot.snapshot_name)
        logger.debug("domain snapshot list is " + str(domain_snapshots_list))
    
        if domain_snapshots_list:
            current_snapshot = domain.snapshotCurrent(0)
            current_snapshot_name = current_snapshot.getName()
            migrate_domain_with_snapshots(vm_details, destination_host_ip, domain, domain_snapshots_list, current_snapshot_name, flags)
        else:
            domain.migrateToURI("qemu+ssh://root@" + destination_host_ip + "/system", flags , None, 0)

        current_host_connection_object.close()
        vm_details.update_record(host_id = destination_host_id)
        current.db.commit()
        
        # Delete directory created for storing dumpxml of vm snapshot
        clean_migration_directory(vm_details)

        message = vm_details.vm_identity + " is migrated successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        logger.debug(" Exception caused...vm details are : " + str(vm_details))
        undo_migration(vm_details, domain_snapshots_list, current_snapshot_name)
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)        
 

# Migrates a vm to a new host
def migrate(parameters):

    vmid = parameters['vm_id']
    destination_host_id = parameters['destination_host']
    if parameters['live_migration'] == 'on':
        live_migration = True
    else:
        live_migration = False
    return migrate_domain(vmid, destination_host_id, live_migration)
  

# Snapshots a vm
def snapshot(parameters):

    vm_id = parameters['vm_id']
    snapshot_type = parameters['snapshot_type']
    try:
        vm_details = current.db.vm_data[vm_id]
        snapshot_name = get_datetime().strftime("%I:%M%p_%B%d,%Y")
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        xmlDesc = "<domainsnapshot><name>%s</name></domainsnapshot>" % (snapshot_name)
        domain.snapshotCreateXML(xmlDesc, 0)
        connection_object.close()
        message = "Snapshotted successfully."
        if snapshot_type != current.SNAPSHOT_USER:
            snapshot_cron = current.db((current.db.snapshot.vm_id == vm_id) & (current.db.snapshot.type == snapshot_type)).select().first()
            #Delete the existing Daily/Monthly/Yearly snapshot
            if snapshot_cron:
                logger.debug(snapshot_cron)
                delete_snapshot({'vm_id':vm_id, 'snapshot_id':snapshot_cron.id})
        current.db.snapshot.insert(vm_id = vm_id, datastore_id = vm_details.datastore_id, snapshot_name = snapshot_name, type = snapshot_type)
        logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message) 

# Reverts to snapshot
def revert(parameters):
    
    logger.debug("Inside revert snapshot")
    vm_id = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db.vm_data[vm_id]
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        domain.revertToSnapshot(snapshot, 0)
        connection_object.close()
        message = "Reverted to snapshot successfully."
        logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Deletes a snapshot
def delete_snapshot(parameters):

    logger.debug("Inside delete snapshot")
    vm_id = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db.vm_data[vm_id]
    logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        snapshot.delete(0)
        connection_object.close()
        message = "Deleted snapshot successfully."
        logger.debug(message)
        current.db(current.db.snapshot.id == snapshotid).delete()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)


def update_security_domain(vm_details, security_domain_id, xmlDesc=None):
    # fetch new private IP from db from given security domain
    private_ip_info = get_private_ip_mac(security_domain_id)
    # update vm config to add new mac address.
    root = etree.fromstring(xmlDesc)
    mac_elem = root.xpath("devices/interface[@type='bridge']/mac")[0]
    mac_elem.set('address', private_ip_info[1])
    
    # update NAT IP mapping, if public IP present
    if vm_details.public_ip != current.PUBLIC_IP_NOT_ASSIGNED:
        create_NAT_IP_mapping('remove', vm_details.public_ip, vm_details.private_ip)
        create_NAT_IP_mapping('add', vm_details.public_ip, private_ip_info[0])
    
    # update vm_data, private_ip_pool
    current.db(current.db.private_ip_pool.private_ip == vm_details.private_ip).update(vm_id = None)
    current.db(current.db.private_ip_pool.private_ip == private_ip_info[0]).update(vm_id = vm_details.id)
    current.db(current.db.vm_data.id == vm_details.id).update(security_domain = security_domain_id, 
                                                              private_ip = private_ip_info[0], 
                                                              mac_addr = private_ip_info[1])
    
    return etree.tostring(root)

# Edits vm configuration
def edit_vm_config(parameters):

    vm_id = parameters['vm_id']    
    vm_details = current.db.vm_data[vm_id]
    message = ""
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)

        if 'vcpus' in parameters:
            new_vcpus = int(parameters['vcpus'])
            domain.setVcpusFlags(new_vcpus, VIR_DOMAIN_AFFECT_CONFIG)
            message += "Edited vCPU successfully."
            current.db(current.db.vm_data.id == vm_id).update(vCPU = new_vcpus)

        if 'ram' in parameters:
            new_ram = int(parameters['ram']) * 1024
            logger.debug(str(new_ram))
            domain.setMemoryFlags(new_ram, VIR_DOMAIN_AFFECT_CONFIG|VIR_DOMAIN_MEM_MAXIMUM)
            message +=  " And edited RAM successfully."
            current.db(current.db.vm_data.id == vm_id).update(RAM = int(parameters['ram']))
            
        if 'public_ip' in parameters:
            enable_public_ip = parameters['public_ip']
            if enable_public_ip:
                public_ip_pool = current.db(current.db.public_ip_pool.vm_id == None).select(orderby='<random>').first()
                if public_ip_pool:
                    create_NAT_IP_mapping('add', public_ip_pool.public_ip, vm_details.private_ip)
                    current.db.public_ip_pool[public_ip_pool.id] = dict(vm_id=vm_id)
                    current.db.vm_data[vm_id] = dict(public_ip=public_ip_pool.public_ip)
                    message += "Edited Public IP successfully."
                    
                else:
                    raise Exception("Available Public IPs are exhausted.")
            else:
                create_NAT_IP_mapping('remove', vm_details.public_ip, vm_details.private_ip)
                current.db(current.db.public_ip_pool.public_ip == vm_details.public_ip).update(vm_id = None)
                current.db.vm_data[vm_id] = dict(public_ip=current.PUBLIC_IP_NOT_ASSIGNED)
        
        if 'security_domain' in parameters:
            logger.debug('Updating security domain')
            xmlfile = update_security_domain(vm_details, parameters['security_domain'], domain.XMLDesc(0))
            domain = connection_object.defineXML(xmlfile)
            domain.reboot(0)
            domain.isActive()

        connection_object.close()
        logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

def get_clone_properties(vm_details, cloned_vm_details):

    vm_properties = {}

    datastore = choose_datastore()
    vm_properties['datastore'] = datastore
    logger.debug("Datastore selected is: " + str(datastore))

    vm_properties['security_domain'] = vm_details.security_domain
    vm_properties['public_ip_req'] = False
    # Finds mac address, ip address and vnc port for the cloned vm
    choose_mac_ip_vncport(vm_properties)
    logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + \
                         " VNCPORT is : " + str(vm_properties['vnc_port']))
  
    # Template and host of parent vm
    vm_properties['template'] = current.db(current.db.template.id == vm_details.template_id).select()[0]
    vm_properties['host'] = current.db.host[vm_details.host_id]

    # Creates a directory for the cloned vm
    logger.debug("Creating directory for cloned vm...")
    if not os.path.exists (get_constant('vmfiles_path') + get_constant('vms') + '/' + cloned_vm_details.vm_identity):
        os.makedirs(get_constant('vmfiles_path') + get_constant('vms') + '/' + cloned_vm_details.vm_identity)
        clone_file_parameters = ' --file ' + get_constant('vmfiles_path') + get_constant('vms') + '/' + \
                                cloned_vm_details.vm_identity + '/' + cloned_vm_details.vm_identity + '.qcow2'
    else:
        raise Exception("Directory with same name as vmname already exists.")

    # Creates a folder for additional disks of the cloned vm
    vm = current.db(current.db.vm_data.vm_identity == vm_details.vm_identity).select().first()
    already_attached_disks = len(current.db(current.db.attached_disks.vm_id == vm.id).select()) 

    if already_attached_disks > 0:
        if not os.path.exists (get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name \
                                  +  '/' + cloned_vm_details.vm_identity):
            logger.debug("Making Directory")          
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + '/'  \
                         + cloned_vm_details.vm_identity)

    while already_attached_disks > 0:
        clone_file_parameters += ' --file ' + get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' \
                                  + datastore.ds_name + '/' + cloned_vm_details.vm_identity + '/' + cloned_vm_details.vm_identity + \
                                  '_disk' + str(already_attached_disks + 1) + '.qcow2'
        already_attached_disks -= 1

    return (vm_properties, clone_file_parameters)
                
# Migrates cloned vm to new host
def migrate_clone_to_new_host(vm_details, cloned_vm_details, new_host_id_for_cloned_vm):

    try:
        new_host_ip_for_cloned_vm = current.db.host[new_host_id_for_cloned_vm]['host_ip']
        logger.debug("New host ip for cloned vm is: " + str(new_host_ip_for_cloned_vm))
        flags = VIR_MIGRATE_PEER2PEER|VIR_MIGRATE_PERSIST_DEST|VIR_MIGRATE_UNDEFINE_SOURCE|VIR_MIGRATE_OFFLINE
        logger.debug("Clone currently on: " + str(vm_details.host_id.host_ip))
        current_host_connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = current_host_connection_object.lookupByName(cloned_vm_details.vm_identity)
        logger.debug("Starting to migrate cloned vm to host " + str(new_host_ip_for_cloned_vm))
        domain.migrateToURI("qemu+ssh://root@" + new_host_ip_for_cloned_vm + "/system", flags , None, 0)
        logger.debug("Successfully migrated cloned vm to host " + str(new_host_ip_for_cloned_vm))
        cloned_vm_details.update_record(host_id = new_host_id_for_cloned_vm)
        return True
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        logger.debug("Error: " + message)
        return False
        
# Clones vm
def clone(vmid):

    cloned_vm_details = current.db.vm_data[vmid]
    vm_details = current.db(current.db.vm_data.id == cloned_vm_details.parent_id).select().first()
    try:
        (vm_properties, clone_file_parameters) = get_clone_properties(vm_details, cloned_vm_details)
        logger.debug("vm_properties: " + str(vm_properties))
        host = vm_properties['host']
        logger.debug("host is: " + str(host))
        logger.debug("host details are: " + str(host))
        (uram, ucpu) = host_resources_used(host.id)
        logger.debug("uram " + str(uram) + " ucpu " + str(ucpu) + " hram " + str(host.RAM) +" hcpu " + str(host.CPUs))
        if (((host.RAM*1024 - uram) >= cloned_vm_details.RAM) & ((host.CPUs - ucpu) >= cloned_vm_details.vCPU)):
            clone_command = "virt-clone --original " + vm_details.vm_identity + " --name " + cloned_vm_details.vm_identity + \
                        clone_file_parameters + " --mac " + vm_properties['mac_addr']
            exec_command_on_host(vm_details.host_id.host_ip, 'root', clone_command)
            logger.debug("Updating db after cloning")
            update_db_after_vm_installation(cloned_vm_details, vm_properties, parent_id = vm_details.id)
            message = "Cloned successfully. "

            try:
                new_host_id_for_cloned_vm = find_new_host(cloned_vm_details.RAM, cloned_vm_details.vCPU)
                if new_host_id_for_cloned_vm != cloned_vm_details.host_id:
                    if migrate_clone_to_new_host(vm_details, cloned_vm_details, new_host_id_for_cloned_vm):
                        message += "Found new host and migrated successfully."
                    else:
                        message += "Found new host but not migrated successfully."
                else:
                    message += "New host selected to migrate cloned vm is same as the host on which it currently resides."
            except:
                message += "Could not find host to migrate cloned vm."
        
            logger.debug(message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message)

        else:
            raise Exception("Host resources exhausted. Migrate the host vms and then try.")        
    except:
        etype, value, tb = sys.exc_info()
        message = ''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error("Exception " + message)
        free_vm_properties(cloned_vm_details)
        return (current.TASK_QUEUE_STATUS_FAILED, str(value)) 

# Attaches extra disk to VM
def attach_extra_disk(parameters):

    vmid = parameters['vm_id']
    disk_size = parameters['disk_size']
    vm_details = current.db.vm_data[vmid]
    logger.debug(str(vm_details))

    try:
        if (serve_extra_disk_request(vm_details, disk_size, vm_details.host_id.host_ip)):
            current.db(current.db.vm_data.id == vmid).update(extra_HDD = vm_details.extra_HDD + disk_size)
            message = "Attached extra disk successfully"
            logger.debug(message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message) 
        else:
            message = " Your request for additional HDD could not be completed at this moment. Check logs."
            logger.debug(message)
            return (current.TASK_QUEUE_STATUS_FAILED, message) 
    except:
        message = log_exception()
        return (current.TASK_QUEUE_STATUS_FAILED, message)            

def shutdown_baadal():
    logger.info('Starting Baadal Shutdown')
    vms = current.db(current.db.vm_data.status.belongs(current.VM_STATUS_RUNNING, current.VM_STATUS_SUSPENDED, current.VM_STATUS_SHUTDOWN)).select()
    for vm_detail in vms:
        try:
            snapshot({'vm_id':vm_detail.id, 'snapshot_type':current.SNAPSHOT_SYSTEM})
            logger.debug('Snapshot of %s completed successfully' %(vm_detail.vm_identity))
            suspend({'vm_id':vm_detail.id})
            logger.debug('%s suspended successfully' %(vm_detail.vm_identity))
        except:
            log_exception()
            pass
    return

def bootup_baadal():
    logger.info('Starting Baadal Bootup')
    vms = current.db(current.db.vm_data.status.belongs(current.VM_STATUS_RUNNING, current.VM_STATUS_SUSPENDED, current.VM_STATUS_SHUTDOWN)).select()
    for vm_detail in vms:
        sys_snapshot = current.db.snapshot(vm_id=vm_detail.id, type=current.SNAPSHOT_SYSTEM)
        if sys_snapshot:
            try:
                revert({'vm_id':vm_detail.id, 'snapshot_id':sys_snapshot['id']})
                logger.debug('Snapshot of %s reverted from %s successfully' %(vm_detail.vm_identity, sys_snapshot.snapshot_name))
                delete_snapshot({'vm_id':vm_detail.id, 'snapshot_id':sys_snapshot['id']})
                logger.debug('Snapshot %s deleted successfully' %(sys_snapshot.snapshot_name))
            except:
                log_exception()
                pass
    return
