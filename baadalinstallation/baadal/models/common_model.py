# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db,URL,session,redirect, HTTP, FORM, INPUT, IS_INT_IN_RANGE
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_fullname, get_datetime, is_moderator, is_orgadmin, is_faculty

def get_hosted_vm_list(vms):
    vmlist = []
    for vm in vms:
        total_cost = add_to_cost(vm.id)
        element = {'id':vm.id,'name':vm.vm_name,'ip':vm.vm_ip, 'owner':get_full_name(vm.owner_id), 'hostip':vm.host_id.host_ip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
        vmlist.append(element)
    return vmlist


def get_pending_vm_list(vms):
    vmlist = []
    for vm in vms:
        element = {'id' : vm.id,
                   'vm_name' : vm.vm_name, 
                   'faculty_name' : get_fullname(vm.owner_id), 
                   'requester_name' : get_fullname(vm.requester_id), 
                   'RAM' : vm.RAM, 
                   'vCPUs' : vm.vCPU, 
                   'HDD' : vm.HDD, 
                   'status' : vm.status}
        vmlist.append(element)
    return vmlist


def add_to_cost(vm_id):
    vm = db.vm_data[vm_id]

    oldtime = vm.start_time
    newtime = get_datetime()
    
    if(oldtime==None):oldtime=newtime
    #Calculate hour difference between start_time and current_time
    hours  = ((newtime - oldtime).total_seconds()) / 3600
    
    if(vm.current_run_level == 0): scale = 0
    elif(vm.current_run_level == 1): scale = 1
    elif(vm.current_run_level == 2): scale = .5
    elif(vm.current_run_level == 3): scale = .25

    totalcost = float(hours*(vm.vCPU*float(COST_CPU) + vm.RAM*float(COST_RAM)/1024)*float(COST_SCALE)*float(scale)) + float(vm.total_cost)
    db(db.vm_data.id == vm_id).update(start_time=get_datetime(),total_cost=totalcost)
    return totalcost

def get_full_name(user_id):
    return get_fullname(user_id)

# Returns VM info, if VM exist
def get_vm_info(_vm_id):
    #Get VM Info, if it is not locked
    vm_info=db((db.vm_data.id==_vm_id) & (db.vm_data.locked == False)).select()
    if not vm_info:
        return None
    return vm_info.first()


def get_task_list(events):

    tasks = []
    for event in events:
        element = {'task_type':event.task_type,
                   'task_id':event.task_id,
                   'vm_name':event.vm_id.vm_name,
                   'user_name':get_full_name(event.vm_id.owner_id),
                   'start_time':event.start_time,
                   'end_time':event.end_time,
                   'error_msg':event.error}
        tasks.append(element)
    return tasks

def get_task_num_form():
    form = FORM('Show:',
                INPUT(_name = 'task_num', _size=2, requires = IS_INT_IN_RANGE(1,101)),
                INPUT(_type = 'submit', _value = 'Refresh'))
    return form
    

def add_vm_task_to_queue(_vm_id, _task_type, destination_host=None, live_migration=None):
    _dict = {}
    _dict['vm_id'] = _vm_id
    if destination_host != None:
        _dict['destination_host'] = destination_host
    if live_migration != None:
        _dict['live_migration'] = live_migration
        
    db.task_queue.insert(task_type=_task_type,
                         vm_id=_vm_id, 
                         parameters=str(_dict), 
                         priority=TASK_QUEUE_PRIORITY_NORMAL,  
                         status=TASK_QUEUE_STATUS_PENDING)
    

# Generic exception handler decorator
def handle_exception(fn):
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except HTTP:
            raise
        except:
            exception_handler()
    return decorator    

def exception_handler():
    import sys, traceback
    etype, value, tb = sys.exc_info()
    error = ''
    msg = ''.join(traceback.format_exception(etype, value, tb, 10))           
    if is_moderator():
        error = msg
    logger.error(msg)                 
    redirect(URL(c='default', f='error',vars={'error':error}))    
    
    
# Generic check moderator decorator
def check_moderator(fn):
    def decorator(*args, **kwargs):
        if (auth.is_logged_in()) & is_moderator():
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have admin privileges"
            redirect(URL(c='default', f='index'))
    return decorator    
   
    
# Generic check orgadmin decorator
def check_orgadmin(fn):
    def decorator(*args, **kwargs):
        if (auth.is_logged_in()) & (is_moderator() | is_orgadmin()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have org admin privileges"
            redirect(URL(c='default', f='index'))
    return decorator    


# Generic check faculty decorator
def check_faculty(fn):
    def decorator(*args, **kwargs):
        if (auth.is_logged_in()) & (is_moderator() | is_orgadmin() | is_faculty()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have faculty privileges"
            redirect(URL(c='default', f='index'))
    return decorator    

def get_pending_approval_count():

    users_of_same_org = db(db(auth.user.id == db.user.id).select(db.user.organisation_id).first()['organisation_id'] == db.user.organisation_id).select(db.user.id)

    return db((db.vm_data.status == VM_STATUS_VERIFIED) 
             & (db.vm_data.requester_id.belongs(users_of_same_org))).count()
