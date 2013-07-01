# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db,auth,request,session
    import gluon
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import get_vm_template_config,get_date, get_fullname

def get_my_vm_list():
    vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select()
    vmlist=[]
    for vm in vms:
        total_cost = add_to_cost(vm.vm_data.vm_name)
        element = {'id':vm.vm_data.id,
                   'name':vm.vm_data.vm_name,
                   'ip':vm.vm_data.vm_ip, 
                   'owner':get_fullname(vm.vm_data.user_id), 
                   'ip':vm.vm_data.vm_ip, 
                   'hostip':vm.vm_data.host_id.host_ip,
                   'RAM':vm.vm_data.RAM,
                   'vcpus':vm.vm_data.vCPU,
                   'level':vm.vm_data.current_run_level,
                   'cost':total_cost}
        vmlist.append(element)
    return vmlist

#Create configuration dropdowns
def get_configuration_elem(form):
    
    xmldoc = get_vm_template_config() # Read vm_template_config.xml
    itemlist = xmldoc.getElementsByTagName('template')
    _id=0 #for default configurations set, id will be configuration_0 
    for item in itemlist:
        if item.attributes['default'].value != 'true': #if not default, get the id 
            _id=item.attributes['id'].value
        select=SELECT(_name='configuration_'+str(_id)) # create HTML select with name as configuration_id
        cfglist = item.getElementsByTagName('config')
        i=0
        for cfg in cfglist:
            #Create HTML options and insert into select
            select.insert(i,OPTION(cfg.attributes['display'].value,_value=cfg.attributes['value'].value))
            i+=1
        
        #Create HTML tr, and insert label and select box
        config_elem = TR(LABEL('Configuration:'),select,_id='config_row__'+str(_id))
        form[0].insert(2,config_elem)#insert tr elemrnt in the form

# Gets CPU, RAM and HDD information on the basis of template selected.
def set_configuration_elem(form):

    configVal = form.vars.configuration_0 #Default configuration dropdown
    template = form.vars.template_id
    
    # if configuration specific to selected template is available
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
    get_configuration_elem(form) # Create dropdowns for configuration
    return form

def add_vm_task_to_queue(_vm_id, _task_type):
    db.task_queue.insert(task_type=_task_type,
                         vm_id=_vm_id, 
                         priority=TASK_QUEUE_PRIORITY_NORMAL,  
                         status=TASK_QUEUE_STATUS_PENDING)
    
def add_user_to_vm(_vm_id):
    db(db.vm_data.id == _vm_id).update(user_id=auth.user.id, status=VM_STATUS_REQUESTED)

def add_to_cost(vm_name):
    vm = db(db.vm_data.vm_name==vm_name).select()[0]

    oldtime = vm.start_time
    newtime = get_date()
    
    if(oldtime==None):oldtime=newtime
    
    hours  = ((newtime - oldtime).total_seconds()) / 3600
    if(vm.current_run_level==0):scale=0
    elif(vm.current_run_level==1):scale=1
    elif(vm.current_run_level==2):scale=.5
    elif(vm.current_run_level==3):scale=.25

    totalcost = float(hours*(vm.vCPU*float(COST_CPU)+vm.RAM*float(COST_RAM)/1024)*float(COST_SCALE)*float(scale)) + float(vm.total_cost)
    db(db.vm_data.vm_name == vm_name).update(start_time=get_date(),total_cost=totalcost)
    return totalcost

def get_vm_user_list(vm_id) :		
    vm_users=db(vm_id == db.user_vm_map.vm_id ).select()
    user_id_lst =[]
    for vm_user in vm_users:
        user_id_lst.append(vm_user.user_id)
    return user_id_lst		

# Returns VM info, if VM exist
def get_vm_info(_vm_id):
    #check if VM exists
    vm_info=db(db.vm_data.id==_vm_id).select()
    if not vm_info:
        return None
    return vm_info.first()

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
        
def get_full_name(user_id):
    return get_fullname(user_id)
