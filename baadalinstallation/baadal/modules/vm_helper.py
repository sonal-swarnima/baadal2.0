# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

import re, os, sys, math, time, commands, libvirt, shutil, paramiko, traceback, random
import xml.etree.ElementTree as etree
from helper import *

# Function to choose datastore from a list of available datastores
def choose_datastore():

    datastores = current.db(current.db.datastore.id>=0).select(orderby = current.db.datastore.used)
    current.logger.debug("Total number of datastores is : " + str(len(datastores)))
    if(len(datastores) == 0):
        current.logger.error("No datastore found.")
        raise Exception("No datastore found.")
    else:
       current.logger.debug("Datastore selected is: " + str(datastores[0]))
       return datastores[0]
       
# Function to compute effective RAM and CPU
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

# Function to find the used host resources
def host_resources_used(hostid):

    RAM = 0.0
    CPU = 0.0

    vms = current.db(current.db.vm_data.host_id == hostid).select(current.db.vm_data.RAM,  current.db.vm_data.vCPU, 
                     current.db.vm_data.current_run_level)

    for vm in vms:
        (effective_ram,effective_cpu) = compute_effective_ram_vcpu(vm.RAM,vm.vCPU,vm.current_run_level)
        RAM = RAM + effective_ram
        CPU = CPU + effective_cpu

    host_ram = current.db(current.db.host.id == hostid).select(current.db.host.RAM)[0].RAM
    host_cpu = current.db(current.db.host.id == hostid).select(current.db.host.CPUs)[0].CPUs
    return (math.ceil(RAM),math.ceil(CPU),host_ram,host_cpu)

#Function to find new host for a vm to be installed
def find_new_host(runlevel,RAM,vCPU):

    hosts = current.db(current.db.host.status == current.HOST_STATUS_UP).select() 
    if (len(hosts) == 0):
        current.logger.error("No host found.")
        raise Exception("No host found.")
    else:
        runlevel = int(runlevel)
        host_selected = None
        for host in hosts:
            current.logger.debug("Checking host = " + host.host_name)
            (used_ram,used_cpu,host_ram,host_cpu) = host_resources_used(host.id)
            current.logger.debug("used ram:" + str(used_ram) + " used cpu:" + str(used_cpu) + " host ram:" + str(host_ram) + " host cpu"+ 
                                  str(host_cpu))
            (effective_ram,effective_vcpu) = compute_effective_ram_vcpu(RAM,vCPU,runlevel)
            if(host_selected == None and (used_ram + effective_ram) <= ((host_ram * 1024))):
                host_selected = host
    if host_selected != None:
        return host_selected
    else:
        current.logger.error("No active host is available for a new vm.")
        raise Exception("No active host is available for a new vm.")

#Function to choose mac and ip address for a vm to be installed
def choose_mac_ip_vncport():

    temporary_pool = current.MAC_IP_POOL
    while True:
        mac_selected = random.choice(temporary_pool.keys())
        current.logger.debug(str(mac_selected))
        mac = current.db(current.db.vm_data.mac_addr == mac_selected).select().first()
        if mac == None:
            break
        else:
            temporary_pool.pop(mac_selected)
        if not temporary_pool:
            raise Exception("Available MACs are exhausted.")

    count = int(get_constant('vmcount')) 
    new_vncport = str(int(get_constant('vncport_range')) + count)
    update_value('vmcount', count + 1)

    current.logger.debug("MAC is : " + str(mac_selected))  
    current.logger.debug("IP is : %s" % current.MAC_IP_POOL[mac_selected])
    current.logger.debug("VNCPORT is : %s" % new_vncport)
    return (mac_selected, current.MAC_IP_POOL[mac_selected], new_vncport)

# Function to allocate vm properties ( datastore, host, ip address, mac address, vnc port, ram, vcpus)
def allocate_vm_properties(vm_details):

    current.logger.debug("Inside allocate_vm_properties()...")
    current.logger.debug("VM Details are: " + str(vm_details))

    datastore = choose_datastore()
    current.logger.debug("Datastore selected is: " + str(datastore))

    host = find_new_host(vm_details.current_run_level, vm_details.RAM, vm_details.vCPU)
    current.logger.debug("Host selected is: " + str(host))

    (new_mac_address, new_ip_address, new_vncport) = choose_mac_ip_vncport()

    (ram, vcpus) = compute_effective_ram_vcpu(vm_details.RAM, vm_details.vCPU, 1)
    return (datastore, host, new_mac_address, new_ip_address, new_vncport, ram, vcpus)

# Function to execute command on host machine using paramiko module
def exec_command_on_host(machine_ip, user_name, command):

    try:
        current.logger.debug("Starting to establish SSH connection with host" + str(machine_ip))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username = user_name)
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
    

# Function to create vm image
def create_vm_image(vm_details, datastore):

    # Creates a directory for the new vm
    current.logger.debug("Creating directory...")
    if not os.path.exists (get_constant('vmfiles_path') + '/' + vm_details.vm_name):
        os.makedirs(get_constant('vmfiles_path') + '/' + vm_details.vm_name)
    else:
        current.logger.error("Directory with same name as vmname already exists.")
        raise Exception("Directory with same name as vmname already exists.")

    # Finds the location of template image that the user has requested for its vm.               
    template = current.db(current.db.template.id == vm_details.template_id).select()[0]
    template_location = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template.hdfile
            
    # Copies the template image from its location to new vm directory
    """
    command_to_execute = 'ndmpcopy ' + datastore.path + '/' + get_constant("templates_dir") + '/' +  template.hdfile + ' ' + datastore.path
                          + '/' + get_constant("templates_dir") + '/tmp'
    """
    vm_image_location = get_constant('vmfiles_path') + '/' + vm_details.vm_name + '/' + vm_details.vm_name + '.qcow2'
    current.logger.debug("Copy in progress...")
    rcode = os.system('cp %s %s' % (template_location, vm_image_location))
    if rcode != 0:
        current.logger.error("Unsuccessful in copying image...")
        raise Exception("Unsuccessful in copying image...")
    return (template, vm_image_location)

# Function to determine install command for vm
def get_install_command(template,vm_details,vm_image_location,ram,vcpus,new_mac_address,new_vncport):
    
    optional = ' --import --os-type=' + template.os_type
    if (template.arch != 'amd64'):
        optional = optional + ' --arch=' + template.arch + ' '

    if (template.type == 'RAW'):
       install_command = 'virt-install \
                         --name=' + vm_details.vm_name + ' \
                         --ram=' + str(ram) + ' \
                         --vcpus=' + str(vcpus) + optional + ' \
                         --disk path=' + vm_image_location +',bus=virtio \
                         --network bridge=br0,model=virtio,mac=' + new_mac_address + ' \
                         --graphics vnc,port=' + new_vncport + ',listen=0.0.0.0,password=duolc \
                         --noautoconsole \
                         --description \
                         --autostart \
                         --force'

    elif (template.type == 'QCOW2'):
        install_command = 'virt-install \
                         --name=' + vm_details.vm_name + ' \
                         --ram=' + str(ram) + ' \
                         --vcpus=' + str(vcpus) + optional + ' \
                         --disk path=' + vm_image_location + ',format=qcow2,bus=virtio \
                         --network bridge=br0,model=virtio,mac=' + new_mac_address + ' \
                         --graphics vnc,port=' + new_vncport + ',listen=0.0.0.0,password=duolc \
                         --noautoconsole \
                         --description \
                         --autostart \
                         --force' 

    return install_command 


# Function to generate xml
def generate_xml(diskpath,target_disk):

    root_element = etree.Element('disk',attrib = {'type':'file','device':'disk'})
    etree.SubElement(root_element, 'driver',attrib = {'name':'qemu','cache':'none'})
    etree.SubElement(root_element, 'source', attrib = {'file':diskpath})
    etree.SubElement(root_element, 'target', attrib = {'dev': target_disk})
    return (etree.tostring(root_element))
    

# Function to attach disk with vm
def attach_disk(vmname, size, hostip, datastore):
   
    vm = current.db(current.db.vm_data.vm_name == vmname).select().first()

    try:
        connection_object = libvirt.open("qemu+ssh://root@" + hostip + "/system")
        domain = connection_object.lookupByName(vmname)
        alreadyattached = len(current.db(current.db.attached_disks.vm_id == vm.id).select(current.db.attached_disks.id)) 
        current.logger.debug("Value of alreadyattached is : " + str(alreadyattached))
        current.logger.debug("Above IF")
        if not os.path.exists (get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + '/' \
                               +vmname):
            current.logger.debug("Making Directory")          
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + '/' + vmname)
        diskpath = get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + datastore.ds_name + "/" + vmname+ "/" + \
                   vmname + str(alreadyattached + 1) + ".raw"

        # Create a new image for the new disk to be attached
        command= "qemu-img create -f raw "+ diskpath + " " + str(size) + "G"
        current.logger.debug(command)
        output = os.system(command)
        current.logger.debug(output)
        if output != 0:
            return False
            
        # Attaching disk to vm using libvirt API
        target_disk = "vd" + chr(97 + alreadyattached + 1)
        xmlDescription = generate_xml(diskpath, target_disk)
        domain.attachDevice(xmlDescription)
        xmlfile = domain.XMLDesc(0)
        domain = connection_object.defineXML(xmlfile)
        domain.isActive()
        current.logger.debug("The disk has been attached successfully. Reboot your vm to see it.")
        connection_object.close()
        return True
    except:
        etype, value, tb = sys.exc_info()
        trace = ''.join(traceback.format_exception(etype, value, tb, 10))
        message = "Check logs for error: " + trace
        current.logger.error(message) 
        return False

# Function to launch vm on host
def launch_vm_on_host(template, vm_details, vm_image_location, ram, vcpus, new_mac_address, new_vncport, host_ip, datastore):

    attach_disk_status_message = 'Your request for additional HDD is completed.'
    install_command = get_install_command(template, vm_details, vm_image_location, ram, vcpus, new_mac_address, new_vncport)  
    # Starts installing a vm
    current.logger.debug("Installation started...")
    current.logger.debug("Host is "+ host_ip)
    current.logger.debug("Installation command : " + install_command)
    exec_command_on_host(host_ip, 'root', install_command)

    # Serving HDD request
    if (int(vm_details.HDD) != 0):
        if (attach_disk(vm_details.vm_name, int(vm_details.HDD), host_ip, datastore)):
            vmid = current.db(current.db.vm_data.vm_name == vm_details.vm_name).select(current.db.vm_data.id)[0].id
            current.db.attached_disks.insert(vm_id = vmid, datastore_id = datastore.id , capacity = int(vm_details.HDD))
        else:
            attach_disk_status_message = " Your request for additional HDD could not be completed at this moment. Check logs."
    return attach_disk_status_message

# Function to check if a newly created vm is defined
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

# Function to free vm properties
def free_vm_properties(vm_details):

    if os.path.exists (get_constant('vmfiles_path') + '/' + vm_details.vm_name):
        shutil.rmtree(get_constant('vmfiles_path') + '/' + vm_details.vm_name)
    return
    
# Function to update db after a vm is installed successfully
def update_db_after_vm_installation(vmid, vm_details, template, datastore, host, new_mac_address, new_ip_address, new_vncport):

    # Update vm_data table
    current.db(current.db.vm_data.id == vmid).update( host_id = host.id, \
                                      datastore_id = datastore.id, \
                                      vm_ip = new_ip_address, \
                                      vnc_port = new_vncport, \
                                      mac_addr = new_mac_address, \
                                      start_time = get_datetime(), \
                                      current_run_level = 3, \
                                      last_run_level = 3,\
                                      total_cost = 0, \
                                      status = current.VM_STATUS_RUNNING)

    # Updating the count of vms on host
    count = current.db(current.db.host.id == host.id).select().first()['vm_count']
    current.logger.debug("count is:" + str(count))
    current.db(current.db.host.id == host.id).update(vm_count = count + 1)

    # Updating the used entry of datastore
    current.db(current.db.datastore.id == datastore.id).update(used = int(datastore.used) + int(vm_details.HDD) + int(template.hdd))
    return
    
# Function to install a vm
def install(vmid):

        current.logger.debug("In install function...")
        try:
            # Fetches vm details from vm_data table
            vm_details = current.db(current.db.vm_data.id == vmid).select()[0]
            current.logger.debug("Vm details are: " + str(vm_details))
	
            # Calling allocate_vm_properties function
            (datastore, host, new_mac_address, new_ip_address, new_vncport, ram, vcpus) = allocate_vm_properties(vm_details)
            current.logger.debug("DATASTORE: " + str(datastore.ds_ip) + " HOST: " + str(host.host_ip) + " MAC: " + str(new_mac_address) +
                                 "NEW IP: " + str(new_ip_address) + " VNCPort: " + str(new_vncport) + " RAM: " + str(ram) + " VCPUs: " + 
                                  str(vcpus))

            # Calling create_vm_image function
            (template, vm_image_location) = create_vm_image(vm_details, datastore)
         
            # Calling launch_vm_on_host
            attach_disk_status_message = launch_vm_on_host(template, vm_details, vm_image_location, ram, vcpus, new_mac_address,
                                                           new_vncport, host.host_ip, datastore)       

            # Checking if vm has been installed successfully
            current.logger.debug("Checking if VM has been successfully created...")
            assert(check_if_vm_defined(host.host_ip, vm_details.vm_name)), "VM is not installed. Check logs."
            update_db_after_vm_installation(vmid, vm_details, template, datastore, host, new_mac_address, new_ip_address, new_vncport) 
            message = "VM is installed successfully." + attach_disk_status_message
            return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    

        except Exception as e:            
            etype, value, tb = sys.exc_info()
            message = ''.join(traceback.format_exception(etype, value, tb, 10))
            current.logger.error("Exception " + message)
            free_vm_properties(vm_details)
            return (current.TASK_QUEUE_STATUS_FAILED, message)

# Function to start a vm
def start(vmid):

    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_name)
        domain.create()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING)  
        message = vm_details.vm_name + " is started successfully."
        current.logger.debug(message) 
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to suspend a vm
def suspend(vmid):

    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_name)
        domain.suspend()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SUSPENDED)       
        message = vm_details.vm_name + " is suspended successfully." 
        current.logger.debug(message)       
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to resume a vm
def resume(vmid):

    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_name)
        domain.resume()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING) 
        message = vm_details.vm_name + " is resumed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to destroy a vm forcefully
def destroy(vmid):

    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_name)
        domain.destroy()
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SHUTDOWN) 
        message = vm_details.vm_name + " is destroyed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to clean up database after vm deletion
def clean_up_database_after_vm_deletion(vm_details):
    
    current.logger.debug("Inside clean up function...")

    # moving vm image folder to archives folder
    if not os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('archives_dir')):
            os.makedirs(get_constant('vmfiles_path') + '/' + get_constant('archives_dir'))
    source_file = get_constant('vmfiles_path') + '/' + vm_details.vm_name
    archive_filename = vm_details.vm_name + str(get_datetime())
    current.logger.debug(archive_filename)
    destination_file = get_constant('vmfiles_path') + '/' + get_constant('archives_dir') + '/' + archive_filename
    shutil.move(source_file, destination_file)

    # removing hdd        
    if os.path.exists(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_name):
        shutil.rmtree(get_constant('vmfiles_path') + '/' + get_constant('datastore_int') + '/' + vm_details.datastore_id.ds_name \
                          + "/" + vm_details.vm_name)

    # updating the count of guest vms on host
    count = current.db(current.db.host.id == vm_details.host_id).select().first()['vm_count']
    current.logger.debug("count is:" + str(count))
    current.db(current.db.host.id == vm_details.host_id).update(vm_count = count - 1)

    # updating the used entry of database
    current.db(current.db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                                                (int(vm_details.HDD) + int(vm_details.template_id.hdd)))
    return
        
# Function to delete a vm
def delete(vmid):
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = connection_object.lookupByName(vm_details.vm_name)
        vm_status = domain.info()[0]
        current.logger.debug(vm_status)
        if (vm_status == 1 or vm_status == 3):
            current.logger.debug("Vm is not shutoff. Shutting it off first.")
            domain.destroy()
        current.logger.debug("Starting to delete it...")
        domain.undefine()
        message = vm_details.vm_name + " is deleted successfully."
        current.logger.debug(message)
        clean_up_database_after_vm_deletion(vm_details)
        current.db(current.db.vm_data.id == vmid).delete()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to migrate a vm to a new host
def migrate(vmid, hostid):

    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        current_host_connection_object = libvirt.open("qemu+ssh://root@" + vm_details.host_id.host_ip + "/system")
        domain = current_host_connection_object.lookupByName(vm_details.vmname)
        destination_host_connection_object = libvirt.open("qemu+ssh://root@" + hostid + "/system")
        domain.migrate(destination_host_connection_object, 1, None, None, 0)
        current.logger.debug("Migrated successfully..")
        message = vm_details.vm_name + " is migrated successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except libvirt.libvirtError,e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)
        
# Prepares VM list to be displayed on webpage
def get_vm_list(vms):
    vmlist = []
    for vm in vms:
        total_cost = add_to_cost(vm.vm_name)
        element = {'id':vm.id,'name':vm.vm_name,'ip':vm.vm_ip, 'owner':get_fullname(vm.user_id), 'ip':vm.vm_ip,   'hostip':vm.host_id.host_ip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
        vmlist.append(element)
    return vmlist

