# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    global auth; auth = gluon.tools.Auth()
    from common_model import *  # @UnusedWildImport
###################################################################################

def get_my_vm_list():
    vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) 
             & (db.vm_data.id==db.user_vm_map.vm_id) 
             & (db.user_vm_map.user_id==auth.user.id)).select()

    vmlist=[]
    for vm in vms:
        print vm
        total_cost = add_to_cost(vm.vm_data.vm_name)
        element = {'name':vm.vm_data.vm_name,
                   'ip':vm.vm_data.vm_ip, 
                   'owner':vm.vm_data.user_id, 
                   'ip':vm.vm_data.vm_ip, 
                   'hostip':'hostip',
                   'RAM':vm.vm_data.RAM,
                   'vcpus':vm.vm_data.vCPU,
                   'level':vm.vm_data.current_run_level,
                   'cost':total_cost}
        vmlist.append(element)

    return vmlist
