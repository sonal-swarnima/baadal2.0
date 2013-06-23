
import re,os,sys,time,commands,libvirt
from paramiko import SSHClient, SSHException

# install
def install(vmid):
    try:
        vm_details = db(db.vm_data.id == vmid).select()[0]
        errormsg = "E1"  #--S
	datastore = give_datastore()
        vmname = vm_details.vm_name
	
        vmcount = int(getconstant("defined_vms")) + 1
	if(vmcount % 100 == 0): 
            vmcount = vmcount + 1
        setconstant("defined_vms", vmcount)
	(newmac,newip,vncport) = new_mac_ip(vmcount)

        print "VMCount = " + str(vmcount) + " MAC: " + str(newmac) + " NEW IP: " + newip + " VNCPort: " + vncport

        #Check if a vm with same name already exists
        if check_vm_with_same_name(vmname) == False:

            print "No vm with the same name exists already in the database. Starting the process..."
            machine = db(db.host.id == req.host_id).select()[0]
            
            print "Creating directory"
            if not os.path.exists (get_constant('vmfiles_path') + '/'+ vmname):
                os.makedirs(get_constant('vmfiles_path') + '/' + vmname)

            vm_location = get_constant('vmfiles_path') + '/' + vmname + '/' + vmname + '.qcow2'

	    template = db(db.template.id == req.template_id).select()[0]
	    template_hdfile = template.hdfile
	    template_location = get_constant('vmfiles_path') + '/' + get_constant('templates_dir') + '/' + template_hdfile

	    print "Copy in progress..."
            #c1 = "cp /mnt/testdatastore/vm_templates/"+str(template_hdfile)+" "+"/mnt/testdatastore/vm_templates/tmp/"
            command = 'ssh root@'+ datastore.ip + ' ndmpcopy ' + datastore.path + '/' + get_constant("templates_dir") + '/' +    
                       template_hdfile + ' ' + datastore.path + '/' + get_constant("templates_dir") + '/tmp'
            print command
	    a = commands.getstatusoutput(command)
            print a
	    errormsg = errormsg + a[1]
        
            print "Move in progress...
            command = 'mv '+ get_constant('vmfiles_path') + '/' + getconstant('templates_dir') + '/' + 'tmp' + '/' + template_hdfile 
                       + ' ' + get_constant('vmfiles_path') + '/' + vmname + '/' + vmname + '.qcow2'
            print command
            a = commands.getstatusoutput(command) 
            print a
            errormsg = errormsg+a[1]
            print "Copied!!!"	    
 
            (ram, vcpus) = computeeffres (vm_details.RAM, vm_details.vCPU, 1)
            optional = ' --import --os-type=' + template.os_type #what its use?
            if (template.arch != 'amd64'):
                optional = optional + ' --arch=' + template.arch + ' '
  
	    # Finds out the type of image (raw or qcow2)
            print "Find the type out image.." 
            location_test_image = getconstant('vmfiles_path') + '/' + getconstant('templates_dir') + '/' + template_hdfile
            print "location_test_image :" + location_test_image
            command_test_image = "qemu-img info %s" % location_test_image
            print "command_test_image :" + command_test_image
            output_test_image = commands.getstatusoutput(str(command_test_image))
            print "output_test_image :" + output_test_image[1]
            image_info = output_test_image[1]
            print "image info :" + image_info
            match = re.search(r"(?:file format:[\s])(?P<image_type>[\w]+)",image_info)
            print match.groupdict()

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
                                 --disk path=' + vm_loc+',format=qcow2,bus=virtio \
                                 --network bridge=br0,model=virtio,mac='+newmac+' \
                                 --graphics vnc,port='+vncport+',listen=0.0.0.0,password=duolc \
                                 --noautoconsole \
                                 --description \
                                 --autostart \
                                 --force'

            print "Installation started..."
            print "Host is "+ machine.ip
            print "Installation command : " + install_cmd
            out = commands.getstatusoutput("ssh root@"+ machine.ip + " " + install_cmd)
            print out
	    errormsg = errormsg + out[1]

            print "Checking if VM has been successfully created..."
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
                    attachdisk(vm_details.vm_name, int(vm_details.HDD))
                    vmid = db(db.vm_data.vm_name == vm_details.vm_name).select(db.vm_data.id)[0].id
                    db.attached_disks.insert(vm_id = vmid, size = int(vm_details.HDD))

                # Updating the count of vms on host
                user_id = vm_details.userid
                vm_name = vm_details.vm_name
                count = db(db.host.id == machine.id).select(db.host.vm_count)[0].vm_count
                db(db.host.id == machine.id).update(vm_count = count + 1)
            
                message = "Installed successfully."
                return (VM_CREATION_SUCCESSFUL, message)

                #db(db.datastores.id==datastore.id).update(used=int(datastore.used)+int(req.HDD)+int(template.hdd))

            else: 
                message = "Some Problem occured while executing " + install_cmd + " on host " + machine.ip + 
                return (VM_CREATION_FAILED, message)
        else:
            message = "VM with same name already exists."
            return (VM_CREATION_FAILED, message)
    except Exception as e:
        import traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Exception"
        print e
	
# start
def start(vmid):
    vm_details = db(db.vm_data.id == vmid).select()[0]
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.vm_details.host_id + "/system")
        if(dom = conn.lookupByName(vm_details.vm_name)):
            dom.create()
            print "%s is started successfully." % dom
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# suspend
def suspend(vmid):
    vm_details = db(db.vm_data.id == vmid).select()[0]
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.vm_details.host_id + "/system")
        if(dom = conn.lookupByName(vm_details.vm_name)):
            dom.suspend()
            print "%s is suspended successfully." % dom
        else:
            return "%s does not exist." % (vm_details.vm_name)
    except:
        return "Connection with host could not be established. Try again."

# resume
def resume(vmid):
    vm_details = db(db.vm_data.id == vmid).select()[0]
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.vm_details.host_id + "/system")
        if(dom = conn.lookupByName(vm_details.vm_name)):
            dom.resume()
            print "%s is resumed successfully." % dom
        else:
            return "%s does not exist." % (vm_details.vm_name)
    else:
        return "Connection with host could not be established. Try again."

# destroy forcefully
def destroy(vmid):
    vm_details = db(db.vm_data.id == vmid).select()[0]
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.vm_details.host_id + "/system")
        if(dom = conn.lookupByName(vm_details.vm_name)):
            dom.destroy()
            print "%s is destroyed successfully." % dom
        else:
            return "%s does not exist." % (vm_details.vm_name)
    else:
        return "Connection with host could not be established. Try again."

# delete
def delete(vmid):
    vm_details = db(db.vm_data.id == vmid).select()[0]
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.vm_details.host_id + "/system")
        if(dom = conn.lookupByName(vm_details.vm_name)):
            dom.undefine()
            print "%s is deleted successfully." % dom
        else:
            return "%s does not exist." % (vm_details.vm_name)
    else:
        return "Connection with host could not be established. Try again."

        




    
