# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    import logger
###################################################################################
import sys, traceback
from helper import get_datetime
from vm_helper import install, start, suspend, resume, destroy, delete, migrate, snapshot, revert, delete_snapshot, edit_vm_config, clone

task = {TASK_TYPE_CREATE_VM          :    install,
        TASK_TYPE_START_VM           :    start,
        TASK_TYPE_SUSPEND_VM         :    suspend,
        TASK_TYPE_RESUME_VM          :    resume,
        TASK_TYPE_DESTROY_VM         :    destroy,
        TASK_TYPE_DELETE_VM          :    delete,
        TASK_TYPE_MIGRATE_VM         :    migrate,
        TASK_TYPE_SNAPSHOT_VM        :    snapshot,
        TASK_TYPE_REVERT_TO_SNAPSHOT :    revert,
        TASK_TYPE_DELETE_SNAPSHOT    :    delete_snapshot,
        TASK_TYPE_EDITCONFIG_VM      :    edit_vm_config,
        TASK_TYPE_CLONE_VM           :    clone
       }


def processTaskQueue(task_id):
    try:
        task_process = db.task_queue[task_id] 
        
        task_queue_query = db(db.task_queue.id==task_id)
        task_event_query = db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.status != TASK_QUEUE_STATUS_IGNORE))
        #Update attention_time for task in the event table
        task_event_query.update(attention_time=get_datetime())
        #Call the corresponding function from vm_helper
        ret = task[task_process.task_type](task_process.parameters)
        #On return, update the status and end time in task event table
        task_event_query.update(status=ret[0], end_time=get_datetime())
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            #For failed task, change task status to Failed, it can be marked for retry by admin later
            task_queue_query.update(status=TASK_QUEUE_STATUS_FAILED)
            #Update task event with the error message
            task_event_query.update(error=ret[1],status=TASK_QUEUE_STATUS_FAILED)
            db.vm_data[task_process.vm_id] = dict(status = -1)
        elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
            # For successful task, delete the task from queue 
            task_queue_query.delete()
        db.commit()
        logger.debug('Task done')
    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        
def processCloneTask(task_id, vm_id):
    try:
        task_queue_query = db(db.task_queue.id==task_id)
        task_event_query = db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.status != TASK_QUEUE_STATUS_IGNORE))
        # Update attention time for first clone task
        db((db.task_queue_event.task_id==task_id) & (db.task_queue_event.attention_time == None)).update(attention_time=get_datetime())
        
        ret = task[TASK_TYPE_CLONE_VM](vm_id)
        if ret[0] == TASK_QUEUE_STATUS_FAILED:
            db.vm_data[vm_id] = dict(status = -1)
        
        task_process = task_queue_query.select().first()
        clone_vm_list = task_process.parameters['clone_vm_id']
        # Remove VM id from the list. Tthis is to check if all the clones for the task are processed.
        clone_vm_list.remove(vm_id)
        
        if not clone_vm_list: #All Clones are processed
            task_event_query.update(status=ret[0], end_time=get_datetime())
            if ret[0] == TASK_QUEUE_STATUS_FAILED:
                task_event_query.update(error=ret[1])
            elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
                task_queue_query.delete()
        else:
            params = {'clone_vm_id' : clone_vm_list}
            db(db.task_queue.id==task_id).update(parameters=params)
        db.commit()

    except:
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)

from gluon.scheduler import Scheduler
vm_scheduler = Scheduler(db, tasks=dict(vm_task=processTaskQueue, clone_task=processCloneTask))
