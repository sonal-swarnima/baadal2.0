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

def approve_vm_request(_vm_id):
    add_vm_task_to_queue(_vm_id, TASK_TYPE_CREATE_VM)
    db(db.vm_data.id == _vm_id).update(status=VM_STATUS_APPROVED)
    db.user_vm_map.insert(user_id=auth.user.id,vm_id=_vm_id);
