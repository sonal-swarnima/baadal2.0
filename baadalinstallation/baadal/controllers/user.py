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
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        logger.debug('VM requested successfully')
        
        redirect(URL(c='default', f='index'))
    return dict(form=form)

def verify_faculty():

    username = request.vars.keywords
    faculty_info = get_faculty_info(username)
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
def list_my_vm():
    try:       
        vm_list = get_my_vm_list()
        return dict(vmlist=vm_list)
    except:
        exp_handlr_errorpage()

@auth.requires_login()
def settings():
    try:       
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
    except:
        exp_handlr_errorpage()

@auth.requires_login()
def start_machine():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_START_VM)
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()
def shutdown_machine():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_STOP_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()     
def destroy_machine():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_DESTROY_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()             
def resume_machine():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_RESUME_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()     
def delete_machine():
    try:
        vm_id = request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()     
def pause_machine():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_SUSPEND_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()     
#Adjust the run level of the virtual machine
def adjrunlevel():
    try:
        vm_id=request.args[0]
        vminfo = vm_permission_check(vm_id)        
        return dict(vm=vminfo)
    except:
        exp_handlr_errorpage()

@auth.requires_login()             
def clonevm():    
    try:
        vm_id=request.args[0]
        vminfo = vm_permission_check(vm_id)        
        #TODO: to be implemented
        return dict(vm=vminfo)
    except:
        exp_handlr_errorpage()
    redirect_list_vm()

@auth.requires_login()
def changelevel():
    try:
        vm_id=request.args[0]
        vm_permission_check(vm_id)        
        add_vm_task_to_queue(vm_id,TASK_TYPE_CHANGELEVEL_VM)        
    except:
        exp_handlr_errorpage()
    redirect_list_vm()
    
def vm_permission_check(vm_id):
    vminfo = get_vm_info(vm_id)
    if vminfo == None:
        session.vm_status = "No such vm exists any more"        
        redirect_list_vm()
    else:
        if (not is_moderator()): #moderator has access rights on all vms 
            if auth.user.id not in get_vm_user_list(vm_id): 
                session.vm_status = "Not authorized"
                session.flash="Not authorized"
                redirect_list_vm()
    return vminfo    


def redirect_list_vm():
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,c='user',f='list_my_vm'))
        
