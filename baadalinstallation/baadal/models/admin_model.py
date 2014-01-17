# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db, request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import IS_MAC_ADDRESS

def get_manage_template_form():
    db.template.id.readable=False # Since we do not want to expose the id field on the grid

    default_sort_order=[db.template.id]

    #Creating the grid object
    form = SQLFORM.grid(db.template, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, csv=False, searchable=False, details=False, showbuttontext=False, maxtextlength=30)
    return form

def get_manage_datastore_form():

    db.datastore.id.readable=False # Since we do not want to expose the used field on the grid

    default_sort_order=[db.datastore.id]

    #Creating the grid object
    form = SQLFORM.grid(db.datastore, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, csv=False, searchable=False, details=False, showbuttontext=False, maxtextlength=30)
    return form


def get_vm_link(row):
    if row.vm_id == None:
        return 'Unassigned'
    else:
        vm_data = db.vm_data[row.vm_id]
        return A(vm_data.vm_name, _href=URL(r=request, c='user',f='settings', args=vm_data.id))


def get_manage_public_ip_pool_form():
    db.public_ip_pool.id.readable=False # Since we do not want to expose the id field on the grid
    db.public_ip_pool.vm_id.readable=False

    default_sort_order=[db.public_ip_pool.id]

    #Creating the grid object
    grid = SQLFORM.grid(db.public_ip_pool, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, links=[dict(header='Assigned to', body=get_vm_link)], csv=False, searchable=False, details=False, showbuttontext=False)

    if grid.create_form:
        grid.create_form[0].insert(-1, TR(SPAN(
                                        LABEL('Range:'),
                                        INPUT(_name='range',value=False,_type='checkbox', _id='public_ip_pool_range')), SPAN(
                                        'From: ',
                                        INPUT(_name='rangeFrom', _id='public_ip_pool_rangeFrom'),
                                        'To: ', 
                                        INPUT(_name='rangeTo', _id='public_ip_pool_rangeTo')),TD()))
        
        grid.create_form.process()

    return grid

def get_manage_private_ip_pool_form():
    db.private_ip_pool.id.readable=False # Since we do not want to expose the id field on the grid
    db.private_ip_pool.vm_id.readable=False

    default_sort_order=[db.private_ip_pool.id]

    #Creating the grid object
    grid = SQLFORM.grid(db.private_ip_pool, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, links=[dict(header='Assigned to', body=get_vm_link)], csv=False, searchable=False, details=False, showbuttontext=False)

    return grid

#Validated IP addresses that are in range
def add_public_ip_range(rangeFrom, rangeTo):
    ip1 = rangeFrom.split('.')
    ip2 = rangeTo.split('.')
    idx =  - (len(ip1[3]))
    subnet = str(rangeFrom[:idx])
    failed = 0
    for x in range(int(ip1[3]), int(ip2[3])+1):
        ip_addr = subnet + str(x)
        if(db.public_ip_pool(public_ip=ip_addr)):
            failed += 1
        else:
            db.public_ip_pool.insert(public_ip=ip_addr)
    return failed
    
def get_org_visibility(row):
    sec_domain = db.security_domain[row.id]
    if sec_domain.visible_to_all:
        return 'All'
    elif sec_domain.org_visibility != None:
        orgs = db(db.organisation.id.belongs(sec_domain.org_visibility)).select()
        return ', '.join(org.name for org in orgs)
    return '-'


def get_security_domain_form():
    
    db.security_domain.id.readable=False 

    fields = (db.security_domain.name, db.security_domain.vlan)
    default_sort_order=[db.security_domain.id]

    form = SQLFORM.grid(db.security_domain, fields=fields, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, links=[dict(header='Visibility', body=get_org_visibility)], csv=False, searchable=False, details=False, selectable=False, showbuttontext=False, maxtextlength=30)
    return form

def check_delete_security_domain(sd_id):
    if db((db.vm_data.security_domain == sd_id)).count() > 0:
        return SECURITY_DOMAIN_DELETE_MESSAGE
    elif db.security_domain[sd_id].name == 'Research':
        return 'Security Domain ''Research'' can''t be deleted.'
    elif db.security_domain[sd_id].name == 'Private':
        return 'Security Domain ''Private'' can''t be deleted.'
    
def get_all_pending_requests():

    vms = db(db.request_queue.status.belongs(REQ_STATUS_REQUESTED, REQ_STATUS_VERIFIED, REQ_STATUS_APPROVED, REQ_STATUS_IN_QUEUE)).select()
    requests = get_pending_request_list(vms)
    for vm_request in requests:
        roles = []
        user_roles = db(db.user_membership.user_id == vm_request['requester_id']).select()
        for user_role in user_roles:
            roles.append(user_role.group_id.role)
        if ADMIN in roles:
            vm_request['requested_by'] = ADMIN
        elif ORGADMIN in roles:
            vm_request['requested_by'] = ORGADMIN
        elif FACULTY in roles:
            vm_request['requested_by'] = FACULTY
        else:
            vm_request['requested_by'] = USER

    return requests


def get_all_vm_list():
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    return get_hosted_vm_list(vms)

def get_all_vm_ofhost(hostid):
    vms = db((db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)) 
             & (db.vm_data.host_id == hostid )).select()
    return get_hosted_vm_list(vms)

def get_vm_identity(vm_name, owner_id):
    vm_owner = db.user[owner_id]
    
    vm_identity = '%s_%s_%s'%(vm_owner.organisation_id.name, vm_owner.username, vm_name)
    
    return vm_identity

def create_clone_task(req_data, params):

    clone_count = req_data.clone_count
    vm_data = db.vm_data[req_data.parent_id]
    
    clone_name = req_data.vm_name
    cnt = 1;
    
    vm_id_list = []
    for count in range(0, clone_count):  # @UnusedVariable

        while(db.vm_data(vm_name=(clone_name+str(cnt)))):
            cnt = cnt+1

        clone_vm_name = clone_name + str(cnt)
        
        clone_vm_id = db.vm_data.insert(
                          vm_name = clone_vm_name, 
                          vm_identity = get_vm_identity(clone_vm_name, vm_data.owner_id), 
                          RAM = vm_data.RAM,
                          HDD = vm_data.HDD,
                          extra_HDD = vm_data.extra_HDD,
                          vCPU = vm_data.vCPU,
                          template_id = vm_data.template_id,
                          owner_id = vm_data.owner_id,
                          requester_id = req_data.requester_id,
                          parent_id = req_data.parent_id,
                          public_ip = PUBLIC_IP_NOT_ASSIGNED,
                          security_domain = vm_data.security_domain,
                          purpose = TASK_TYPE_CLONE_VM,
                          status = VM_STATUS_IN_QUEUE)

        vm_id_list.append(clone_vm_id)
        
        add_vm_users(clone_vm_id, vm_data.requester_id, vm_data.owner_id)
        cnt = cnt+1
        
    params.update({'clone_vm_id':vm_id_list})
    add_vm_task_to_queue(req_data.parent_id, TASK_TYPE_CLONE_VM, params=params, requested_by=req_data.requester_id)

def create_install_task(req_data, params):

    vm_id = db.vm_data.insert(
                  vm_name = req_data.vm_name, 
                  vm_identity = get_vm_identity(req_data.vm_name, req_data.owner_id), 
                  RAM = req_data.RAM,
                  HDD = req_data.HDD,
                  extra_HDD = req_data.extra_HDD,
                  vCPU = req_data.vCPU,
                  template_id = req_data.template_id,
                  requester_id = req_data.requester_id,
                  owner_id = req_data.owner_id,
                  purpose = req_data.purpose,
                  public_ip = PUBLIC_IP_NOT_ASSIGNED if not(req_data.public_ip) else None,
                  security_domain = req_data.security_domain,
                  status = VM_STATUS_IN_QUEUE)
        
    add_vm_users(vm_id, req_data.requester_id, req_data.owner_id, req_data.collaborators)
    add_vm_task_to_queue(vm_id, TASK_TYPE_CREATE_VM, params=params, requested_by=req_data.requester_id)

def create_edit_config_task(req_data, params):
    
    vm_data = db.vm_data[req_data.parent_id]
    
    if vm_data.RAM != req_data.RAM : params['ram'] = req_data.RAM
    if vm_data.vCPU != req_data.vCPU : params['vcpus'] = req_data.vCPU
    if vm_data.public_ip != req_data.public_ip : params['public_ip'] = req_data.public_ip
#     if vm_data.enable_service != req_data.enable_service : params['enable_service'] = req_data.enable_service
    if vm_data.security_domain != req_data.security_domain : params['security_domain'] = req_data.security_domain

    add_vm_task_to_queue(req_data.parent_id, req_data.request_type, params=params)

def enqueue_vm_request(request_id):
    
    req_data = db.request_queue[request_id]
    params={'request_id' : request_id}
    
    if req_data.request_type == TASK_TYPE_CLONE_VM:
        create_clone_task(req_data, params)
    elif req_data.request_type == TASK_TYPE_CREATE_VM:
        create_install_task(req_data, params)
    elif req_data.request_type == TASK_TYPE_EDITCONFIG_VM:
        create_edit_config_task(req_data, params)
    elif req_data.request_type == TASK_TYPE_ATTACH_DISK:
        params.update({'disk_size' : req_data.attach_disk})
        add_vm_task_to_queue(req_data.parent_id, req_data.request_type, params=params, requested_by=req_data.requester_id)
    
    db(db.request_queue.id == request_id).update(status=REQ_STATUS_IN_QUEUE)


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
        results.append({'ip'    :host.host_ip, 
                        'id'    :host.id, 
                        'name'  :host.host_name, 
                        'status':host.status, 
                        'RAM'   :host.RAM,
                        'CPUs'  :host.CPUs})    
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
    events = db(db.task_queue_event.status.belongs(task_status)).select(orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))
    return get_task_list(events)
    

def update_task_retry(event_id):

    task_event = db.task_queue_event[event_id]
    task_queue = db.task_queue[task_event.task_id]
    
    if 'request_id' in task_queue.parameters:
        #Mark status for request as 'In Queue'
        request_id = task_queue.parameters['request_id']
        if db.request_queue[request_id]:
            db.request_queue[request_id] = dict(status=REQ_STATUS_IN_QUEUE)
    
    if task_event.task_type == TASK_TYPE_CREATE_VM:
        db.vm_data[task_event.vm_id] = dict(status=VM_STATUS_IN_QUEUE)
    elif task_event.task_type == TASK_TYPE_CLONE_VM:
        vm_list = task_queue.parameters['clone_vm_id']
        for vm in vm_list:
            db.vm_data[vm] = dict(status=VM_STATUS_IN_QUEUE)

    #Mark current task event for the task as IGNORE. 
    task_event.update_record(status=TASK_QUEUE_STATUS_IGNORE)
    #Mark task as RETRY. This will call task_queue_update_callback; which will schedule a new task
    task_queue.update_record(status=TASK_QUEUE_STATUS_RETRY)


def update_task_ignore(event_id):

    task_event = db.task_queue_event[event_id]
    task_queue = db.task_queue[task_event.task_id]

    if 'request_id' in task_queue.parameters:
        request_id = task_queue.parameters['request_id']
        if db.request_queue[request_id]:
            del db.request_queue[request_id]
    
    if task_event.task_type == TASK_TYPE_CREATE_VM:
        if db.vm_data[task_event.vm_id]: del db.vm_data[task_event.vm_id]
    elif task_event.task_type == TASK_TYPE_CLONE_VM:
        vm_list = task_queue.parameters['clone_vm_id']
        for vm in vm_list:
            if db.vm_data[vm]: del db.vm_data[vm]

    task_event.update_record(task_id = None, status=TASK_QUEUE_STATUS_IGNORE)

    #Delete task from task_queue
    if db.task_queue[task_queue.id]:
        del db.task_queue[task_queue.id]


def get_search_host_form():
    form = FORM('Host IP :',
                INPUT(_name = 'host_ip', _id='host_ip_id', requires = [
                                IS_IPV4(error_message=IP_ERROR_MESSAGE),
                                IS_NOT_IN_DB(db, 'host.host_ip', error_message='Host IP is already configured')]),
                INPUT(_type = 'button', _value = 'Get Details', _class = 'btn-submit'))
    return form


def get_configure_host_form():
    form = FORM('Host MAC:',
                INPUT(_name = 'host_mac_addr', _id='host_mac_id', requires = [
                                IS_MAC_ADDRESS(),
                                IS_NOT_IN_DB(db, 'host.mac_addr', error_message='Host MAC is already configured')]),
                INPUT(_type = 'button', _value = 'Configure', _class = 'btn-submit'))
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
    

def configure_host_by_mac(mac_addr):
    
    avl_ip = db((~db.private_ip_pool.private_ip.belongs(db()._select(db.host.host_ip)))&(db.private_ip_pool.vlan==1)).select(db.private_ip_pool.private_ip).first()['private_ip']
    logger.debug('Available IP for mac address %s is %s'%(mac_addr, avl_ip))
    host_name = 'host'+str(avl_ip.split('.')[3])
    import os
    command = 'echo -e  "host %s {\n\thardware ethernet %s;\n\tfixed-address %s;\n}" >> /etc/dhcp/dhcpd.conf' %(host_name, mac_addr, avl_ip)
    os.system(command)
    command = '/etc/init.d/isc-dhcp-server restart'
    os.system(command)
    db.host[0] = dict(host_ip=avl_ip, 
                      host_name=host_name, 
                      mac_addr=mac_addr, 
                      status=HOST_STATUS_DOWN)

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
   

def validate_user(form):
    username = request.post_vars.user_id
    vm_id = request.args[0]
    user_info = get_user_info(username, [USER,FACULTY,ORGADMIN, ADMIN])

    if not user_info:
        form.errors.user_id = 'Username is not valid'
    else:
        if db((db.user_vm_map.user_id == user_info[0]) 
              & (db.user_vm_map.vm_id == vm_id)).select():
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
    
def updte_host_status(host_id, status):
    db(db.host.id == host_id).update(status = status)
    
def delete_host_from_db(host_id):
    del db.host[host_id]
    
def get_util_period_form():
    
    _dict = {VM_UTIL_24_HOURS : 'Last 24 hours' , 
             VM_UTIL_ONE_WEEK : 'Last One Week',
             VM_UTIL_ONE_MNTH : 'Last One Month',
             VM_UTIL_ONE_YEAR : 'Last One Year'}
    
    form = FORM(TR("Show:", 
           SELECT(_name='util_period', _id='period_select_id',
           *[OPTION(_dict[key], _value=str(key)) for key in _dict.keys()]), 
            A(SPAN(_class='icon-refresh'), _onclick = '$(this).closest(\'form\').submit()', _href='#')))
    return form

def get_vm_util_data(util_period):
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    vmlist = []
    for vm in vms:
        util_result = fetch_rrd_data(vm.vm_identity, util_period)
        element = {'vm_id' : vm.id,
                   'vm_name' : vm.vm_name,
                   'memory' : round(util_result[0], 2),
                   'cpu' : round(util_result[1], 2),
                   'diskr' : round(util_result[2], 2),
                   'diskw' : round(util_result[3], 2),
                   'nwr' : round(util_result[4], 2),
                   'nww' : round(util_result[5], 2)}
        vmlist.append(element)
    return vmlist
        
