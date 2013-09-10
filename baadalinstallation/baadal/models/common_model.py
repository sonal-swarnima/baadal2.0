# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db,URL,session,redirect,HTTP,FORM,INPUT,H3,IS_INT_IN_RANGE,A,B,SPAN,IMG,request,SQLFORM,DIV
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import os
import shutil
import time

import rrdtool

from helper import get_fullname, get_datetime, is_moderator, is_orgadmin, is_faculty, get_constant

def get_vm_status(iStatus):
    vm_status_map = {
            VM_STATUS_REQUESTED   :    'Requested',
            VM_STATUS_REJECTED    :    'Rejected',
            VM_STATUS_VERIFIED    :    'Verified',
            VM_STATUS_APPROVED    :    'Approved',
            VM_STATUS_RUNNING     :    'Running',
            VM_STATUS_SUSPENDED   :    'Paused',
            VM_STATUS_SHUTDOWN    :    'Shutdown'
        }
    return vm_status_map[iStatus]


def get_hosted_vm_grid(vm_query):
    
    db.vm_data.id.readable=False
    
    fields =(db.vm_data.id,
             db.vm_data.vm_name, 
             db.vm_data.owner_id, 
             db.host.host_ip, 
             db.vm_data.private_ip, 
             db.vm_data.public_ip, 
             db.vm_data.RAM, 
             db.vm_data.vCPU,  
             db.vm_data.status)
    default_sort_order=[~db.vm_data.start_time]
    
    links = [lambda row: A(IMG(_src=URL('static','images/settings.png'), _height=18, _width=18),
            _href=URL(r=request, c='user',f='settings', args=[row.vm_data.id]), 
            _title="Settings", 
            _alt="Settings")]
    
    form = SQLFORM.grid(query=vm_query, fields=fields, orderby=default_sort_order, links = links,
                        paginate=ITEMS_PER_PAGE, csv=False, searchable=False, deletable=False, editable=False,
                        details=False, create=False, showbuttontext=False)
    return form

def public_ip_icon(public_ip):
    if (public_ip == PUBLIC_IP_NOT_ASSIGNED):
        return SPAN(_class='icon-ok')
    else:
        return SPAN(_class='icon-remove')
    
def approve_reject_icon(status, vm_id):
    if status == VM_STATUS_APPROVED:
        return A(IMG(_src=URL('static','images/vm_add.png'), _height=18, _width=18),
            _href='#', 
            _title="Installation in Progress", 
            _alt="Installation in Progress")
    else:
        return DIV(A(IMG(_src=URL('static','images/accept.png'), _height=18, _width=18),
            _href=URL(r=request, c='admin',f='approve_request', args=[vm_id]), 
            _title="Approve Request", 
            _alt="Approve Request", _onclick='tab_refresh()'),
             A(IMG(_src=URL('static','images/reject.png'), _height=18, _width=18),
            _href=URL(r=request, c='admin',f='reject_request', args=[vm_id]), 
            _title="Reject Request", 
            _alt="Reject Request", _onclick='tab_refresh()'))

def get_pending_vm_grid(vm_query):

    db.vm_data.id.readable=False
    db.vm_data.public_ip.readable=False
    fields =(db.vm_data.id,
             db.vm_data.vm_name, 
             db.vm_data.owner_id, 
             db.vm_data.requester_id, 
             db.vm_data.RAM, 
             db.vm_data.vCPU,  
             db.vm_data.status,
             db.vm_data.public_ip)
    default_sort_order=[~db.vm_data.id]
    
    links = [dict(header='Public IP', body=lambda row: public_ip_icon(row.public_ip)), 
             lambda row: approve_reject_icon(row.status, row.id)]
    
    form = SQLFORM.grid(query=vm_query, fields=fields, orderby=default_sort_order, links = links,
                        paginate=ITEMS_PER_PAGE, csv=False, searchable=False, deletable=False, editable=False,
                        details=False, create=False, showbuttontext=False)
    return form


def get_hosted_vm_list(vms):
    vmlist = []
    for vm in vms:
        total_cost = add_to_cost(vm.id)
        element = {'id' : vm.id,
                   'name' : vm.vm_name,
                   'public_ip' : vm.public_ip, 
                   'private_ip' : vm.private_ip, 
                   'owner' : get_full_name(vm.owner_id), 
                   'hostip' : vm.host_id.host_ip,
                   'RAM' : vm.RAM,
                   'vcpus' : vm.vCPU,
                   'status' : get_vm_status(vm.status),
                   'cost' : total_cost}
        vmlist.append(element)
    return vmlist


def get_pending_vm_list(vms):
    vmlist = []
    for vm in vms:
        request_type = 'Install'
        if vm.parameters and vm.parameters['clone_count']:
            request_type = 'Clone[' + str(vm.parameters['clone_count']) + ']'

        element = {'id' : vm.id,
                   'vm_name' : vm.vm_name, 
                   'faculty_name' : get_fullname(vm.owner_id), 
                   'requester_name' : get_fullname(vm.requester_id), 
                   'RAM' : vm.RAM, 
                   'vCPUs' : vm.vCPU, 
                   'HDD' : vm.HDD, 
                   'public_ip' : (vm.public_ip != PUBLIC_IP_NOT_ASSIGNED), 
                   'status' : vm.status,
                   'request_type' : request_type}
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
    vm_info = db((db.vm_data.id == _vm_id) & (db.vm_data.locked == False)).select()
    if not vm_info:
        return None

    logger.info(vm_info)
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
    

def add_vm_task_to_queue(vm_id, task_type, params = {}):

    params['vm_id'] = vm_id
        
    db.task_queue.insert(task_type=task_type,
                         vm_id=vm_id, 
                         parameters=params, 
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
        if (auth.is_logged_in()) & (is_faculty() | is_orgadmin() | is_moderator()):
            return fn(*args, **kwargs)
        else:
            session.flash = "You don't have faculty privileges"
            redirect(URL(c='default', f='index'))
    return decorator    

def get_pending_approval_count():
    
    users_of_same_org = db(auth.user.organisation_id == db.user.organisation_id)._select(db.user.id)
    vm_count = db((db.vm_data.requester_id.belongs(users_of_same_org)) & (db.vm_data.status == VM_STATUS_VERIFIED)).count()

    return vm_count
             
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

        if is_moderator():

            if (db(db.host.id > 0).count() >= 2):

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
                _href=URL(r=request,c='user', f='clone_vm', args=vm_id), _title="Request Clone vm", _alt="Request Clone vm"))
                               
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

def create_graph(vm_name, graph_type, rrd_file_path, graph_period):

    logger.debug(vm_name+" : "+graph_type+" : "+rrd_file_path+" : "+graph_period)
    rrd_file = vm_name + '.rrd'       

    shutil.copyfile(rrd_file_path, rrd_file)
    graph_file = vm_name + "_" + graph_type + ".png"

    start_time = None
    grid = None
    ret = None
    consolidation = 'AVERAGE'
    ds = ds1 = ds2 = None
    line = line1 = line2 = None
    vdef1 = vdef2 = None
    
    if graph_period == 'hour':
        start_time = 'now - ' + str(24*60*60)
        grid = 'HOUR:1:HOUR:1:HOUR:1:0:%k'
        consolidation = 'MIN'
    elif graph_period == 'day':
        start_time = '-1w'
        grid = 'DAY:1:DAY:1:DAY:1:86400:%a'
    elif graph_period == 'month':
        start_time = '-1y'
        grid = 'MONTH:1:MONTH:1:MONTH:1:2592000:%b'
    elif graph_period == 'week':
        start_time = '-1m'
        grid = 'WEEK:1:WEEK:1:WEEK:1:604800:Week %W'
    elif graph_period == 'year':
        start_time = '-5y'
        grid = 'YEAR:1:YEAR:1:YEAR:1:31536000:%Y'
  
    if ((graph_type == 'ram') or (graph_type == 'cpu')):

        if graph_type == 'ram':
            ds = 'DEF:ram=' + vm_name + '.rrd:memory:' + consolidation
            line = 'LINE1:ram#0000FF:Memory'
        elif graph_type == 'cpu':
            ds = 'DEF:cpu=' + vm_name + '.rrd:cpus:' + consolidation
            line = 'LINE1:cpu#0000FF:CPU'
                
        rrdtool.graph(graph_file, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', 'VM Name: ' + vm_name, '--x-grid', grid, ds, line)

    else:

        if graph_type == 'nw':
            ds1 = 'DEF:nwr=' + vm_name + '.rrd:nwr:' + consolidation
            ds2 = 'DEF:nww=' + vm_name + '.rrd:nww:' + consolidation
            line1 = 'LINE1:nwr#0000FF:Receive'
            line2 = 'LINE2:nww#FF7410:Transmit'
            vdef1 = "VDEF:nwread=nwr,read"
            vdef2 = "VDEF:nwwrite=nww"

        elif graph_type == 'disk':
            ds1 = 'DEF:diskr=' + vm_name + '.rrd:diskr:' + consolidation
            ds2 = 'DEF:diskw=' + vm_name + '.rrd:diskw:' + consolidation
            line1 = 'LINE1:diskr#0000FF:DiskRead'
            line2 = 'LINE2:diskw#FF7410:DiskWrite'
            vdef1 = "VDEF:diskread=diskr"
            vdef2 = "VDEF:diskwrite=diskw"

        rrdtool.graph(graph_file, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', 'VM Name: ' + vm_name, '--x-grid', grid, ds1, ds2, line1, line2)

    shutil.copy2(graph_file, get_constant('graph_file_dir'))

    if os.path.exists(get_constant('graph_file_dir') + os.sep + graph_file):
        return True
    else:
        return False
    
def get_performance_graph(graph_type, vm, graph_period):

    error = None
    img = IMG(_src = URL("static" , "images/no_graph.jpg") , _style = "height:100px")

    try:
        rrd_file = get_constant("vmfiles_path") + os.sep + get_constant("vm_rrds_dir") + os.sep + vm + ".rrd"
  
        if os.path.exists(rrd_file):
            if create_graph(vm, graph_type, rrd_file, graph_period):   
               img_pos = "vm_graphs/" + vm + "_" + graph_type + ".png"
               img = IMG(_src = URL("static", img_pos), _style = "height:100%")
               logger.info("Graph created successfully")
            else:
               logger.warn("Unable to create graph from rrd file!!!")
               error = H3("Unable to create graph from rrd file")
        else:
            logger.warn("VMs RRD File Unavailable!!!")
            error = "VMs RRD File Unavailable!!!"
		
    except: 

        import sys, traceback
        etype, value, tb = sys.exc_info()
        logger.warn("Error occured while creating graph.")
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))           
        logger.error(msg)           
        error = msg

    finally:
        if (is_moderator() and (error != None)):
            return H3(error)
        else:
            logger.info("Returning image.")
            return img





