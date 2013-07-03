# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

import re,os,sys,math,time,commands,libvirt,shutil,paramiko
from paramiko import SSHClient, SSHException
import xml.etree.ElementTree as etree
from helper import *
from gluon import *
db = current.db
logger = current.logger


# Function to check if vm name already exists
def check_vm_name_exist(vmname):
    vm = db(db.vm_data.vm_name == vmname).select().first()
    if vm != None:
        return False
    else:
        return True    


# Function to choose datastore from a list of available datastores
def choose_datastore():
    datastores = db(db.datastore.id >= 0).select()
    logger.debug("Total number of datastores is : " + str(len(datastores)))
    if(len(datastores) == 0):
        logger.exception("No datastore found.")
    else:
       logger.debug("Datastore selected is: " + str(datastores[0]))
       return datastores[0]
        

# Function to compute effective RAM and CPU
def compute_effective_ram_vcpu(RAM, vCPU, runlevel):

    effective_ram = 1024
    effective_cpu = 1
    divideby = 1

    if(runlevel == 0): 
        divideby = 0
    elif(runlevel == 1): 
        divideby = 1
    elif(runlevel == 2): 
        divideby = 2
    elif(runlevel == 3): 
        divideby = 4

    if(divideby != 0):
        if(RAM/divideby >= 1024):
            effective_ram = RAM/divideby
        if(vCPU/divideby >= 1): 
            effective_cpu = vCPU/divideby

    if(divideby == 0):
        effective_ram = 0
        effective_cpu = 0

    return (effective_ram, effective_cpu)

# Function to find the used host resources
def host_resources_used(hostid):
    RAM = 0.0
    CPU = 0.0
    vms = db(db.vm_data.host_id == hostid).select(db.vm_data.RAM, db.vm_data.vCPU,db.vm_data.current_run_level)
    for vm in vms:
        (effective_ram,effective_cpu) = compute_effective_ram_vcpu(vm.RAM,vm.vCPU,vm.current_run_level)
        RAM = RAM + effective_ram
        CPU = CPU + effective_cpu
    host_ram = db(db.host.id == hostid).select(db.host.RAM)[0].RAM
    host_cpu = db(db.host.id == hostid).select(db.host.CPUs)[0].CPUs
    return (math.ceil(RAM),math.ceil(CPU),host_ram,host_cpu)

#Function to find new host for a new vm to be installed
def find_new_host(runlevel,RAM,vCPU):
    hosts = db(db.host.status == 1).select()
    runlevel = int(runlevel)
    host_selected = None
    for host in hosts:
        logger.debug("Checking host =" + host.host_name)
        (used_ram,used_cpu,host_ram,host_cpu) = host_resources_used(host.id)
        logger.debug("used ram:" + str(used_ram) + "used cpu:" + str(used_cpu) + "host ram:" + str(host_ram) + "host cpu"+ str(host_cpu))
        (effective_ram,effective_vcpu) = compute_effective_ram_vcpu(RAM,vCPU,runlevel)
        if(host_selected == None and (used_ram + effective_ram) <= ((host_ram * 1024))):
        #if(dhost==None and (uram+effram)<=hram*1024 and (ucpu+effvcpu)<=hcpu):
            host_selected = host
    return host_selected

# Function to find vm configuration ( datastore, host, ip address, mac address, vnc port, ram, vcpus)
def find_vm_configuration(vm_details):

    logger.debug("Inside find_vm_configuration()...")
    logger.debug("VM Details are: " + str(vm_details))
    datastore = choose_datastore()
    logger.debug("Datastore selected is:" + str(datastore))
    #put code for finding host
    host = db(db.host.id == 1).select()[0]
    logger.debug("Host selected is:" + str(host))	
    vmcount = int(get_constant('defined_vms')) + 1

    if(vmcount % 100 == 0): 
        vmcount = vmcount + 1

    new_mac_address = str(get_constant('mac_range')) + str(int(vmcount/100)) + ":" + str(vmcount-int(vmcount/100)*100)
    logger.debug("New mac address is" + new_mac_address)
    new_ip_address = get_constant('ip_range') + str(int(1+vmcount/100)) + "." + str(vmcount-int(vmcount/100)*100)
    logger.debug("New ip address is" + str(new_ip_address))
    new_vncport = str(int(get_constant('vncport_range')) + vmcount)
    logger.debug("New vnc port is" + new_vncport)
    (ram, vcpus) = compute_effective_ram_vcpu(vm_details.RAM, vm_details.vCPU, 1)
    return (datastore,host,new_mac_address,new_ip_address,new_vncport,ram,vcpus)

# Function that uses paramiko module for ssh connections
def call_paramiko(machine_ip, user_name, command):
    logger.debug("Inside paramiko function...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(machine_ip, username = user_name)
    stdin,stdout,stderr = ssh.exec_command(command)
    logger.debug(stdout.readlines())
    logger.error(stderr.readlines())
    return
    

# Function to create vm image
def create_vm_image(vm_details, datastore):
    # Creates a directory for the new vm
    logger.debug("Creating directory...")
    command_to_execute = 'mkdir /mnt/testdatastore/' + str(vm_details.vm_name)
    logger.debug("Directory: " + command_to_execute)
    call_paramiko('10.208.21.68','root',command_to_execute)
    """
    if not os.path.exists (str(get_constant('vmfiles_path')) + '/' + vm_details.vm_name):
        os.makedirs(str(get_constant('vmfiles_path')) + '/' + vm_details.vm_name)
    else:
        logger.exception("Directory with same name as vmname already exists.")
    """

    # Finds the location of template image that the user has requested for its vm.               
    template = db(db.template.id == vm_details.template_id).select()[0]
    template_location = str(get_constant('vmfiles_path')) + '/' + str(get_constant('templates_dir')) + '/' + template.hdfile
            
    # Copies the template image from its location to tmp directory
    logger.debug("Copy in progress...")
    #command_to_execute = 'ndmpcopy ' + datastore.path + '/' + get_constant("templates_dir") + '/' +  template.hdfile + ' ' + datastore.path + '/' + get_constant("templates_dir") + '/tmp'
    # To be changed
    command_to_execute = 'cp /mnt/testdatastore'+ '/' + get_constant("templates_dir") + '/' +  template.hdfile + ' ' + '/mnt/testdatastore' + '/' + get_constant("templates_dir") + '/tmp'
    call_paramiko('10.208.21.68', 'root', command_to_execute)
    logger.debug("Copied!!!")

    # Moves the template image in tmp directory to new directory created for user's vm          
    logger.debug('Move in progress...')
    template_location = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + 'tmp' + '/' + template.hdfile
    new_image_location = get_constant('vmfiles_path') + '/' + vm_details.vm_name + '/' + vm_details.vm_name + '.qcow2'
    vm_location = get_constant('vmfiles_path') + '/' + vm_details.vm_name + '/' + vm_details.vm_name + '.qcow2'
    #shutil.move(template_location,new_image_location)
    command_to_execute = 'mv ' + template_location + ' ' + new_image_location
    call_paramiko('10.208.21.68', 'root', command_to_execute)
    logger.debug("Moved!!!")    
    return (template, vm_location)

# Function to determine install command for vm
def get_install_command(template,vm_details,vm_location,ram,vcpus,new_mac_address,new_vncport):

        optional = ' --import --os-type=' + template.os_type
        
        if (template.arch != 'amd64'):
            optional = optional + ' --arch=' + template.arch + ' '

        return 'virt-install --name=' + vm_details.vm_name + ' \
                         --ram=' + str(ram) + ' \
                         --vcpus='+str(vcpus)+optional+' \
                         --disk path=' + vm_location+',bus=virtio \
                         --network bridge=br0,model=virtio,mac='+new_mac_address+' \
                         --graphics vnc,port='+new_vncport+',listen=0.0.0.0,password=duolc \
                         --noautoconsole \
                         --description \
                         --autostart \
                         --force'

"""
    # Finds out the type of image (raw or qcow2)
    logger.debug("Find the type out image..") 
    location_test_image = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template.hdfile
    logger.debug("location_test_image :" + location_test_image)
    command_test_image = "qemu-img info %s" % location_test_image
    logger.debug("command_test_image :" + command_test_image)
    output_test_image = commands.getstatusoutput(str(command_test_image))
    logger.debug("output_test_image :" + output_test_image[1])
    image_info = output_test_image[1]
    logger.debug("image info :" + image_info)
    match = re.search(r"(?:file format:[\s])(?P<image_type>[\w]+)",image_info)
    logger.debug(match.groupdict())

    optional = ' --import --os-type=' + template.os_type
    if (template.arch != 'amd64'):
        optional = optional + ' --arch=' + template.arch + ' '

    if (match.group('image_type') == 'raw'):

    install_command = 'virt-install \
                         --name=' + vm_details.vm_name + ' \
                         --ram=' + str(ram) + ' \
                         --vcpus='+str(vcpus)+optional+' \
                         --disk path=' + vm_location+',bus=virtio \
                         --network bridge=br0,model=virtio,mac='+new_mac_address+' \
                         --graphics vnc,port='+new_vncport+',listen=0.0.0.0,password=duolc \
                         --noautoconsole \
                         --description \
                         --autostart \
                         --force'

    elif (match.group('image_type') == 'qcow2'):
        install_command = 'virt-install \
                         --name=' + vm_details.vm_name + ' \
                         --ram=' + str(ram) + ' \
                         --vcpus='+str(vcpus)+optional+' \
                         --disk path=' + vm_location+',format=qcow2,bus=virtio \
                         --network bridge=br0,model=virtio,mac='+new_mac_address+' \
                         --graphics vnc,port='+new_vncport+',listen=0.0.0.0,password=duolc \
                         --noautoconsole \
                         --description \
                         --autostart \
                         --force' 

    return install_command 
"""

# Function to check if a newly created vm is defined
def check_if_vm_defined(hostip, vmname):
    domains=[]    # It will contain the domain information of all the available domains
    exists = False
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+ hostip +'/system')
        print conn
        ids = conn.listDomainsID()

        for _id in ids:
            domains.append(conn.lookupByID(_id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            if(vmname == dom.name()):
                exists=True
        conn.close()
        return exists
    except:
        return False

# Function to generate xml
def generate_xml(diskpath,target_disk):
    root_element = etree.Element('disk',attrib = {'type':'file','device':'disk'})
    etree.SubElement(root_element, 'driver',attrib = {'name':'qemu','cache':'none'})
    etree.SubElement(root_element, 'source', attrib = {'file':diskpath})
    etree.SubElement(root_element, 'target', attrib = {'dev': target_device})
    return (etree.tostring(root_element))
    

# Function to attach disk with vm
def attach_disk(vmname, size, hostip):
   
    vm = db(db.vm_data.vm_name == vmname).select().first()
    #out = "Error attaching disk"
    try:
        conn = libvirt.open("qemu+ssh://root@" + hostip + "/system")
        domain = conn.lookupByName(vmname)
        alreadyattached = len(db(db.attached_disks.vm_id == vm.id).select(db.attached_disks.id))
        if(domain.isActive() != 1):
            logger.exception("Cannot attach disk to inactive domain..")
        else:
            diskpath = get_constant('vmfiles_path') + get_constant('datastore_int') + vm.datastore.ds_name + "/" + vmname+ "/" + vmname + str(alreadyattached +1) + ".raw"
            logger.debug("Above IF")
            if not os.path.exists (get_constant('vmfiles_path')+ get_constant('datastore_int') + vm.datastore_id.ds_name+ '/' +vmname):
                logger.debug("Making Directory")          
                os.makedirs(get_constant('vmfiles_path') + get_constant('datastore_int') + vm.datastore_id.ds_name+'/' + vmname)
            else:
                logger.exception("%s already exists." % diskpath)
           
            command= "qemu-img create -f raw "+ diskpath + " " + str(size) + "G"
            logger.debug(command)
            output = commands.getstatusoutput(command)
            logger.debug(output)
            #command = "ssh root@" + vm.host_id.host_ip + " virsh attach-disk " + vmname + " " + diskpath + " vd" + chr(97+alreadyattached+1) + " --type disk"
            target_disk = "vd" + chr(97 + alreadyattached + 1)
            xmlDescription = generate_xml(diskpath, target_disk)
            domain.attachDevice(xmlDescription)
            xmlfile = domain.XMLDesc(0)
            domain = conn.defineXML(xmlfile)
            out = domain.isActive()
            logger.debug(out)
            if(out == 1): 
                logger.debug("The disk has been attached successfully. Reboot your vm to see it.")
        conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        out = "Some Error Occured\n" + msg
        logger.error(out) 




# Function to install a vm
def install(vmid):
        logger.debug("In install function...")
        try:
            # Fetches vm details from vm_data table
            vm_details = db(db.vm_data.id == vmid).select()[0]
            logger.debug("Vm details are: " + str(vm_details))
    
            # Checks if a vm with same name doesn't exist and then start the process
            if not check_vm_name_exist(vm_details.vm_name):
	
                logger.debug("No vm with the same name exists in the database. Starting the process...")

                # Calling find_vm_configuration function
                (datastore,host,new_mac_address,new_ip_address,new_vncport,ram,vcpus) = find_vm_configuration(vm_details)
                logger.debug("DATASTORE: " + str(datastore.ds_ip) + " HOST: " + str(host.host_ip) + " MAC: " + str(new_mac_address) + " NEW IP: " + str(new_ip_address) + " VNCPort: " + str(new_vncport))

                # Calling create_vm_image function
                (template,vm_location) = create_vm_image(vm_details,datastore)
         
                # Calling form_install_command
                #install_command = get_install_command(template,vm_details,vm_location,ram,vcpus,new_mac_address,new_vncport) 
                install_command = get_install_command(template,vm_details,vm_location,ram,vcpus,new_mac_address,new_vncport)      
		logger.debug("install command is : " + install_command)

                # Starts installing a vm
                logger.debug("Installation started...")
                logger.debug("Host is "+ host.host_ip)
                logger.debug("Installation command : " + install_command)
                #call_paramiko(host.host_ip,install_command)
                call_paramiko('10.208.21.68','root',install_command)

                logger.debug("Checking if VM has been successfully created...")
                logger.debug(str(check_if_vm_defined(host.host_ip, vm_details.vm_name)) + "result of function")
                if (check_if_vm_defined(host.host_ip, vm_details.vm_name)):

                    # updating count after vm is successfully installed
                    logger.debug("value of defined_vms:")
                    logger.debug(int(get_constant('defined_vms')))
                    vmcount = int(get_constant('defined_vms')) + 1
                    if(vmcount % 100 == 0): 
                        vmcount = vmcount + 1
                    logger.debug('vmcount is:')
                    logger.debug(vmcount)
                    update_value("defined_vms", vmcount)

                    # Update vm_data table
                    db(db.vm_data.id == vmid).update( \
                                                    host_id = host.id, \
                                                    datastore_id = datastore.id, \
                                                    vm_ip = new_ip_address, \
                                                    vnc_port = new_vncport, \
                                                    mac_addr = new_mac_address, \
                                                    start_time = get_datetime(), \
                                                    current_run_level = 3, \
                                                    last_run_level = 3,\
                                                    total_cost = 0, \
                                                    status = 2 )
                    """                
                    # Serving HDD request
                    if (int(vm_details.HDD) != 0):
                        attach_disk(vm_details.vm_name, int(vm_details.HDD), host.host_ip)
                        vmid = db(db.vm_data.vm_name == vm_details.vm_name).select(db.vm_data.id)[0].id
                        db.attached_disks.insert(vm_id = vmid, size = int(vm_details.HDD))
                    """
                    # Updating the count of vms on host
                    count = db(db.host.id == host.id).select().first()['vm_count']
                    logger.debug("count is:")
                    logger.debug(count)
                    db(db.host.id == host.id).update(vm_count = count + 1)
            
                    message = "Installed successfully."
                    return (3, message)

                    #db(db.datastores.id==datastore.id).update(used=int(datastore.used)+int(req.HDD)+int(template.hdd))

                else: 
                    message = "Problem with installation of vm. Check logs." 
                    return (4, message)
            else:
                message = "VM with same name already exists."
                return (4, message)
        except Exception as e:
            import traceback
            etype, value, tb = sys.exc_info()
            msg = ''.join(traceback.format_exception(etype, value, tb, 10))
            logger.error("Exception")
            logger.error(e)

# start
def start(vm_id):
    vm_details = db(db.vm_data.id == vm_id).select().first()
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm_details.host_id + "/system")
        dom = conn.lookupByName(vm_details.vm_name)
        if dom != 'None':
            dom.create()
            logger.debug("%s is started successfully." % dom)
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# suspend
def suspend(vmid):
    vm_details = db(db.vm_data.id == vmid).select().first()
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm_details.host_id + "/system")
        dom = conn.lookupByName(vm_details.vm_name)
        if dom != 'None':
            dom.suspend()
            logger.debug("%s is suspended successfully." % dom)
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# resume
def resume(vmid):
    vm_details = db(db.vm_data.id == vmid).select().first()
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm_details.host_id + "/system")
        dom = conn.lookupByName(vm_details.vm_name)
        if dom != 'None':
            dom.resume()
            logger.debug("%s is resumed successfully." % dom)
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# destroy forcefully
def destroy(vmid):
    vm_details = db(db.vm_data.id == vmid).select().first()
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm_details.host_id + "/system")
        dom = conn.lookupByName(vm_details.vm_name)
        if dom != 'None':
            dom.destroy()
            logger.debug("%s is destroyed successfully." % dom)
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# delete
def delete(vmid):
    vm_details = db(db.vm_data.id == vmid).select().first()
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm_details.host_id + "/system")
        dom = conn.lookupByName(vm_details.vm_name)
        if dom != 'None':
            dom.undefine()
            logger.debug("%s is deleted successfully." % dom)
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."
