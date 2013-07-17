# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import auth,request,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

@auth.requires_login()
def list_all_vm():
    check_moderator()
    try:
        vm_list = get_all_vm_list()
        return dict(vmlist=vm_list)
    except:
        exp_handlr_errorpage()

@auth.requires_login()
def hosts_vms():
    check_moderator()
    try:
        hostvmlist=get_vm_groupby_hosts()        
        return dict(hostvmlist=hostvmlist)
    except:
        exp_handlr_errorpage()

@auth.requires_login()
def add_template():

    form = get_add_template_form()
    templates = get_templates()
    if form.accepts(request.vars, session):
        session.flash = 'New Template Created'
        redirect(URL(c='admin', f='add_template'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form, templates=templates)

@auth.requires_login()
def host_details():
    check_moderator()
    try:
        hosts = get_all_hosts()
        results = []
        for host in hosts:
            results.append({'ip':host.host_ip, 'id':host.id, 'name':host.host_name, 'status':host.status})    
    except:
        exp_handlr_errorpage()

    form=get_search_host_form()
    if form.accepts(request.vars,session):
        session.flash='Check the details'
        redirect(URL(c='admin', f='add_host',args=form.vars.host_ip))
    elif form.errors:
        session.flash='Error in form'
        
    return dict(form=form,hosts=results)
        

@auth.requires_login()
def add_host():
    if_redirect = False
    try:
        check_moderator()
        host_ip = request.args[0]
        form = get_host_form(host_ip)
        if form.accepts(request.vars,session):
            session.flash='New Host added'
            if_redirect = True
        elif form.errors:
            session.flash='Error in form'
    except:
        exp_handlr_errorpage()
    if if_redirect :
        redirect(URL(c='admin', f='host_details'))
    else :
        return dict(form=form)


@auth.requires_login()    
def add_datastore():

    form = get_add_datastore_form()
    datastores = get_datastores()

    if form.accepts(request.vars, session):
        logger.debug('New datastore added')
        redirect(URL(c='admin', f='add_datastore'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form, datastores=datastores)

@auth.requires_login()
def delete_user_vm():	
    check_moderator()
    try:
        vm_id=request.args[0]
        user_id=request.args[1]
        delete_user_vm_access(vm_id,user_id)				
        session.flash = 'User access is eradicated.'
    except:
        exp_handlr_errorpage()	
    redirect(URL(r=request,c='user',f='settings', args=[vm_id]))

@auth.requires_login()	
#MIGRATE VM HOST1 TO HOST2
def migrate_vm():
    check_moderator()
    request.flash="Has to be implemented"

@auth.requires_login()
def lockvm():
    check_moderator()
    try:
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
    except:
        exp_handlr_errorpage()    

@auth.requires_login()
def task_list():
    check_moderator()
    try:
        #TODO:Pagination to be implemented
        pending = get_task_list(TASK_QUEUE_STATUS_PENDING)
        success = get_task_list(TASK_QUEUE_STATUS_SUCCESS)
        failed = get_task_list(TASK_QUEUE_STATUS_FAILED)
        
        return dict(pending=pending, success=success, failed=failed)
    except:
        exp_handlr_errorpage()    

@auth.requires_login()
def ignore_task():
    try:
        task_id=request.args[0]
        update_task_ignore(task_id)
    except:
        exp_handlr_errorpage()    
    
    redirect(URL(r=request,c='admin',f='task_list'))

@auth.requires_login()
def retry_task():
    try:
        task_id=request.args[0]
        update_task_retry(task_id)
    except:
        exp_handlr_errorpage()    
    
    redirect(URL(r=request,c='admin',f='task_list'))

@auth.requires_login()
def delete_machine():   
    check_moderator()
    try:
        vm_id=request.args[0]
        add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)
    except:
        exp_handlr_errorpage()
    redirect(URL(r=request,c='admin',f='list_all_vm'))

@auth.requires_login()	
def edit_vmconfig():
    check_moderator()
    session.flash="Has to be implemented"

@auth.requires_login()	
def mailToGUI():
    check_moderator()
    session.flash="Has to be implemented"

@auth.requires_login()    
def add_disk():
    check_moderator()
    session.flash="Has to be implemented"

@auth.requires_login()
def pending_requests():
    pending_requests = get_verified_vm_list()
    return dict(pending_requests=pending_requests)
        
@auth.requires_login()
def approve_request():
    
    vm_id=request.args[0]
    check_moderator()
    
    approve_vm_request(vm_id);
    session.flash = 'Installation request added to queue'
    redirect(URL(c='admin', f='pending_requests'))
    
@auth.requires_login()
def reject_request():

    vm_id=request.args[0]
    check_moderator()

    reject_vm_request(vm_id);
    session.flash = 'Request Rejected'
    redirect(URL(c='admin', f='pending_requests'))


def check_moderator() :
    from helper import is_moderator
    if not is_moderator() :
        session.flash = "You don't have admin privileges"
        redirect(URL(c='default', f='index'))
