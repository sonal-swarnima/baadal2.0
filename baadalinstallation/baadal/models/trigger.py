# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,db
    from task_scheduler import vm_scheduler
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import logger

def schedule_task(fields, _id):
    #Add entry into task_queue_event
    vm_data = db.vm_data[fields['vm_id']]
    task_event_id = db.task_queue_event.insert(task_id = _id,
                            task_type = fields['task_type'],
                            vm_id = fields['vm_id'],
                            vm_name = vm_data.vm_name,
                            requester_id = fields['requester_id'],
                            parameters = fields['parameters'],
                            status = TASK_QUEUE_STATUS_PENDING)
    #Schedule the task in the scheduler 
    if fields['task_type'] == TASK_TYPE_CLONE_VM:
        # In case of clone vm, Schedule as many task as the number of clones
        for clone_vm_id in fields['parameters']['clone_vm_id']:
            vm_scheduler.queue_task('clone_task', pvars = dict(task_event_id = task_event_id, vm_id = clone_vm_id),start_time = request.now, timeout = 30 * MINUTES)
    else:
        vm_scheduler.queue_task('vm_task', pvars = dict(task_event_id = task_event_id),start_time = request.now, timeout = 30 * MINUTES)

def vm_data_insert_callback(fields, _id):
    db.vm_data_event.insert(vm_id        = _id,
                            vm_name      = fields['vm_name'],
                            vm_identity  = fields['vm_identity'],
                            vCPU         = fields['vCPU'],
                            RAM          = fields['RAM'],
                            HDD          = fields['HDD'],
                            extra_HDD    = fields['extra_HDD'],
                            purpose      = fields['purpose'],
                            template_id  = fields['template_id'],
                            requester_id = fields['requester_id'],
                            owner_id     = fields['owner_id'])

db.vm_data._after_insert = [vm_data_insert_callback]

def task_queue_insert_callback(fields, _id):
    schedule_task(fields, _id)

db.task_queue._after_insert = [task_queue_insert_callback]

def task_queue_update_callback(dbset, new_fields):
#   If task queue status is set to retry, re-schedule the task
    if 'status' in new_fields and new_fields['status'] == TASK_QUEUE_STATUS_RETRY:
        fields = dbset.select().first()
        schedule_task(fields,fields['id'])

db.task_queue._after_update = [task_queue_update_callback]

def vm_data_delete_callback(dbset):

    for vm_data in dbset.select():
        logger.debug('Deleting references for ' + vm_data.vm_identity)
        
        db(db.private_ip_pool.vm_id == vm_data.id).update(vm_id = None)
        db(db.public_ip_pool.vm_id == vm_data.id).update(vm_id = None)
        db(db.vm_data.parent_id == vm_data.id).update(parent_id = None)
        db(db.task_queue_event.vm_id == vm_data.id).update(vm_id = None)

db.vm_data._before_delete = [vm_data_delete_callback]


import ast
def scheduler_task_update_callback(dbset, new_fields):

    logger.debug("~~~~~~in callback~~~~~")
    logger.debug(dbset.select())
    logger.debug(dir(new_fields))
    logger.debug(new_fields)
    if 'status' in new_fields and 'next_run_time' in new_fields:
      if new_fields['status']=='TIMEOUT':
        logger.debug(new_fields['next_run_time'])
        next_run_time = str(new_fields['next_run_time'])
        next_run_time = next_run_time.split(".")
        logger.debug(next_run_time[0])
        rows =db((db.scheduler_task.status==new_fields['status']) & (db.scheduler_task.next_run_time==next_run_time[0])).select()
	for row in rows:
            logger.debug("status"+str(row.status))
            logger.debug("next_run_time"+str(row.next_run_time))
            logger.debug(row.vars)
            if 'task_event_id' in row.vars:
                a_dict = ast.literal_eval(row.vars)
                logger.debug(a_dict)
                task_event_id1 = a_dict['task_event_id']
                logger.debug("Task TimedOut with task_event_id: "+ str(task_event_id1))
                task_timeout_cleanup(task_event_id1,row)
            else:
                logger.debug("Task TimedOut without cleanup")

            
    logger.debug("~~~~~~exiting callback~~~~~")

db.scheduler_task._after_update = [scheduler_task_update_callback]


def task_timeout_cleanup(task_event_id, scheduler_row):
    msg = ""
    logger.debug("cleaning up for "+scheduler_row.status+" task: " + str(task_event_id))
    task_event_data = db.task_queue_event[task_event_id]
    task_queue_data = db.task_queue[task_event_data.task_id]
    vm_data = db.vm_data[task_event_data.vm_id]
    if task_queue_data.status == TASK_QUEUE_STATUS_PENDING:
       logger.debug(task_queue_data.status)
    #On return, update the status and end time in task event table^M
       if scheduler_row.status == 'TIMEOUT':
          msg = "Timeout"
       elif scheduler_row.status == 'FAILED':
          rows = db(db.scheduler_run.task_id==scheduler_row.id).select()
          rows.sort(lambda row: row.stop_time, reverse=True)
          msg = rows.first().traceback
       task_event_data.update_record(status=TASK_QUEUE_STATUS_FAILED, message=msg, end_time=get_datetime())
       task_queue_data.update_record(status=TASK_QUEUE_STATUS_FAILED)
       if task_queue_data.task_type == TASK_TYPE_CREATE_VM:
          db.vm_data[task_queue_data.vm_id] = dict(status = VM_STATUS_UNKNOWN)
       if 'request_id' in task_queue_data.parameters:
          logger.debug(type(task_queue_data.parameters))
          db.request_queue[task_queue_data.parameters['request_id']] = dict(status = REQ_STATUS_FAILED)
