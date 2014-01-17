# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db,request
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import sys, traceback
from helper import get_datetime
from vm_helper import install, start, suspend, resume, destroy, delete, migrate, snapshot, revert, delete_snapshot, edit_vm_config, clone, attach_extra_disk

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


def processTaskQueue(task_event_id):

    task_event = db.task_queue_event[task_event_id]
    task_process = db.task_queue[task_event.task_id] 
    try:
        #Update attention_time for task in the event table
        task_event.update_record(attention_time=get_datetime())
        #Call the corresponding function from vm_helper
        ret = task[task_process.task_type](task_process.parameters)
        #On return, update the status and end time in task event table
        task_event.update_record(status=ret[0], message=ret[1], end_time=get_datetime())
        
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
#             markFailedTask(task_process.id, task_event_id, ret[1])
            task_process.update_record(status=TASK_QUEUE_STATUS_FAILED)
            if task_process.task_type == TASK_TYPE_CREATE_VM:
                db.vm_data[task_process.vm_id] = dict(status = VM_STATUS_UNKNOWN)
            if 'request_id' in task_process.parameters:
                db.request_queue[task_process.parameters['request_id']] = dict(status = REQ_STATUS_FAILED)

        elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
            # For successful task, delete the task from queue 
            del db.task_queue[task_process.id]
            if 'request_id' in task_process.parameters:
                del db.request_queue[task_process.parameters['request_id']]
        
        db.commit()
    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        task_event.update_record(status=TASK_QUEUE_STATUS_FAILED, message=msg)
        
def processCloneTask(task_event_id, vm_id):

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
        if task_event.status != None and task_event.status != current_status:
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
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        vm_data = db.vm_data[vm_id]
        message = message + '\n' + vm_data.vm_name + ': ' + msg
        task_event.update_record(status=TASK_QUEUE_STATUS_FAILED, message=message)


# Handles periodic snapshot task
def processSnapshotVM(snapshot_type):
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    for vm in vms:
        params={'snapshot_type':snapshot_type}
        add_vm_task_to_queue(vm.id,TASK_TYPE_SNAPSHOT_VM, params)
        db.commit()
        

from gluon.scheduler import Scheduler
vm_scheduler = Scheduler(db, tasks=dict(vm_task=processTaskQueue, 
                                        clone_task=processCloneTask,
                                        snapshot_vm=processSnapshotVM))

ss_query = (db.scheduler_task.task_name == 'snapshot_vm') & (db.scheduler_task.status=='QUEUED')
res = vm_scheduler.task_status(ref=ss_query)
# If snapshot task is not queued already, create task. This is a one-time job.
if not res:
    vm_scheduler.queue_task('snapshot_vm', 
                        pvars = dict(snapshot_type = SNAPSHOT_DAILY),
                        repeats = 0, # run indefinitely
                        start_time = request.now, 
                        period = 24 * HOURS, # every 24h
                        timeout = 5 * MINUTES)
    
    vm_scheduler.queue_task('snapshot_vm', 
                        pvars = dict(snapshot_type = SNAPSHOT_WEEKLY),
                        repeats = 0, # run indefinitely
                        start_time = request.now, 
                        period = 7 * DAYS, # every 7 days
                        timeout = 5 * MINUTES)
    
    vm_scheduler.queue_task('snapshot_vm', 
                        pvars = dict(snapshot_type = SNAPSHOT_MONTHLY),
                        repeats = 0, # run indefinitely
                        start_time = request.now, 
                        period = 30 * DAYS, # every 30 days
                        timeout = 5 * MINUTES)
    
