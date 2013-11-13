# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################


def get_all_orglevel_vm_list():

    users_of_same_org = db(auth.user.organisation_id == db.user.organisation_id)._select(db.user.id)
    vms = db((db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)) &
              (db.vm_data.id == db.user_vm_map.vm_id) &
              (db.user_vm_map.user_id.belongs(users_of_same_org))).select(db.vm_data.ALL)
    
    return get_hosted_vm_list(vms)
    


def get_verified_requests():

    users_of_same_org = db(auth.user.organisation_id == db.user.organisation_id)._select(db.user.id)

    requests = db((db.request_queue.status.belongs(REQ_STATUS_VERIFIED, REQ_STATUS_APPROVED))
             & (db.request_queue.requester_id.belongs(users_of_same_org))).select(db.request_queue.ALL)

    return get_pending_request_list(requests)
    

def approve_vm_request(request_id):
    db(db.request_queue.id == request_id).update(status=REQ_STATUS_APPROVED)
