# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    global auth; auth = gluon.tools.Auth()
    from common_model import add_to_cost
###################################################################################
import helper

def get_my_vm_list():
    vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select()
    vmlist=[]
    for vm in vms:
        total_cost = add_to_cost(vm.vm_data.vm_name)
        element = {'name':vm.vm_data.vm_name,
                   'ip':vm.vm_data.vm_ip, 
                   'owner':vm.vm_data.user_id, 
                   'ip':vm.vm_data.vm_ip, 
                   'hostip':'hostip',
                   'RAM':vm.vm_data.RAM,
                   'vcpus':vm.vm_data.vCPU,
                   'level':vm.vm_data.current_run_level,
                   'cost':total_cost}
        vmlist.append(element)

    return vmlist

def get_request_vm_form():
    
    form_fields = ['vm_name','template_id','HDD','purpose']
    form_labels = {'vm_name':'Name of VM','HDD':'Optional Additional Harddisk(GB)','template_id':'Template Image','purpose':'Purpose of this VM'}

    form =SQLFORM(db.vm_data, fields = form_fields, labels = form_labels)
    helper.get_configuration_elem(form)
    return form

def add_vm_request_to_queue(_vm_id, _task_type):
    
    db.task_queue.insert(task_type=_task_type,
                         vm_id=_vm_id, 
                         priority=TASK_QUEUE_PRIORITY_NORMAL,  
                         status=TASK_QUEUE_STATUS_PENDING)

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



    
