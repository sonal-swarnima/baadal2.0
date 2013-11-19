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
from helper import is_moderator, is_orgadmin, is_faculty, get_vm_template_config
from auth_user import fetch_ldap_user, create_or_update_user

def get_my_pending_vm():
    
    requests = db(db.request_queue.requester_id==auth.user.id).select(db.request_queue.ALL)
    return get_pending_request_list(requests)


def get_my_hosted_vm():
    vms = db((~db.vm_data.status.belongs(VM_STATUS_IN_QUEUE, VM_STATUS_UNKNOWN)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select(db.vm_data.ALL)

    return get_hosted_vm_list(vms)

#Create configuration dropdowns
def get_configuration_elem(form):
    
    xmldoc = get_vm_template_config() # Read vm_template_config.xml
    itemlist = xmldoc.getElementsByTagName('template')
    _id=0 #for default configurations set, select box id will be configuration_0 
    for item in itemlist:
        if item.attributes['default'].value != 'true': #if not default, get the id 
            _id=item.attributes['id'].value
        select=SELECT(_name='configuration_'+str(_id)) # create HTML select with name as configuration_id
        cfglist = item.getElementsByTagName('config')
        i=0
        for cfg in cfglist:
            #Create HTML options and insert into select
            select.insert(i,OPTION(cfg.attributes['display'].value,_value=cfg.attributes['value'].value))
            i+=1
        
        #Create HTML tr, and insert label and select box
        config_elem = TR(LABEL('Configuration:'),select,TD(),_id='config_row__'+str(_id))
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
    faculty_user = request.post_vars.vm_owner
    faculty_user_name = request.post_vars.faculty_user
    
    if(faculty_user != ''):
        faculty_info = get_user_info(faculty_user, [FACULTY])
        if faculty_info[1] == faculty_user_name:
            form.vars.owner_id = faculty_info[0]
            form.vars.status = REQ_STATUS_REQUESTED
            return
    
    faculty_info = get_user_info(faculty_user_name, [FACULTY])
    if faculty_info != None:
        form.vars.owner_id = faculty_info[0]
        form.vars.status = REQ_STATUS_REQUESTED
    else:
        form.errors.faculty_user='Faculty Approver Username is not valid'


def send_remind_faculty_email(vm_id):
    vm_data = db.vm_data[vm_id]
    send_email_to_faculty(vm_data.owner_id, vm_data.vm_name, vm_data.start_time)

def get_request_status():
    status = REQ_STATUS_REQUESTED
    if (is_moderator() | is_orgadmin()):
        status = REQ_STATUS_APPROVED
    elif is_faculty():
        status = REQ_STATUS_VERIFIED

    return status
    
def request_vm_validation(form):
    set_configuration_elem(form)
    form.vars.status = get_request_status()

    if (is_moderator() | is_orgadmin()):
        form.vars.owner_id = auth.user.id
    elif is_faculty():
        form.vars.owner_id = auth.user.id
    else:
        validate_approver(form)

    form.vars.security_domain = form.vars.sec_domain
    vm_users = request.post_vars.vm_users
    user_list = []
    if vm_users and len(vm_users) > 1:
        for vm_user in vm_users[1:-1].split('|'):
            user_list.append(db(db.user.username == vm_user).select(db.user.id).first()['id'])
    form.vars.collaborators = user_list
    

def add_faculty_approver(form):

    _input=INPUT(_name='faculty_user',_id='faculty_user') # create INPUT
    _link = TD(A('Verify', _href='#',_onclick='verify_faculty()'))
    faculty_elem = TR(LABEL('Faculty Approver:'),_input,_link,_id='faculty_row')
    form[0].insert(-1,faculty_elem)#insert tr element in the form


def add_collaborators(form):

    _input=INPUT(_name='collaborator',_id='collaborator') # create INPUT
    _link = TD(A('Add', _href='#',_onclick='add_collaborator()'))
    collaborator_elem = TR(LABEL('Collaborators:'),_input,_link,_id='collaborator_row')
    form[0].insert(-1, collaborator_elem)#insert tr element in the form


def get_security_domain():
    sec_domains = db((db.security_domain.visible_to_all == True) | (db.security_domain.org_visibility.contains(auth.user.organisation_id))).select()
    return sec_domains


def add_security_domain(form):
    
    select=SELECT(_name='sec_domain') # create HTML select
    i=0
    for sec_domain in get_security_domain():
        select.insert(i, OPTION(sec_domain['name'], _value = sec_domain['id']))
        i = i+1

    vlan_elem = TR(LABEL('Security Domain:'), select ,TD(), _id='security_domain_row')
    form[0].insert(-1, vlan_elem)#insert tr element in the form


def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','extra_HDD','purpose', 'enable_ssh', 'enable_http', 'public_ip']

    db.request_queue.request_type.default = TASK_TYPE_CREATE_VM
    db.request_queue.requester_id.default = auth.user.id

    form =SQLFORM(db.request_queue, fields = form_fields, hidden=dict(vm_owner='',vm_users='|'))
    get_configuration_elem(form) # Create dropdowns for configuration
    
    if not(is_moderator() | is_orgadmin() | is_faculty()):
        add_faculty_approver(form)
    add_collaborators(form)
    add_security_domain(form)
    return form


def get_user_info(username, roles):
    user_query = db((db.user.username == username) 
             & (db.user.id == db.user_membership.user_id)
             & (db.user_membership.group_id == db.user_group.id)
             & (db.user_group.role.belongs(roles)))
    user = user_query.select().first()
    # If user not present in DB
    if not user:
        if current.auth_type == 'ldap':
            user_info = fetch_ldap_user(username)
            if user_info:
                if [obj for obj in roles if obj in user_info['roles']]:
                    create_or_update_user(user_info, False)
                    user = user_query.select().first()
    
    if user:
        return (user.user.id, (user.user.first_name + ' ' + user.user.last_name))	


def get_my_task_list(task_status, task_num):
    task_query = db((db.task_queue_event.status == task_status) 
                    & (db.task_queue_event.vm_id == db.vm_data.id) 
                    & (db.vm_data.requester_id==auth.user.id))

    events = task_query.select(db.task_queue_event.ALL, orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))

    return get_task_list(events)

   
def get_vm_config(vm_id):

    vminfo = get_vm_info(vm_id)
    
    vm_info_map = {'id'              : str(vminfo.id),
                   'name'            : str(vminfo.vm_name),
                   'hdd'             : str(vminfo.HDD),
                   'extrahdd'        : str(vminfo.extra_HDD),
                   'ram'             : str(vminfo.RAM),
                   'vcpus'           : str(vminfo.vCPU),
                   'status'          : get_vm_status(vminfo.status),
                   'ostype'          : 'Linux',
                   'purpose'         : str(vminfo.purpose),
                   'totalcost'       : str(vminfo.total_cost),
                   'currentrunlevel' : str(vminfo.current_run_level)}

    if is_moderator():
        vm_info_map.update({'host' : str(vminfo.host_id),
                             'vnc'  : str(vminfo.vnc_port)})

    return vm_info_map  
    
    
def get_vm_user_list(vm_id) :		
    vm_users = db((vm_id == db.user_vm_map.vm_id) & (db.user_vm_map.user_id == db.user.id)).select(db.user.ALL)
    user_id_lst = []
    for vm_user in vm_users:
        user_id_lst.append(vm_user)
    return user_id_lst

def is_snapshot_request_in_queue(vm_id):
    if db((db.task_queue.vm_id == vm_id) 
          & (db.task_queue.task_type == TASK_TYPE_SNAPSHOT_VM) 
          & db.task_queue.status.belongs(TASK_QUEUE_STATUS_PENDING, TASK_QUEUE_STATUS_PROCESSING)).select():
        return True
    else:
        return False

def check_snapshot_limit(vm_id):
    snapshots = db(db.snapshot.vm_id == vm_id).count()
    logger.debug("No of snapshots are " + str(snapshots))
    if snapshots < SNAPSHOTTING_LIMIT:
        return True
    else:
        return False

def get_clone_vm_form(vm_id):

    vm_data = db.vm_data[vm_id]
    
    clone_name = vm_data.vm_name + '_clone'
    cnt = 1;
    while(db.vm_data(vm_name=(clone_name+str(cnt)))):
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
    db.request_queue.clone_count.requires = IS_INT_IN_RANGE(1,101)
    
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
    db.request_queue.enable_ssh.default = vm_data.enable_ssh
    db.request_queue.enable_http.default = vm_data.enable_http
    db.request_queue.public_ip.default = (vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED)
    db.request_queue.security_domain.default = vm_data.security_domain
    db.request_queue.request_type.default = TASK_TYPE_EDITCONFIG_VM
    db.request_queue.status.default = get_request_status()
    db.request_queue.requester_id.default = auth.user.id
    db.request_queue.owner_id.default = vm_data.owner_id
    
    form_fields = ['vm_name','RAM','vCPU','enable_ssh', 'enable_http', 'public_ip', 'security_domain', 'purpose']
    
    return SQLFORM(db.request_queue, fields = form_fields)

def get_mail_admin_form():
    form = FORM(TABLE(TR('Type:'),
                TR(TABLE(TR(TD(INPUT(_name='email_type', _type='radio', _value='report_bug', value='report_bug')),TD('Report Bug'),
                TD(INPUT(_name='email_type', _type='radio', _value='request')),TD('Log Request'),
                TD(INPUT(_name='email_type', _type='radio', _value='complaint')),TD('Lodge Complaint')))),TR('Subject:'),
                TR(TEXTAREA(_name='email_subject',_style='height:50px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),TR('Message:'),
                TR(TEXTAREA(_name='email_message',_style='height:100px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),
                
                TR(INPUT(_type = 'submit', _value = 'Send Email')),_style='width:100%; border:0px'))
    return form

