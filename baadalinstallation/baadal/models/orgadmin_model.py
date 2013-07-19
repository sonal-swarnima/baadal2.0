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
    vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) 
    & (auth.user.organisation_id == db.user.organisation_id) 
    & (db.vm_data.id == db.user_vm_map.vm_id)
    & (db.user.id == db.user_vm_map.user_id)).select(db.vm_data.ALL)
    return get_hosted_vm_list(vms)


def get_verified_vm_list():
    vms = db((db.vm_data.status == VM_STATUS_VERIFIED) | (db.vm_data.status == VM_STATUS_APPROVED)).select()
    return get_pending_vm_list(vms)
