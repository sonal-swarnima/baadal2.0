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
from helper import is_moderator, is_faculty, is_orgadmin

@auth.requires_login()
@handle_exception
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        add_vm_users(form.vars.id, form.vars.requester_id, 
                     form.vars.owner_id, request.post_vars.vm_users)
        
        send_email_to_user(form.vars.vm_name)
        if not(is_moderator() | is_orgadmin() | is_faculty()):
            send_email_to_faculty(form.vars.owner_id, form.vars.vm_name, form.vars.start_time)

        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def verify_faculty():

    username = request.vars.keywords
    faculty_info = get_user_info(username, [FACULTY])
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
@handle_exception
def add_collaborator():

    username = request.vars.keywords
    user_info = get_user_info(username, [USER,FACULTY,ORGADMIN, ADMIN])
    if user_info != None:
        return user_info[1]

@auth.requires_login()
@handle_exception
def list_my_vm():
    pending_vm = get_my_pending_vm()
    hosted_vm = get_my_hosted_vm()        
    
    return dict(pending_vm = pending_vm, hosted_vm = hosted_vm)


@auth.requires_login()
@handle_exception
def settings():

    vm_id=request.args[0]
    vm_users = None
    vm_info = get_vm_config(vm_id)
    
    if is_moderator() | is_faculty() | is_orgadmin():
        vm_users = get_vm_user_list(vm_id)
    
    vm_operations = get_vm_operations(vm_id)

    vm_snapshots = get_vm_snapshots(vm_id)
    
    return dict(vminfo = vm_info , vmoperations = vm_operations, vmsnapshots = vm_snapshots, vmusers = vm_users)     


@auth.requires_login()
@handle_exception
def start_machine():
    vm_id=request.args[0]       
    add_vm_task_to_queue(vm_id,TASK_TYPE_START_VM)
    session.flash = 'Request to start machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception
def shutdown_machine():
    vm_id=request.args[0]      
    add_vm_task_to_queue(vm_id,TASK_TYPE_STOP_VM)        
    session.flash = 'Request to shutdown machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception
def destroy_machine():
    vm_id=request.args[0]       
    add_vm_task_to_queue(vm_id,TASK_TYPE_DESTROY_VM)        
    session.flash = 'Request to destroy machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception       
def resume_machine():
    vm_id=request.args[0]     
    add_vm_task_to_queue(vm_id,TASK_TYPE_RESUME_VM)        
    session.flash = 'Request to resume machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception       
def delete_machine():
    vm_id = request.args[0]      
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)        
    session.flash = 'Request to delete machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception       
def pause_machine():
    vm_id=request.args[0]  
    add_vm_task_to_queue(vm_id,TASK_TYPE_SUSPEND_VM)        
    session.flash = 'Request to pause machine added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception       
def adjrunlevel():
    #Adjust the run level of the virtual machine
    vm_id=request.args[0]
    vminfo = get_vm_config(vm_id)        
    return dict(vm=vminfo)

@auth.requires_login()
@handle_exception       
def changelevel():
    vm_id=request.args[0]     
    add_vm_task_to_queue(vm_id,TASK_TYPE_CHANGELEVEL_VM)        
    session.flash = 'Request to change level added to queue'
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception       
def snapshot():
    vm_id = int(request.args[0])
   
    if check_snapshot_limit(vm_id):
        add_vm_task_to_queue(vm_id,TASK_TYPE_SNAPSHOT_VM)
        session.flash = "Your VM snapshoting request has been queued"

    else:
        session.flash = "Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception
def delete_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    add_vm_task_to_queue(vm_id, TASK_TYPE_DELETE_SNAPSHOT, {'snapshot_id':snapshot_id})
    session.flash = "Your delete snapshot request has been queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception
def revert_to_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    add_vm_task_to_queue(vm_id, TASK_TYPE_REVERT_TO_SNAPSHOT, {'snapshot_id':snapshot_id})
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
    
    pending = get_my_task_list(TASK_QUEUE_STATUS_PENDING, task_num)
    success = get_my_task_list(TASK_QUEUE_STATUS_SUCCESS, task_num)
    failed = get_my_task_list(TASK_QUEUE_STATUS_FAILED, task_num)

    return dict(pending=pending, success=success, failed=failed, form=form)  

@auth.requires_login()
@handle_exception       
def show_vm_performance():
    vm_id = int(request.args[0])
    vm_info = get_vm_info(vm_id)    
    return dict(vm_name = vm_info['vm_name'])

@auth.requires_login()
@handle_exception       
def get_updated_graph():

        logger.debug(request.vars['graphType'])
        logger.debug(request.vars['vmName'])
        logger.debug(request.vars['graphPeriod'])
        return get_performance_graph(request.vars['graphType'], request.vars['vmName'], request.vars['graphPeriod'])

@auth.requires_login()
@handle_exception       
def clone_vm():

    vm_id = request.args[0]
    form = get_clone_vm_form(vm_id)
    if form.accepts(request.vars,session, onvalidation=clone_vm_validation):
        session.flash = "Your request has been sent for approval."
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.flash = "Error in form."

    return dict(form=form)

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

