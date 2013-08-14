# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import libvirt
from libvirt import *  # @UnusedWildImport

vm_state_map = {
        VIR_DOMAIN_RUNNING     :    VM_STATUS_RUNNING,
        VIR_DOMAIN_PAUSED      :    VM_STATUS_SUSPENDED,
        VIR_DOMAIN_SHUTDOWN    :    VM_STATUS_SHUTDOWN,
        VIR_DOMAIN_SHUTOFF     :    VM_STATUS_SHUTDOWN
    }


def vminfo_to_state(vm_state):

    if(vm_state == VIR_DOMAIN_NOSTATE): status = "No_State"
    elif(vm_state == VIR_DOMAIN_RUNNING): status = "Running"
    elif(vm_state == VIR_DOMAIN_BLOCKED): status = "Blocked"
    elif(vm_state == VIR_DOMAIN_PAUSED): status = "Paused"
    elif(vm_state == VIR_DOMAIN_SHUTDOWN): status = "Being_Shut_Down"
    elif(vm_state == VIR_DOMAIN_SHUTOFF): status = "Off"
    elif(vm_state == VIR_DOMAIN_CRASHED): status = "Crashed"
    else: status = "Unknown"

    return status


def check_sanity():
    vmcheck=[]
    vm_list = []
    hosts=db(db.host.status == HOST_STATUS_UP).select()
    for host in hosts:
        try:
            #Establish a read only remote connection to libvirtd
            #find out all domains running and not running
            #Since it might result in an error add an exception handler
            conn = libvirt.openReadOnly('qemu+ssh://root@'+host.host_ip+'/system')
            domains=[]
            ids = conn.listDomainsID()
            for _id in ids:
                domains.append(conn.lookupByID(_id))
            names = conn.listDefinedDomains()
            for name in names:
                domains.append(conn.lookupByName(name))
            for dom in domains:
                try:
                    name = dom.name()
                    vm = db(db.vm_data.vm_name == name).select().first()
                    vm_state = dom.info()[0]
                    status = vminfo_to_state(vm_state)
                    if(vm):
                        if(vm.host_id != host.id):
                            vmcheck.append({'host':host.host_name, 
                                            'host_id':host.id,
                                            'vmname':vm.vm_name,
                                            'status':status,
                                            'message':'Moved from '+vm.host_id.host_name+' to '+host.host_name, 'operation':'None'})#Bad VMs
                            #If VM has been migrated to another host; Host information updated
                            db(db.vm_data.vm_name==name).update(host_id = host.id)
                        else:
                            vmcheck.append({'host':host.host_name,
                                            'host_id':host.id,
                                            'vmname':vm.vm_name,
                                            'status':status,
                                            'message':'VM is on expected host '+vm.host_id.host_name, 'operation':'None'})#Good VMs
                        if vm_state_map[vm_state] != vm.status:
                            #If not in sync with actual state of VM; status of VM updated in DB
                            db(db.vm_data.vm_name == name).update(status = vm_state_map[vm_state])
                            
                        vm_list.append(vm.vm_name)
                            
                    else:
                        vmcheck.append({'host':host.host_name,
                                        'host_id':host.id,
                                        'vmname':dom.name(),
                                        'status':status,
                                        'message':'Orphan, VM is not in database', 
                                        'operation':'Orphan'})#Orphan VMs

                except Exception as e:
                    logger.error(e)
                    if(vm):
                        vmcheck.append({'vmname':vm.vm_name,
                                        'host':'Unknown',
                                        'host_id':'0',
                                        'status':'Unknown',
                                        'message':'Some Error Occurred', 
                                        'operation':'Error'})

            domains=[]
            names=[]
            conn.close()
        except:pass
        db.commit()
        db_vms=db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
        
        for db_vm in db_vms:
            if(db_vm.vm_name not in vm_list):
                vmcheck.append({'vmname':db_vm.vm_name,
                                'host':db_vm.host_id.host_name,
                                'host_id':db_vm.host_id,
                                'status':'Undefined',
                                'message':'VM not found', 
                                'operation':'Undefined'})
            
    return vmcheck


def delete_orhan_vm(vm_name, host_id):
    
    host_details = db.host[host_id]
    connection_object = libvirt.open("qemu+ssh://root@" + host_details.host_ip + "/system")
    domain = connection_object.lookupByName(vm_name)
    vm_state = domain.info()[0]
    if (vm_state == VIR_DOMAIN_RUNNING or vm_state == VIR_DOMAIN_PAUSED):
        logger.debug("VM is not shutoff. Shutting it off first.")
        domain.destroy()

    domain.undefine()
    logger.debug(vm_name + " is deleted successfully.")


#To be implemented
def add_orhan_vm(vm_name, host_id):
    return

#To be implemented
def delete_vm_info(vm_name):

    vm_details = db(db.vm_data.vm_name == vm_name).select().first()
    count = vm_details.host_id.vm_count
    db(db.host.id == vm_details.host_id).update(vm_count = count - 1)

    # updating the used entry of database
    if vm_details.HDD != None:
        db(db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                                         (int(vm_details.HDD) + int(vm_details.template_id.hdd)))
    #this will delete vm_data entry and also its references
    db(db.vm_data.id == vm_details.id).delete()
    
    return
