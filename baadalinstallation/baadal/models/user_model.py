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
from helper import is_moderator, is_orgadmin, is_faculty, get_vm_template_config, get_fullname, get_config_file, get_email, send_mail, push_email
from auth_user import fetch_ldap_user, create_or_update_user

config = get_config_file()

def get_my_pending_vm():
    vms = db(db.vm_data.status.belongs(VM_STATUS_REQUESTED, VM_STATUS_VERIFIED) 
             & (db.vm_data.requester_id==auth.user.id)).select(db.vm_data.ALL)

    return get_pending_vm_list(vms)


def get_my_hosted_vm():
    vms = db((db.vm_data.status > VM_STATUS_APPROVED) 
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
    faculty_user = request.post_vars.user_name
    faculty_user_name = request.post_vars.faculty_user
    
    if(faculty_user != ''):
        faculty_info = get_user_info(faculty_user, [FACULTY])
        if faculty_info[1] == faculty_user_name:
            form.vars.owner_id = faculty_info[0]
            form.vars.status = VM_STATUS_REQUESTED
            return
    
    faculty_info = get_user_info(faculty_user_name, [FACULTY])
    if faculty_info != None:
        form.vars.owner_id = faculty_info[0]
        form.vars.status = VM_STATUS_REQUESTED
    else:
        form.errors.faculty_user='Faculty Approver Username is not valid'
        
def request_vm_validation(form):
    set_configuration_elem(form)
    if not(is_moderator() | is_orgadmin() | is_faculty()):
        validate_approver(form)
        user_name = get_user_fullname()
        faculty_info = get_faculty_info(form.vars.owner_id)
        send_email_to_faculty(form.vars.owner_id, form.vars.vm_name, user_name, form.vars.start_time, faculty_info)
    else:
        form.vars.owner_id = auth.user.id
        form.vars.status = VM_STATUS_VERIFIED
    email_address = get_email(auth.user.id)
    send_email_to_user(form.vars.vm_name, user_name, email_address)
    form.vars.requester_id = auth.user.id
    if form.vars.req_public_ip == 'on':
        form.vars.public_ip = None
    print form.vars.public_ip


def add_faculty_approver(form):

    _input=INPUT(_name='faculty_user',_id='faculty_user') # create INPUT
    _link = TD(A('Verify', _href='#',_onclick='verify_faculty()'))
    faculty_elem = TR(LABEL('Faculty Approver:'),_input,_link,_id='faculty_row')
    form[0].insert(-1,faculty_elem)#insert tr element in the form


def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','extra_HDD','purpose']
    form_labels = {'vm_name':'Name of VM','extra_HDD':'Optional Additional Harddisk(GB)','template_id':'Template Image','purpose':'Purpose of this VM'}

    form =SQLFORM(db.vm_data, fields = form_fields, labels = form_labels, hidden=dict(user_name=''))
    get_configuration_elem(form) # Create dropdowns for configuration
    
    form[0].insert(-1, TR(LABEL('Public IP:'), 
                          INPUT(_type = 'checkbox', _name = 'req_public_ip'), 
                          _id='public_ip_row'))      

    if not(is_moderator() | is_orgadmin() | is_faculty()):
        add_faculty_approver(form)
    
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

def check_snapshot_limit(vm_id):
    snapshots = len(db(db.snapshot.vm_id == vm_id).select())
    logger.debug("No of snapshots are " + str(snapshots))
    if snapshots < SNAPSHOTTING_LIMIT:
        return True
    else:
        return False

def get_clone_vm_form(vm_id):

    vm_info = db.vm_data[vm_id]
    clone_name = vm_info['vm_name'] + '_clone'
    form =SQLFORM(db.vm_data, fields = ['purpose'], labels = {'purpose':'Purpose'}, hidden=dict(parent_vm_id=vm_id))
    form[0].insert(0, TR(LABEL('VM Name:'), INPUT(_name = 'clone_name',  _value = clone_name, _readonly=True)))
    form[0].insert(1, TR(LABEL('No. of Clones:'), INPUT(_name = 'no_of_clones', requires = [IS_NOT_EMPTY(), IS_INT_IN_RANGE(1,101)])))

    return form

def clone_vm_validation(form):

    parent_vm_id = request.post_vars.parent_vm_id
    vm_info = db.vm_data[parent_vm_id]
    clone_name = form.vars.clone_name
    cnt = 1;
    while(db.vm_data(vm_name=(clone_name+str(cnt)))):
        cnt = cnt+1
    
    form.vars.vm_name = clone_name + str(cnt)
    form.vars.RAM = vm_info.RAM
    form.vars.HDD = vm_info.HDD
    form.vars.extra_HDD = vm_info.extra_HDD
    form.vars.vCPU = vm_info.vCPU
    form.vars.template_id = vm_info.template_id
    form.vars.requester_id = auth.user.id
    form.vars.owner_id = vm_info.owner_id
    form.vars.parent_id = parent_vm_id
    form.vars.parameters = dict(clone_count = form.vars.no_of_clones)
    if (is_moderator() | is_orgadmin() | is_faculty()):
        form.vars.status = VM_STATUS_VERIFIED
    else:
        form.vars.status = VM_STATUS_REQUESTED

def send_email_to_user(vm_name, user_name, email_address):
    context = dict(userName=user_name, vmName = vm_name)
    noreply_email = config.get("MAIL_CONF","mail_noreply")
    send_mail(email_address, VM_REQUEST_SUBJECT_FOR_USER, VM_REQUEST_TEMPLATE_FOR_USER, context, noreply_email)
    
def send_email_to_admin(email_subject, email_message, email_type):
    if email_type == 'request':
        email_address = config.get("MAIL_CONF","mail_admin_bug_report")
    if email_type == 'report_bug':
        email_address = config.get("MAIL_CONF","mail_admin_request")
    if email_type == 'complaint':
        email_address = config.get("MAIL_CONF","mail_admin_complaint")
    user_email_address = get_email(auth.user.id)
    logger.info("MAIL ADMIN: type:"+email_type+", subject:"+email_subject+", message:"+email_message+", from:"+user_email_address)
    push_email(email_address, email_subject, email_message,user_email_address)

def get_user_fullname():
    return get_fullname(auth.user.id)
    

def get_mail_admin_form():
    form = FORM(TABLE(TR('Type:'),
                TR(TABLE(TR(TD(INPUT(_name='email_type', _type='radio', _value='report_bug', value='report_bug')),TD('Report Bug'),
                TD(INPUT(_name='email_type', _type='radio', _value='request')),TD('Log Request'),
                TD(INPUT(_name='email_type', _type='radio', _value='complaint')),TD('Lodge Complaint')))),TR('Subject:'),
                TR(TEXTAREA(_name='email_subject',_style='height:50px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),TR('Message:'),
                TR(TEXTAREA(_name='email_message',_style='height:100px; width:100%', _cols='30', _rows='20',requires=IS_NOT_EMPTY())),
                
                TR(INPUT(_type = 'submit', _value = 'Send Email')),_style='width:100%; border:0px'))
    return form



