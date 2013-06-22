# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from common_model import *  # @UnusedWildImport
    global db; db = gluon.sql.DAL()
###################################################################################

def approve_vm_request(_vm_id):
    add_vm_request_to_queue(_vm_id, TASK_TYPE_REQUEST_VM)
    db(db.vm_data.id == _vm_id).update(status=VM_STATUS_APPROVED)
