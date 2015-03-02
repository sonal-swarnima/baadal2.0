# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import libvirt
from libvirt import *  # @UnusedWildImport
from lxml import etree
from helper import execute_remote_cmd, log_exception
from host_helper import HOST_STATUS_UP, get_host_domains
from nat_mapper import remove_mapping
from log_handler import logger

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


def get_host_sanity_form():
    _dict = {-1 : 'None', 0 : 'All'}

    hosts=db(db.host.status == HOST_STATUS_UP).select()
    for host in hosts:
        _dict.update({host.id : host.host_name})
    
    form = FORM(TR("Show:", 
           SELECT(_name='host_selected', _id='host_select_id',
           *[OPTION(_dict[key], _value=str(key)) for key in _dict.keys()]), 
            A(SPAN(_class='icon-refresh'), _onclick = '$(this).closest(\'form\').submit()', _href='#')))
    return form


def check_vm_sanity(host_id = 0):
    vmcheck=[]
    vm_list = []
    
    if host_id == 0:
        hosts=db(db.host.status == HOST_STATUS_UP).select()
    else:
        hosts=db(db.host.id == host_id).select()
    
    for host in hosts:
        try:
            logger.info('Starting sanity check for host %s' %(host.host_name))
            #Get list of the domains(running and not running) on the hypervisor
            domains = get_host_domains(host.host_ip.private_ip)
            for dom in domains:
                try:
                    domain_name = dom.name()
                    vm = db((db.vm_data.vm_identity == domain_name) & 
                            (db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN))).select().first()
                    
                    vm_state = dom.info()[0]
                    status = vminfo_to_state(vm_state)
                    if(vm):
                        if(vm.host_id != host.id):
                            vmcheck.append({'vm_id':vm.id,
                                            'host':host.host_name, 
                                            'host_id':host.id,
                                            'vmname':vm.vm_name,
                                            'status':status,
                                            'message':'Moved from '+vm.host_id.host_name+' to '+host.host_name, 'operation':'None'})#Bad VMs
                            #If VM has been migrated to another host; Host information updated
                            db(db.vm_data.vm_identity == domain_name).update(host_id = host.id)
                        else:
                            vmcheck.append({'vm_id':vm.id,
                                            'host':host.host_name,
                                            'host_id':host.id,
                                            'vmname':vm.vm_name,
                                            'status':status,
                                            'message':'VM is on expected host '+vm.host_id.host_name, 'operation':'None'})#Good VMs
                        if vm_state_map[vm_state] != vm.status:
                            #If not in sync with actual state of VM; status of VM updated in DB
                            db(db.vm_data.vm_identity == domain_name).update(status = vm_state_map[vm_state])

                            #Adding into vm_event_log about the vm details
                            db.vm_event_log.insert(vm_id = vm.id,
                                                   attribute = 'VM Status',
                                                   requester_id = SYSTEM_USER,
                                                   old_value = get_vm_status(vm.status),
                                                   new_value = get_vm_status(vm_state_map[vm_state]))

                        vm_list.append(vm.vm_identity)
                            
                    elif vm_state != VIR_DOMAIN_CRASHED:
                        vmcheck.append({'host':host.host_name,
                                        'host_id':host.id,
                                        'vmname':dom.name(),
                                        'status':status,
                                        'message':'Orphan, VM is not in database', 
                                        'operation':'Orphan'})#Orphan VMs

                except Exception:
                    log_exception()
                    if(vm):
                        vmcheck.append({'vmname':vm.vm_name,
                                        'host':'Unknown',
                                        'host_id':'0',
                                        'status':'Unknown',
                                        'message':'Some Error Occurred', 
                                        'operation':'Error'})

        except:pass
        db.commit()
        
    if host_id == 0:
        db_vms=db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
        for db_vm in db_vms:
            if(db_vm.vm_identity not in vm_list):
                vmcheck.append({'vmname':db_vm.vm_identity,
                                'host':db_vm.host_id.host_name,
                                'host_id':db_vm.host_id,
                                'status':'Undefined',
                                'message':'VM not found', 
                                'operation':'Undefined'})
            
    return vmcheck


def add_orphan_vm(vm_name, host_id):

    host_details = db.host[host_id]
    host_ip = host_details.host_ip.private_ip
    connection_object = libvirt.openReadOnly("qemu+ssh://root@" + host_ip + "/system")
    domain = connection_object.lookupByName(vm_name)
    vm_state = domain.info()[0]
    vm_status = vm_state_map[vm_state]    
    # Parse domain XML to get information about VM
    root = etree.fromstring(domain.XMLDesc(0))

    ram_elem = root.xpath('memory')[0]
    ram_in_kb = int(ram_elem.text)
    ram_in_mb = int(round(int(ram_in_kb)/(1024),0))

    cpu_elem = root.xpath('vcpu')[0]
    cpu = int(cpu_elem.text)

    vnc_elem = root.xpath("devices/graphics[@type='vnc']")[0]
    vnc_port = vnc_elem.attrib['port']
    
    mac_elem = root.xpath("devices/interface[@type='network']/mac")[0]
    mac_address = mac_elem.attrib['address']

    ip_addr = db.private_ip_pool(mac_addr = mac_address)
    ip_address = None
    if ip_addr:
        ip_address = ip_addr['id']
    
    template_elem = root.xpath("devices/disk[@type='file']/source")[0]
    template_file = template_elem.attrib['file']
    
    command = "qemu-img info " + template_file + " | grep 'virtual size'"
    ret = execute_remote_cmd(host_ip, 'root', command) # Returns e.g. virtual size: 40G (42949672960 bytes)
    hdd = int(ret[ret.index(':')+1:ret.index('G ')].strip())

    security_domain_row = db.security_domain(vlan=ip_addr['vlan'])
    
    db.vm_data.insert(
        vm_name = vm_name, 
        vm_identity = (vm_name), 
        RAM = ram_in_mb,
        HDD = hdd,
        extra_HDD = 0,
        vCPU = cpu,
        host_id = host_id,
        template_id = 1, #TBD
        datastore_id = 1, #TBD
        owner_id = SYSTEM_USER,
        requester_id = SYSTEM_USER,
        private_ip = ip_address,
        vnc_port = vnc_port,
        purpose = 'Added by System',
        security_domain = security_domain_row['id'],
        status = vm_status)
        
    return

def delete_vm_info(vm_identity):

    vm_details = db(db.vm_data.vm_identity == vm_identity).select().first()

    # updating the used entry of database
    if vm_details.HDD != None:
        db(db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                                         (int(vm_details.HDD) + int(vm_details.template_id.hdd)))

    if vm_details.public_ip != None:
        remove_mapping(vm_details.public_ip.public_ip, vm_details.private_ip.private_ip)
    #this will delete vm_data entry and also its references
    db(db.vm_data.id == vm_details.id).delete()
    
    return


def check_vm_snapshot_sanity(vm_id):
    vm_data = db.vm_data[vm_id]
    snapshot_check = []
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+vm_data.host_id.host_ip.private_ip+'/system')
        domain = conn.lookupByName(vm_data.vm_identity)
        
        dom_snapshot_names = domain.snapshotListNames(0)
        logger.debug(dom_snapshot_names)
        conn.close()
            
        snapshots = db(db.snapshot.vm_id == vm_id).select()
        for snapshot in snapshots:
            if snapshot.snapshot_name in dom_snapshot_names:
                snapshot_check.append({'snapshot_name' : snapshot.snapshot_name,
                                       'snapshot_type' : get_snapshot_type(snapshot.type),
                                       'message' : 'Snapshot present',
                                       'operation' : 'None'})
                dom_snapshot_names.remove(snapshot.snapshot_name)
            else:
                snapshot_check.append({'snapshot_id' : snapshot.id,
                                       'snapshot_name' : snapshot.snapshot_name,
                                       'snapshot_type' : get_snapshot_type(snapshot.type),
                                       'message' : 'Snapshot not present',
                                       'operation' : 'Undefined'})

        for dom_snapshot_name in dom_snapshot_names:
                snapshot_check.append({'vm_name' : vm_data.vm_identity,
                                       'snapshot_name' : dom_snapshot_name,
                                       'snapshot_type' : 'Unknown',
                                       'message' : 'Orphan Snapshot',
                                       'operation' : 'Orphan'})
                        
    except Exception:
        log_exception()
    logger.debug(snapshot_check)
    return (vm_data.id, vm_data.vm_name, snapshot_check)


def delete_orphan_snapshot(domain_name, snapshot_name):
    
    logger.debug('Deleting orphan snapshot %s of VM %s' %(snapshot_name, domain_name))
    vm_data = db(db.vm_data.vm_identity == domain_name).select().first()

    conn = libvirt.open('qemu+ssh://root@'+vm_data.host_id.host_ip.private_ip+'/system')
    domain = conn.lookupByName(vm_data.vm_identity)
    
    snapshot = domain.snapshotLookupByName(snapshot_name, 0)        
    snapshot.delete(0)
    conn.close
    logger.debug('Orphan VM deleted')    

def delete_snapshot_info(snapshot_id):
    logger.debug('Deleting snapshot info for ' + str(snapshot_id))
    del db.snapshot[snapshot_id]
    logger.debug('Snapshot info deleted')