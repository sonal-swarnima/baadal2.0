# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
# from task_scheduler import test123
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,db
    from task_scheduler import vm_scheduler
###################################################################################

def schedule_task(fields, _id):
    db.task_queue_event.insert(task_id = _id,
                            task_type = fields['task_type'],
                            vm_id = fields['vm_id'],
                            parameters = fields['parameters'],
                            status = TASK_QUEUE_STATUS_PENDING)
    #Schedule the task in the scheduler 
    if fields['task_type'] == TASK_TYPE_CLONE_VM:
        
        for clone_vm_id in fields['parameters']['clone_vm_id']:
            vm_scheduler.queue_task('clone_task', pvars = dict(task_id = _id, vm_id = clone_vm_id),start_time = request.now, timeout = 1800)
    else:
        vm_scheduler.queue_task('vm_task', pvars = dict(task_id = _id),start_time = request.now, timeout = 1800)


def vm_data_insert_callback(fields, _id):
    db.vm_data_event.insert(vm_id = _id,
                            vm_name = fields['vm_name'],
                            vCPU = fields['vCPU'],
                            RAM = fields['RAM'],
                            HDD = fields['HDD'],
                            extra_HDD = fields['extra_HDD'],
                            purpose = fields['purpose'],
                            template_id = fields['template_id'],
                            requester_id = fields['requester_id'],
                            owner_id = fields['owner_id'])

db.vm_data._after_insert = [vm_data_insert_callback]

def task_queue_insert_callback(fields, _id):
    schedule_task(fields, _id)

db.task_queue._after_insert = [task_queue_insert_callback]

def task_queue_update_callback(dbset, new_fields):
    if 'status' in new_fields and new_fields['status'] == TASK_QUEUE_STATUS_RETRY:
        fields = dbset.select().first()
        schedule_task(fields,fields['id'])

db.task_queue._after_update = [task_queue_update_callback]

def update_vm_data_event(fields, _id):
    db(db.vm_data_event.id == _id).update(host_id = fields['host_id'], 
                                          datastore_id = fields['datastore_id'], 
                                          public_ip = fields['public_ip'], 
                                          private_ip = fields['private_ip'], 
                                          vnc_port = fields['vnc_port'], 
                                          mac_addr = fields['mac_addr'], 
                                          start_time = fields['start_time'], 
                                          current_run_level = fields['current_run_level'],
                                          last_run_level = fields['last_run_level'],
                                          total_cost = fields['total_cost'],
                                          status = fields['status'] )

def vm_data_update_callback(dbset, new_fields):
        fields = dbset.select().first()
        update_vm_data_event(fields,fields['id'])

db.vm_data._after_update = [vm_data_update_callback]

