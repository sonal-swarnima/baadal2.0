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
from helper import is_moderator

@auth.requires_login()
@handle_exception
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def verify_faculty():

    username = request.vars.keywords
    faculty_info = get_faculty_info(username)
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
@handle_exception
def list_my_vm():
    pending_vm = get_my_pending_vm()
    hosted_vm = get_my_hosted_vm()        
    
    return dict(pending_vm = pending_vm, hosted_vm = hosted_vm)


@auth.requires_login()
@handle_exception
def settings_org():
    vm_id=request.args[0]
    vminfo = vm_permission_check(vm_id)     
    #TODO : Analyze
    # as state attr is not the live state of the machine              
    state=vminfo.status  #current state of VM
    data={'id':vminfo.id,
          'name':vminfo.vm_name,
          'hdd':vminfo.HDD,
          'ram':vminfo.RAM,
          'vcpus':vminfo.vCPU,
          'status':state,
          'hostip':vminfo.host_id.host_ip,
          'port':vminfo.vnc_port,
          'ostype':vminfo.template_id.ostype,
          'expire_date':vminfo.expiry_date,
          'purpose':vminfo.purpose}
    if is_moderator() :
        return dict(data=data,users=get_vm_user_list(vm_id))
    else :
        return dict(data=data)

@auth.requires_login()
@handle_exception
def settings():

    vm_id=request.args[0]
    vm_users = None
    vm_info = get_vm_config(vm_id)
    
    if is_moderator() | is_faculty() | is_orgadmin():
        vm_users = get_vm_user_list(vm_id)
    
    vm_operations = get_vm_operations(vm_id)
    
    return dict(vminfo = vm_info , vmoperations = vm_operations, vmsnapshots = None, vmusers = vm_users)     

"""    vm_usrs = None
    vm_conf = get_vm_config(vm_id)
    vm_ops = get_valid_vm_operations(vm_id)
    vm_snaps = get_vm_snapshots(vm_id)

    if is_moderator() or is_orgadmin():
        vm_users = get_vm_users(vm_id)

    return dict(vm_config = vm_conf, vm_operations = vm_ops, vm_snapshots = vm_snaps, vm_users = vm_usrs)
"""	


@auth.requires_login()
@handle_exception
def start_machine():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_START_VM)
    redirect_list_vm()


@auth.requires_login()
@handle_exception
def shutdown_machine():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_STOP_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception
def destroy_machine():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_DESTROY_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def resume_machine():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_RESUME_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def delete_machine():
    vm_id = request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)        
    redirect_list_vm()


@auth.requires_login()
@handle_exception       
def pause_machine():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_SUSPEND_VM)        
    redirect_list_vm()

@auth.requires_login()
@handle_exception       
def adjrunlevel():
    #Adjust the run level of the virtual machine
    vm_id=request.args[0]
    vminfo = vm_permission_check(vm_id)        
    return dict(vm=vminfo)

@auth.requires_login()
def clonevm():    
    session.flash="Has to be implemented"

@auth.requires_login()
@handle_exception       
def changelevel():
    vm_id=request.args[0]
    vm_permission_check(vm_id)        
    add_vm_task_to_queue(vm_id,TASK_TYPE_CHANGELEVEL_VM)        
    redirect_list_vm()

@auth.requires_login()
@handle_exception       
def list_my_task():
    form = get_task_num_form()
    task_num = TASK_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_my_task_list(TASK_QUEUE_STATUS_PENDING, task_num)
    success = get_my_task_list(TASK_QUEUE_STATUS_SUCCESS, task_num)
    failed = get_my_task_list(TASK_QUEUE_STATUS_FAILED, task_num)

    return dict(pending=pending, success=success, failed=failed, form=form)  


def redirect_list_vm():
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,c='user',f='list_my_vm'))
        
