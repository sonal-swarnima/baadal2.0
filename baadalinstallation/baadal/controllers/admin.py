# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

@check_moderator
@exception_handler
def list_all_vm():
    vm_list = get_all_vm_list()
    return dict(vmlist = vm_list)

@check_moderator
@exception_handler
def hosts_vms():
    hostvmlist = get_vm_groupby_hosts()        
    return dict(hostvmlist = hostvmlist)

@check_moderator
@exception_handler
def add_template():
    form = get_add_template_form()
    templates = get_templates()
    if form.accepts(request.vars, session):
        session.flash = 'New Template Created'
        templates = get_templates()
    elif form.errors:
        raise Exception('Error in form')
    return dict(form = form, templates = templates)

@check_moderator
def host_details():
    hosts = get_all_hosts()

    form=get_search_host_form()
    if form.accepts(request.vars,session):
        session.flash='Check the details'
        redirect(URL(c='admin', f='add_host',args=form.vars.host_ip))
    elif form.errors:
        session.flash='Error in form'
        
    return dict(form=form,hosts=hosts)   

@check_moderator
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
@exception_handler
def add_datastore():
    form = get_add_datastore_form()
    datastores = get_datastores()

    if form.accepts(request.vars, session):
        logger.debug('New datastore added')
        datastores = get_datastores()
    elif form.errors:
        raise Exception('Error in form')
    return dict(form=form, datastores=datastores)

@check_moderator
def delete_user_vm():
    try:
        vm_id=request.args[0]
        user_id=request.args[1]
        delete_user_vm_access(vm_id,user_id)				
        session.flash = 'User access is eradicated.'
    except:
        handle_exception()	
    redirect(URL(r=request,c = 'user',f = 'settings', args = [vm_id]))

@check_moderator
@exception_handler
def migrate_vm():
    session.flash="Has to be implemented"

@check_moderator
@exception_handler
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
    redirect(URL(r=request,c='admin',f='list_all_vm'))

@check_moderator
@exception_handler
def task_list():
    #TODO:Pagination to be implemented
    pending = get_task_by_status(TASK_QUEUE_STATUS_PENDING)
    success = get_task_by_status(TASK_QUEUE_STATUS_SUCCESS)
    failed = get_task_by_status(TASK_QUEUE_STATUS_FAILED)
    
    return dict(pending=pending, success=success, failed=failed)

@check_moderator
@exception_handler
def ignore_task():
    task_id=request.args[0]
    update_task_ignore(task_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@exception_handler
def retry_task():
    task_id=request.args[0]
    update_task_retry(task_id)
    
    redirect(URL(r=request,c='admin',f='task_list'))

@check_moderator
@exception_handler
def delete_machine():   
    vm_id=request.args[0]
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)

    redirect(URL(r=request,c='admin',f='list_all_vm'))

@check_moderator
@exception_handler
def edit_vmconfig():
    session.flash="Has to be implemented"

@check_moderator
@exception_handler
def mailToGUI():
    session.flash="Has to be implemented"


@check_moderator
@exception_handler
def add_disk():
    session.flash="Has to be implemented"
