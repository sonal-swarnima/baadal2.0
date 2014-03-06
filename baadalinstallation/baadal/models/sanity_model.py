# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import libvirt
from libvirt import *  # @UnusedWildImport
from lxml import etree
from helper import execute_remote_cmd
from host_helper import HOST_STATUS_UP

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

# def check_host_sanity():

def check_vm_sanity():
    vmcheck=[]
    vm_list = []
    hosts=db(db.host.status == HOST_STATUS_UP).select()
    for host in hosts:
        try:
            #Establish a read only remote connection to libvirtd
            #find out all domains running and not running
            conn = libvirt.openReadOnly('qemu+ssh://root@'+host.host_ip+'/system')
            domains=[]
            ids = conn.listDomainsID()
            for _id in ids:
                domains.append(conn.lookupByID(_id))
            names = conn.listDefinedDomains()
            for dom_name in names:
                domains.append(conn.lookupByName(dom_name))
            for dom in domains:
                try:
                    domain_name = dom.name()
                    vm = db(db.vm_data.vm_identity == domain_name).select().first()
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
                            db(db.vm_data.vm_identity == domain_name).update(host_id = host.id)
                        else:
                            vmcheck.append({'host':host.host_name,
                                            'host_id':host.id,
                                            'vmname':vm.vm_name,
                                            'status':status,
                                            'message':'VM is on expected host '+vm.host_id.host_name, 'operation':'None'})#Good VMs
                        if vm_state_map[vm_state] != vm.status:
                            #If not in sync with actual state of VM; status of VM updated in DB
                            db(db.vm_data.vm_identity == domain_name).update(status = vm_state_map[vm_state])
                            
                        vm_list.append(vm.vm_identity)
                            
                    elif vm_state != VIR_DOMAIN_SHUTOFF:
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
        if(db_vm.vm_identity not in vm_list):
            vmcheck.append({'vmname':db_vm.vm_identity,
                            'host':db_vm.host_id.host_name,
                            'host_id':db_vm.host_id,
                            'status':'Undefined',
                            'message':'VM not found', 
                            'operation':'Undefined'})
            
    return vmcheck


def add_orhan_vm(vm_name, host_id):

    host_details = db.host[host_id]
    connection_object = libvirt.openReadOnly("qemu+ssh://root@" + host_details.host_ip + "/system")
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
    ip_address = '127.0.0.1'
    if ip_addr:
        ip_address = ip_addr['private_ip']
    
    template_elem = root.xpath("devices/disk[@type='file']/source")[0]
    template_file = template_elem.attrib['file']
    
    command = "qemu-img info " + template_file + " | grep 'virtual size'"
    ret = execute_remote_cmd(host_details.host_ip, 'root', command) # Returns e.g. virtual size: 40G (42949672960 bytes)
    hdd = int(ret[ret.index(':')+1:ret.index('G ')].strip())

    security_domain_row = db.security_domain(vlan=ip_addr['vlan'])
    
    vm_id = db.vm_data.insert(
        vm_name = vm_name, 
        vm_identity = (vm_name), 
        RAM = ram_in_mb,
        HDD = hdd,
        extra_HDD = 0,
        vCPU = cpu,
        host_id = host_id,
        template_id = 1, #TBD
        datastore_id = 1, #TBD
        owner_id = -1,
        requester_id = -1,
        private_ip = ip_address,
        mac_addr = mac_address,
        vnc_port = vnc_port,
        purpose = 'Added by System',
        security_domain = security_domain_row['id'],
        status = vm_status)
        
    db.private_ip_pool[ip_addr['id']] = dict(vm_id=vm_id)
    return

def delete_vm_info(vm_identity):

    vm_details = db(db.vm_data.vm_identity == vm_identity).select().first()
    count = vm_details.host_id.vm_count
    db(db.host.id == vm_details.host_id).update(vm_count = count - 1)

    # updating the used entry of database
    if vm_details.HDD != None:
        db(db.datastore.id == vm_details.datastore_id).update(used = int(vm_details.datastore_id.used) -  \
                                                                         (int(vm_details.HDD) + int(vm_details.template_id.hdd)))
    #this will delete vm_data entry and also its references
    db(db.vm_data.id == vm_details.id).delete()
    
    return
