# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global session; session = gluon.globals.Session()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator
@auth.requires_login()
def request_vm():

    form = get_request_vm_form()
    
    if form.accepts(request.vars, session, onvalidation=set_configuration_elem):
        add_user_to_vm(form.vars.id)
        logger.debug('VM requested successfully')
        
        #TODO:Approve functionality to be implemented
        approve_vm_request(form.vars.id)
        redirect(URL(c='default', f='index'))
    return dict(form=form)
@auth.requires_login()
def list_my_vm():
    vm_list = get_my_vm_list()
    return dict(vmlist=vm_list)
@auth.requires_login()
def settings():
	try:       
		vmname=request.args[0]		
		vminfo =existsandlock_check(vmname)  #where is vm.lock attribute?? in vm_data table				 
		
		permitted_uids=getpermitteduserids_forvmid(vminfo.id)#get uids of all authorizied users on that vm
					
		perm_check(auth.user.id,permitted_uids)   #check whether is authorized or not
        
		hostip= gethostinfo_fromhostid(vminfo.host_id).host_ip # IN common_model.py
		ostype= gettemplateinfo_fromtemplateid(vminfo.template_id).os_type   # IN common_model.py

		users=[]
		users=getusersofvm_frompermitted_uids(permitted_uids)   #users having access rights on vm
        #TODO : focus more on this issue
              # as state attr is not the live state of the machine              
		state=vminfo.status  #current state of vm      #vminfotostate(dom.info()[0])
		data={'name':vmname,'hdd':vminfo.HDD,'ram':vminfo.RAM,'vcpus':vminfo.vCPU,'status':state,'hostip':hostip,'port':vminfo.vnc_port,'ostype':ostype,'expire_date':vminfo.expiry_date,'purpose':vminfo.purpose}
		if is_moderator() :
			return dict(data=data,users=users)
		else :
			return dict(data=data)
		
	except:
		exp_handlr_errorpage()
@auth.requires_login()
def start_machine():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_START_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)
	except:
		exp_handlr_errorpage()
	redirect_listvm()
@auth.requires_login()
def shutdown_machine():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_STOP_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)		
	except:
		exp_handlr_errorpage()
	redirect_listvm()
@auth.requires_login()     
def destroy_machine():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_DESTROY_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)
	except:
		exp_handlr_errorpage()
	redirect_listvm()
@auth.requires_login()             
def resume_machine():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_RESUME_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)
	except:
		exp_handlr_errorpage()
	redirect_listvm()
@auth.requires_login()     
def pause_machine():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_SUSPEND_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)		
	except:
		exp_handlr_errorpage()
	redirect_listvm()
@auth.requires_login()     
#ADJUST THE RUN LEVEL OF THE VIRTUAL MACHINE
def adjrunlevel():
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        		
		return dict(vm=vminfo)
	except:
		exp_handlr_errorpage()
@auth.requires_login()		     
def clonevm():    
	try:
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		#TODO should know more about workflow
		return dict(vm=vminfo)
	except:
		exp_handlr_errorpage()
	redirect_listvm()
     
@auth.requires_login()
def changelevel():
	try:
		level=request.args[1]        
		vmname=request.args[0]
		vminfo =prerequisite_check(vmname)        
		insertinto_taskqueue(TASK_TYPE_CHANGELEVEL_VM,vminfo.id,TASK_QUEUE_STATUS_PENDING,TASK_QUEUE_PRIORITY_NORMAL)		
	except:
		exp_handlr_errorpage()
	redirect_listvm()
     
