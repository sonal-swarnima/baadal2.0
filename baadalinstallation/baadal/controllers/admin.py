# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global response; request = gluon.globals.Response
    global session; session = gluon.globals.Session()
    global db; db = gluon.sql.DAL()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator
#from gluon import current
@auth.requires_login()
def list_all_vm():
	check_moderator()
	vm_list = get_all_vm_list()
	return dict(vmlist=vm_list)
@auth.requires_login()
def hosts_vms():  
	check_moderator()
	try:
		hostvmlist=getvm_groupbyhosts()        
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

    hosts = db(db.host.id >= 0).select()
    results = []
    for host in hosts:
        results.append({'ip':host.host_ip, 'id':host.id, 'name':host.host_name, 'status':host.status})

    return dict(hosts=results)
@auth.requires_login()
def add_host():
    form = get_add_host_form()

    if form.accepts(request.vars, session):
        db(db.host.id == form.vars.id).update(status=HOST_STATUS_DOWN)  # @UndefinedVariable
        logger.debug('New Host Added')
        response.flash = 'New Host Added'
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
 		vmname=request.args[0]
		username=request.args[1]
		vminfo =prerequisite_check(vmname) 
		userinfo =getuserinfo_fromusername(username)		
		deleteuser_accesstovm(vminfo.id,userinfo.id)				
		response.flash = 'User access is eradicated.'
	except:
		exp_handlr_errorpage()	
	redirect(URL(r=request,c='user',f='settings', args=[vmname]))
@auth.requires_login()	
#MIGRATE VM HOST1 TO HOST2
def migrate_vm():
	check_moderator()
	request.flash="Has to be implemented"
@auth.requires_login()
def lockvm():
	#modify db.py to include extra attribute locked in vm_data as its not existing 
	#then enable this code
	check_moderator()
	vmname=request.args[0]
	vminfo =prerequisite_check(vmname)        
    if(not vminfo.locked):	    
			insertinto_taskqueue(TASK_TYPE_DESTROY_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)
            session.flash = "VM will be force Shutoff and locked. Check the task queue."
            lockandunlockvm(True)
	else:
			lockandunlockvm(False)
            session.flash = "Lock Released. Start VM yourself."
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
@auth.requires_login()
#DELETE A VIRTUAL MACHINE
def delete_machine():   
	check_moderator()
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_DELETE_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)
	except:
		exp_handlr_errorpage()
	redirect_listvm()
     
