# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

import re,os,sys,time,commands,libvirt
from helper import *  # @UnusedWildImport
db = current.db

# install
def install(vmid):
    try:
        vm_details = db(db.vm_data.id == vmid).select()[0]
        errormsg = "E1"  #--S
        datastore = give_datastore()
        vmname = vm_details.vm_name
        
        vmcount = int(get_constant("defined_vms")) + 1
        if(vmcount % 100 == 0): 
            vmcount = vmcount + 1
        set_constant("defined_vms", vmcount)
        (newmac,newip,vncport) = new_mac_ip(vmcount)

        logger.debug("VMCount = " + str(vmcount) + " MAC: " + str(newmac) + " NEW IP: " + newip + " VNCPort: " + vncport)

        #Check if a vm with same name already exists
        if check_vm_with_same_name(vmname) == False:

            logger.debug("No vm with the same name exists already in the database. Starting the process...")
            machine = db(db.host.id == vm_details.host_id).select()[0]
            
            logger.debug("Creating directory")
            if not os.path.exists (get_constant('vmfiles_path') + '/'+ vmname):
                os.makedirs(get_constant('vmfiles_path') + '/' + vmname)

            vm_location = get_constant('vmfiles_path') + '/' + vmname + '/' + vmname + '.qcow2'
            
            template = db(db.template.id == vm_details.template_id).select()[0]
            template_hdfile = template.hdfile
            template_location = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template_hdfile
            
            logger.debug("Copy in progress...")
            command = 'ssh root@'+ datastore.ip + ' ndmpcopy ' + datastore.path + '/' + get_constant("templates_dir") + '/' +  template_hdfile + ' ' + datastore.path + '/' + get_constant("templates_dir") + '/tmp'
            logger.debug(command)
            a = commands.getstatusoutput(command)
            logger.debug(a)
            errormsg = errormsg + a[1]
            
            logger.debug('Move in progress...')
            command = 'mv '+ get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + 'tmp' + '/' + template_hdfile + ' ' + get_constant('vmfiles_path') + '/' + vmname + '/' + vmname + '.qcow2'
            logger.debug(command)
            a = commands.getstatusoutput(command) 
            logger.debug(a)
            errormsg = errormsg+a[1]
            logger.debug("Copied!!!")        
 
            (ram, vcpus) = computeeffres (vm_details.RAM, vm_details.vCPU, 1)
            optional = ' --import --os-type=' + template.os_type #what its use?
            if (template.arch != 'amd64'):
                optional = optional + ' --arch=' + template.arch + ' '
  
            # Finds out the type of image (raw or qcow2)
            logger.debug("Find the type out image..") 
            location_test_image = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template_hdfile
            logger.debug("location_test_image :" + location_test_image)
            command_test_image = "qemu-img info %s" % location_test_image
            logger.debug("command_test_image :" + command_test_image)
            output_test_image = commands.getstatusoutput(str(command_test_image))
            logger.debug("output_test_image :" + output_test_image[1])
            image_info = output_test_image[1]
            logger.debug("image info :" + image_info)
            match = re.search(r"(?:file format:[\s])(?P<image_type>[\w]+)",image_info)
            logger.debug(match.groupdict())

            if (match.group('image_type') == 'raw'):
                install_cmd = 'virt-install \
                                 --name=' + vmname + ' \
                                 --ram=' + str(ram) + ' \
                                 --vcpus='+str(vcpus)+optional+' \
                                 --disk path=' + vm_location+',bus=virtio \
                                 --network bridge=br0,model=virtio,mac='+newmac+' \
                                 --graphics vnc,port='+vncport+',listen=0.0.0.0,password=duolc \
                                 --noautoconsole \
                                 --description \
                                 --autostart \
                                 --force'

            elif (match.group('image_type') == 'qcow2'):
                install_cmd = 'virt-install \
                                 --name=' + vmname + ' \
                                 --ram=' + str(ram) + ' \
                                 --vcpus='+str(vcpus)+optional+' \
                                 --disk path=' + vm_location+',format=qcow2,bus=virtio \
                                 --network bridge=br0,model=virtio,mac='+newmac+' \
                                 --graphics vnc,port='+vncport+',listen=0.0.0.0,password=duolc \
                                 --noautoconsole \
                                 --description \
                                 --autostart \
                                 --force'

            logger.debug("Installation started...")
            logger.debug("Host is "+ machine.ip)
            logger.debug("Installation command : " + install_cmd)
            out = commands.getstatusoutput("ssh root@"+ machine.ip + " " + install_cmd)
            logger.debug(out)
            errormsg = errormsg + out[1]

            logger.debug("Checking if VM has been successfully created...")
            if (check_if_vm_defined(machine.ip, vmname)):

                # Update vm_data table
                db(db.vm_data.id == vmid).update( \
                  host_id = machine.id, \
                  datastore_id = datastore.id, \
                  vm_ip = newip, \
                  vnc_port = vncport, \
                  mac_addr = newmac, \
                  start_time = get_date(), \
                  current_run_level = 3, \
                  last_run_level = 3,\
                  total_cost = 0, \
                  status = VM_STATUS_RUNNING )
                
                # Update vm_data_event table
                db(db.vm_data_event.id == vmid).update( \
                  host_id = machine.id, \
                  datastore_id = datastore.id, \
                  vm_ip = newip, \
                  vnc_port = vncport, \
                  mac_addr = newmac, \
                  start_time = get_date(), \
                  current_run_level = 3, \
                  last_run_level = 3,\
                  total_cost = 0, \
                  status = VM_STATUS_RUNNING )

                """
                vm=db(db.vm.name==req.vmname).select(db.vm.id)[0]
                db.vmaccpermissions.insert(userid=req.userid, vmid=vm.id)
                faculty=None
                if(req.faculty!=None and req.faculty!=""):
                    faculty=db(db.auth_user.username==req.faculty).select()[0]
                    if(faculty.id != req.userid):
                        db.vmaccpermissions.insert(userid=faculty.id, vmid=vm.id)
                    faculty=faculty.username
                """
                # Serving HDD request
                if (int(vm_details.HDD) != 0):
                    attach_disk(vm_details.vm_name, int(vm_details.HDD))
                    vmid = db(db.vm_data.vm_name == vm_details.vm_name).select(db.vm_data.id)[0].id
                    db.attached_disks.insert(vm_id = vmid, size = int(vm_details.HDD))

                # Updating the count of vms on host
                count = db(db.host.id == machine.id).select(db.host.vm_count)[0].vm_count
                db(db.host.id == machine.id).update(vm_count = count + 1)
            
                message = "Installed successfully."
                return (TASK_QUEUE_STATUS_SUCCESS, message)

                #db(db.datastores.id==datastore.id).update(used=int(datastore.used)+int(req.HDD)+int(template.hdd))

            else: 
                message = "Some Problem occured while executing " + install_cmd + " on host " + machine.ip
                return (TASK_QUEUE_STATUS_FAILED, message)
        else:
            message = "VM with same name already exists."
            return (TASK_QUEUE_STATUS_FAILED, message)
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