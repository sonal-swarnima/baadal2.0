# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db,URL,session,redirect, HTTP, FORM, INPUT, IS_INT_IN_RANGE,A,SPAN,IMG,request
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
    totalcost = round(totalcost,2)
    db(db.vm_data.id == vm_id).update(start_time=get_datetime(),total_cost=totalcost)
    return totalcost

def get_full_name(user_id):
    return get_fullname(user_id)

# Returns VM info, if VM exist
def get_vm_info(_vm_id):
    #Get VM Info, if it is not locked
    vm_info=db((db.vm_data.id == _vm_id) & (db.vm_data.locked == False)).select()
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
                INPUT(_name = 'task_num', _class='task_num', requires = IS_INT_IN_RANGE(1,101)),
                A(SPAN(_class='icon-refresh'), _onclick = 'tab_refresh();$(this).closest(\'form\').submit()', _href='#'))
    return form
    

def add_vm_task_to_queue(_vm_id, _task_type, destination_host = None, live_migration = None, updated_vm_config = None, snapshot_id = None):

    _dict = {}
    _dict['vm_id'] = _vm_id
    
    if destination_host:
        _dict['destination_host'] = destination_host
    if live_migration:
        _dict['live_migration'] = live_migration
    if updated_vm_config:
        _dict['ram'] = updated_vm_config['ram']
        _dict['vcpus'] = updated_vm_config['vcpus']
    if snapshot_id:
        _dict['snapshot_id'] = snapshot_id
        
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
        if (auth.is_logged_in()) & (is_faculty()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have faculty privileges"
            redirect(URL(c='default', f='index'))
    return decorator    

def get_pending_approval_count():

    users_of_same_org = db(db(auth.user.id == db.user.id).select(db.user.organisation_id).first()['organisation_id'] == db.user.organisation_id).select(db.user.id)

    return db((db.vm_data.status == VM_STATUS_VERIFIED) 
             & (db.vm_data.requester_id.belongs(users_of_same_org))).count()
             
def get_vm_operations(vm_id):

    valid_operations_list = []
    vmstatus = int(db(db.vm_data.id == vm_id).select(db.vm_data.status).first()['status'])
   
    if (vmstatus == VM_STATUS_RUNNING) or (vmstatus == VM_STATUS_SUSPENDED) or (vmstatus == VM_STATUS_SHUTDOWN):

        valid_operations_list.append(A(IMG(_src=URL('static','images/snapshot.png'), _height=20, _width=20),
                    _href=URL(r=request, c='user' ,f='snapshot', args=[vm_id]), 
                    _title="Take VM snapshot", _alt="Take VM snapshot"))

        valid_operations_list.append(A(IMG(_src=URL('static','images/performance.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='default' ,f='page_under_construction', args=[vm_id]), 
                    _title="Check VM performance", _alt="Check VM Performance"))

        if is_moderator():
            valid_operations_list.append(A(IMG(_src=URL('static','images/migrate.png'), _height=20, _width=20),
               	 	_href=URL(r=request, c = 'admin' , f='migrate_vm', args=[vm_id]), 
                	_title="Migrate this virtual machine", _alt="Migrate this virtual machine"))

        if is_moderator() or is_orgadmin() or is_faculty():
            valid_operations_list.append(A(IMG(_src=URL('static','images/delete.png'), _height=20, _width=20),
               	 	_onclick="confirm_vm_deletion()",	_title="Delete this virtual machine",	_alt="Delete this virtual machine"))
  
        if vmstatus == VM_STATUS_SUSPENDED:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/play2.png'), _height=20, _width=20),
                _href=URL(r=request, f='resume_machine', args=[vm_id]), 
                _title="Unpause this virtual machine", _alt="Unpause on this virtual machine"))
                
            valid_operations_list.append(A(IMG(_src=URL('static','images/cpu.png'), _height=20, _width=20),
                _href=URL(r=request, f='adjrunlevel', args = vm_id),
                _title="Adjust your machines resource utilization", _alt="Adjust your machines resource utilization"))
            
        if vmstatus == VM_STATUS_SHUTDOWN:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/on-off.png'), _height=20, _width=20),
               	 	_href=URL(r=request, f='start_machine', args=[vm_id]), 
                	_title="Turn on this virtual machine", _alt="Turn on this virtual machine"))

            valid_operations_list.append(A(IMG(_src=URL('static','images/clonevm.png'), _height=20, _width=20),
                _href=URL(r=request,c='default', f='request_clonevm', args=vm_id), _title="Request Clone vm", _alt="Request Clone vm"))
                               
            valid_operations_list.append(A(IMG(_src=URL('static','images/disk.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='default' ,f='page_under_construction', args=[vm_id]), 
                    _title="Attach Extra Disk", _alt="Attach Extra Disk"))
                    
            if is_moderator():
            
                valid_operations_list.append(A(IMG(_src=URL('static','images/vnc.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='default' ,f='page_under_construction', args=[vm_id]), 
                    _title="Assign VNC", _alt="Assign VNC"))
                    
                valid_operations_list.append(A(IMG(_src=URL('static','images/editme.png'), _height=20, _width=20),
                    _href=URL(r = request, c = 'admin', f = 'edit_vmconfig', args = vm_id), _title="Edit VM Config", 
                    _alt="Edit VM Config"))
                
        if vmstatus == VM_STATUS_RUNNING:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/pause2.png'), _height=20, _width=20),
                    _href=URL(r=request, f='pause_machine', args=[vm_id]), 
                    _title="Pause this virtual machine", _alt="Pause this virtual machine"))

            valid_operations_list.append(A(IMG(_src=URL('static','images/shutdown2.png'), _height=20, _width=20),
                    _href=URL(r=request, f='shutdown_machine', args=[vm_id]), _title="Gracefully shut down this virtual machine",
                    _alt="Gracefully shut down this virtual machine"))
                    
                    
        if (vmstatus == VM_STATUS_RUNNING) or (vmstatus == VM_STATUS_SUSPENDED):
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/on-off.png'), _height=20, _width=20),
                    _href=URL(r=request, f='destroy_machine', args= [vm_id]), 
                    _title="Forcefully power off this virtual machine",
                    _alt="Forcefully power off this virtual machine"))

    if is_moderator():
   
        valid_operations_list.append(A(IMG(_src=URL('static','images/user_add.png'), _height=20, _width=20),
                    _href=URL(r = request, c = 'admin', f = 'user_details', args = vm_id), _title="Add User to VM", 
                    _alt="Add User to VM"))
   
   
    else:
        logger.error("INVALID VM STATUS!!!")
        raise
    return valid_operations_list  

def get_vm_snapshots(vm_id):
    vm_snapshots_list = []
    snapshot_dict = {}
    for snapshot in db(db.snapshot.vm_id == vm_id).select():
        
        snapshot_dict['name'] = snapshot.snapshot_name
        snapshot_dict['delete'] = A(IMG(_src=URL('static','images/delete-snapshot.gif'), _height = 20, _width = 20),
                                       _href=URL(r=request, f='delete_snapshot', args= [vm_id, snapshot.id]),
               	 	               _title = "Delete this snapshot",	_alt = "Delete this snapshot")
        snapshot_dict['revert'] = A(IMG(_src=URL('static','images/revertTosnapshot.png'),_height = 20, _width = 20),
                                       _href=URL(r=request, f='revert_to_snapshot', args= [vm_id, snapshot.id]),
                                       _title = "Revert to this snapshot", _alt = "Revert to this snapshot")
        vm_snapshots_list.append(snapshot_dict)

    return vm_snapshots_list
   
   
