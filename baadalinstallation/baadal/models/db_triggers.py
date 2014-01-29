# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,db
    from task_scheduler import vm_scheduler
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

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
