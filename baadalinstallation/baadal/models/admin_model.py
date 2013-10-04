# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db, request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

def get_add_template_form():
    db.template.id.readable=False # Since we do not want to expose the id field on the grid

    #Define the fields to show on grid. 
    fields = (db.template.name, db.template.os_type, db.template.arch, db.template.hdd, db.template.hdfile, db.template.type, db.template.datastore_id)

    default_sort_order=[db.template.id]

    #Creating the grid object
    form = SQLFORM.grid(db.template, fields=fields, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, csv=False, searchable=False, details=False, showbuttontext=False)
    return form

def get_add_datastore_form():

    db.datastore.id.readable=False # Since we do not want to expose the used field on the grid
    #Define the fields to show on grid. 
    fields = (db.datastore.ds_name, db.datastore.ds_ip, db.datastore.capacity, db.datastore.username, db.datastore.path)

    default_sort_order=[db.datastore.id]

    #Creating the grid object
    form = SQLFORM.grid(db.datastore, fields=fields, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, csv=False, searchable=False, details=False, showbuttontext=False)
    return form

def get_all_pending_vm():
    vms = db(db.vm_data.status.belongs(VM_STATUS_REQUESTED, VM_STATUS_VERIFIED, VM_STATUS_APPROVED, VM_STATUS_IN_QUEUE)).select()
    pending_vms = get_pending_vm_list(vms)
    for vm in pending_vms:
        collaborators = []
        vm_users = db(db.user_vm_map.vm_id == vm['id']).select()
        for vm_user in vm_users:
            if vm_user.user_id != vm_user.vm_id.requester_id:
                collaborators.append(vm_user.user_id.first_name + ' ' + vm_user.user_id.last_name)
        if not collaborators:
            vm['collaborators'] = '-'
        else:
            vm['collaborators'] = ', '.join(collaborators)
        
        roles = []
        user_roles = db(db.user_membership.user_id == vm['requester_id']).select()
        for user_role in user_roles:
            roles.append(user_role.group_id.role)
        if ADMIN in roles:
            vm['requested_by'] = ADMIN
        elif ORGADMIN in roles:
            vm['requested_by'] = ORGADMIN
        elif FACULTY in roles:
            vm['requested_by'] = FACULTY
        else:
            vm['requested_by'] = USER
            
    return pending_vms

def get_all_vm_list():
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    return get_hosted_vm_list(vms)

def get_all_vm_ofhost(hostid):
    vms = db((db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)) & (db.vm_data.host_id == hostid )).select()
    return get_hosted_vm_list(vms)

def create_clone_task(vm_data):
    
    vm_id = vm_data.id
    clone_count = vm_data.parameters['clone_count']
    
    vm_id_list = []
    for count in range(1, clone_count+1):
        clone_vm_name = vm_data.vm_name + str(count)
        clone_vm_id = db.vm_data.insert(
                          vm_name = clone_vm_name, 
                          RAM = vm_data.RAM,
                          HDD = vm_data.HDD,
                          extra_HDD = vm_data.extra_HDD,
                          vCPU = vm_data.vCPU,
                          template_id = vm_data.template_id,
                          requester_id = vm_data.requester_id,
                          owner_id = vm_data.owner_id,
                          parent_id = vm_data.parent_id,
                          purpose = vm_data.purpose,
                          status = VM_STATUS_IN_QUEUE)

        vm_id_list.append(clone_vm_id)
        
        add_vm_users(clone_vm_id, vm_data.requester_id, vm_data.owner_id)
            
    # Update the status of clone request vm_data to -1 
    db.vm_data[vm_id] = dict(status=-1)
    
    add_vm_task_to_queue(vm_id, TASK_TYPE_CLONE_VM, {'clone_vm_id':vm_id_list})


def enqueue_vm_request(vm_id):
    
    vm_data = db.vm_data[vm_id]
    params = {}
    if vm_data.parameters and 'clone_count' in vm_data.parameters:
        create_clone_task(vm_data)
        return
    task_type = TASK_TYPE_CREATE_VM
   
    if vm_data.parameters and 'disk_size' in vm_data.parameters:
        task_type = TASK_TYPE_ATTACH_DISK
        params = {'disk_size' : vm_data.parameters['disk_size']}
    db(db.vm_data.id == vm_id).update(status=VM_STATUS_IN_QUEUE)
    add_vm_task_to_queue(vm_id, task_type, params)


def delete_user_vm_access(vm_id,user_id) :    
    db((db.user_vm_map.vm_id == vm_id) & (db.user_vm_map.user_id == user_id)).delete()  


def add_user_vm_access(vm_id, user_id) :    
    db.user_vm_map.insert(vm_id = vm_id, user_id = user_id)       


def update_vm_lock(vminfo,flag) :
        db(db.vm_data.id == vminfo.id).update(locked = flag)


def get_all_hosts() :
    
    hosts = db().select(db.host.ALL) 
    results = []
    for host in hosts:
        results.append({'ip':host.host_ip, 
                        'id':host.id, 
                        'name':host.host_name, 
                        'status':host.status, 
                        'RAM':host.RAM,
                        'CPUs':host.CPUs})    
    return results


def get_vm_groupby_hosts() :
    hosts = get_all_hosts()              
    hostvmlist = []
    for host in hosts:    # for each host get all the vm's that runs on it and add them to list                          
        vmlist = get_all_vm_ofhost(host['id'])
        hostvms = {'hostIP':host['ip'], 'details':vmlist, 'ram':host['RAM'], 'cpus':host['CPUs']}
        hostvmlist.append(hostvms)    
    return (hostvmlist)


def get_task_by_status(task_status, task_num):
    events = db(db.task_queue_event.status == task_status).select(orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))
    return get_task_list(events)
    

def update_task_retry(_task_id):
    #Mark status for VM as 'In Queue'
    db(db.vm_data.id.belongs(db(_task_id == db.task_queue.id)._select(db.task_queue.vm_id))).update(status = VM_STATUS_IN_QUEUE)
    #Mark current task event for the task as IGNORE. 
    db(db.task_queue_event.task_id == _task_id).update(status = TASK_QUEUE_STATUS_IGNORE)
    #Mark task as RETRY. This will call task_queue_update_callback; which will schedule the task
    db(db.task_queue.id == _task_id).update(status = TASK_QUEUE_STATUS_RETRY)


def update_task_ignore(_task_id):
    db(db.task_queue_event.task_id == _task_id).update(status = TASK_QUEUE_STATUS_IGNORE)
    #Delete task from task_queue
    db(db.task_queue.id == _task_id).delete()


def get_search_host_form():
    form = FORM('Host IP:',
                INPUT(_name = 'host_ip',requires = IS_NOT_EMPTY()),
                INPUT(_type = 'submit', _value = 'Get Details'))
    return form


def get_add_host_form():
    form_fields = ['host_ip','host_name','mac_addr','HDD','RAM','CPUs']
    form_labels = {'host_ip':'Host IP','host_name':'Host Name','mac_addr':'MAC Address','HDD':'Harddisk(GB)','RAM':'RAM size in GB:','CPUs':'No. of CPUs:'}

    form = SQLFORM(db.host, fields = form_fields, labels = form_labels, submit_button = 'Add Host')
    return form


def get_host_form(host_ip):
    
    form = get_add_host_form()
    form.vars.host_name = 'host'+str(host_ip.split('.')[3])
    form.vars.host_ip = host_ip
    if is_host_available(host_ip):
        form.vars.mac_addr = get_mac_address(host_ip)
        form.vars.CPUs = get_cpu_num(host_ip)
        form.vars.RAM  = get_ram(host_ip)
        form.vars.status = HOST_STATUS_UP
    else:
        form.vars.status = HOST_STATUS_DOWN

    form.vars.HDD = '300'
    return form 
    

def is_host_available(host_ip):
    try:
        execute_command(host_ip,'root','pwd')
        return True
    except:
        return False


def get_mac_address(host_ip):
    command = "ifconfig -a | grep eth0 | head -n 1"
    ret = execute_command(host_ip, 'root',command)#Returns e.g. eth0      Link encap:Ethernet  HWaddr 18:03:73:0d:e4:49
    ret=ret.strip()
    mac_addr = ret[ret.rindex(' '):].lstrip()
    return mac_addr


def get_cpu_num(host_ip):
    command = "cat /proc/cpuinfo | grep processor | wc -l"
    ret = execute_command(host_ip, 'root',command)
    return int(ret)/2
    

def get_ram(host_ip):
    command = "cat /proc/meminfo | grep MemTotal"
    ret = execute_command(host_ip, 'root',command)#Returns e.g. MemTotal:       32934972 kB
    ram_in_kb = ret[ret.index(' '):-3].strip()
    ram_in_gb = int(round(int(ram_in_kb)/(1024*1024),0))
    return ram_in_gb


def execute_command(machine_ip, user_name, command):

    logger.debug("Starting to establish SSH connection with host" + str(machine_ip))
    import paramiko

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(machine_ip, username = user_name)
    stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable
    output = stdout.readlines()
    logger.debug(output)
    if stderr.readlines():
        logger.error(stderr.readlines())
        raise
    return output[0]

def add_live_migration_option(form):
    live_migration_element = TR('Live Migration:' , INPUT(_type = 'checkbox', _name = 'live_migration')) 
    form[0].insert(3, live_migration_element)      

def get_migrate_vm_form(vm_id):

    host_id = db(db.vm_data.id == vm_id).select(db.vm_data.host_id).first()['host_id']
    host_options = [OPTION(host.host_ip, _value = host.id) for host in db(db.host.id != host_id).select()]

    form = FORM(TABLE(TR('VM Name:', INPUT(_name = 'vm_name', _readonly = True)), 
                      TR('Current Host:', INPUT(_name = 'current_host', _readonly = True)),
                      TR('Destination Host:' , SELECT(*host_options, **dict(_name = 'destination_host', requires = IS_IN_DB(db, 'host.id')))),
                      TR('', INPUT(_type='submit', _value = 'Migrate'))))

    form.vars.vm_name = db(db.vm_data.id == vm_id).select(db.vm_data.vm_name).first()['vm_name']  
    form.vars.current_host = db(db.host.id == host_id).select(db.host.host_ip).first()['host_ip']

    if is_vm_running(vm_id):
        add_live_migration_option(form)
        
    return form

# Check if vm is running
def is_vm_running(vmid):
    vm_status = db(db.vm_data.id == vmid).select().first()['status']
    if vm_status == VM_STATUS_RUNNING:
        return True
    else:
        return False
   
#return the form required to edit vm configs        
def get_edit_vm_config_form(vm_info):
    form = FORM(INPUT(_name='vmname',_type='hidden',requires=IS_NOT_EMPTY()),
                  TABLE(TR('New RAM(MB):',INPUT(_name = 'ram', _value = vm_info['ram'], requires = [IS_NOT_EMPTY(), IS_INT_IN_RANGE(1024,8192)])),
                  TR('New vCPU:',INPUT(_name='vcpus', _value = vm_info['vcpus'], requires=[IS_NOT_EMPTY(), IS_INT_IN_RANGE(1,8)])),
                  TR("",INPUT(_type='submit',_value="Update!"))))
    return form


def validate_user(form):
    username = request.post_vars.user_id
    vm_id = request.args[0]
    user_info = get_user_info(username, [USER,FACULTY,ORGADMIN, ADMIN])

    if not user_info:
        form.errors.user_id = 'Username is not valid'
    else:
        if db((db.user_vm_map.user_id == user_info[0]) & (db.user_vm_map.vm_id == vm_id)).select():
            form.errors.user_id = 'User is already this vm user'
    return form


def get_search_user_form():
    form = FORM('User ID:',
                INPUT(_name = 'user_id',requires = IS_NOT_EMPTY(), _id='add_user_id'),
                INPUT(_type = 'submit', _value = 'Verify'))
    return form
    

def get_user_form(username, vm_id):

    user_info = get_user_info(username, [USER,FACULTY,ORGADMIN, ADMIN])
    user_details = db.user[user_info[0]]
    
    form = FORM(TABLE(TR('Username:', INPUT(_name = 'username', _value = user_details.username, _readonly = True)), 
                      TR('First Name:', INPUT(_name = 'first_name',_value = user_details.first_name, _readonly = True)),
                      TR('Last Name:' , INPUT(_name = 'last_name',_value = user_details.last_name, _readonly = True)),
                      TR('Email ID:' , INPUT(_name = 'email',_value = user_details.email, _readonly = True)),
                      TR(INPUT(_type='button', _value = 'Cancel', _onclick = "window.location='%s';"%URL(r=request,c = 'user', f='settings', args = vm_id )),INPUT(_type = 'submit', _value = 'Confirm Details'))))

    form.vars.user_id = user_details.id
    form.vars.username = user_details.username
    form.vars.first_name = user_details.first_name
    form.vars.last_name = user_details.last_name
    form.vars.email = user_details.email

    return form

def vm_has_snapshots(vm_id):
    if (db(db.snapshot.vm_id == vm_id).select()):
        return True
    else:
        return False
