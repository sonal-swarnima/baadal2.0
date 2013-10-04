# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    import logger
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

def markFailedTask(task_id, error_msg, vm_id):
    #For failed task, change task status to Failed, it can be marked for retry by admin later
    db(db.task_queue.id==task_id).update(status=TASK_QUEUE_STATUS_FAILED)
    #Update task event with the error message
    db((db.task_queue_event.task_id==task_id) & 
       (db.task_queue_event.status != TASK_QUEUE_STATUS_IGNORE)).update(error=error_msg,status=TASK_QUEUE_STATUS_FAILED)


def processTaskQueue(task_id):

    task_process = db.task_queue[task_id] 
    try:
        task_event_query = db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.status != TASK_QUEUE_STATUS_IGNORE))
        #Update attention_time for task in the event table
        task_event_query.update(attention_time=get_datetime())
        #Call the corresponding function from vm_helper
        ret = task[task_process.task_type](task_process.parameters)
        #On return, update the status and end time in task event table
        task_event_query.update(status=ret[0], end_time=get_datetime())
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            markFailedTask(task_id, ret[1], task_process.vm_id)
            if task_process.task_type == TASK_TYPE_CREATE_VM:
                db.vm_data[task_process.vm_id] = dict(status = -1)

        elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
            # For successful task, delete the task from queue 
            db(db.task_queue.id==task_id).delete()
        db.commit()
        logger.debug('Task done')
    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        markFailedTask(task_id, msg, task_process.vm_id)
        
def processCloneTask(task_id, vm_id):
    try:
        task_event_query = db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.status != TASK_QUEUE_STATUS_IGNORE))
        # Update attention time for first clone task
        db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.attention_time == None)).update(attention_time=get_datetime())
        
        ret = task[TASK_TYPE_CLONE_VM](vm_id)
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            db.vm_data[vm_id] = dict(status = -1)
        
        clone_vm_list = db.task_queue[task_id].parameters['clone_vm_id']
        # Remove VM id from the list. This is to check if all the clones for the task are processed.
        clone_vm_list.remove(vm_id)
        
        task_event = task_event_query.select().first()
        # Find the status of all clone tasks combined
        current_status = task_event.status
        if current_status == None:
            current_status = ret[0]
        elif current_status != TASK_QUEUE_STATUS_PARTIAL_SUCCESS:
            if ret[0] != current_status:
                current_status = TASK_QUEUE_STATUS_PARTIAL_SUCCESS

        if not clone_vm_list: #All Clones are processed
            task_event_query.update(status=current_status, end_time=get_datetime())
            if current_status == TASK_QUEUE_STATUS_FAILED:
                task_event_query.update(error=ret[1])
            else:
                del db.task_queue[task_id]
        else:
            params = {'clone_vm_id' : clone_vm_list}
            db(db.task_queue.id==task_id).update(parameters=params, status=current_status)
        db.commit()

    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)

from gluon.scheduler import Scheduler
vm_scheduler = Scheduler(db, tasks=dict(vm_task=processTaskQueue, clone_task=processCloneTask))
