# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

def get_add_template_form():
    form_fields = ['name','os_type','arch','hdd','hdfile','type','datastore_id']
    form_labels = {'name':'Name of Template','hdd':'Harddisk(GB)','os_type':'Operating System','arch':'Architecture', 'hdfile':'HD File','type':'Template Type', 'datastore_id':'Datastore'}

    form = SQLFORM(db.template, fields = form_fields, labels = form_labels, submit_button = 'Add Template')
    return form


def get_templates():
    return db().select(db.template.ALL) 


def get_add_datastore_form():
    form_fields = ['ds_name', 'ds_ip', 'capacity', 'username', 'password', 'path']
    form_labels = {'ds_name':'Name', 'ds_ip':'Mount IP', 'capacity':'Capacity (GB)', 'username':'Username', 'password':'Password', 'path':'Path'}

    form = SQLFORM(db.datastore, fields = form_fields, labels = form_labels, submit_button = 'Add Datastore')
    return form


def get_datastores():
    return db().select(db.datastore.ALL) 


def get_all_vm_list():
    vms = db(db.vm_data.status > VM_STATUS_APPROVED).select()
    return get_hosted_vm_list(vms)

def get_all_vm_ofhost(hostid):
    vms = db((db.vm_data.status > VM_STATUS_APPROVED) & (db.vm_data.host_id == hostid )).select()
    return get_hosted_vm_list(vms)


def approve_vm_request(vm_id):
    
    db(db.vm_data.id == vm_id).update(status=VM_STATUS_APPROVED)
    
    vm_data = db(db.vm_data.id == vm_id).select().first()
    add_user_to_vm(vm_data.owner_id, vm_id)
    if(vm_data.owner_id != vm_data.requester_id):
        add_user_to_vm(vm_data.requester_id, vm_id)
    add_vm_task_to_queue(vm_id, TASK_TYPE_CREATE_VM)


def delete_user_vm_access(vm_id,user_id) :    
    db((db.user_vm_map.vm_id == vm_id) & (db.user_vm_map.user_id == user_id)).delete()        


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
        exec_command_on_host(host_ip,'root','pwd')
        return True
    except:
        return False


def get_mac_address(host_ip):
    command = "ifconfig -a | grep eth0 | head -n 1"
    ret = exec_command_on_host(host_ip, 'root',command)#Returns e.g. eth0      Link encap:Ethernet  HWaddr 18:03:73:0d:e4:49
    ret=ret.strip()
    mac_addr = ret[ret.rindex(' '):].lstrip()
    return mac_addr


def get_cpu_num(host_ip):
    command = "cat /proc/cpuinfo | grep processor | wc -l"
    ret = exec_command_on_host(host_ip, 'root',command)
    return int(ret)/2
    

def get_ram(host_ip):
    command = "cat /proc/meminfo | grep MemTotal"
    ret = exec_command_on_host(host_ip, 'root',command)#Returns e.g. MemTotal:       32934972 kB
    ram_in_kb = ret[ret.index(' '):-3].strip()
    ram_in_gb = int(round(int(ram_in_kb)/(1024*1024),0))
    return ram_in_gb


def exec_command_on_host(machine_ip, user_name, command):

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

