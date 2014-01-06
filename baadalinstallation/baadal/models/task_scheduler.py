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

def markFailedTask(task_id, task_event_id, error_msg):
    #For failed task, change task status to Failed, it can be marked for retry by admin later
    db.task_queue[task_id] = dict(status=TASK_QUEUE_STATUS_FAILED)
    #Update task event with the error message
    db.task_queue_event[task_event_id] = dict(status=TASK_QUEUE_STATUS_FAILED, error=error_msg)


def processTaskQueue(task_event_id):

    task_event = db.task_queue_event[task_event_id]
    task_process = db.task_queue[task_event.task_id] 
    try:
        #Update attention_time for task in the event table
        db.task_queue_event[task_event_id] = dict(attention_time=get_datetime())
        #Call the corresponding function from vm_helper
        ret = task[task_process.task_type](task_process.parameters)
        #On return, update the status and end time in task event table
        db.task_queue_event[task_event_id] = dict(status=ret[0], end_time=get_datetime())
        
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            markFailedTask(task_process.id, task_event_id, ret[1])
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
        logger.debug('Task done')
    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        markFailedTask(task_process.id, task_event_id, msg)
        
def processCloneTask(task_event_id, vm_id):
    try:
        task_event = db.task_queue_event[task_event_id]
        task_process = db.task_queue[task_event.task_id] 
        # Update attention time for first clone task
        db((db.task_queue_event.id==task_event_id) & (db.task_queue_event.attention_time == None)).update(attention_time=get_datetime())
        
        ret = task[TASK_TYPE_CLONE_VM](vm_id)
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            db.vm_data[vm_id] = dict(status = -1)
        
#       task_queue = db.task_queue[task_id]
        clone_vm_list = task_event.parameters['clone_vm_id']
        # Remove VM id from the list. This is to check if all the clones for the task are processed.
        clone_vm_list.remove(vm_id)
        
        # Find the status of all clone tasks combined
        current_status = task_event.status
        if current_status == None:
            current_status = ret[0]
        elif current_status != TASK_QUEUE_STATUS_PARTIAL_SUCCESS:
            if ret[0] != current_status:
                current_status = TASK_QUEUE_STATUS_PARTIAL_SUCCESS

        if not clone_vm_list: #All Clones are processed
            db.task_queue_event[task_event_id] = dict(status=ret[0], end_time=get_datetime())
            del db.request_queue[task_process.parameters['request_id']]
            if current_status == TASK_QUEUE_STATUS_FAILED:
                markFailedTask(task_process.id, task_event_id, ret[1])
            else:
                del db.task_queue[task_process.id]
        else:
            params = task_event.parameters
            params.update({'clone_vm_id' : clone_vm_list})
            db.task_queue_event[task_event_id] = dict(parameters=params, status=current_status)
        db.commit()

    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)

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
                        period = 7 * DAYS, # every 24h
                        timeout = 5 * MINUTES)
    
