# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import get_vm_template_config,get_date, get_fullname,is_moderator

def get_my_vm_list():
	vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select()
	vmlist=[]
	for vm in vms:
		total_cost = add_to_cost(vm.vm_data.vm_name)
		hostip=gethostinfo_fromhostid(vm.vm_data.host_id).host_ip
		element = {'name':vm.vm_data.vm_name,
                   'ip':vm.vm_data.vm_ip, 
                   'owner':get_fullname(vm.vm_data.user_id), 
                   'ip':vm.vm_data.vm_ip, 
                   'hostip':hostip,
                   'RAM':vm.vm_data.RAM,
                   'vcpus':vm.vm_data.vCPU,
                   'level':vm.vm_data.current_run_level,
                   'cost':total_cost}
		vmlist.append(element)

	return vmlist

def get_configuration_elem(form):
    
    xmldoc = get_vm_template_config()
    itemlist = xmldoc.getElementsByTagName('template')
    _id=0
    for item in itemlist:
        if item.attributes['default'].value != 'true':
            _id=item.attributes['id'].value
        select=SELECT(_name='configuration_'+str(_id))
        cfglist = item.getElementsByTagName('config')
        i=0
        for cfg in cfglist:
            select.insert(i,OPTION(cfg.attributes['display'].value,_value=cfg.attributes['value'].value))
            i+=1
        
        config_elem = TR(LABEL('Configuration:'),select,_id='config_row__'+str(_id))
        form[0].insert(2,config_elem)

def set_configuration_elem(form):

    configVal = form.vars.configuration_0
    template = form.vars.template_id
    
    if eval('form.vars.configuration_'+str(template)) != None:
        configVal = eval('form.vars.configuration_'+str(template))

    configVal = configVal.split(',')
    
    form.vars.vCPU = int(configVal[0])
    form.vars.RAM = int(configVal[1])*1024
    form.vars.HDD = int(configVal[2])
    return


def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','HDD','purpose']
    form_labels = {'vm_name':'Name of VM','HDD':'Optional Additional Harddisk(GB)','template_id':'Template Image','purpose':'Purpose of this VM'}

    form =SQLFORM(db.vm_data, fields = form_fields, labels = form_labels)
    get_configuration_elem(form)
    return form

def add_vm_request_to_queue(_vm_id, _task_type):
    
    db.task_queue.insert(task_type=_task_type,
                         vm_id=_vm_id, 
                         priority=TASK_QUEUE_PRIORITY_NORMAL,  
                         status=TASK_QUEUE_STATUS_PENDING)
    
def add_user_to_vm(_vm_id):
    db(db.vm_data.id == _vm_id).update(user_id=auth.user.id, status=VM_STATUS_REQUESTED)

def add_to_cost(vm_name):
    vm = db(db.vm_data.vm_name==vm_name).select()[0]
    oldtime = vm.start_time
    hours=0
    if oldtime!=None:
        hours=0

    if(vm.current_run_level==0):scale=0
    elif(vm.current_run_level==1):scale=1
    elif(vm.current_run_level==2):scale=.5
    elif(vm.current_run_level==3):scale=.25

    totalcost = float(hours*(vm.vCPU*float(COST_CPU)+vm.RAM*float(COST_RAM)/1024)*float(COST_SCALE)*float(scale)) + float(vm.total_cost)
    db(db.vm_data.vm_name == vm_name).update(start_time=get_date(),total_cost=totalcost)
    return totalcost

def getuserinfo_fromusername(username) :    		
		names=username.split('_')
		firstname=names[0]
		lastname=names[1]
		userinfo = db(db.user.first_name == firstname and db.user.last_name == lastname ).select()[0]
		return userinfo

def getvminfo_fromvmname(vmname) :        
        vminfo = db(db.vm_data.vm_name == vmname).select()[0]
        return vminfo
        
def gethostinfo_fromhostid(hostid) :		
		hostinfo=db(db.host.id==hostid).select()[0]
		return hostinfo
		
def gettemplateinfo_fromtemplateid(templateid)	:	
		templateinfo=db(db.template.id == templateid).select()
		if templateinfo :
			templateinfo=templateinfo[0]
			return templateinfo

def	getusersofvm_frompermitted_uids(permitted_uids) :						
		usernames=[]
		for uid in permitted_uids :
			username=get_fullname(uid.user_id)#db(uid.user_id == db.user.id).select(db.user.first_name,db.user.last_name)[0]			
			usernames.append(username)
		return usernames
		
def getpermitteduserids_forvmid(vmid) :		
		userids=db(vmid == db.user_vm_map.vm_id ).select(db.user_vm_map.user_id)
		return userids		
	
def existsandlock_check(vmname) :
	#check for existance of VM
	#TODO check for VM locked if that feature is available
	
	 vminfo=db(db.vm_data.vm_name==vmname).select()
	 if not vminfo  :
		session.vm_status = "No such vm exists any more"		
		redirect_listvm()
	 else :
			return vminfo[0]
					
def perm_check(uid,permitted_uids) :
    if (not is_moderator() ):   #moderator has access rights on all vms		
		if checkuser(uid,permitted_uids) == False  :  # indirectly searching for username in accessible user list
				session.vm_status = "Not authorized"
				response.flash="Not authorized"
				redirect_listvm()
					
def checkuser(uid,permitted_uids) :
	for puid in permitted_uids :		
		if  uid == puid.user_id :
			return True
	return False

def prerequisite_check(vmname) :
		vminfo=existsandlock_check(vmname)  #where is vm.lock attribute	?			
		
		permitted_uids=getpermitteduserids_forvmid(vminfo.id)#get uids of all authorizied users on that vm
					
		perm_check(auth.user.id,permitted_uids)   #check whether is authorized or not
		return vminfo
def exp_handlr_errorpage():
		import sys, traceback
		etype, value, tb = sys.exc_info()
		msg = ''.join(traceback.format_exception(etype, value, tb, 10))
		session.flash=msg
		redirect(URL(c='default', f='error'))   
def redirect_listvm():
		if (session.prev_url != None):
					redirect(URL(r=request,f=session.prev_url))
		else :
					redirect(URL(r=request,c='user',f='list_my_vm'))

def insertinto_taskqueue(tasktype,vmid,status,priority) :
		db.task_queue.insert(task_type=tasktype,vm_id=vmid,status=status,priority=priority)
		session.flash = "Your task has been task_queued. Please check your task list for status."
