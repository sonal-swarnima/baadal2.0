# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db,URL,session,redirect,HTTP,FORM,INPUT,IS_INT_IN_RANGE,A,SPAN,IMG,request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

from helper import get_fullname, get_datetime, is_moderator, is_orgadmin, is_faculty

def get_vm_status(iStatus):
    vm_status_map = {
            VM_STATUS_UNKNOWN     :    'Unknown',
            VM_STATUS_IN_QUEUE    :    'In-Queue',
            VM_STATUS_RUNNING     :    'Running',
            VM_STATUS_SUSPENDED   :    'Paused',
            VM_STATUS_SHUTDOWN    :    'Shutdown'
        }
    return vm_status_map[iStatus]

def get_request_status(iStatus):
    req_status_map = {
            REQ_STATUS_REQUESTED   :    'Requested',
            REQ_STATUS_REJECTED    :    'Rejected',
            REQ_STATUS_VERIFIED    :    'Verified',
            REQ_STATUS_APPROVED    :    'Approved',
            REQ_STATUS_IN_QUEUE    :    'In-Queue',
        }
    return req_status_map[iStatus]

def get_hosted_vm_list(vms):
    vmlist = []
    for vm in vms:
        element = {'id' : vm.id,
                   'name' : vm.vm_name,
                   'organisation' : vm.owner_id.organisation_id.name,
                   'owner' : vm.owner_id.first_name + ' ' + vm.owner_id.last_name if vm.owner_id > 0 else 'System User', 
                   'private_ip' : vm.private_ip, 
                   'public_ip' : vm.public_ip, 
                   'hostip' : vm.host_id.host_ip,
                   'RAM' : vm.RAM,
                   'vcpus' : vm.vCPU,
                   'status' : get_vm_status(vm.status)}
        vmlist.append(element)
    return vmlist

#Update the dictionary with values specific to pending Install request tab
def update_install_vm_request(vm_request, element):
    collaborators = '-'
    if vm_request.collaborators != None:
        vm_users = db(db.user.id.belongs(vm_request.collaborators)).select()
        collaborators = ', '.join((vm_user.first_name + ' ' + vm_user.last_name) for vm_user in vm_users)
    element['collaborators'] = collaborators
    element['public_ip'] = vm_request.public_ip; 
#     element['services_enabled'] = ', '.join(ser for ser in vm_request.enable_service) if len(vm_request.enable_service) != 0 else '-'; 
    element['security_domain'] = vm_request.security_domain.name if vm_request.security_domain != None else '-';
    
    if vm_request.extra_HDD != 0:
        element['HDD'] = str(vm_request.HDD)+'GB + ' + str(vm_request.extra_HDD) + 'GB'
    
#Update the dictionary with values specific to pending Clone request tab
def update_clone_vm_request(vm_request, element):
    element['clone_count'] = vm_request.clone_count
    
#Update the dictionary with values specific to pending Attach Disk request tab
def update_attach_disk_request(vm_request, element):
    element['parent_vm_id'] = vm_request.parent_id
    element['extra_HDD'] = str(vm_request.extra_HDD) + 'GB' if vm_request.extra_HDD !=0 else 'None'
    element['attach_disk'] = str(vm_request.attach_disk) + 'GB'
    

#Update the dictionary with values specific to pending Edit Configuration request tab
def update_edit_config_request(vm_request, element):
    vm_data = db.vm_data[vm_request.parent_id]
    
    element['parent_vm_id'] = vm_request.parent_id
    element['old_RAM'] = str(vm_data.RAM/1024)+'GB'
    if vm_request.RAM == vm_data.RAM:
        element['RAM'] = 'Same'
    
    element['old_vCPUs'] = str(vm_data.vCPU) +' CPU'
    if vm_request.vCPU == vm_data.vCPU:
        element['vCPUs'] = 'Same'

    element['old_public_ip'] = (vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED)
    element['public_ip'] = vm_request.public_ip
#     element['old_services_enabled'] = ', '.join(ser for ser in vm_data.enable_service) if vm_data.enable_service != None else '-';
#     element['services_enabled'] = ', '.join(ser for ser in vm_request.enable_service) if vm_request.enable_service != vm_data.enable_service else 'Same'

    element['old_security_domain'] = vm_data.security_domain.name if vm_data.security_domain != None else '-';
    if vm_request.security_domain == vm_data.security_domain: element['security_domain'] = 'Same'
    else: element['security_domain'] = vm_request.security_domain.name if vm_request.security_domain != None else None;


def get_pending_request_query(statusList):

    if is_moderator():
        _query = db(db.request_queue.status.belongs(statusList))
    elif is_orgadmin():
        users_of_same_org = db(auth.user.organisation_id == db.user.organisation_id)._select(db.user.id)
        _query = db((db.request_queue.status.belongs(statusList)) & (db.request_queue.requester_id.belongs(users_of_same_org)))
    else:
        _query = db((db.request_queue.status.belongs(statusList)) & (db.request_queue.owner_id == auth.user.id))
        
    return _query


def get_pending_approval_count():
    
    _query = get_pending_request_query([REQ_STATUS_VERIFIED])
    return _query.count()

def get_all_pending_req_count():

    _query = get_pending_request_query([REQ_STATUS_REQUESTED, REQ_STATUS_VERIFIED, REQ_STATUS_APPROVED])
    return _query.count()

#Creates dictionary of pending requests for differnt request types.
#It is used for HTML rendering
def get_pending_request_list(vm_requests):

    request_list = []
    for vm_request in vm_requests:
        
        element = {'id' : vm_request.id,
                   'vm_name' : vm_request.vm_name, 
                   'faculty_name' : vm_request.owner_id.first_name + ' ' + vm_request.owner_id.last_name, 
                   'requester_id' : vm_request.requester_id, 
                   'owner_id' : vm_request.owner_id,
                   'requester_name' : vm_request.requester_id.first_name + ' ' + vm_request.requester_id.last_name,
                   'org_id' : vm_request.requester_id.organisation_id,
                   'organisation' : vm_request.requester_id.organisation_id.name,
                   'vCPUs' : str(vm_request.vCPU)+' CPU', 
                   'RAM' : str(vm_request.RAM/1024) + 'GB' if vm_request.RAM else None, 
                   'HDD' : str(vm_request.HDD) + 'GB' if vm_request.HDD else None,
                   'request_type' : vm_request.request_type,
                   'status' : vm_request.status}
        
        if vm_request.request_type == TASK_TYPE_CREATE_VM:
            update_install_vm_request(vm_request, element)
        elif vm_request.request_type == TASK_TYPE_CLONE_VM:
            update_clone_vm_request(vm_request, element)
        elif vm_request.request_type == TASK_TYPE_ATTACH_DISK:
            update_attach_disk_request(vm_request, element)
        elif vm_request.request_type == TASK_TYPE_EDITCONFIG_VM:
            update_edit_config_request(vm_request, element)
        
        request_list.append(element)
    return request_list

def get_segregated_requests(request_list):
    
    install_requests = []
    clone_requests = []
    disk_requests = []
    edit_requests = []
    for req in request_list:
        if req['request_type'] == TASK_TYPE_CREATE_VM:
            install_requests.append(req)
        elif req['request_type'] == TASK_TYPE_CLONE_VM:
            clone_requests.append(req)
        elif req['request_type'] == TASK_TYPE_ATTACH_DISK:
            disk_requests.append(req)
        elif req['request_type'] == TASK_TYPE_EDITCONFIG_VM:
            edit_requests.append(req)
    return (install_requests, clone_requests, disk_requests, edit_requests)
    
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
    return get_fullname(user_id) if user_id > 0 else 'System User'

# Returns VM info, if VM exist
def get_vm_info(_vm_id):
    #Get VM Info, if it is not locked
    vm_info = db((db.vm_data.id == _vm_id) & (db.vm_data.locked == False)).select()
    if not vm_info:
        return None

    return vm_info.first()

def get_request_info(request_id):
    return db.request_queue[request_id]

def is_vm_owner(vm_id):
    if is_moderator() or is_orgadmin():
        return True
    
    if db((db.user_vm_map.vm_id == vm_id) & (db.user_vm_map.user_id == auth.user.id)).count()>0:
        return True
    else:
        return False

def get_task_list(events):

    tasks = []
    for event in events:
        element = {'event_id'  :event.id,
                   'task_type' :event.task_type,
                   'task_id'   :event.task_id,
                   'vm_name'   :event.vm_id.vm_name,
                   'user_name' :get_full_name(event.requester_id),
                   'start_time':event.start_time,
                   'att_time'  :event.attention_time,
                   'end_time'  :event.end_time,
                   'error_msg' :event.message}
        tasks.append(element)
    return tasks

def get_task_num_form():
    form = FORM('Show:',
                INPUT(_name = 'task_num', _class='task_num', requires = IS_INT_IN_RANGE(1,101), _id='task_num_id'),
                A(SPAN(_class='icon-refresh'), _onclick = 'tab_refresh();$(this).closest(\'form\').submit()', _href='#'))
    return form
    

def add_vm_task_to_queue(vm_id, task_type, params = {}, requested_by=None):
    
    if requested_by == None:
        if auth.user:
            requested_by = auth.user.id
        else:
            requested_by = -1

    params.update({'vm_id' : vm_id})
    db.task_queue.insert(task_type=task_type,
                         vm_id=vm_id, 
                         requester_id=requested_by,
                         parameters=params, 
                         priority=TASK_QUEUE_PRIORITY_NORMAL,  
                         status=TASK_QUEUE_STATUS_PENDING)
    

def add_vm_users(_vm_id, requester_id, owner_id, vm_users=None):
    user_list = [requester_id, owner_id]
    if vm_users: user_list.extend(vm_users)
    for _user_id in set(user_list):
        db.user_vm_map.insert(user_id=_user_id,vm_id=_vm_id);


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
        if is_moderator():
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have admin privileges"
            redirect(URL(c='default', f='index'))
    return decorator    
   
    
# Generic check orgadmin decorator
def check_orgadmin(fn):
    def decorator(*args, **kwargs):
        if (is_moderator() or is_orgadmin()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have org admin privileges"
            redirect(URL(c='default', f='index'))
    return decorator    


# Generic check faculty decorator
def check_faculty(fn):
    def decorator(*args, **kwargs):
        if (is_faculty() or is_orgadmin() or is_moderator()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have faculty privileges"
            redirect(URL(c='default', f='index'))
    return decorator    


def get_vm_operations(vm_id):

    valid_operations_list = []
    vmstatus = int(db(db.vm_data.id == vm_id).select(db.vm_data.status).first()['status'])
   
    if (vmstatus == VM_STATUS_RUNNING) or (vmstatus == VM_STATUS_SUSPENDED) or (vmstatus == VM_STATUS_SHUTDOWN):

        valid_operations_list.append(A(IMG(_src=URL('static','images/snapshot.png'), _height=20, _width=20),
                    _href=URL(r=request, c='user' ,f='snapshot', args=[vm_id]), 
                    _title="Take VM snapshot", _alt="Take VM snapshot"))

        valid_operations_list.append(A(IMG(_src=URL('static','images/performance.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='user' ,f='show_vm_performance', args=[vm_id]), 
                    _title="Check VM performance", _alt="Check VM Performance"))

        if is_moderator() or is_orgadmin() or is_faculty():
            valid_operations_list.append(A(IMG(_src=URL('static','images/delete.png'), _height=20, _width=20),
                        _onclick="confirm_vm_deletion()",    _title="Delete this virtual machine",    _alt="Delete this virtual machine"))
  
        if vmstatus == VM_STATUS_SUSPENDED:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/play2.png'), _height=20, _width=20),
                _href=URL(r=request, f='handle_vm_operation', args= [TASK_TYPE_RESUME_VM, vm_id]), 
                _title="Unpause this virtual machine", _alt="Unpause on this virtual machine"))
                
        elif vmstatus == VM_STATUS_SHUTDOWN:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/on-off.png'), _height=20, _width=20),
                        _href=URL(r=request, f='handle_vm_operation', args=[TASK_TYPE_START_VM, vm_id]), 
                    _title="Turn on this virtual machine", _alt="Turn on this virtual machine"))

            valid_operations_list.append(A(IMG(_src=URL('static','images/clonevm.png'), _height=20, _width=20),
                _href=URL(r=request,c='user', f='clone_vm', args=vm_id), _title="Request Clone vm", _alt="Request Clone vm"))
                               
            valid_operations_list.append(A(IMG(_src=URL('static','images/disk.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='user' ,f='attach_extra_disk', args=[vm_id]), 
                    _title="Attach Extra Disk", _alt="Attach Extra Disk"))
                    
            valid_operations_list.append(A(IMG(_src=URL('static','images/editme.png'), _height=20, _width=20),
                _href=URL(r = request, c = 'user', f = 'edit_vm_config', args = vm_id), _title="Edit VM Config", 
                _alt="Edit VM Config"))
                
            if is_moderator():
            
                valid_operations_list.append(A(IMG(_src=URL('static','images/vnc.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='default' ,f='page_under_construction', args=[vm_id]), 
                    _title="Assign VNC", _alt="Assign VNC"))
                    
        elif vmstatus == VM_STATUS_RUNNING:
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/pause2.png'), _height=20, _width=20),
                    _href=URL(r=request, f='handle_vm_operation', args= [TASK_TYPE_SUSPEND_VM, vm_id]), 
                    _title="Pause this virtual machine", _alt="Pause this virtual machine"))

            valid_operations_list.append(A(IMG(_src=URL('static','images/shutdown2.png'), _height=20, _width=20),
                    _href=URL(r=request, f='handle_vm_operation', args=[TASK_TYPE_STOP_VM, vm_id]), _title="Gracefully shut down this virtual machine",
                    _alt="Gracefully shut down this virtual machine"))

            valid_operations_list.append(A(IMG(_src=URL('static','images/disk.jpg'), _height=20, _width=20),
                    _href=URL(r=request, c='user' ,f='attach_extra_disk', args=[vm_id]), 
                    _title="Attach Extra Disk", _alt="Attach Extra Disk"))
                                      
                    
        if (vmstatus == VM_STATUS_RUNNING) or (vmstatus == VM_STATUS_SUSPENDED):
            
            valid_operations_list.append(A(IMG(_src=URL('static','images/on-off.png'), _height=20, _width=20),
                    _href=URL(r=request, f='handle_vm_operation', args= [TASK_TYPE_DESTROY_VM, vm_id]), 
                    _title="Forcefully power off this virtual machine",
                    _alt="Forcefully power off this virtual machine"))

        if is_moderator():

            valid_operations_list.append(A(IMG(_src=URL('static','images/user_add.png'), _height=20, _width=20),
                        _href=URL(r = request, c = 'admin', f = 'user_details', args = vm_id), _title="Add User to VM", 
                        _alt="Add User to VM"))

            if (db(db.host.id > 0).count() >= 2):

                valid_operations_list.append(A(IMG(_src=URL('static','images/migrate.png'), _height=20, _width=20),
                        _href=URL(r=request, c = 'admin' , f='migrate_vm', args=[vm_id]), 
                     _title="Migrate this virtual machine", _alt="Migrate this virtual machine"))

   
   
    else:
        logger.error("INVALID VM STATUS!!!")
        raise
    return valid_operations_list  

def get_vm_snapshots(vm_id):
    vm_snapshots_list = []
    for snapshot in db(db.snapshot.vm_id == vm_id).select():

        snapshot_dict = {}
        snapshot_type = {SNAPSHOT_USER    : 'User',
                         SNAPSHOT_DAILY   : 'Daily',
                         SNAPSHOT_WEEKLY  : 'Weekly',
                         SNAPSHOT_MONTHLY : 'Monthly'}
        
        snapshot_dict['type'] = snapshot_type[snapshot.type]
        snapshot_dict['name'] = snapshot.snapshot_name
        if snapshot.type == SNAPSHOT_USER:
            snapshot_dict['delete'] = A(IMG(_src=URL('static','images/delete-snapshot.gif'), _height = 20, _width = 20),
                                           _href=URL(r=request, f='delete_snapshot', args= [vm_id, snapshot.id]),
                                           _title = "Delete this snapshot",    _alt = "Delete this snapshot")
        else:
            snapshot_dict['delete'] = ' '
        snapshot_dict['revert'] = A(IMG(_src=URL('static','images/revertTosnapshot.png'),_height = 20, _width = 20),
                                       _href=URL(r=request, f='revert_to_snapshot', args= [vm_id, snapshot.id]),
                                       _title = "Revert to this snapshot", _alt = "Revert to this snapshot")
        vm_snapshots_list.append(snapshot_dict)
    return vm_snapshots_list

def get_faculty_info(faculty_id):
    faculty_info = db(db.user.id==faculty_id).select()
    if not faculty_info:
        return None
    return faculty_info.first()
