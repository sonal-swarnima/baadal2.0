# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,db
    from task_scheduler import vm_scheduler
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
""" trigger.py:  This file has methods to handle db trigger requests.
    Following handlers are defined:
    Table              Trigger
    vm_data            After Insert
    vm_data            Before delete
    task_queue         After Insert
    task_queue         After Update
    scheduler_task     After Update
"""

from helper import logger, get_datetime

def schedule_task(fields, _id):
    #Add entry into task_queue_event
    vm_id = fields['parameters']['vm_id'] if 'vm_id' in fields['parameters'] else None
    vm_name = db.vm_data[vm_id].vm_name if vm_id else ""

    task_event_id = db.task_queue_event.insert(task_id = _id,
                            task_type = fields['task_type'],
                            vm_id = vm_id,
                            vm_name = vm_name,
                            requester_id = fields['requester_id'],
                            parameters = fields['parameters'],
                            status = TASK_QUEUE_STATUS_PENDING)
    #Schedule the task in the scheduler 
    if fields['task_type'] == VM_TASK_CLONE:
        # In case of clone vm, Schedule as many task as the number of clones
        for clone_vm_id in fields['parameters']['clone_vm_id']:
            vm_scheduler.queue_task('clone_task', 
                                    pvars = dict(task_event_id = task_event_id, vm_id = clone_vm_id),
                                    start_time = request.now, 
                                    timeout = 30 * MINUTES, 
                                    group_name = 'vm_task')
    else:
        vm_scheduler.queue_task('vm_task', 
                                pvars = dict(task_event_id = task_event_id),
                                start_time = request.now, 
                                timeout = 30 * MINUTES, 
                                group_name = 'vm_task')


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

    if 'status' in new_fields:
        fields = dbset.select().first()
        # If task queue status is set to retry, re-schedule the task
        if new_fields['status'] == TASK_QUEUE_STATUS_RETRY:
            schedule_task(fields,fields['id'])
        # If task queue status is set to retry is set to failed, 
        elif new_fields['status'] == TASK_QUEUE_STATUS_FAILED:
            # 1. update vm_data status to -1 if task is Create VM
            if fields['task_type'] == VM_TASK_CREATE:
                vm_id = fields['parameters']['vm_id']
                db.vm_data[vm_id] = dict(status = VM_STATUS_UNKNOWN)
            # 2. update request_queue status to -1 if task has request_id
            if 'request_id' in fields['parameters']:
                db.request_queue[fields['parameters']['request_id']] = dict(status = REQ_STATUS_FAILED)

db.task_queue._after_update = [task_queue_update_callback]


def vm_data_delete_callback(dbset):

    for vm_data in dbset.select():
        logger.debug('Deleting references for ' + vm_data.vm_identity)        
        db(db.vm_data.parent_id == vm_data.id).update(parent_id = None)

db.vm_data._before_delete = [vm_data_delete_callback]


import ast
def scheduler_task_update_callback(dbset, new_fields):

    if 'status' in new_fields and 'next_run_time' in new_fields:

        if new_fields['status']=='TIMEOUT':
            db_query = dbset.as_dict()['query']
            id_query = db_query.as_dict()['first']
            row = db(id_query).select().first()

            if 'task_event_id' in row.vars:
                param_dict = ast.literal_eval(row.vars)
                task_event_id = param_dict['task_event_id']
                logger.debug("Task TimedOut with task_event_id: "+ str(task_event_id))
                task_timeout_cleanup(task_event_id,row)
            else:
                logger.debug("Task TimedOut without cleanup")
          
db.scheduler_task._after_update = [scheduler_task_update_callback]


def task_timeout_cleanup(task_event_id, scheduler_row):
    
    logger.debug("cleaning up for "+scheduler_row.status+" task: " + str(task_event_id))
    task_event_data = db.task_queue_event[task_event_id]
    task_queue_data = db.task_queue[task_event_data.task_id]

    if task_queue_data.status == TASK_QUEUE_STATUS_PENDING:
        #On return, update the status and end time in task event table
        msg = ""
        if scheduler_row.status == 'TIMEOUT':
            msg = "Task Timeout " # + task_event_data['message']
        elif scheduler_row.status == 'FAILED':
            rows = db(db.scheduler_run.task_id==scheduler_row.id).select()
            rows.sort(lambda row: row.stop_time, reverse=True)
            msg = rows.first().traceback
          
        task_event_data.update_record(status=TASK_QUEUE_STATUS_FAILED, message=msg, end_time=get_datetime())
        task_queue_data.update_record(status=TASK_QUEUE_STATUS_FAILED)
