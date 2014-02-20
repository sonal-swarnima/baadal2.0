# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,response,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from host_helper import delete_orhan_vm
from helper import get_constant, update_constant
from vm_helper import shutdown_baadal, bootup_baadal

@check_moderator
@handle_exception
def list_all_vm():
    vm_list = get_all_vm_list()
    return dict(vmlist = vm_list)

@check_moderator
@handle_exception
def list_all_pending_requests():
    pending_requests = get_all_pending_requests()
    requests = get_segregated_requests(pending_requests)

    return dict(install_requests = requests[0], 
                clone_requests   = requests[1], 
                disk_requests    = requests[2], 
                edit_requests    = requests[3])

@check_moderator
@handle_exception
def approve_users():
    pending_users = get_all_unregistered_users()
    users = get_users_with_organisation(pending_users)
    types = get_user_role_types()
    return dict(users = users,
                type_options = types)
                
@check_moderator
@handle_exception
def modify_user_role():
    active_users = get_users_with_roles()
    all_roles = get_user_role_types()
    return dict(users = active_users,
                type_options = all_roles)
    
def modify_roles():
    user_id = request.args[0]
    user_roles = request.args[1]
    if user_roles == "empty":
        user_roles = None
    else:
        user_roles = user_roles.split('_')
    user_id = long(user_id)
    delete_all_user_roles(user_id)
    session.flash= specify_user_roles(user_id, user_roles)
    redirect(URL(c='admin',f='modify_user_role'))

@check_moderator
@handle_exception
def hosts_vms():
    hostvmlist = get_vm_groupby_hosts()        
    return dict(hostvmlist = hostvmlist)

@check_moderator
@handle_exception
def manage_template():
    form = get_manage_template_form(request.args(0))
    return dict(form = form)

@check_moderator
@handle_exception
def manage_security_domain():

    req_type = request.args(0)
    if req_type == 'delete' or request.vars['delete_this_record'] == 'on':
        error_message = check_delete_security_domain(request.args(2))
        if error_message != None:
            session.flash = error_message
            redirect(URL(c='admin', f='manage_security_domain'))

    form = get_security_domain_form(req_type)
    return dict(form = form)

@check_moderator
@handle_exception
def host_details():
    hosts = get_all_hosts()

    form1=get_search_host_form()
    form2=get_configure_host_form()

    if form1.process(formname='form_ip').accepted:
        session.flash='Check the details'
        redirect(URL(c='admin', f='add_host',args=form1.vars.host_ip))
        
    if form2.process(formname='form_mac').accepted:
        message = configure_host_by_mac(form2.vars.host_mac_addr)
        session.flash=message
        redirect(URL(c='admin', f='host_details'))

    return dict(form1=form1, form2=form2, hosts=hosts)   

@check_moderator
@handle_exception
def add_host():
    if_redirect = False
    host_ip = request.args[0]
    form = get_host_form(host_ip)
    if form.accepts(request.vars,session):
        session.flash='New Host added'
        if_redirect = True
    elif form.errors:
        session.flash='Error in form'
    if if_redirect :
        redirect(URL(c='admin', f='host_details'))
    else :
        return dict(form=form)

@check_moderator
@handle_exception
def manage_datastore():
    form = get_manage_datastore_form(request.args(0))
    return dict(form=form)

@check_moderator
@handle_exception
def user_details():
    vm_id = request.args[0]
    form = get_search_user_form()
    if form.accepts(request.vars, session, onvalidation = validate_user):
        redirect(URL(c ='admin', f = 'add_user_to_vm', args = [form.vars.user_id, vm_id]))
    elif form.errors:
        session.form = 'Invalid user id'

    return dict(form=form)

@check_moderator
@handle_exception
def add_user_to_vm():
    username = request.args[0]
    vm_id = request.args[1]
    form = get_user_form(username, vm_id)

    if form.accepts(request.vars,session):
        add_user_vm_access(vm_id, form.vars.user_id)
        session.flash = "User is added to vm"
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.form = 'Error in form'
    return dict(form = form)

@check_moderator
@handle_exception
def delete_user_vm():
    vm_id=request.args[0]
    user_id=request.args[1]
    delete_user_vm_access(vm_id,user_id)    			
    session.flash = 'User access is eradicated.'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
@handle_exception
def migrate_vm():

    if_redirect = False
    vm_id = request.args[0]
    
    form = get_migrate_vm_form(vm_id)

    if form.accepts(request.vars,session,keepvalues = True):

        migrate_vm = True

        if form.vars.live_migration == None:
            if is_vm_running(vm_id):
                response.flash = "Your VM is already running. Kindly turn it off and then retry!!!"
                migrate_vm = False

        if migrate_vm:
            params={}
            params['destination_host'] = form.vars.destination_host
            params['live_migration'] = form.vars.live_migration
            add_vm_task_to_queue(vm_id, TASK_TYPE_MIGRATE_VM, params)
            session.flash = 'Your task has been queued. Please check your task list for status.'
            if_redirect = True

    elif form.errors:
        response.flash = 'Error in form'

    if if_redirect :
        redirect(URL(c = 'admin', f = 'hosts_vms'))
    return dict(form=form)
        
    
@check_moderator
@handle_exception
def lockvm():
    vm_id=request.args[0]
    vminfo=get_vm_info(vm_id)
    if(not vminfo.locked):
        add_vm_task_to_queue(vm_id, TASK_TYPE_DESTROY_VM)
        session.flash = "VM will be force Shutoff and locked. Check the task queue."
        update_vm_lock(vm_id,True)
    else:
        update_vm_lock(vm_id,False)
        session.flash = "Lock Released. Start VM yourself."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
@handle_exception
def task_list():

    form = get_task_num_form()
    task_num = ITEMS_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_task_by_status([TASK_QUEUE_STATUS_PENDING], task_num)
    success = get_task_by_status([TASK_QUEUE_STATUS_SUCCESS], task_num)
    failed = get_task_by_status([TASK_QUEUE_STATUS_FAILED, TASK_QUEUE_STATUS_PARTIAL_SUCCESS], task_num)
    
    return dict(pending=pending, success=success, failed=failed, form=form)

@check_moderator
@handle_exception
def ignore_task():
    task_id=request.args[0]
    update_task_ignore(task_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@handle_exception
def retry_task():
    event_id=request.args[0]
    update_task_retry(event_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@handle_exception
def delete_machine():   
    vm_id=request.args[0]
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)    

    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_moderator
def sanity_check():
    output = check_vm_sanity()
    return dict(vms=output)
    
@check_moderator
def sync_vm():
    task = request.args[0]
    vm_name = request.args[1]
    host_id = request.args[2]
    if task == 'Delete_Orphan':
        delete_orhan_vm(vm_name, host_id)
    elif task == 'Add_Orphan':
        add_orhan_vm(vm_name, host_id)
    elif task == 'Delete_VM_Info':
        delete_vm_info(vm_name)
    redirect(URL(r=request,c='admin',f='sanity_check'))

@check_moderator
@handle_exception
def approve_request():
    request_id=request.args[0] 
    enqueue_vm_request(request_id);
    session.flash = 'Installation request added to queue'
    redirect(URL(c='admin', f='list_all_pending_requests'))

@check_moderator
@handle_exception
def reject_request():
    request_id=request.args[0]
    reject_vm_request(request_id);
    session.flash = 'Request Rejected'
    redirect(URL(c='admin', f='list_all_pending_requests'))

@check_moderator
@handle_exception
def maintenance_host():
    host_id=request.args[0]
    #migration requests to be added to queue
    updte_host_status(host_id, HOST_STATUS_MAINTENANCE)
    redirect(URL(c='admin', f='host_details'))
    
@check_moderator
@handle_exception
def boot_up_host():
    host_id=request.args[0]
    updte_host_status(host_id, HOST_STATUS_UP)
    redirect(URL(c='admin', f='host_details'))
    
@check_moderator
@handle_exception
def shut_down_host():
    host_id=request.args[0]
    #shut down to be implemented
    updte_host_status(host_id, HOST_STATUS_DOWN)
    redirect(URL(c='admin', f='host_details'))
    
@check_moderator
@handle_exception
def delete_host():
    host_id=request.args[0]
    delete_host_from_db(host_id)
    redirect(URL(c='admin', f='host_details'))
    
@check_moderator
@handle_exception
def manage_public_ip_pool():
    form = get_manage_public_ip_pool_form()
    return dict(form=form)

@check_moderator
@handle_exception
def validate_public_ip_range():
    rangeFrom = request.vars['rangeFrom']
    rangeTo = request.vars['rangeTo']
    
    from helper import validate_ip_range
    if validate_ip_range(rangeFrom, rangeTo):
        failed = add_public_ip_range(rangeFrom, rangeTo)
        return str(failed)
    else:
        return '-1'

@check_moderator
@handle_exception
def validate_private_ip_range():
    rangeFrom = request.vars['rangeFrom']
    rangeTo = request.vars['rangeTo']
    vlan = request.vars['vlan']
    
    from helper import validate_ip_range
    if validate_ip_range(rangeFrom, rangeTo):
        failed = add_private_ip_range(rangeFrom, rangeTo, vlan)
        return str(failed)
    else:
        return '-1'

@check_moderator
@handle_exception
def manage_private_ip_pool():
    form = get_manage_private_ip_pool_form()
    return dict(form=form)

@check_moderator
@handle_exception
def vm_utilization():

    form = get_util_period_form()
    util_period = VM_UTIL_24_HOURS
    form.vars.util_period = util_period

    if form.accepts(request.vars, session, keepvalues=True):
        util_period = int(form.vars.util_period)
    
    vm_util_data = get_vm_util_data(util_period)
    
    return dict(vm_util_data=vm_util_data, form=form)

@check_moderator
@handle_exception
def remind_orgadmin():
    vm_id=request.args[0]
    send_remind_orgadmin_email(vm_id)
    session.flash = 'Organisation Admin Reminded'
    redirect(URL(c='orgadmin', f='pending_approvals'))

@check_moderator
@handle_exception
def verify_vm_resource():

    request_id = request.vars['request_id']
    return check_vm_resource(request_id)

@check_moderator
@handle_exception
def add_user_with_role():
    user_id = request.args[0]
    user_roles = request.args[1]
    if user_roles == "empty":
        user_roles = None
    else:
        user_roles = user_roles.split('_')
    user_id = long(user_id)
    send_email_on_successful_registration(user_id)
    session.flash= specify_user_roles(user_id, user_roles)
    redirect(URL(c='admin',f='approve_users'))
 
@check_moderator
@handle_exception   
def remove_user():
    user_id=request.args[0]
    send_email_on_registration_denied(user_id)
    session.flash = disable_user(user_id)
    redirect(URL(c='admin',f='approve_users'))

@check_moderator
@handle_exception   
def baadal_status():
    vm_list = get_baadal_status_info()
    baadal_status = get_constant('baadal_status')
    return dict(vm_list=vm_list, baadal_status=baadal_status)

@check_moderator
@handle_exception   
def start_shutdown():
    update_constant('baadal_status', BAADAL_STATUS_DOWN_IN_PROGRESS)
    shutdown_baadal()
    update_constant('baadal_status', BAADAL_STATUS_DOWN)
    
@check_moderator
@handle_exception   
def start_bootup():
    update_constant('baadal_status', BAADAL_STATUS_UP_IN_PROGRESS)
    bootup_baadal()
    update_constant('baadal_status', BAADAL_STATUS_UP)
