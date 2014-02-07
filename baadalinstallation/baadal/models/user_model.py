# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db,auth,request
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from auth_user import fetch_ldap_user, create_or_update_user
from helper import is_moderator, is_orgadmin, is_faculty

def get_my_requests():
    
    requests = db(db.request_queue.requester_id==auth.user.id).select(db.request_queue.ALL)
    return get_pending_request_list(requests)


def get_my_hosted_vm():
    vms = db((~db.vm_data.status.belongs(VM_STATUS_IN_QUEUE, VM_STATUS_UNKNOWN)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select(db.vm_data.ALL)

    return get_hosted_vm_list(vms)

#Create configuration dropdowns
def get_configuration_elem(form):
    
    vm_configs = db().select(db.vm_config.ALL, orderby =db.vm_config.template_id)
    _label = LABEL(SPAN('Configuration:', ' ', SPAN('*', _class='fld_required'), ' '))
    _id=0
    i=0
    select = SELECT(_name='configuration_'+str(_id))
    for config in vm_configs:
        if config.template_id != _id:
            config_elem = TR(_label, select, TD(), _id='config_row__'+str(_id))
            form[0].insert(2,config_elem)#insert tr element in the form
            _id = config.template_id
            select = SELECT(_name='configuration_'+str(_id))
            i=0
        
        display = str(config.CPU) + ' CPU, ' + str(config.RAM) + 'GB RAM, ' + str(config.HDD) + 'GB HDD'
        value = str(config.CPU) + ',' + str(config.RAM) + ',' + str(config.HDD)
        select.insert(i,OPTION(display, _value=value))
        i+=1
        
        #Create HTML tr, and insert label and select box
    config_elem = TR(_label,select,TD(),_id='config_row__'+str(_id))
    form[0].insert(2,config_elem)#insert tr element in the form

# Gets CPU, RAM and HDD information on the basis of template selected.
def set_configuration_elem(form):

    configVal = form.vars.configuration_0 #Default configuration dropdown
    template = form.vars.template_id
    
    # if configuration specific to selected template is available
    if eval('form.vars.configuration_'+str(template)) != None:
        configVal = eval('form.vars.configuration_'+str(template))

    configVal = configVal.split(',')
    
    form.vars.vCPU = int(configVal[0])
    form.vars.RAM = int(configVal[1])*1024
    form.vars.HDD = int(configVal[2])
    if form.vars.extra_HDD == None:
        form.vars.extra_HDD = 0


def validate_approver(form):

    faculty_user_name = request.post_vars.faculty_user
    
    faculty_info = get_user_info(faculty_user_name, [FACULTY])
    if faculty_info != None:
        form.vars.owner_id = faculty_info[0]
        form.vars.status = REQ_STATUS_REQUESTED
    else:
        form.errors.faculty_user='Faculty Approver Username is not valid'


def send_remind_faculty_email(req_id):
    req_data = db.request_queue[req_id]
    send_email_to_approver(req_data.owner_id, req_data.requester_id, req_data.request_type, req_data.request_time)


def send_remind_orgadmin_email(req_id):
    req_data = db.request_queue[req_id]
    admins = db((db.user.organisation_id == req_data.requester_id.organisation_id) 
                & (db.user.id == db.user_membership.user_id) 
                & (db.user_membership.group_id == db.user_group.id) 
                & (db.user_group.role == ORGADMIN)).select(db.user.id)
                
    for admin in admins:
        send_email_to_approver(admin.id, req_data.requester_id, req_data.request_type, req_data.request_time)


def get_request_status():
    status = REQ_STATUS_REQUESTED
    if (is_moderator() or is_orgadmin()):
        status = REQ_STATUS_APPROVED
    elif is_faculty():
        status = REQ_STATUS_VERIFIED

    return status
    
def request_vm_validation(form):
    
    set_configuration_elem(form)
    form.vars.status = get_request_status()

    if (is_moderator() or is_orgadmin() or is_faculty()):
        form.vars.owner_id = auth.user.id
    else:
        validate_approver(form)

    vm_users = request.post_vars.vm_users
    user_list = []
    if vm_users and len(vm_users) > 1:
        for vm_user in vm_users[1:-1].split('|'):
            user_list.append(db(db.user.username == vm_user).select(db.user.id).first()['id'])
    
    if request.post_vars.faculty_user:
        user_list.append(form.vars.owner_id)
    form.vars.collaborators = user_list

    user_set = set(user_list)
    user_set.add(auth.user.id)

    vms = db((db.vm_data.id == db.user_vm_map.vm_id) & 
             (db.user_vm_map.user_id.belongs(user_set))).select(db.vm_data.vm_name)
    
    if vms.find(lambda row: row.vm_name == form.vars.vm_name, limitby=(0,1)):
        form.errors.vm_name = 'VM name should be unique for the user. Choose another name.'

    requests = db((db.request_queue.owner_id.belongs(user_set)) |
             (db.request_queue.requester_id.belongs(user_set))).select(db.request_queue.vm_name)
    
    if requests.find(lambda row: row.vm_name == form.vars.vm_name, limitby=(0,1)):
        form.errors.vm_name = 'VM name should be unique for the user. Choose another name.'
        

def add_faculty_approver(form):

    _input=INPUT(_name='faculty_user',_id='faculty_user') # create INPUT
    _link = TD(A('Verify', _href='#',_onclick='verify_faculty()'))
    _label = LABEL(SPAN('Faculty Approver:', ' ', SPAN('*', _class='fld_required'), ' '))
    faculty_elem = TR(_label,_input,_link,_id='faculty_row')
    form[0].insert(-1,faculty_elem)#insert tr element in the form


def add_collaborators(form):

    _input=INPUT(_name='collaborator',_id='collaborator') # create INPUT
    _link = TD(A('Add', _href='#',_onclick='check_collaborator()'))
    collaborator_elem = TR(LABEL('Collaborators:'),_input,_link,_id='collaborator_row')
    form[0].insert(-1, collaborator_elem)#insert tr element in the form


def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','extra_HDD','purpose', 'security_domain', 'public_ip']

    db.request_queue.request_type.default = TASK_TYPE_CREATE_VM
    db.request_queue.requester_id.default = auth.user.id
    _query = (db.security_domain.visible_to_all == True) | (db.security_domain.org_visibility.contains(auth.user.organisation_id))
    db.request_queue.security_domain.requires = IS_IN_DB(db(_query), 'security_domain.id', '%(name)s', zero=None)
    db.request_queue.security_domain.default = 2
    db.request_queue.security_domain.notnull = True
    db.request_queue.template_id.notnull = True

    mark_required(db.request_queue)
    form =SQLFORM(db.request_queue, fields = form_fields, hidden=dict(vm_users='|'))
    get_configuration_elem(form) # Create dropdowns for configuration
    
    if not(is_moderator() or is_orgadmin() or is_faculty()):
        add_faculty_approver(form)
    add_collaborators(form)
    return form


def get_user_info(username, roles):
    user_query = db((db.user.username == username) 
             & (db.user.organisation_id == auth.user.organisation_id)
             & (db.user.id == db.user_membership.user_id)
             & (db.user_membership.group_id == db.user_group.id)
             & (db.user_group.role.belongs(roles)))
    
    user = user_query.select(db.user.ALL).first()
    
    # If user not present in DB
    if not user:
        if current.auth_type == AUTH_TYPE_LDAP :
            user_info = fetch_ldap_user(username)
            if user_info:
                if [obj for obj in roles if obj in user_info['roles']]:
                    create_or_update_user(user_info, False)
                    user = user_query.select(db.user.ALL).first()
    
    if user:
        return (user['id'], (user['first_name'] + ' ' + user['last_name']))	


def get_my_task_list(task_status, task_num):
    
    task_query = db((db.task_queue_event.status.belongs(task_status)) 
                    & ((db.task_queue_event.vm_id.belongs(
                            db(auth.user.id == db.user_vm_map.user_id)._select(db.user_vm_map.vm_id))) 
                     | (db.task_queue_event.requester_id == auth.user.id)))
    events = task_query.select(db.task_queue_event.ALL, distinct=True, orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))

    return get_task_list(events)

   
def get_vm_config(vm_id):

    vminfo = get_vm_info(vm_id)
    if not vminfo : return
    
    vm_info_map = {'id'               : str(vminfo.id),
                   'name'             : str(vminfo.vm_name),
                   'hdd'              : str(vminfo.HDD)+'GB' + ('+ ' + str(vminfo.extra_HDD) + 'GB' if vminfo.extra_HDD!=0 else ''),
                   'ram'              : str(vminfo.RAM),
                   'vcpus'            : str(vminfo.vCPU),
                   'status'           : get_vm_status(vminfo.status),
                   'ostype'           : 'Linux',
                   'purpose'          : str(vminfo.purpose),
                   'private_ip'       : str(vminfo.private_ip),
                   'public_ip'        : str(vminfo.public_ip),
                   'security_domain'  : str(vminfo.security_domain.name)}

    if is_moderator():
        vm_info_map.update({'host' : str(vminfo.host_id.host_ip),
                             'vnc'  : str(vminfo.vnc_port)})

    return vm_info_map  
    
    
def get_vm_user_list(vm_id) :		
    vm_users = db((vm_id == db.user_vm_map.vm_id) & (db.user_vm_map.user_id == db.user.id)).select(db.user.ALL)
    user_id_lst = []
    for vm_user in vm_users:
        user_id_lst.append(vm_user)
    return user_id_lst

def is_request_in_queue(vm_id, task_type, snapshot_id=None):

    _data =  db((db.task_queue.vm_id == vm_id) & (db.task_queue.task_type == task_type) 
                   & db.task_queue.status.belongs(TASK_QUEUE_STATUS_PENDING, TASK_QUEUE_STATUS_PROCESSING)).select()
    if _data:
        if snapshot_id != None:
            for req_data in _data:    
                params = req_data.parameters
                if params['snapshot_id'] == snapshot_id:
                    return True
        else:
            return True
    else:
        return False

def check_snapshot_limit(vm_id):
    snapshots = db((db.snapshot.vm_id == vm_id) & (db.snapshot.type == SNAPSHOT_USER)).count()
    logger.debug("No of snapshots are " + str(snapshots))
    if snapshots < SNAPSHOTTING_LIMIT:
        return True
    else:
        return False

def get_clone_vm_form(vm_id):
    vm_data = db.vm_data[vm_id]
    
    clone_name = vm_data.vm_name + '_clone'
    cnt = 1;
    while(db.request_queue(vm_name=(clone_name+str(cnt)))):
        cnt = cnt+1
    
    db.request_queue.parent_id.default = vm_data.id
    db.request_queue.vm_name.default = clone_name + str(cnt)
    db.request_queue.HDD.default = vm_data.HDD
    db.request_queue.RAM.default = vm_data.RAM
    db.request_queue.vCPU.default = vm_data.vCPU
    db.request_queue.request_type.default = TASK_TYPE_CLONE_VM
    db.request_queue.status.default = get_request_status()
    db.request_queue.requester_id.default = auth.user.id
    db.request_queue.owner_id.default = vm_data.owner_id
    db.request_queue.security_domain.default = vm_data.security_domain
    db.request_queue.clone_count.requires = IS_INT_IN_RANGE(1,101)
    db.request_queue.vm_name.writable = False
    form_fields = ['vm_name', 'clone_count', 'purpose']
    
    form =SQLFORM(db.request_queue, fields = form_fields)
    return form    


def get_attach_extra_disk_form(vm_id):

    vm_data = db.vm_data[vm_id]
    
    db.request_queue.parent_id.default = vm_data.id
    db.request_queue.vm_name.default = vm_data.vm_name
    db.request_queue.RAM.default = vm_data.RAM
    db.request_queue.vCPU.default = vm_data.vCPU
    db.request_queue.HDD.default = vm_data.HDD
    db.request_queue.extra_HDD.default = vm_data.extra_HDD
    db.request_queue.request_type.default = TASK_TYPE_ATTACH_DISK
    db.request_queue.status.default = get_request_status()
    db.request_queue.requester_id.default = auth.user.id
    db.request_queue.owner_id.default = vm_data.owner_id
    db.request_queue.attach_disk.requires = IS_INT_IN_RANGE(1,101)
    db.request_queue.vm_name.writable = False
    db.request_queue.HDD.writable = False
    db.request_queue.extra_HDD.writable = False

    form_fields = ['vm_name', 'HDD', 'extra_HDD', 'attach_disk', 'purpose']
    
    form =SQLFORM(db.request_queue, fields = form_fields)
    return form    


def get_edit_vm_config_form(vm_id):
    
    vm_data = db.vm_data[vm_id]
    db.request_queue.parent_id.default = vm_data.id
    db.request_queue.vm_name.default = vm_data.vm_name
    db.request_queue.RAM.default = vm_data.RAM
    db.request_queue.RAM.requires = IS_IN_SET(VM_RAM_SET, zero=None)
    db.request_queue.vCPU.default = vm_data.vCPU
    db.request_queue.vCPU.requires = IS_IN_SET(VM_vCPU_SET, zero=None)
    db.request_queue.HDD.default = vm_data.HDD
#     db.request_queue.enable_service.default = vm_data.enable_service
    db.request_queue.public_ip.default = (vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED)
    db.request_queue.security_domain.default = vm_data.security_domain
    db.request_queue.request_type.default = TASK_TYPE_EDITCONFIG_VM
    db.request_queue.status.default = get_request_status()
    db.request_queue.requester_id.default = auth.user.id
    db.request_queue.owner_id.default = vm_data.owner_id
    _query = (db.security_domain.visible_to_all == True) | (db.security_domain.org_visibility.contains(vm_data.requester_id.organisation_id))
    db.request_queue.security_domain.requires = IS_IN_DB(db(_query), 'security_domain.id', '%(name)s', zero=None)
    
    form_fields = ['vm_name', 'RAM', 'vCPU', 'public_ip', 'security_domain','purpose']
    form = SQLFORM(db.request_queue, fields = form_fields)
#     add_security_domain(form, vm_id=vm_id)
    return form

def get_mail_admin_form():
    form = FORM(TABLE(TR('Type:'),
                TR(TABLE(TR(TD(INPUT(_name='email_type', _type='radio', _value='report_bug', value='report_bug')),TD('Report Bug'),
                TD(INPUT(_name='email_type', _type='radio', _value='request')),TD('Log Request'),
                TD(INPUT(_name='email_type', _type='radio', _value='complaint')),TD('Lodge Complaint')))),TR('Subject:'),
                TR(TEXTAREA(_name='email_subject',_style='height:50px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),TR('Message:'),
                TR(TEXTAREA(_name='email_message',_style='height:100px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),
                
                TR(INPUT(_type = 'submit', _value = 'Send Email')),_style='width:100%; border:0px'))
    return form

def get_vm_history(vm_id):
    
    vm_history = []
    for vm_log in db(db.vm_event_log.vm_id == vm_id).select(orderby = ~db.vm_event_log.timestamp):
        element = {'attribute' : vm_log.attribute,
                   'old_value' : vm_log.old_value,
                   'new_value' : vm_log.new_value,
                   'requested_by' : vm_log.requester_id.first_name + ' ' + vm_log.requester_id.last_name if vm_log.requester_id > 0 else 'System User', 
                   'timestamp' : vm_log.timestamp}
        vm_history.append(element)
    return vm_history
