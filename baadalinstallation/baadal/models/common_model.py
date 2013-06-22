# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import get_vm_template_config,get_date

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


def get_create_vm_form():
    
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

def get_vm_list(vm_data): 
    vmlist=[]
    for vm in vm_data:
        print vm.id
        total_cost = add_to_cost(vm.vm_name)
        element = {'name':vm.vm_name,'ip':vm.vm_ip, 'owner':vm.user_id, 'ip':vm.vm_ip, 'hostip':'hostip','RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
        vmlist.append(element)

    return vmlist

def get_all_vm_list():

    vms = db((db.vm_data.status != VM_STATUS_REQUESTED)&(db.vm_data.status != VM_STATUS_APPROVED)).select()
    return get_vm_list(vms)
    
def get_my_vm_list():
    
    vms = db((db.vm_data.status != VM_STATUS_REQUESTED)&(db.vm_data.status != VM_STATUS_APPROVED)&(db.vm_data.user_id==auth.user.id)).select()
    return get_vm_list(vms)

def get_fullname(_user_id):
    
    row = db(db.user.id==_user_id).select().first()    
    return row['first_name'] + ' ' + row['last_name']

    
