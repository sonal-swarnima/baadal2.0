# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db, request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import IS_MAC_ADDRESS, create_dhcp_entry, get_ips_in_range, generate_random_mac,\
    remove_dhcp_entry, create_dhcp_bulk_entry
from host_helper import migrate_all_vms_from_host, is_host_available, get_host_mac_address,\
    get_host_cpu, get_host_ram, get_host_hdd, HOST_STATUS_UP, HOST_STATUS_DOWN, HOST_STATUS_MAINTENANCE
from vm_utilization import fetch_rrd_data, VM_UTIL_24_HOURS, VM_UTIL_ONE_WEEK, VM_UTIL_ONE_MNTH, \
    VM_UTIL_ONE_YEAR
from log_handler import logger

def get_manage_template_form(req_type):
    db.template.id.readable=False # Since we do not want to expose the id field on the grid

    default_sort_order=[db.template.id]

    if req_type in ('new','edit'):
        mark_required(db.template)
    #Creating the grid object
    form = SQLFORM.grid(db.template, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, 
                        csv=False, searchable=False, details=False, showbuttontext=False, maxtextlength=30)
    return form

def get_manage_datastore_form(req_type):

    db.datastore.id.readable=False # Since we do not want to expose the used field on the grid

    default_sort_order=[db.datastore.id]

    if req_type in ('new','edit'):
        mark_required(db.datastore)
    #Creating the grid object
    form = SQLFORM.grid(db.datastore, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, 
                        csv=False, searchable=False, details=False, showbuttontext=False, maxtextlength=30)
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
    grid = SQLFORM.grid(db.public_ip_pool, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, 
                        csv=False, searchable=False, details=False, showbuttontext=False, 
                        links=[dict(header='Assigned to', body=get_vm_link)])

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

def private_ip_on_delete(private_ip_pool_id):
    private_ip_data = db.private_ip_pool[private_ip_pool_id]
    if private_ip_data.vlan != HOST_VLAN_ID:
        remove_dhcp_entry(None, private_ip_data.mac_addr ,private_ip_data.private_ip)
    
def get_manage_private_ip_pool_form():
    db.private_ip_pool.id.readable=False # Since we do not want to expose the id field on the grid
    db.private_ip_pool.vm_id.readable=False

    default_sort_order=[db.private_ip_pool.id]
    #Creating the grid object
    grid = SQLFORM.grid(db.private_ip_pool, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, 
                        csv=False, searchable=False, details=False, showbuttontext=False, 
                        links=[dict(header='Assigned to', body=get_vm_link)], 
                        ondelete=lambda _table, _id: private_ip_on_delete(_id))

    if grid.create_form:
        grid.create_form[0].insert(-1, TR(SPAN(
                                        LABEL('Range:'),
                                        INPUT(_name='range',value=False,_type='checkbox', _id='private_ip_pool_range')), SPAN(
                                        'From: ',
                                        INPUT(_name='rangeFrom', _id='private_ip_pool_rangeFrom'),
                                        'To: ', 
                                        INPUT(_name='rangeTo', _id='private_ip_pool_rangeTo')),TD()))
        
        grid.create_form.process(onsuccess=lambda form: add_private_ip(form.vars.id))

    return grid

#Add Validated IP addresses that are in range
def add_public_ip_range(rangeFrom, rangeTo):

    failed = 0
    for ip_addr in get_ips_in_range(rangeFrom, rangeTo):
        if(db.public_ip_pool(public_ip=ip_addr)):
            failed += 1
        else:
            db.public_ip_pool.insert(public_ip=ip_addr)
    return failed
    
#Generate mac address and add them with IPs
def add_private_ip_range(rangeFrom, rangeTo, vlan):

    failed = 0
    dhcp_info_list = []
    for ip_addr in get_ips_in_range(rangeFrom, rangeTo):
        mac_address = None
        if vlan != HOST_VLAN_ID:
            while True:
                mac_address = generate_random_mac()
                if not (db.private_ip_pool(mac_addr=mac_address)):break
        
        if(db.private_ip_pool(private_ip=ip_addr)):
            failed += 1
        else:
            db.private_ip_pool.insert(private_ip=ip_addr, mac_addr=mac_address, vlan=vlan)
            if vlan != HOST_VLAN_ID:
                dhcp_info_list.append((None, mac_address, ip_addr))
    
    create_dhcp_bulk_entry(dhcp_info_list)
    
    return failed


#Generate mac address and add them with IP
def add_private_ip(ip_pool_id):

    private_ip_pool = db.private_ip_pool[ip_pool_id]
    if private_ip_pool.vlan != HOST_VLAN_ID:
        mac_address = private_ip_pool.mac_addr
        if mac_address == None:
            while True:
                mac_address = generate_random_mac()
                if not (db.private_ip_pool(mac_addr=mac_address)):break
            #Update generated mac address in DB
            private_ip_pool.update_record(mac_addr=mac_address)

        create_dhcp_entry(None, mac_address, private_ip_pool.private_ip)


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
    
    create = True
    avl_vlan = db(~db.vlan.id.belongs(db()._select(db.security_domain.vlan))).count()
    if avl_vlan == 0: create = False

    form = SQLFORM.grid(db.security_domain, fields=fields, orderby=default_sort_order, paginate=ITEMS_PER_PAGE, create=create, 
                        csv=False, searchable=False, details=False, selectable=False, showbuttontext=False, maxtextlength=30, 
                        links=[dict(header='Visibility', body=get_org_visibility)])
    return form

# Check if the security domain can be deleted
def check_delete_security_domain(sd_id):
    if db.vm_data(security_domain = sd_id):
        return SECURITY_DOMAIN_DELETE_MESSAGE
    elif db.security_domain[sd_id].name in ('Research', 'Private', 'Infrastructure'):
        return 'Security Domain %s can''t be deleted.' %(db.security_domain[sd_id].name)
    
def check_delete_private_ip(private_ip_id):
    if not db.private_ip_pool(id=private_ip_id, vm_id = None):
        return PRIVATE_IP_DELETE_MESSAGE

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

def get_all_unregistered_users():
    unregistered_users=db(db.user.registration_key == USER_PENDING_APPROVAL).select()
    return unregistered_users

def get_users_with_roles():
    all_users = db((db.user.registration_key == "") & (db.user.block_user == False)).select()
    for user in all_users:
        user['organisation'] = user.organisation_id.name
        roles=[]
        for membership in db(db.user_membership.user_id == user.id).select(db.user_membership.group_id):
            roles.extend([membership.group_id])
        user['roles'] = roles
    return all_users
            

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
                          purpose = req_data.purpose,
                          status = VM_STATUS_IN_QUEUE)

        vm_id_list.append(clone_vm_id)
        
        vm_users=[]
        for user in db(db.user_vm_map.vm_id == vm_data.id).select(db.user_vm_map.user_id):
            vm_users.append(user['user_id'])

        add_vm_users(clone_vm_id, vm_data.requester_id, vm_data.owner_id, vm_users=vm_users)
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
    if (vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED) ^ req_data.public_ip:
        params['public_ip'] = req_data.public_ip
    
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


def delete_user_vm_access(vm_id, user_id) :

    vm_data = db.vm_data[vm_id]
    if vm_data.owner_id == user_id:
        vm_data.update_record(owner_id = -1)
    if vm_data.requester_id == user_id:
        vm_data.update_record(requester_id = -1)

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

    task_event_data = db.task_queue_event[event_id]
    task_queue_data = db.task_queue[task_event_data.task_id]
    
    if 'request_id' in task_queue_data.parameters:
        #Mark status for request as 'In Queue'
        request_id = task_queue_data.parameters['request_id']
        if db.request_queue[request_id]:
            db.request_queue[request_id] = dict(status=REQ_STATUS_IN_QUEUE)
    
    if task_event_data.task_type == TASK_TYPE_CREATE_VM:
        db.vm_data[task_event_data.vm_id] = dict(status=VM_STATUS_IN_QUEUE)
    elif task_event_data.task_type == TASK_TYPE_CLONE_VM:
        vm_list = task_queue_data.parameters['clone_vm_id']
        for vm in vm_list:
            db.vm_data[vm] = dict(status=VM_STATUS_IN_QUEUE)

    #Mark current task event for the task as IGNORE. 
    task_event_data.update_record(status=TASK_QUEUE_STATUS_RETRY)
    #Mark task as RETRY. This will call task_queue_update_callback; which will schedule a new task
    task_queue_data.update_record(status=TASK_QUEUE_STATUS_RETRY)


def update_task_ignore(event_id):

    task_event_data = db.task_queue_event[event_id]
    task_queue_data = db.task_queue[task_event_data.task_id]

    if 'request_id' in task_queue_data.parameters:
        request_id = task_queue_data.parameters['request_id']
        if db.request_queue[request_id]:
            del db.request_queue[request_id]
    
    if task_event_data.task_type == TASK_TYPE_CREATE_VM:
        if db.vm_data[task_event_data.vm_id]: del db.vm_data[task_event_data.vm_id]
    elif task_event_data.task_type == TASK_TYPE_CLONE_VM:
        vm_list = task_queue_data.parameters['clone_vm_id']
        for vm in vm_list:
            if db.vm_data[vm]: del db.vm_data[vm]

    task_event_data.update_record(task_id = None, status=TASK_QUEUE_STATUS_IGNORE)

    #Delete task from task_queue
    if db.task_queue[task_queue_data.id]:
        del db.task_queue[task_queue_data.id]


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
        form.vars.mac_addr = get_host_mac_address(host_ip)
        form.vars.CPUs = get_host_cpu(host_ip)
        form.vars.RAM  = get_host_ram(host_ip)
        form.vars.HDD = get_host_hdd(host_ip)
        form.vars.status = HOST_STATUS_UP
    else:
        form.vars.status = HOST_STATUS_DOWN

    return form
    

def configure_host_by_mac(mac_addr):
    
    avl_private_ip = None
    ip_info = db.private_ip_pool(mac_addr=mac_addr)
    if ip_info:
        avl_private_ip = ip_info.private_ip
    else:
        avl_ip = db((~db.private_ip_pool.private_ip.belongs(db()._select(db.host.host_ip)))
                    & (db.private_ip_pool.vlan == HOST_VLAN_ID)).select(db.private_ip_pool.private_ip)
        if avl_ip.first():
            avl_private_ip = avl_ip.first()['private_ip']
            

    if avl_private_ip:
        logger.debug('Available IP for mac address %s is %s'%(mac_addr, avl_private_ip))
        host_name = 'host'+str(avl_private_ip.split('.')[3])
        create_dhcp_entry(host_name, mac_addr, avl_private_ip)
        db.host[0] = dict(host_ip=avl_private_ip, 
                          host_name=host_name, 
                          mac_addr=mac_addr, 
                          status=HOST_STATUS_DOWN)
        return 'Host configured. Proceed for PXE boot.'
    else:
        logger.error('Available Private IPs for host are exhausted.')
        return 'Available Private IPs for host are exhausted.'


def add_live_migration_option(form):
    live_migration_element = TR('Live Migration:' , INPUT(_type = 'checkbox', _name = 'live_migration')) 
    form[0].insert(3, live_migration_element)      


def get_migrate_vm_form(vm_id):

    form = None
    host_id = db(db.vm_data.id == vm_id).select(db.vm_data.host_id).first()['host_id']
    host_options = [OPTION(host.host_ip, _value = host.id) for host in db((db.host.id != host_id) & (db.host.status == 1)).select()]
    if host_options:
        form = FORM(TABLE(TR('VM Name:', INPUT(_name = 'vm_name', _readonly = True)), 
                      TR('Current Host:', INPUT(_name = 'current_host', _readonly = True)),
                      TR('Destination Host:' , SELECT(*host_options, **dict(_name = 'destination_host', requires = IS_IN_DB(db, 'host.id')))),
                      TR('', INPUT(_type='submit', _value = 'Migrate'))))

        form.vars.vm_name = db(db.vm_data.id == vm_id).select(db.vm_data.vm_name).first()['vm_name']  
        form.vars.current_host = db(db.host.id == host_id).select(db.host.host_ip).first()['host_ip']

        if is_vm_running(vm_id):
            add_live_migration_option(form)

    else:
        session.flash = "No host available right now"
        
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
    host_data = db.host[host_id]
    if status == HOST_STATUS_UP:
        if is_host_available(host_data.host_ip):
            if host_data.CPUs == 0:
                cpu_num = get_host_cpu(host_data.host_ip)
                ram_gb = get_host_ram(host_data.host_ip)
                hdd_gb = get_host_hdd(host_data.host_ip)
                host_data.update_record(CPUs=cpu_num, RAM=ram_gb, HDD=hdd_gb)
        else:
            return False
    elif status == HOST_STATUS_MAINTENANCE:
        migrate_all_vms_from_host(host_data.host_ip)
        host_data.update_record(status=HOST_STATUS_MAINTENANCE)
    host_data.update_record(status = status)
    return True
        
def delete_host_from_db(host_id):
    
    host_data = db.host[host_id]
    private_ip_data = db.private_ip_pool(private_ip = host_data.host_ip)    
    if private_ip_data:
        remove_dhcp_entry(host_data.host_name, host_data.mac_addr, private_ip_data['private_ip'])
    db(db.scheduler_task.uuid == (UUID_VM_UTIL_RRD + "=" + str(host_data.host_ip))).delete()
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


def check_vm_resource(request_id):
    
    req_data = db.request_queue[request_id]
    security_domain_id = req_data.security_domain
    
    vlans = db(db.security_domain.id == security_domain_id)._select(db.security_domain.vlan)
    avl_ip = db((db.private_ip_pool.vm_id == None) & (db.private_ip_pool.vlan.belongs(vlans))).count()
    
    message = None
    if req_data.request_type == TASK_TYPE_CREATE_VM:
        if avl_ip == 0:
            message = "No private IPs available for security domain '%s" % req_data.security_domain.name
        if req_data.public_ip:
            
            if db(db.public_ip_pool.vm_id == None).count() == 0:
                message = "" if message == None else message + ", "
                message += "No public IP available"
            
    elif req_data.request_type == TASK_TYPE_CLONE_VM:
        if avl_ip < req_data.clone_count:
            message = "%s private IP(s) available for security domain '%s" % (str(avl_ip), req_data.security_domain.name)

    return message if message != None else 'Success'
    
def specify_user_roles(user_id, user_roles):
    message = None
    try:
        if not user_roles:
            message = "Only user role activated for user"
        else:
            for role in user_roles:
                db.user_membership.insert(user_id=user_id, group_id=role) 
            message = "User Activated with specified roles"
        db(db.user.id == user_id).update(registration_key='')    
        for row in db(db.user_group.role == USER).select(db.user_group.id):
                role_type_user = row.id
        db.user_membership.insert(user_id=user_id, group_id=role_type_user)
    except Exception:
        logger.debug("Ignoring duplicate role entry")
    return message
    
def disable_user(user_id):
    db(db.user.id == user_id).update(registration_key='disable')
    return "User disabled in DB"

def get_baadal_status_info():
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    vm_info = []
    for vm_detail in vms:
#         sys_snapshot = db.snapshot(vm_id=vm_detail.id,type=SNAPSHOT_SYSTEM)
        element = {'id' : vm_detail.id,
                   'vm_name' : vm_detail.vm_identity, 
                   'host_ip' : vm_detail.host_id.host_ip, 
                   'vm_status' : get_vm_status(vm_detail.status),
                   'sys_snapshot': True if (vm_detail.status == VM_STATUS_SHUTDOWN) else False}
        vm_info.append(element)
    return vm_info





def get_baadal_status_info():
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    vm_info = []
    for vm_detail in vms:
#         sys_snapshot = db.snapshot(vm_id=vm_detail.id,type=SNAPSHOT_SYSTEM)
        element = {'id' : vm_detail.id,
                   'vm_name' : vm_detail.vm_identity, 
                   'host_ip' : vm_detail.host_id.host_ip, 
                   'vm_status' : get_vm_status(vm_detail.status),
                   'sys_snapshot': True if (vm_detail.status == VM_STATUS_SHUTDOWN) else False}
        vm_info.append(element)
    return vm_info

def get_host_config(host_ip):
    hosts=db(db.host.host_ip==host_ip).select()
    host_info=[]
    for host_detail in hosts:
        element = {'id' : host_detail.id,
                   'name' : host_detail.host_name, 
                   'host_ip' : host_detail.host_ip, 
                   'hdd' :  str(host_detail.HDD) + ' GB', 
                   'ram' : str(host_detail.RAM ) + ' GB', 
                   'vcpus' : str(host_detail.CPUs) + ' CPU',
                   'mac_addr':host_detail.mac_addr,
                   'status':host_detail.status}
        host_info.append(element)
    return host_info

