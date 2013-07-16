from vm_helper import get_vm_list

def get_all_orglevel_vm_list():
    vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) & (auth.user.organisation_id == )).select()
    return get_vm_list(vms)

