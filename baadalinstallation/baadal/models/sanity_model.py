# -*- coding: utf-8 -*-
"""
sanity_model.py: This model has functions to check sanity of the system
and sync database information with ground reality.
By default, in case of discrepancy database information of VM is updated 
with actual status of hosted VMs.
It also provides functionalities to update VM definition and snapshots as 
per the information stored in database.
"""
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from cont_handler import Container
from container_create import get_node_to_deploy, list_container
from helper import execute_remote_cmd, log_exception
from host_helper import HOST_STATUS_UP, get_host_domains
from images import getImage
from libvirt import * # @UnusedWildImport
from log_handler import logger
from lxml import etree
from nat_mapper import remove_mapping
import libvirt

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


def cont_state_to_status(cont_state):
    if (cont_state == 'running') : status = VM_STATUS_RUNNING
    elif (cont_state == 'exited') : status = VM_STATUS_SHUTDOWN
    else: status = VM_STATUS_UNKNOWN
    
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
    """
    Checks if database information of VM status is in sync with ground reality.
    In case of discrepancy database is updated.
        - For each host, get list of the domains(running and not running).
        - If VM has migrated to another host; host information updated in database.
        - If VM not in sync with actual state of VM; status of VM updated in DB.
        - If VM is not present in database, it is marked Orphan.
        - If VM is not found on any of the hosts, it is marked Undefined.
    """
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
                            logger.info("vm_identity="+str(domain_name)+" vm_state_map[vm_state]="+str(vm_state_map[vm_state])+"and vm.status is" + str(vm.status))
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
    """
    Add Orphan VM information to database. VM information is retrieved from the VM definition XML.
    'System User' is added as owner of the VM.
    """
    host_details = db.host[host_id]
    host_ip = host_details.host_ip.private_ip
    connection_object = libvirt.openReadOnly("qemu+ssh://root@" + host_ip + "/system")
    domain = connection_object.lookupByName(vm_name)
    vm_state = domain.info()[0]
    vm_status = vm_state_map[vm_state]    
    # Parse domain XML to get information about VM
    root = etree.fromstring(domain.XMLDesc(0))

    ram_elem = root.findall('memory')[0]
    ram_in_kb = int(ram_elem.text)
    ram_in_mb = int(round(int(ram_in_kb)/(1024),0))

    cpu_elem = root.findall('vcpu')[0]
    cpu = int(cpu_elem.text)

    vnc_elem = root.findall("devices/graphics[@type='vnc']")[0]
    vnc_port = vnc_elem.attrib['port']
    
    mac_elem = root.findall("devices/interface[@type='bridge']/mac")[0]
    mac_address = mac_elem.attrib['address']

    ip_addr = db.private_ip_pool(mac_addr = mac_address)
    ip_address = None
    if ip_addr:
        ip_address = ip_addr['id']
    
    template_elem = root.findall("devices/disk[@type='file']/source")[0]
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
    """
    For undefined VMs, VM info and references are deleted from the database.
    Public IP mapping is removed, if present
    """
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
    """
    Checks if the snapshot information of VM is in sync with actual snapshots of the VM.
    """
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
    """
    Deletes orphan snapshot of the VM.
    Orphan snapshots are checkpoints of VM that are not present in database.
    """
    logger.debug('Deleting orphan snapshot %s of VM %s' %(snapshot_name, domain_name))
    vm_data = db(db.vm_data.vm_identity == domain_name).select().first()

    conn = libvirt.open('qemu+ssh://root@'+vm_data.host_id.host_ip.private_ip+'/system')
    domain = conn.lookupByName(vm_data.vm_identity)
    
    snapshot = domain.snapshotLookupByName(snapshot_name, 0)        
    snapshot.delete(0)
    conn.close
    logger.debug('Orphan VM deleted')    

def delete_snapshot_info(snapshot_id):
    """
    Deletes undefined snapshot info of the VM from database.
    These are checkpoints of VM that is present in database but not on VM.
    """
    logger.debug('Deleting snapshot info for ' + str(snapshot_id))
    del db.snapshot[snapshot_id]
    logger.debug('Snapshot info deleted')
    
    
def check_cont_sanity():

    cont_check= []
    cont_list = []
    
    nodes = get_node_to_deploy()
    containers = list_container( showall=True);

    for node in nodes:
        ip_port = node['IP'].split(":")
        node_data = db(db.node_data.node_ip == str(ip_port[0])).select().first()
        if not node_data:
            db.node_data.insert(
                  node_name = node['Name'],
                  node_ip = ip_port[0],
                  node_port = ip_port[1],
                  CPUs = node['Reserved CPUs'],
                  memory = node['Reserved Memory'],
                  version = node['ServerVersion'])
            
    try:
        for container in containers:
            names = container['Names'][0].split("/")
            cont_data = db(db.container_data.name == names[2]).select().first()
            cont_list.append(names[2])
            if cont_data:
                updated = False
                if cont_data.status != cont_state_to_status(container['State']):
                    cont_data.update_record(status = cont_state_to_status(container['State']))
                    updated = True
                node_name = cont_data.current_node.node_name if cont_data.current_node else None
                if names[1] != node_name:
                    new_node = db(db.node_data.node_name == names[1]).select().first()
                    cont_data.update_record(current_node=new_node.id)
                    
                message = 'Information updated' if updated else 'As expected'
                cont_check.append({'cont_id':cont_data.id,
                                   'cont_uuid':container['Id'],
                                   'node_name': names[1], 
                                   'cont_name':names[2],
                                   'status':container['State'],
                                   'message':message, 
                                   'operation':'None'})
                
            else:
                cont_check.append({'cont_id':None,
                                   'cont_uuid':container['Id'],
                                   'node_name': names[1], 
                                   'cont_name':names[2],
                                   'status':container['State'],
                                   'message':'Orphan, Container is not in database', 
                                   'operation':'Orphan'})#Orphan Containers

    except:
        log_exception()
        pass

    db(~db.user_container_map.cont_id.belongs(db().select(db.container_data.id))).delete()
    db.commit()
    
    db_conts=db(db.container_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED, VM_STATUS_SHUTDOWN)).select()
    for db_cont in db_conts:
        if(db_cont.name not in cont_list):
            cont_check.append({'cont_id'  : db_cont.id,
                               'cont_uuid': None,
                               'node_name': "-", 
                               'cont_name': db_cont.name,
                               'status'   : "-",
                               'message'  :'Container not present', 
                               'operation':'Undefined'})#Orphan Containers
            
    return cont_check


def delete_orphan_cont(cont_uuid):
    container = Container(cont_uuid);
    container.remove()
    return

def add_orphan_cont(cont_uuid):
    container = Container(cont_uuid);
    print("In add_orphan_cont")
    if container:
        container.updatedetails()
        
        cont_details = container.properties
        logger.debug(cont_details)
        image_details = getImage(cont_details['ImageName'])

        db.container_data.insert(
                  name = cont_details['Name'][1:],
                  RAM = int(int(cont_details['Memory'])/1024/1024),
                  vCPU = 1,
                  UUID = cont_uuid,
                  image_id = image_details['templateid'],
                  image_profile = image_details['type'],
                  restart_policy = None,
                  requester_id = SYSTEM_USER,
                  owner_id = SYSTEM_USER,
                  purpose = 'Added by System',
                  status = cont_state_to_status(cont_details['State']))
    return

def delete_cont_info(cont_id):
    db(db.container_data.id == cont_id).delete()
    
    return

    
