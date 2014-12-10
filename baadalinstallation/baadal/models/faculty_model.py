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

def verify_vm_request(request_id):
    db(db.request_queue.id == request_id).update(status=REQ_STATUS_VERIFIED)


def reject_vm_request(request_id):
    #Send Mail
    db(db.request_queue.id == request_id).delete()


def get_pending_requests():

    _query = get_pending_request_query([REQ_STATUS_REQUESTED])
    vm_requests = _query.select(db.request_queue.ALL)
    return get_pending_request_list(vm_requests)

def get_pending_requests_count():

    _query = get_pending_request_query([REQ_STATUS_REQUESTED])
    return _query.count()

def get_edit_pending_request_form(request_id):
    
    edit_req = db.request_queue[request_id]
    db.request_queue.id.readable=False
    db.request_queue.vm_name.writable=False
    db.request_queue.request_type.writable=False
    db.request_queue.purpose.writable=False
    form_fields = ['vm_name', 'request_type']
    
    if edit_req.request_type in (VM_TASK_CREATE, VM_TASK_EDIT_CONFIG) :
        db.request_queue.RAM.requires = IS_IN_SET(VM_RAM_SET, zero=None)
        db.request_queue.vCPU.requires = IS_IN_SET(VM_vCPU_SET, zero=None)
        _query = (db.security_domain.visible_to_all == True) | (db.security_domain.org_visibility.contains(edit_req.requester_id.organisation_id))
        db.request_queue.security_domain.requires = IS_IN_DB(db(_query), 'security_domain.id', '%(name)s', zero=None)
        db.request_queue.HDD.writable=False

        if edit_req.request_type == VM_TASK_EDIT_CONFIG:
            form_fields.extend(['RAM', 'vCPU', 'security_domain', 'public_ip'])
        else:
            form_fields.extend(['template_id', 'RAM', 'vCPU', 'HDD', 'extra_HDD', 'security_domain', 'public_ip'])
    
    elif edit_req.request_type == VM_TASK_CLONE:
        form_fields.append('clone_count')
    
    elif edit_req.request_type == VM_TASK_ATTACH_DISK:
        db.request_queue.HDD.writable=False
        db.request_queue.extra_HDD.writable=False
        form_fields.extend(['HDD', 'extra_HDD', 'attach_disk'])
        
    form_fields.append('purpose')
    form = SQLFORM(db.request_queue, edit_req, fields=form_fields)
    return form