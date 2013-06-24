# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    import logger
###################################################################################
from vm_helper import install,start,suspend,resume,destroy,delete

task = {TASK_TYPE_CREATE_VM    :   install,
        TASK_TYPE_START_VM     :   start,
        TASK_TYPE_SUSPEND_VM     :   suspend,
        TASK_TYPE_RESUME_VM     :   resume,
        TASK_TYPE_DESTROY_VM     :   destroy,
        TASK_TYPE_DELETE_VM     :   delete
}

import time,sys,commands
import traceback
from helper import get_date

while True:
    db = current.db
    db.commit()
    try :
        processes=db(db.task_queue.status==TASK_QUEUE_STATUS_PENDING).select(orderby=db.task_queue.priority|db.task_queue.id)
        logger.debug(len(processes))
        if(len(processes) >= 1):
            try:
                logger.debug(commands.getstatusoutput('date')[1])
                process=processes.first()
                logger.debug(str(process))
                ret = task[process['task_type']](process['vm_id'])
                db(db.task_queue.task_id==process[id]).update(status=ret[0])
                db(db.task_queue_event.task_id==process[id]).update(status=ret[0])
                if(ret[0] == TASK_QUEUE_STATUS_FAILED):
                    db(db.task_queue_event.task_id==process[id]).update(error=ret[1])
                db.commit()
                logger.debug("Task done")
            except Exception as e:
                logger.error(e)
                etype, value, tb = sys.exc_info()
                msg=''.join(traceback.format_exception(etype, value, tb, 10))
                db(db.queue.id==process['id']).update(status=-1,comments=msg,ftime=get_date())
    except :
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        logger.error(msg)
        time.sleep(10)
