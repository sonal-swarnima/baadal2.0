# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db,request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_datetime, log_exception, logger
from vm_helper import install, start, suspend, resume, destroy, delete, migrate, snapshot, revert, delete_snapshot, edit_vm_config, clone, attach_extra_disk
from host_helper import host_status_sanity_check
# from vm_utilization import update_rrd

UUID_SNAPSHOT_DAILY = 'scheduler-uuid-snapshot-daily'
UUID_SNAPSHOT_WEEKLY = 'scheduler-uuid-snapshot-weekly'
UUID_SNAPSHOT_MONTHLY = 'scheduler-uuid-snapshot-monthly'
UUID_VM_SANITY_CHECK = 'scheduler-uuid-vm-sanity-check'
UUID_HOST_SANITY_CHECK = 'scheduler-uuid-host-sanity-check'
UUID_VM_UTIL_RRD = 'scheduler-uuid-vm-util-rrd'

task = {TASK_TYPE_CREATE_VM               :    install,
        TASK_TYPE_START_VM                :    start,
        TASK_TYPE_STOP_VM                 :    destroy,
        TASK_TYPE_SUSPEND_VM              :    suspend,
        TASK_TYPE_RESUME_VM               :    resume,
        TASK_TYPE_DESTROY_VM              :    destroy,
        TASK_TYPE_DELETE_VM               :    delete,
        TASK_TYPE_MIGRATE_VM              :    migrate,
        TASK_TYPE_SNAPSHOT_VM             :    snapshot,
        TASK_TYPE_REVERT_TO_SNAPSHOT      :    revert,
        TASK_TYPE_DELETE_SNAPSHOT         :    delete_snapshot,
        TASK_TYPE_EDITCONFIG_VM           :    edit_vm_config,
        TASK_TYPE_CLONE_VM                :    clone,
        TASK_TYPE_ATTACH_DISK             :    attach_extra_disk
       }

def send_task_complete_mail(task_event):
    
    vm_users = []
    if task_event.vm_id != None:
        for user in db(db.user_vm_map.vm_id == task_event.vm_id).select(db.user_vm_map.user_id):
            vm_users.append(user['user_id'])
    else:
        vm_users.append(task_event.requester_id)
    send_email_to_vm_user(task_event.task_type, task_event.vm_name, task_event.start_time, vm_users)
    
#Logs action data into vm_event_log table
def log_vm_event(old_vm_data, task_queue_data):

    vm_data = db.vm_data[old_vm_data.id]
    if task_queue_data.task_type in (TASK_TYPE_START_VM, 
                                     TASK_TYPE_STOP_VM, 
                                     TASK_TYPE_SUSPEND_VM, 
                                     TASK_TYPE_RESUME_VM, 
                                     TASK_TYPE_DESTROY_VM):
        db.vm_event_log.insert(vm_id = vm_data.id,
                               attribute = 'VM Status',
                               requester_id = task_queue_data.requester_id,
                               old_value = get_vm_status(old_vm_data.status),
                               new_value = get_vm_status(vm_data.status))
    elif task_queue_data.task_type == TASK_TYPE_EDITCONFIG_VM:
        parameters = task_queue_data.parameters
        data_list = []
        if 'vcpus' in parameters:
            vm_log = {'vm_id' : vm_data.id, 
                      'requester_id' : task_queue_data.requester_id,
                      'attribute' : 'Edit CPU',
                      'old_value' : str(old_vm_data.vCPU) + ' CPU',
                      'new_value' : str(vm_data.vCPU) + ' CPU'}
            data_list.append(vm_log)
        if 'ram' in parameters:
            vm_log = {'vm_id' : vm_data.id, 
                      'requester_id' : task_queue_data.requester_id,
                      'attribute' : 'Edit RAM',
                      'old_value' : str(old_vm_data.RAM) + ' MB',
                      'new_value' : str(vm_data.RAM) + ' MB'}
            data_list.append(vm_log)
        if 'public_ip' in parameters:
            vm_log = {'vm_id' : vm_data.id, 
                      'requester_id' : task_queue_data.requester_id,
                      'attribute' : 'Public IP',
                      'old_value' : old_vm_data.public_ip,
                      'new_value' : vm_data.public_ip}
            data_list.append(vm_log)
        if 'security_domain' in parameters:
            vm_log = {'vm_id' : vm_data.id, 
                      'requester_id' : task_queue_data.requester_id,
                      'attribute' : 'Security Domain',
                      'old_value' : old_vm_data.security_domain.name,
                      'new_value' : vm_data.security_domain.name}
            data_list.append(vm_log)
            vm_log = {'vm_id' : vm_data.id, 
                      'requester_id' : task_queue_data.requester_id,
                      'attribute' : 'Private IP',
                      'old_value' : old_vm_data.private_ip,
                      'new_value' : vm_data.private_ip}
            data_list.append(vm_log)
            
        db.vm_event_log.bulk_insert(data_list)        

# Invoked when scheduler runs task of type 'vm_task'
def process_task_queue(task_event_id):

    logger.debug("Processing task: " + str(task_event_id))
    task_event_data = db.task_queue_event[task_event_id]
    task_queue_data = db.task_queue[task_event_data.task_id]
    vm_data = db.vm_data[task_event_data.vm_id]
    try:
        #Update attention_time for task in the event table
        task_event_data.update_record(attention_time=get_datetime())
        #Call the corresponding function from vm_helper
        ret = task[task_queue_data.task_type](task_queue_data.parameters)
        #On return, update the status and end time in task event table
        task_event_data.update_record(status=ret[0], message=ret[1], end_time=get_datetime())
        
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
#             markFailedTask(task_process.id, task_event_id, ret[1])
            task_queue_data.update_record(status=TASK_QUEUE_STATUS_FAILED)
            if task_queue_data.task_type == TASK_TYPE_CREATE_VM:
                db.vm_data[task_queue_data.vm_id] = dict(status = VM_STATUS_UNKNOWN)
            if 'request_id' in task_queue_data.parameters:
                db.request_queue[task_queue_data.parameters['request_id']] = dict(status = REQ_STATUS_FAILED)

        elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
            # Create log event for the task
            log_vm_event(vm_data, task_queue_data)
            # For successful task, delete the task from queue 
            if db.task_queue[task_queue_data.id]:
                del db.task_queue[task_queue_data.id]
            if 'request_id' in task_queue_data.parameters:
                del db.request_queue[task_queue_data.parameters['request_id']]
            
            send_task_complete_mail(task_event_data)
        
        db.commit()
    except:
        msg = log_exception()
        task_event_data.update_record(status=TASK_QUEUE_STATUS_FAILED, message=msg)
        
# Invoked when scheduler runs task of type 'clone_task'
def process_clone_task(task_event_id, vm_id):

    logger.debug("Processing clone task: " + str(task_event_id))
    task_event = db.task_queue_event[task_event_id]
    task_queue = db.task_queue[task_event.task_id]
    message = task_event.message if task_event.message != None else ''
    try:
        # Update attention time for first clone task
        if task_event.attention_time == None:
            task_event.update_record(attention_time=get_datetime())
        
        ret = task[TASK_TYPE_CLONE_VM](vm_id)

        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            vm_data = db.vm_data[vm_id]
            message = message + '\n' + vm_data.vm_name + ': ' + ret[1]
            vm_data.update_record(status = VM_STATUS_UNKNOWN)
        elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
            params = task_queue.parameters
            # Delete successful vms from list. So, that in case of retry, only failed requests are retried.
            params['clone_vm_id'].remove(vm_id)
            task_queue.update_record(parameters=params)
        
        clone_vm_list = task_event.parameters['clone_vm_id']
        # Remove VM id from the list. This is to check if all the clones for the task are processed.
        clone_vm_list.remove(vm_id)
        
        # Find the status of all clone tasks combined
        current_status = ret[0]
        if task_event.status != TASK_QUEUE_STATUS_PENDING and task_event.status != current_status:
            current_status = TASK_QUEUE_STATUS_PARTIAL_SUCCESS
        
        if not clone_vm_list: #All Clones are processed
            if current_status == TASK_QUEUE_STATUS_SUCCESS:
                del db.request_queue[task_queue.parameters['request_id']]
                del db.task_queue[task_queue.id]
            else:
                if 'request_id' in task_queue.parameters:
                    db.request_queue[task_queue.parameters['request_id']] = dict(status = REQ_STATUS_FAILED)
                task_queue.update_record(status=current_status)
            task_event.update_record(status=current_status, message=message, end_time=get_datetime())
        else:
            task_event.update_record(parameters={'clone_vm_id' : clone_vm_list}, status=current_status, message=message)
        
        db.commit()

    except:
        msg = log_exception()
        vm_data = db.vm_data[vm_id]
        message = message + '\n' + vm_data.vm_name + ': ' + msg
        task_event.update_record(status=TASK_QUEUE_STATUS_FAILED, message=message)


# Handles snapshot task
# Invoked when scheduler runs task of type 'snapshot_vm'
def process_snapshot_vm(snapshot_type, vm_id = None):

    logger.debug("Processing rolling snapshot task: " + str(snapshot_type))

    if snapshot_type == SNAPSHOT_SYSTEM:
        params={'snapshot_type' : SNAPSHOT_SYSTEM, 'vm_id' : vm_id}
        task[TASK_TYPE_SNAPSHOT_VM](params)
    else:    
        vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
        for vm_data in vms:
            params={'snapshot_type' : SNAPSHOT_SYSTEM, 'vm_id' : vm_data.id}
            vm_scheduler.queue_task('snapshot_vm', pvars = params, start_time = request.now, timeout = 30 * MINUTES)
          
# Handles periodic VM sanity check
# Invoked when scheduler runs task of type 'vm_sanity'
def vm_sanity_check():

    logger.info("Starting VM Sanity Check")
    check_vm_sanity()

# Handles periodic Host sanity check
# Called when scheduler runs task of type 'host_sanity'
def host_sanity_check():

    logger.info("Starting Host Sanity Check")
    host_status_sanity_check()

    
# Defining scheduler tasks
from gluon.scheduler import Scheduler
vm_scheduler = Scheduler(db, tasks=dict(vm_task=process_task_queue, 
                                        clone_task=process_clone_task,
                                        snapshot_vm=process_snapshot_vm,
                                        vm_sanity=vm_sanity_check,
                                        host_sanity=host_sanity_check))

midnight_time = request.now.replace(hour=23, minute=59, second=59)

vm_scheduler.queue_task('snapshot_vm', 
                    pvars = dict(snapshot_type = SNAPSHOT_DAILY),
                    repeats = 0, # run indefinitely
                    start_time = midnight_time, 
                    period = 24 * HOURS, # every 24h
                    timeout = 5 * MINUTES,
                    uuid = UUID_SNAPSHOT_DAILY)

vm_scheduler.queue_task('snapshot_vm', 
                    pvars = dict(snapshot_type = SNAPSHOT_WEEKLY),
                    repeats = 0, # run indefinitely
                    start_time = midnight_time, 
                    period = 7 * DAYS, # every 7 days
                    timeout = 5 * MINUTES,
                    uuid = UUID_SNAPSHOT_WEEKLY)

vm_scheduler.queue_task('snapshot_vm', 
                    pvars = dict(snapshot_type = SNAPSHOT_MONTHLY),
                    repeats = 0, # run indefinitely
                    start_time = midnight_time, 
                    period = 30 * DAYS, # every 30 days
                    timeout = 5 * MINUTES,
                    uuid = UUID_SNAPSHOT_MONTHLY)

vm_scheduler.queue_task('vm_sanity', 
                    repeats = 0, # run indefinitely
                    start_time = request.now, 
                    period = 30 * MINUTES, # every 30 minutes
                    timeout = 5 * MINUTES,
                    uuid = UUID_VM_SANITY_CHECK)

vm_scheduler.queue_task('host_sanity', 
                    repeats = 0, # run indefinitely
                    start_time = request.now, 
                    period = 10 * MINUTES, # every 10 minutes
                    timeout = 5 * MINUTES,
                    uuid = UUID_HOST_SANITY_CHECK)

# vm_scheduler.queue_task('vm_util_rrd', 
#                     repeats = 0, # run indefinitely
#                     start_time = request.now, 
#                     period = 5 * MINUTES, # every 5 minutes
#                     timeout = 5 * MINUTES,
#                     uuid = UUID_VM_UTIL_RRD)

