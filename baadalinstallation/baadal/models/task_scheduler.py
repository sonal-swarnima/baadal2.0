# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    import logger
###################################################################################
import time,sys,traceback
from helper import get_datetime
from vm_helper import install,start,suspend,resume,destroy,delete

task = {TASK_TYPE_CREATE_VM    :   install,
        TASK_TYPE_START_VM     :   start,
        TASK_TYPE_SUSPEND_VM     :   suspend,
        TASK_TYPE_RESUME_VM     :   resume,
        TASK_TYPE_DESTROY_VM     :   destroy,
        TASK_TYPE_DELETE_VM     :   delete
}

def processTaskQueue(task_id):
    db.commit()
    try :
        processes=db(db.task_queue.id==task_id).select()
        if(len(processes) >= 1):
            try:
                process=processes.first() 
                #Update attention_time for task in the event table
                db(db.task_queue_event.task_id==task_id).update(attention_time=get_datetime())
                #Call the corresponding function from vm_helper
                ret = task[process['task_type']](process['vm_id'])
                #On return, update the status and end time in task event table
                db(db.task_queue_event.task_id==task_id).update(status=ret[0], end_time=get_datetime())
                if ret[0] == TASK_QUEUE_STATUS_FAILED:
                    #For failed task, change task status to RETRY
                    db(db.task_queue.id==task_id).update(status=TASK_QUEUE_STATUS_RETRY)
                    #Update task event with the error message
                    db(db.task_queue_event.task_id==task_id).update(error=ret[1],status=TASK_QUEUE_STATUS_FAILED)
                elif ret[0] == TASK_QUEUE_STATUS_SUCCESS:
                    # For successful task, delete the task from queue 
                    db(db.task_queue.id==task_id).delete()
                db.commit()
                logger.debug("Task done")
            except Exception as e:
                logger.error(e)
                etype, value, tb = sys.exc_info()
                msg=''.join(traceback.format_exception(etype, value, tb, 10))
                db(db.task_queue.id==task_id).update(status=-1)
    except :
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        time.sleep(10)

from gluon.scheduler import Scheduler
scheduler = Scheduler(db, tasks=dict(vm_task=processTaskQueue))

