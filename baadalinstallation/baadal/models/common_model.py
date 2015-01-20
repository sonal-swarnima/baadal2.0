# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db, request, session
    from gluon import *  # @UnusedWildImport
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

from helper import log_exception, logger

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
        element = {'id'           : vm.id,
                   'name'         : vm.vm_name,
                   'organisation' : vm.owner_id.organisation_id.name if vm.owner_id > 0 else 'System',
                   'owner'        : vm.owner_id.first_name + ' ' + vm.owner_id.last_name if vm.owner_id > 0 else 'System User', 
                   'private_ip'   : vm.private_ip.private_ip, 
                   'public_ip'    : vm.public_ip.public_ip if vm.public_ip else PUBLIC_IP_NOT_ASSIGNED, 
                   'hostip'       : vm.host_id.host_ip.private_ip,
                   'RAM'          : str(round((vm.RAM/1024.0),2)) + ' GB',
                   'vcpus'        : str(vm.vCPU) + ' CPU',
                   'status'       : get_vm_status(vm.status)}
        vmlist.append(element)
    return vmlist

#Update the dictionary with values specific to pending Install request tab
def update_install_vm_request(vm_request, element):

    collaborators = '-'
    if vm_request.collaborators != None:
        vm_users = db(db.user.id.belongs(vm_request.collaborators)).select()
        if len(vm_users) > 0:
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
    element['extra_HDD'] = str(vm_request.extra_HDD) + 'GB' if vm_request.extra_HDD != None else '-'
    element['attach_disk'] = str(vm_request.attach_disk) + 'GB'
    

#Update the dictionary with values specific to pending Edit Configuration request tab
def update_edit_config_request(vm_request, element):
    vm_data = db.vm_data[vm_request.parent_id]
    
    element['parent_vm_id'] = vm_request.parent_id
    element['old_RAM'] = str(round((vm_data.RAM/1024.0),2))+' GB'
    if vm_request.RAM == vm_data.RAM:
        element['RAM'] = 'Same'
    
    element['old_vCPUs'] = str(vm_data.vCPU) +' CPU'
    if vm_request.vCPU == vm_data.vCPU:
        element['vCPUs'] = 'Same'

    element['old_public_ip'] = (vm_data.public_ip == None)
    element['public_ip'] = vm_request.public_ip

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
                   'RAM' : str(round((vm_request.RAM/1024.0),2)) + ' GB' if vm_request.RAM else None, 
                   'HDD' : str(vm_request.HDD) + ' GB' if vm_request.HDD else None,
                   'request_type' : vm_request.request_type,
                   'status' : vm_request.status}
        
        if vm_request.request_type == VM_TASK_CREATE:
            update_install_vm_request(vm_request, element)
        elif vm_request.request_type == VM_TASK_CLONE:
            update_clone_vm_request(vm_request, element)
        elif vm_request.request_type == VM_TASK_ATTACH_DISK:
            update_attach_disk_request(vm_request, element)
        elif vm_request.request_type == VM_TASK_EDIT_CONFIG:
            update_edit_config_request(vm_request, element)
        
        request_list.append(element)
    return request_list

def get_segregated_requests(request_list):
    
    install_requests = []
    clone_requests = []
    disk_requests = []
    edit_requests = []
    for req in request_list:
        if req['request_type'] == VM_TASK_CREATE:
            install_requests.append(req)
        elif req['request_type'] == VM_TASK_CLONE:
            clone_requests.append(req)
        elif req['request_type'] == VM_TASK_ATTACH_DISK:
            disk_requests.append(req)
        elif req['request_type'] == VM_TASK_EDIT_CONFIG:
            edit_requests.append(req)
    return (install_requests, clone_requests, disk_requests, edit_requests)
   
def get_users_with_organisation(pending_users):
    users_with_org=[]
    for user in pending_users:
        user['organisation']=user.organisation_id.name
        users_with_org.append(user)
    return users_with_org
        
def get_user_role_types():
    user_types=db(db.user_group.role != USER).select(db.user_group.id, db.user_group.role);
    return user_types
        
def delete_all_user_roles(user_id):
    db(db.user_membership.user_id == user_id).delete()        
        

# Get user name and email
def get_user_details(user_id):
    if user_id < 0:
            return ('System User',None, None)
    else:
        user = db.user[user_id]
        if user :
            username = user.first_name + ' ' + user.last_name
            email = user.email if user.mail_subscribed else None
 
            return (username, email, user.username)
        else:
            return (None, None, None)


def get_full_name(user_id):
    return get_user_details(user_id)[0]
    
    
# Returns VM info, if VM exist
def get_vm_info(_vm_id):
    #Get VM Info, if it is not locked
    vm_info = db((db.vm_data.id == _vm_id) & (db.vm_data.template_id==db.template.id)).select()
    
    if not vm_info:
        return None

    return vm_info.first()

def get_request_info(request_id):
    return db.request_queue[request_id]

def is_vm_owner(vm_id):
    if auth.user:
        if is_moderator() or is_orgadmin() or (db.user_vm_map(vm_id=vm_id, user_id=auth.user.id)):
            return True

    return False

def get_task_list(events):

    tasks = []
    for event in events:
        element = {'event_id'  :event.id,
                   'task_type' :event.task_type,
                   'task_id'   :event.task_id,
                   'vm_name'   :event.vm_name,
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
            requested_by = SYSTEM_USER

    params.update({'vm_id' : long(vm_id)})
    db.task_queue.insert(task_type=task_type,
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
    msg = log_exception('Exception: ') 
    if is_moderator():
        error = msg
    else:
        error = 'Some error has occurred'
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
        if not is_vm_user():
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have faculty privileges"
            redirect(URL(c='default', f='index'))
    return decorator    


# checks vm owner, assumes first argument of request is vm_id
def check_vm_owner(fn):
    def decorator(*args, **kwargs):
        vm_id = request.args[0]
        if (is_vm_owner(vm_id)):
            return fn(*args, **kwargs)
        else:
            session.flash = "Unauthorized access"
            redirect(URL(c='default', f='index'))
    return decorator    


def get_vm_operations(vm_id):

    vm_operations = {'start_vm'              : ('user', 'on-off.png', 'Turn on this virtual machine'),
                     'suspend_vm'            : ('user', 'pause2.png', 'Suspend this Virtual Machine'),
                     'resume_vm'             : ('user', 'play2.png', 'Unpause this virtual machine'),
                     'stop_vm'               : ('user', 'shutdown2.png', 'Gracefully shut down this virtual machine'),
                     'destroy_vm'            : ('user', 'on-off.png', 'Forcefully power off this virtual machine'),
                     'clone_vm'              : ('user', 'clonevm.png', 'Request VM Clone'),
                     'attach_extra_disk'     : ('user', 'disk.jpg', 'Attach Extra Disk'),
                     'snapshot'              : ('user', 'snapshot.png', 'Take VM snapshot'),
                     'edit_vm_config'        : ('user', 'editme.png', 'Edit VM Config'),
                     'show_vm_performance'   : ('user', 'performance.jpg', 'Check VM Performance'),
                     'vm_history'            : ('user', 'history.png', 'Show VM History'),
                     'grant_vnc'             : ('user', 'vnc.jpg', 'Grant VNC Access'),
                     'confirm_vm_deletion()' : ( None, 'delete.png', 'Delete this virtual machine'),
                     'migrate_vm'            : ('admin', 'migrate.png', 'Migrate this virtual machine'),
                     'user_details'          : ('admin', 'user_add.png', 'Add User to VM'),
                     'save_as_template'      : ('user', 'save.png', 'Save as Template'),
                     'mail_user'             : ('admin','email_icon.png','Send Mail to users of the VM')}

    valid_operations_list = []
    
    vm_status = db.vm_data[vm_id].status
    
    if vm_status not in (VM_STATUS_UNKNOWN, VM_STATUS_IN_QUEUE):
        valid_operations = ['snapshot', 'show_vm_performance']

        if vm_status == VM_STATUS_RUNNING:
            valid_operations.extend(['suspend_vm' , 'stop_vm', 'destroy_vm'])
        elif vm_status == VM_STATUS_SUSPENDED:
            valid_operations.extend(['resume_vm'])
        elif vm_status == VM_STATUS_SHUTDOWN:
            #Start VM option is not valid if edit VM or attach disk option is in queue
            if not (is_request_in_queue(vm_id, VM_TASK_EDIT_CONFIG) | 
                    is_request_in_queue(vm_id, VM_TASK_ATTACH_DISK)):
                valid_operations.extend(['start_vm'])

            valid_operations.extend(['clone_vm', 'edit_vm_config', 'attach_extra_disk', 'save_as_template'])

        if not is_vm_user():
            valid_operations.extend(['confirm_vm_deletion()'])
            if is_moderator():
                valid_operations.extend(['migrate_vm'])
                valid_operations.extend(['user_details'])
                valid_operations.extend(['mail_user'])

        valid_operations.extend(['grant_vnc', 'vm_history'])
        
        #Disable all links if Delete VM option is in queue
        link_disabled = True if is_request_in_queue(vm_id, VM_TASK_DELETE) else False
        for valid_operation in valid_operations:
            
            op_data = vm_operations[valid_operation]
            op_image = IMG(_src=URL('static','images/'+op_data[1]), _style='height:20px;weight:20px')
            
            if link_disabled:
                valid_operations_list.append(op_image)
            else:
                if op_data[0] != None:
                    valid_operations_list.append(A(op_image, _title=op_data[2], _alt=op_data[2], 
                                                   _href=URL(r=request, c = op_data[0] , f=valid_operation, args=[vm_id])))
                else:
                    valid_operations_list.append(A(op_image, _title=op_data[2], _alt=op_data[2], 
                                                   _onclick=valid_operation))
   
    else:
        logger.error("INVALID VM STATUS!!!")
        raise
    return valid_operations_list  

def get_snapshot_type(snapshot_type):
    snapshot_map = {SNAPSHOT_USER    : 'User',
                     SNAPSHOT_DAILY   : 'Daily',
                     SNAPSHOT_WEEKLY  : 'Weekly',
                     SNAPSHOT_MONTHLY : 'Monthly'}
    
    return snapshot_map[snapshot_type]

def get_vm_snapshots(vm_id):
    vm_snapshots_list = []
    for snapshot in db(db.snapshot.vm_id == vm_id).select():

        snapshot_dict = {'id' : snapshot.id}
        
        snapshot_dict['type'] = get_snapshot_type(snapshot.type)
        snapshot_dict['name'] = snapshot.snapshot_name
        if snapshot.type == SNAPSHOT_USER:
            snapshot_dict['delete'] = A(IMG(_src=URL('static','images/delete-snapshot.gif'), _style='height:20px;weight:20px'),
                                           _href=URL(r=request, f='delete_snapshot', args= [vm_id, snapshot.id]),
                                           _title = "Delete this snapshot",    _alt = "Delete this snapshot")
        else:
            snapshot_dict['delete'] = ' '
        snapshot_dict['revert'] = A(IMG(_src=URL('static','images/revertTosnapshot.png'), _style='height:20px;weight:20px'),
                                       _href=URL(r=request, f='revert_to_snapshot', args= [vm_id, snapshot.id]),
                                       _title = "Revert to this snapshot", _alt = "Revert to this snapshot")
        vm_snapshots_list.append(snapshot_dict)
    return vm_snapshots_list

def get_faculty_info(faculty_id):
    faculty_info = db(db.user.id==faculty_id).select()
    if not faculty_info:
        return None
    return faculty_info.first()


def mark_required(table):
    
    marker = SPAN('*', _class='fld_required')
    for field in table:
        required = False
        if field.notnull:
            required = True
        elif field.requires:
            required=isinstance(field.requires,(IS_IN_SET, IS_IPV4))
        if required:
            _label = field.label
            field.label = SPAN(_label, ' ', marker, ' ')

def is_moderator():
    return (ADMIN in auth.user_groups.values())

def is_faculty():
    return (FACULTY in auth.user_groups.values())
    
def is_orgadmin():
    return (ORGADMIN in auth.user_groups.values())

def is_vm_user():
    return not(is_moderator() or is_orgadmin() or is_faculty())
