# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator

def verify_vm_request(vm_id):
    db(db.vm_data.id == vm_id).update(status=VM_STATUS_VERIFIED)

def reject_vm_request(vm_id):
    db(db.vm_data_event.vm_id == vm_id).update(status=VM_STATUS_REJECTED)
    db(db.vm_data.id == vm_id).delete()

def add_vm_user(_user_id, _vm_id):
    db.user_vm_map.insert(user_id=_user_id,vm_id=_vm_id);
    
def get_pending_requests():

    if is_moderator():
        vm_query = db(db.vm_data.status == VM_STATUS_REQUESTED)
    else:
        vm_query = db((db.vm_data.status == VM_STATUS_REQUESTED) & (db.vm_data.owner_id == auth.user.id))
    
    vms = vm_query.select(db.vm_data.ALL)
    return get_pending_vm_list(vms)

