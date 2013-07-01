# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db,auth,request,response,session
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
    
    if form.accepts(request.vars, session):
        logger.debug('New Template Created')
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)

@auth.requires_login()
def host_details():
    check_moderator()
    try:
        hosts = get_all_hosts()
        results = []
        for host in hosts:
            results.append({'ip':host.host_ip, 'id':host.id, 'name':host.host_name, 'status':host.status})
    
        return dict(hosts=results)
    except:
        exp_handlr_errorpage()

@auth.requires_login()
def add_host():

    form = get_add_host_form()

    if form.accepts(request.vars, session):
        db(db.host.id == form.vars.id).update(status=HOST_STATUS_DOWN)  # @UndefinedVariable
        logger.debug('New Host Added')
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)

@auth.requires_login()    
def add_datastore():

    form = get_add_datastore_form()

    if form.accepts(request.vars, session):
        logger.debug('New datastore added')
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)

@auth.requires_login()
def delete_user_vm():	
    check_moderator()
    try:
        vm_id=request.args[0]
        user_id=request.args[1]
        delete_user_vm_access(vm_id,user_id)				
        response.flash = 'User access is eradicated.'
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
        redirect_listvm()
    except:
        exp_handlr_errorpage()    

@auth.requires_login()
#Delete a virtual machine
def delete_machine():   
    check_moderator()
    try:
        vm_id=request.args[0]
        add_vm_task_to_queue(vm_id,TASK_TYPE_DELETE_VM)
    except:
        exp_handlr_errorpage()
    redirect_listvm()
     
@auth.requires_login()	
def edit_vmconfig():
    check_moderator()
    request.flash="Has to be implemented"

@auth.requires_login()	
def mailToGUI():
    check_moderator()
    request.flash="Has to be implemented"

