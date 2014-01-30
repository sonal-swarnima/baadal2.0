# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

import sys, math, shutil, paramiko, traceback, libvirt
import xml.etree.ElementTree as etree
#from mail_handler import send_email_for_vm_creation
from libvirt import *  # @UnusedWildImport
from helper import *  # @UnusedWildImport

# Chooses datastore from a list of available datastores
def choose_datastore():

    datastores = current.db(current.db.datastore.id >= 0).select(orderby = current.db.datastore.used)
 
    if(len(datastores) == 0):
        raise Exception("No datastore found.")
    else:
        return datastores[0]
       
# Computes effective RAM and CPU
def compute_effective_ram_vcpu(RAM, vCPU, runlevel):

    effective_ram = 1024
    effective_cpu = 1
    divideby = 1

    if(runlevel == 0): 
        effective_ram = 0
        effective_cpu = 0
    else:

        if(runlevel == 1): 
            divideby = 1
        elif(runlevel == 2): 
            divideby = 2
        elif(runlevel == 3): 
            divideby = 4

        if(RAM/divideby >= 1024):
            effective_ram = RAM/divideby

        if(vCPU/divideby >= 1): 
            effective_cpu = vCPU/divideby

    return (effective_ram, effective_cpu)

# Finds the used host resources
def host_resources_used(hostid):

    RAM = 0.0
    CPU = 0.0

    vms = current.db(current.db.vm_data.host_id == hostid).select(current.db.vm_data.RAM,  current.db.vm_data.vCPU, 
                     current.db.vm_data.current_run_level)

    for vm in vms:
        (effective_ram, effective_cpu) = compute_effective_ram_vcpu(vm.RAM, vm.vCPU, vm.current_run_level)
        RAM = RAM + effective_ram
        CPU = CPU + effective_cpu

    host_ram = current.db(current.db.host.id == hostid).select(current.db.host.RAM)[0].RAM
    host_cpu = current.db(current.db.host.id == hostid).select(current.db.host.CPUs)[0].CPUs

    return (math.ceil(RAM), math.ceil(CPU), host_ram, host_cpu)

# Finds new host for a vm to be installed
def find_new_host(runlevel, RAM, vCPU):

    hosts = current.db(current.db.host.status == current.HOST_STATUS_UP).select() 

    if (len(hosts) == 0):
        raise Exception("No host found.")
    else:
        runlevel = int(runlevel)
        host_selected = None
        for host in hosts:
            current.logger.debug("Checking host = " + host.host_name)
            (used_ram,used_cpu,host_ram,host_cpu) = host_resources_used(host.id)
            current.logger.debug("used ram:" + str(used_ram) + " used cpu:" + str(used_cpu) + " host ram:" + str(host_ram) +  \
                                 " host cpu" + str(host_cpu))
            (effective_ram,effective_vcpu) = compute_effective_ram_vcpu(RAM,vCPU,runlevel)
            if(host_selected == None and ((used_ram + effective_ram) <= ((host_ram * 1024)))):
                host_selected = host

    if host_selected != None:
        return host_selected
    else:
        raise Exception("No active host is available for a new vm.")

def set_portgroup_in_vm(domain,portgroup,host_ip):
    conn = libvirt.open("qemu+ssh://root@" + host_ip + "/system")
    dom = conn.lookupByName(domain)
    xml = etree.fromstring(dom.XMLDesc(0))
    source_network_element = xml.find('.//interface/source')
    current.logger.debug("source network is "+etree.tostring(source_network_element))
    source_network_element.set('portgroup',portgroup)
    current.logger.debug("source network is "+etree.tostring(source_network_element))
    domain = conn.defineXML(etree.tostring(xml))
    domain.destroy()
    domain.create()
    domain.isActive()
    
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

    count = int(get_constant('vmcount')) 
    vm_properties['vnc_port'] = str(int(get_constant('vncport_range')) + count)
    update_constant('vmcount', count + 1)
    

# Allocates vm properties ( datastore, host, ip address, mac address, vnc port, ram, vcpus)
def allocate_vm_properties(vm_details):
    
    current.logger.debug("Inside allocate_vm_properties()...")
    vm_properties = {}

    vm_properties['datastore'] = choose_datastore()
    current.logger.debug("Datastore selected is: " + str(vm_properties['datastore']))

    vm_properties['host'] = find_new_host(vm_details.current_run_level, vm_details.RAM, vm_details.vCPU)
    current.logger.debug("Host selected is: " + str(vm_properties['host']))

    vm_properties['public_ip_req'] = False if (vm_details.public_ip == current.PUBLIC_IP_NOT_ASSIGNED) else True
    vm_properties['security_domain'] = vm_details.security_domain
    choose_mac_ip_vncport(vm_properties)

    current.logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + " VNCPORT is : "  \
                          + str(vm_properties['vnc_port']))
    
    (vm_properties['ram'], vm_properties['vcpus']) = compute_effective_ram_vcpu(vm_details.RAM, vm_details.vCPU, 1)

    return vm_properties


# Executes command on host machine using paramiko module
def exec_command_on_host(machine_ip, user_name, command, password=None):

    try:
        current.logger.debug("Starting to establish SSH connection with host " + str(machine_ip))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username = user_name, password = password)
        stdin,stdout,stderr = ssh.exec_command(command)
        current.logger.debug(stdout.readlines())
        install_error_message = stderr.readlines()
        if (stdout.channel.recv_exit_status()) == 1:
            current.logger.error(install_error_message)
            raise Exception(install_error_message)
    except paramiko.SSHException:
        etype, value, tb = sys.exc_info()
        message = ''.join(traceback.format_exception(etype, value, tb, 10))
        current.logger.error("Exception " + message)
        raise Exception(message)
    finally:
        if ssh:
            ssh.close()
    return
    
# Creates a vm image
def create_vm_image(vm_details, datastore):

    # Creates a directory for the new vm
    current.logger.debug("Creating vm directory...")
    if not os.path.exists (get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity):
        os.makedirs(get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity)
    else:
        raise Exception("Directory with same name as vmname already exists.")

    # Finds the location of template image that the user has requested for its vm.               
    template = current.db(current.db.template.id == vm_details.template_id).select()[0]
    template_location = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template.hdfile
    vm_image_location = get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity + '/' + \
                        vm_details.vm_identity + '.qcow2'
            
    # Copies the template image from its location to new vm directory
    config = get_config_file()
    storage_type = config.get("GENERAL_CONF","storage_type")

    if storage_type == current.STORAGE_NETAPP_NFS:
        command_to_execute = 'ndmpcopy ' + datastore.path + '/' + get_constant("templates_dir") + '/' +  \
                             template.hdfile + ' ' + datastore.path + '/' + get_constant('vms') + '/' + \
                             vm_details.vm_identity + '/' + vm_details.vm_identity + '.qcow2'
        current.logger.debug("Copy in progress (storage type =  netapp_nfs)...")
        exec_command_on_host(datastore.ds_ip, datastore.username, command_to_execute, datastore.password)
        current.logger.debug("Copied successfully.")
    else:
        current.logger.debug("Copy in progress (storage_type = linux_nfs)...")
        rcode = os.system('cp %s %s' % (template_location, vm_image_location))
        if rcode != 0:
            current.logger.error("Unsuccessful in copying image...")
            raise Exception("Unsuccessful in copying image...")
	else:
            current.logger.debug("Copied successfully.")

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
                     --disk path=' + vm_image_location + format_command + bus + ' \
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
        current.logger.debug("Value of alreadyattached is : " + str(already_attached_disks))

        if not os.path.exists (get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name \
                               +  '/' +vmname):
            current.logger.debug("Making Directory")          
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
        current.logger.debug("The disk has been attached successfully.")
        connection_object.close()
        return True
    except:
        etype, value, tb = sys.exc_info()
        trace = ''.join(traceback.format_exception(etype, value, tb, 10))
        message = "Check logs for error: " + trace
        current.logger.error(message) 
        return False

# Serves extra disk request and updates db
def serve_extra_disk_request(vm_details, disk_size, host_ip):

    current.logger.debug("Starting to serve extra disk request...")
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

    attach_disk_status_message = 'Your request for additional HDD is completed.'
    install_command = get_install_command(vm_details, vm_image_location, vm_properties)  
    # Starts installing a vm
    host_ip = vm_properties['host'].host_ip
    current.logger.debug("Installation started...")
    current.logger.debug("Host is "+ host_ip)
    current.logger.debug("Installation command : " + install_command)
    exec_command_on_host(host_ip, 'root', install_command)
    set_portgroup_in_vm(vm_details['vm_identity'],vm_properties['vlan_name'],host_ip)

    # Serving HDD request
    if (int(vm_details.extra_HDD) != 0):
        if (serve_extra_disk_request(vm_details, vm_details.extra_HDD, host_ip)):
            message = "Attached extra disk successfully"
            current.logger.debug(message)
        else:
            attach_disk_status_message = " Your request for additional HDD could not be completed at this moment. Check logs."
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

    if os.path.exists (get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity):
        shutil.rmtree(get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity)
    return
    

# Updates db after a vm is installed successfully
def update_db_after_vm_installation(vm_details, vm_properties, parent_id = None):

    hostid = vm_properties['host'].id
    datastore = vm_properties['datastore']
    template_hdd = vm_properties['template'].hdd
    current.logger.debug("Inside update db after installation")
    current.logger.debug(str(hostid))

    # Updating the count of vms on host
    count = current.db(current.db.host.id == hostid).select().first()['vm_count']
    current.logger.debug("Count is " + str(hostid))
    current.db(current.db.host.id == hostid).update(vm_count = count + 1)

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
                                                               current_run_level = 3, 
                                                               last_run_level = 3,
                                                               parent_id = parent_id,
                                                               status = vm_status)

    current.logger.debug("Updated db")    
    return


def create_NAT_IP_mapping(action, public_ip, private_ip):
    config = get_config_file()
    nat_ip = config.get("GENERAL_CONF","nat_ip")
    nat_user = config.get("GENERAL_CONF","nat_user")
    nat_script = config.get("GENERAL_CONF","nat_script_path")
    
    command = "sh %s %s %s %s"%(nat_script, action, public_ip, private_ip)
    
    exec_command_on_host(nat_ip, nat_user, command)
    
    
# Installs a vm
def install(parameters):
 
        vmid = parameters['vm_id']
        current.logger.debug("In install function...")
        vm_details = current.db.vm_data[vmid]

        try:
            # Fetches vm details from vm_data table
            current.logger.debug("VM details are: " + str(vm_details))
    
            # Calling allocate_vm_properties function
            vm_properties = allocate_vm_properties(vm_details)

            # Calling create_vm_image function
            (vm_properties['template'], vm_image_location) = create_vm_image(vm_details, vm_properties['datastore'])
         
            # Calling launch_vm_on_host
            attach_disk_status_message = launch_vm_on_host(vm_details, vm_image_location, vm_properties)       

            # Checking if vm has been installed successfully
            assert(check_if_vm_defined(vm_properties['host'].host_ip, vm_details.vm_identity)), "VM is not installed. Check logs."

            if vm_properties['public_ip_req']:
                create_NAT_IP_mapping('add', vm_properties['public_ip'], vm_properties['private_ip'])

            # Update database after vm installation
            update_db_after_vm_installation(vm_details, vm_properties) 

            message = "VM is installed successfully." + attach_disk_status_message

            return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    

        except:            
            etype, value, tb = sys.exc_info()
            message = ''.join(traceback.format_exception(etype, value, tb, 10))
            current.logger.error("Exception " + message)
            free_vm_properties(vm_details)
            return (current.TASK_QUEUE_STATUS_FAILED, str(value))

# Starts a vm
def start(parameters):
    
    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.create()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING)  
        message = vm_details.vm_identity + " is started successfully."
        current.logger.debug(message) 
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Suspends a vm
def suspend(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.suspend()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SUSPENDED)       
        message = vm_details.vm_identity + " is suspended successfully." 
        current.logger.debug(message)       
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Resumes a vm
def resume(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.resume()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING) 
        message = vm_details.vm_identity + " is resumed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Destroys a vm forcefully
def destroy(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        domain.destroy()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SHUTDOWN) 
        message = vm_details.vm_identity + " is destroyed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Function to clean up database after vm deletion
def clean_up_database_after_vm_deletion(vm_details):
    
    current.logger.debug("Inside clean up function...")

    # moving vm image folder to archives folder
    if not os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('archives_dir')):
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('archives_dir'))
    source_file = get_constant('vmfiles_path') + get_constant('vms') + '/' + vm_details.vm_identity
    archive_filename = vm_details.vm_identity + str(get_datetime())
    current.logger.debug(archive_filename)
    destination_file = get_constant('vmfiles_path') + '/' + get_constant('archives_dir') + '/' + archive_filename
    shutil.move(source_file, destination_file)

    # removing hdd        
    if os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_identity):
        shutil.rmtree(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_identity)

    # updating the count of guest vms on host
    count = current.db(current.db.host.id == vm_details.host_id).select().first()['vm_count']
    current.db(current.db.host.id == vm_details.host_id).update(vm_count = count - 1)

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

# Deletes all vm snapshots
def delete_vm_snapshots(vmid, domain):

    try:
        for row in current.db(current.db.snapshot.vm_id == vmid).select(current.db.snapshot.snapshot_name) :
            current.logger.debug(row.snapshot_name)
            snapshot = domain.snapshotLookupByName(row.snapshot_name, 0)
            snapshot.delete(0)
            current.logger.debug("Deleted " + row.snapshot_name + " snapshot successfully.")
    except:
        raise Exception("Could not delete snapshots. Try later")
        
# Deletes a vm
def delete(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        current.logger.debug(str(vm_details.status))
        if (vm_details.status == current.VM_STATUS_RUNNING or vm_details.status == current.VM_STATUS_SUSPENDED):
            current.logger.debug("Vm is not shutoff. Shutting it off first.")
            #domain.destroy()
        if (vm_has_snapshots(vmid)):
            delete_vm_snapshots(vmid, domain)
        current.logger.debug("Starting to delete it...")
        domain.undefine()
        message = vm_details.vm_identity + " is deleted successfully."
        current.logger.debug(message)
        clean_up_database_after_vm_deletion(vm_details)
        current.db(current.db.vm_data.id == vmid).delete()
        current.db.commit()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

def migrate_domain(vm_id, destination_host_id, live_migration=False):

    flags = VIR_MIGRATE_PEER2PEER|VIR_MIGRATE_TUNNELLED|VIR_MIGRATE_PERSIST_DEST|VIR_MIGRATE_UNDEFINE_SOURCE
    live_migration = False
    if live_migration:
        flags |= VIR_MIGRATE_LIVE

    current.logger.debug("Flags: " + str(flags))       
    vm_details = current.db(current.db.vm_data.id == vm_id).select().first()
    destination_host_ip = current.db.host[destination_host_id].host_ip
    current_host_connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
    domain = current_host_connection_object.lookupByName(vm_details.vm_identity)            
    domain.migrateToURI("qemu+ssh://root@" + destination_host_ip + "/system", flags , None, 0)
    current.logger.debug("Migrated successfully..")
    current.db(current.db.vm_data.id == vm_id).update(host_id = destination_host_id)
    vm_count_on_old_host = current.db(current.db.host.id == vm_details.host_id).select().first()['vm_count']
    current.db(current.db.host.id == vm_details.host_id).update(vm_count = vm_count_on_old_host - 1)
    vm_count_on_new_host = current.db(current.db.host.id == destination_host_id).select().first()['vm_count']
    current.db(current.db.host.id == destination_host_id).update(vm_count = vm_count_on_new_host + 1) 
    message = vm_details.vm_identity + " is migrated successfully."
    return message

# Migrates a vm to a new host
def migrate(parameters):

    vmid = parameters['vm_id']
    destination_host_id = parameters['destination_host']
    live_migration = False
    if 'live_migration' in parameters:
        live_migration = True
  
    try:
        message = migrate_domain(vmid, destination_host_id, live_migration)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message) 


# Snapshots a vm
def snapshot(parameters):

    vmid = parameters['vm_id']
    snapshot_type = parameters['snapshot_type']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        snapshot_name = get_datetime().strftime("%I:%M%p on %B %d,%Y")
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        datetime = get_datetime()
        xmlDesc = "<domainsnapshot><name>%s</name></domainsnapshot>" % (snapshot_name)
        domain.snapshotCreateXML(xmlDesc, 0)
        message = "Snapshotted successfully."
        if snapshot_type != current.SNAPSHOT_USER:
            snapshot_cron = current.db((current.db.snapshot.vm_id == vmid) & (current.db.snapshot.type == snapshot_type)).select().first()
            #Delete the existing Daily/Monthly/Yearly snapshot
            if snapshot_cron:
                current.logger.debug(snapshot_cron)
                delete_snapshot({'vm_id':vmid, 'snapshot_id':snapshot_cron.id})
        current.db.snapshot.insert(vm_id = vmid, datastore_id = vm_details.datastore_id, snapshot_name = snapshot_name, type = snapshot_type)
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message) 

# Reverts to snapshot
def revert(parameters):
    
    current.logger.debug("Inside revert snapshot")
    vmid = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        domain.revertToSnapshot(snapshot, 0)
        message = "Reverted to snapshot successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)

# Deletes a snapshot
def delete_snapshot(parameters):

    current.logger.debug("Inside delete snapshot")
    vmid = parameters['vm_id']
    snapshotid = parameters['snapshot_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)
        snapshot_name = current.db(current.db.snapshot.id == snapshotid).select().first()['snapshot_name']
        snapshot = domain.snapshotLookupByName(snapshot_name, 0)
        snapshot.delete(0)
        message = "Deleted snapshot successfully."
        current.logger.debug(message)
        current.db(current.db.snapshot.id == snapshotid).delete()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)


def update_security_domain(vm_details, security_domain_id, xmlDesc):
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

    vmid = parameters['vm_id']    
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    message = ""
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_identity)

        if 'vcpus' in parameters:
            new_vcpus = int(parameters['vcpus'])
            domain.setVcpusFlags(new_vcpus, VIR_DOMAIN_AFFECT_CONFIG)
            message += "Edited vCPU successfully."
            current.db(current.db.vm_data.id == vmid).update(vCPU = new_vcpus)

        if 'ram' in parameters:
            new_ram = int(parameters['ram']) * 1024
            current.logger.debug(str(new_ram))
            domain.setMemoryFlags(new_ram, VIR_DOMAIN_AFFECT_CONFIG|VIR_DOMAIN_MEM_MAXIMUM)
            message +=  " And edited RAM successfully."
            current.db(current.db.vm_data.id == vmid).update(RAM = int(parameters['ram']))
            
        if 'public_ip' in parameters:
            enable_public_ip = parameters['public_ip']
            if enable_public_ip:
                public_ip_pool = current.db(current.db.public_ip_pool.vm_id == None).select(orderby='<random>').first()
                if public_ip_pool:
                    create_NAT_IP_mapping('add', public_ip_pool.public_ip, vm_details.private_ip)
                    current.db.public_ip_pool[public_ip_pool.id] = dict(vm_id=vmid)
                    current.db.vm_data[vmid] = dict(public_ip=public_ip_pool.public_ip)
                    
                else:
                    raise Exception("Available Public IPs are exhausted.")
            else:
                create_NAT_IP_mapping('remove', vm_details.public_ip, vm_details.private_ip)
                current.db(current.db.public_ip_pool.public_ip == vm_details.public_ip).update(vm_id = None)
                current.db.vm_data[vmid] = dict(public_ip=current.PUBLIC_IP_NOT_ASSIGNED)
        
        if 'security_domain' in parameters:
            current.logger.debug('Updating security domain')
            xmlfile = update_security_domain(vm_details, parameters['security_domain'], domain.XMLDesc(0))
            domain = connection_object.defineXML(xmlfile)
            domain.reboot(0)
            domain.isActive()

        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return (current.TASK_QUEUE_STATUS_FAILED, message)


def get_clone_properties(vm_details, cloned_vm_details):

    vm_properties = {}

    datastore = choose_datastore()
    vm_properties['datastore'] = datastore
    current.logger.debug("Datastore selected is: " + str(datastore))

    vm_properties['security_domain'] = vm_details.security_domain
    vm_properties['public_ip_req'] = False
    # Finds mac address, ip address and vnc port for the cloned vm
    choose_mac_ip_vncport(vm_properties)
    current.logger.debug("MAC is : " + str(vm_properties['mac_addr']) + " IP is : " + str(vm_properties['private_ip']) + \
                         " VNCPORT is : " + str(vm_properties['vnc_port']))
  
    # Template and host of parent vm
    vm_properties['template'] = current.db(current.db.template.id == vm_details.template_id).select()[0]
    vm_properties['host'] = current.db(current.db.host.id == vm_details.host_id).select()[0]

    # Creates a directory for the cloned vm
    current.logger.debug("Creating directory for cloned vm...")
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
            current.logger.debug("Making Directory")          
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + '/'  \
                         + cloned_vm_details.vm_identity)

    while already_attached_disks > 0:
        clone_file_parameters += ' --file ' + get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' \
                                  + datastore.ds_name + '/' + cloned_vm_details.vm_identity + '/' + cloned_vm_details.vm_identity + \
                                  '_disk' + str(already_attached_disks + 1) + '.qcow2'
        already_attached_disks -= 1

    return (vm_properties, clone_file_parameters)
        
# Clones vm
def clone(vmid):

    cloned_vm_details = current.db.vm_data[vmid]
    vm_details = current.db(current.db.vm_data.id == cloned_vm_details.parent_id).select().first()
    try:
        (vm_properties, clone_file_parameters) = get_clone_properties(vm_details, cloned_vm_details)
        clone_command = "virt-clone --original " + vm_details.vm_identity + " --name " + cloned_vm_details.vm_identity + \
                        clone_file_parameters + " --mac " + vm_properties['mac_addr']
        exec_command_on_host(vm_details.host_id.host_ip, 'root', clone_command)
        current.logger.debug("Updating db after cloning")
        update_db_after_vm_installation(cloned_vm_details, vm_properties, parent_id = vm_details.id)
        message = "Cloned successfully"
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)        
    except:
        etype, value, tb = sys.exc_info()
        message = ''.join(traceback.format_exception(etype, value, tb, 10))
        current.logger.error("Exception " + message)
        return (current.TASK_QUEUE_STATUS_FAILED, str(value)) 

# Attaches extra disk to VM
def attach_extra_disk(parameters):

    vmid = parameters['vm_id']
    disk_size = parameters['disk_size']
    vm_details = current.db.vm_data[vmid]
    current.logger.debug(str(vm_details))

    try:
        if (serve_extra_disk_request(vm_details, disk_size, vm_details.host_id.host_ip)):
            current.db(current.db.vm_data.id == vmid).update(extra_HDD = vm_details.extra_HDD + disk_size)
            message = "Attached extra disk successfully"
            current.logger.debug(message)
            return (current.TASK_QUEUE_STATUS_SUCCESS, message) 
        else:
            message = " Your request for additional HDD could not be completed at this moment. Check logs."
            current.logger.debug(message)
            return (current.TASK_QUEUE_STATUS_FAILED, message) 
    except:
        etype, value, tb = sys.exc_info()
        message = ''.join(traceback.format_exception(etype, value, tb, 10))
        current.logger.error("Exception " + message)
        return (current.TASK_QUEUE_STATUS_FAILED, message)            

