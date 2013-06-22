# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
from vm_helper import install_vm,delete_vm
from helper import get_date
if 0:
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

task = {TASK_TYPE_REQUEST_VM    :   install_vm,
        TASK_TYPE_DELETE_VM     :   delete_vm
}

import time,sys,commands
import traceback

while True:
    db.commit()
    try :
        processes=db(db.task_queue.status==TASK_QUEUE_STATUS_PENDING).select(orderby=db.task_queue.priority|db.task_queue.id)
        print len(processes)
        if(len(processes) >= 1):
            try:
                print commands.getstatusoutput('date')[1]
                process=processes.first()
                print str(process)
                task[process['task_type']](process['vm_id'])
                db.commit()
                print "Task done"
            except Exception as e:
                print e
                etype, value, tb = sys.exc_info()
                msg=''.join(traceback.format_exception(etype, value, tb, 10))
                db(db.queue.id==process['id']).update(status=-1,comments=msg,ftime=get_date())
    except :
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        print msg
        time.sleep(10)