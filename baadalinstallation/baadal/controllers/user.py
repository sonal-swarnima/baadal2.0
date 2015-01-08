# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import auth,request,session
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from log_handler import logger
from vm_utilization import get_performance_graph

@auth.requires_login()
@handle_exception
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        
        send_email_to_requester(form.vars.vm_name)
        if is_vm_user():
            send_remind_faculty_email(form.vars.id)

        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def verify_faculty():

    username = request.vars['keywords']
    faculty_info = get_user_info(username, [FACULTY])
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
@handle_exception
def add_collaborator():

    username = request.vars['keywords']
    user_info = get_user_info(username)
    if user_info != None:
        return user_info[1]

@auth.requires_login()
@handle_exception
def list_my_vm():
    hosted_vm = get_my_hosted_vm()
    saved_templates = get_my_saved_templates()   
    return dict(hosted_vm = hosted_vm, saved_templates = saved_templates)

@check_vm_owner
@handle_exception
def settings():

    vm_id=request.args[0]
    vm_users = None
    vm_info = get_vm_config(vm_id)
    if not vm_info:
        redirect(URL(f='list_my_vm'))
    if not is_vm_user():
        vm_users = get_vm_user_list(vm_id)
    
    vm_operations = get_vm_operations(vm_id)
    vm_snapshots = get_vm_snapshots(vm_id)
    
    return dict(vminfo = vm_info , vmoperations = vm_operations, vmsnapshots = vm_snapshots, vmusers = vm_users)     


def handle_vm_operation(vm_id, task_type):

    if is_request_in_queue(vm_id, VM_TASK_DELETE):
        session.flash = "Delete request is in queue. No operation can be performed"
    elif is_request_in_queue(vm_id, task_type):
        session.flash = "%s request already in queue." %task_type
    else:
        add_vm_task_to_queue(vm_id,task_type)
        session.flash = '%s request added to queue.' %task_type
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception
def start_vm():
    handle_vm_operation(request.args[0], VM_TASK_START)

@check_vm_owner
@handle_exception
def stop_vm():
    handle_vm_operation(request.args[0], VM_TASK_STOP)

@check_vm_owner
@handle_exception
def resume_vm():
    handle_vm_operation(request.args[0], VM_TASK_RESUME)

@check_vm_owner
@handle_exception
def suspend_vm():
    handle_vm_operation(request.args[0], VM_TASK_SUSPEND)

@check_vm_owner
@handle_exception
def destroy_vm():
    handle_vm_operation(request.args[0], VM_TASK_DESTROY)

@check_vm_owner
@handle_exception
def delete_vm():
    handle_vm_operation(request.args[0], VM_TASK_DELETE)

@check_vm_owner
@handle_exception       
def snapshot():
    vm_id = int(request.args[0])
    if is_request_in_queue(vm_id, VM_TASK_SNAPSHOT):
        session.flash = "Snapshot request already in queue."
    elif check_snapshot_limit(vm_id):
        add_vm_task_to_queue(vm_id, VM_TASK_SNAPSHOT, {'snapshot_type': SNAPSHOT_USER})
        session.flash = "Your request to snapshot VM has been queued"
    else:
        session.flash = "Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception
def delete_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    if is_request_in_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Delete Snapshot request already in queue."
    else:
        add_vm_task_to_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, {'snapshot_id':snapshot_id})
        session.flash = "Your delete snapshot request has been queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception
def revert_to_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    if is_request_in_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Delete Snapshot request in queue. Revert operation aborted."
    elif is_request_in_queue(vm_id, VM_TASK_REVERT_TO_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Revert to Snapshot request already in queue."
    else:
        add_vm_task_to_queue(vm_id, VM_TASK_REVERT_TO_SNAPSHOT, {'snapshot_id':snapshot_id})
        session.flash = "Your revert to snapshot request has been queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception       
def list_my_task():
    form = get_task_num_form()
    task_num = ITEMS_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_my_task_list([TASK_QUEUE_STATUS_PENDING], task_num)
    success = get_my_task_list([TASK_QUEUE_STATUS_SUCCESS], task_num)
    failed = get_my_task_list([TASK_QUEUE_STATUS_FAILED, TASK_QUEUE_STATUS_PARTIAL_SUCCESS], task_num)

    return dict(pending=pending, success=success, failed=failed, form=form)  

@check_vm_owner
@handle_exception       
def show_vm_performance():
    vm_id = int(request.args[0])
    vm_info = get_vm_info(vm_id)    
    return dict(vm_id = vm_id, vm_identity = vm_info.vm_data.vm_identity)

@auth.requires_login()
@handle_exception       
def get_updated_graph():

        logger.debug(request.vars['graphType'])
        logger.debug(request.vars['vmIdentity'])
        logger.debug(request.vars['graphPeriod'])
        graphRet = get_performance_graph(request.vars['graphType'], request.vars['vmIdentity'], request.vars['graphPeriod'])
        if not isinstance(graphRet, IMG):
            if is_moderator():
                return H3(graphRet)
            else:
                return H3('VMs RRD File Unavailable!!!')
        else:
            return graphRet

@check_vm_owner
@handle_exception       
def clone_vm():

    vm_id = request.args[0]
    form = get_clone_vm_form(vm_id)
    if form.accepts(request.vars,session):
        session.flash = "Your request has been sent for approval."
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.flash = "Error in form."

    return dict(form=form)

@check_vm_owner
@handle_exception       
def attach_extra_disk():

    vm_id = request.args[0]
    form = get_attach_extra_disk_form(vm_id)
    if form.accepts(request.vars, session):
        session.flash = "Your request has been sent for approval."
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.flash = "Error in form."

    return dict(form=form)

@check_vm_owner
@handle_exception       
def edit_vm_config():

    vm_id = request.args[0]
    form = get_edit_vm_config_form(vm_id)

    if form.accepts(request.vars, session, onvalidation=edit_vm_config_validation, hideerror=True):
        session.flash = "Your request has been queued!!!"
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

    elif form.errors:
        session.flash = "Error in form!!!"

    return dict(form=form)

@check_vm_owner
@handle_exception       
def save_as_template():
    vm_id = int(request.args[0])
    if is_request_in_queue(vm_id, VM_TASK_SAVE_AS_TEMPLATE):    
        session.flash = "Request to save VM as template already in queue."
    elif check_vm_template_limit(vm_id):
        add_vm_task_to_queue(vm_id, VM_TASK_SAVE_AS_TEMPLATE)
        session.flash = "Your request to save VM as template is queued"
    else:
        session.flash = "Template for this VM already present. Delete a previous template to save new template."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@handle_exception       
def delete_template():
    
    vm_id = int(request.args[0])
    params = {'template_id' : request.args[1]}
    add_vm_task_to_queue(vm_id, VM_TASK_DELETE_TEMPLATE, params)
    session.flash = "Your request to delete template is queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception
def mail_admin():
    form = get_mail_admin_form()
    if form.accepts(request.vars, session):
        email_type = form.vars.email_type
        email_subject = form.vars.email_subject
        email_message = form.vars.email_message
        send_email_to_admin(email_subject, email_message, email_type)
        redirect(URL(c='default', f='index'))
    return dict(form = form)

@auth.requires_login()
@handle_exception
def list_my_requests():
    my_requests = get_my_requests()
    requests = get_segregated_requests(my_requests)

    return dict(install_requests = requests[0], 
                clone_requests = requests[1], 
                disk_requests = requests[2], 
                edit_requests= requests[3])
        
@check_vm_owner
@handle_exception       
def vm_history():

    vm_id = request.args[0]
    vm_history = get_vm_history(vm_id)        
    return dict(vm_id = vm_id, vm_history = vm_history)

@check_vm_owner
@handle_exception       
def grant_vnc():

    vm_id = request.args[0]
    session.flash = grant_vnc_access(vm_id)
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception       
def configure_snapshot():

    vm_id = int(request.args[0])
    flag = request.vars['snapshot_flag']
    update_snapshot_flag(vm_id, flag) 
