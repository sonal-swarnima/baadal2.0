# -*- coding: utf-8 -*-
###################################################################################

from log_handler import logger
from vm_helper import snapshot, destroy, revert, delete_snapshot, start, suspend
from helper import log_exception, update_constant
from threading import Thread
from Queue import Queue
from gluon import current

THREAD_POOL_COUNT = 5

BAADAL_STATUS_UP='up'
BAADAL_STATUS_UP_IN_PROGRESS='up-progress'
BAADAL_STATUS_DOWN='down'
BAADAL_STATUS_DOWN_IN_PROGRESS='down-progress'
SNAPSHOT_SYSTEM=6


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e:
                print e
            finally:
                self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


def snapshot_and_destroy(vm_id, vm_identity, vm_status):
    try:
        logger.debug('Inside snapshot_and_destroy for %s' %(vm_identity))
        if vm_status == current.VM_STATUS_RUNNING:
            snapshot({'vm_id':vm_id, 'snapshot_type':SNAPSHOT_SYSTEM})
            logger.debug('Snapshot of %s completed successfully' %(vm_identity))

        destroy({'vm_id':vm_id})
        logger.debug('%s destroyed successfully' %(vm_identity))
    except:
        log_exception()
        pass

def shutdown_baadal():
    logger.info('Starting Baadal Shutdown')
    update_constant('baadal_status', BAADAL_STATUS_DOWN_IN_PROGRESS)
    current.db.commit()

    vms = current.db(current.db.vm_data.status.belongs(current.VM_STATUS_RUNNING, current.VM_STATUS_SUSPENDED)).select()
    
#     pool = ThreadPool(THREAD_POOL_COUNT)

    for vm_detail in vms:
        snapshot_and_destroy(vm_detail.id, vm_detail.vm_identity, vm_detail.status)
        current.db.vm_event_log.insert(vm_id = vm_detail.id,
                                       attribute    = 'VM Status',
                                       requester_id = -1,
                                       old_value    = vm_detail.status,
                                       new_value    = 'System Shutdown')
#         pool.add_task(snapshot_and_suspend, vm_detail.id, vm_detail.vm_identity)

#     pool.wait_completion()    
    update_constant('baadal_status', BAADAL_STATUS_DOWN)
    current.db.commit()


def shutdown_host(host_id_list):
    logger.info('Starting Host Shutdown')
    vms = current.db((current.db.vm_data.status.belongs(current.VM_STATUS_RUNNING, current.VM_STATUS_SUSPENDED)) & 
                     current.db.vm_data.host_id.belongs(host_id_list)).select()
    
#     pool = ThreadPool(THREAD_POOL_COUNT)

    for vm_detail in vms:
        snapshot_and_destroy(vm_detail.id, vm_detail.vm_identity, vm_detail.status)
        current.db.vm_event_log.insert(vm_id = vm_detail.id,
                                       attribute    = 'VM Status',
                                       requester_id = -1,
                                       old_value    = vm_detail.status,
                                       new_value    = 'System Shutdown')
        current.db.commit()
#         pool.add_task(snapshot_and_suspend, vm_detail.id, vm_detail.vm_identity)

#     pool.wait_completion()    


def revert_and_resume(vm_id, vm_identity):

    try:
        sys_snapshot = current.db.snapshot(vm_id=vm_id, type=SNAPSHOT_SYSTEM)
        if sys_snapshot:
            revert({'vm_id' : vm_id, 'snapshot_id' : sys_snapshot.id})
            logger.debug('Snapshot of %s reverted from %s successfully' %(vm_identity, sys_snapshot.snapshot_name))
            delete_snapshot({'vm_id':vm_id, 'snapshot_id':sys_snapshot.id})
            logger.debug('Snapshot %s deleted successfully' %(sys_snapshot.snapshot_name))
        
        event_data = current.db.vm_event_log(vm_id = vm_id, new_value = 'System Shutdown')
#         event_data = current.db((current.db.vm_event_log.vm_id == vm_id) & (current.db.vm_event_log.new_value == 'System Shutdown')).select(current.db.vm_event_log.ALL)
        print event_data
        if event_data:
            start({'vm_id':vm_id})
            if int(event_data.old_value) == current.VM_STATUS_SUSPENDED:
                suspend({'vm_id':vm_id})
                
            del current.db.vm_event_log[event_data.id]
        current.db.commit()
    except:
        log_exception()
        pass

def bootup_baadal():
    logger.info('Starting Baadal Bootup')
    update_constant('baadal_status', BAADAL_STATUS_UP_IN_PROGRESS)
    current.db.commit()

#     pool = ThreadPool(THREAD_POOL_COUNT)
    
    vms = current.db(~current.db.vm_data.status.belongs(current.VM_STATUS_UNKNOWN, current.VM_STATUS_IN_QUEUE)).select()
    for vm_detail in vms:
        revert_and_resume(vm_detail.id, vm_detail.vm_identity)
#             pool.add_task(revert_and_delete_snapshot, vm_detail.id, vm_detail.vm_identity, sys_snapshot.id, sys_snapshot.snapshot_name)

#     pool.wait_completion()    
    update_constant('baadal_status', BAADAL_STATUS_UP)
    current.db.commit()


def bootup_host(host_id_list):
    logger.info('Starting Host Bootup')

#     pool = ThreadPool(THREAD_POOL_COUNT)
    
    vms = current.db(~current.db.vm_data.status.belongs(current.VM_STATUS_UNKNOWN, current.VM_STATUS_IN_QUEUE) & 
                     current.db.vm_data.host_id.belongs(host_id_list)).select()
    for vm_detail in vms:
            revert_and_resume(vm_detail.id, vm_detail.vm_identity)
#             pool.add_task(revert_and_delete_snapshot, vm_detail.id, vm_detail.vm_identity, sys_snapshot.id, sys_snapshot.snapshot_name)

#     pool.wait_completion()    
