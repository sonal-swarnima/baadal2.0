# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
###################################################################################
import libvirt,commands  # @UnusedImport
from libvirt import *  # @UnusedWildImport
from vm_helper import *  # @UnusedWildImport
from helper import *  # @UnusedWildImport

HOST_STATUS_DOWN = 0
HOST_STATUS_UP = 1
HOST_STATUS_MAINTENANCE = 2

def check_host_status(host_ip):
    out=commands.getstatusoutput("ping -c 2 -W 1 " + host_ip)[0]
    current.logger.debug("Host Check command response for %s: %s" %(host_ip, str(out)))
    if(out == 0):
        if check_host_service_status(host_ip):
            return HOST_STATUS_UP
        else:
            return HOST_STATUS_DOWN
    else: 
        return HOST_STATUS_DOWN

def is_host_available(host_ip):
    try:
        execute_remote_cmd(host_ip,'root','pwd')
        return True
    except:
        return False

def get_host_mac_address(host_ip):
    command = "ifconfig -a | grep eth0 | head -n 1"
    ret = execute_remote_cmd(host_ip, 'root',command)#Returns e.g. eth0      Link encap:Ethernet  HWaddr 18:03:73:0d:e4:49
    ret=ret.strip()
    mac_addr = ret[ret.rindex(' '):].lstrip()
    return mac_addr


def get_host_cpu(host_ip):
    command = "grep -c processor /proc/cpuinfo"
    ret = execute_remote_cmd(host_ip, 'root',command)
    return int(ret)/2
    

def get_host_ram(host_ip):
    command = "cat /proc/meminfo | grep MemTotal"
    ret = execute_remote_cmd(host_ip, 'root',command)#Returns e.g. MemTotal:       32934972 kB
    ram_in_kb = ret[ret.index(' '):-3].strip()
    ram_in_gb = int(round(int(ram_in_kb)/(1024*1024),0))
    return ram_in_gb


def get_host_hdd(host_ip):
    import math
    command = "fdisk -l | egrep 'Disk.*bytes' | awk '{ sub(/,/,\"\"); sum +=$3;} END {print sum}'"
    ret = execute_remote_cmd(host_ip, 'root',command)#Returns e.g. 500.1 kB
    current.logger.debug("Host HDD is %s" %ret)
    hdd_in_gb = int(math.ceil(float(ret)))
    return hdd_in_gb


def check_host_service_status(host_ip):
    #Check libvirt status
    command = "status libvirt-bin | grep -w 'running' | wc -l"
    ret = execute_remote_cmd(host_ip, 'root',command)
    if ret == 0 :
        current.logger.error("Critical: Libvirt service is not running on host " + host_ip)
        return False
    #Check OVS status
    command = "service openvswitch-switch status | grep -w 'running' | wc -l"
    ret = execute_remote_cmd(host_ip, 'root',command)
    if ret == 0 :
        current.logger.error("Critical: OVS switch is not running on host " + host_ip)
        return False
    return True
    
def host_status_sanity_check():
    for host in current.db().select(current.db.host.ALL):
        if host.status != HOST_STATUS_MAINTENANCE:
            host_status=check_host_status(host.host_ip)
        if(host_status != host.status):
            current.logger.debug("Changing status of " + host.host_name +" to " + str(host_status))
            host.update_record(status=host_status)
    current.db.commit()

def has_running_vm(host_ip):
    found=False
    if not check_host_status(host_ip):
        current.logger.debug("Host %s is down" %(host_ip))
        return False
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+host_ip+'/system')
        domains=[]
        for domain_id in conn.listDomainsID():
            domains.append(conn.lookupByID(domain_id))
        
        for name in conn.listDefinedDomains():
            domains.append(conn.lookupByName(name))

        for dom in domains:
            current.logger.debug("Checking "+str(dom.name()))
            if(dom.info()[0] != VIR_DOMAIN_SHUTOFF):
                found=True

        domains=None
        conn.close()
    except:
        current.logger.exception('Exception: ')
    return found

#Move all dead vms of this host to the host first in list of hosts
def move_all_dead_vms(host_ip):

    current.logger.debug("\nMoving all dead vms of this host "+host_ip+"\n-----------------------------------\n")
    if not check_host_status(host_ip):
        current.logger.debug("\nHost is down\n")
        return
    if(has_running_vm(host_ip)):
        current.logger.debug("All the vms on this host are not Off")
        return
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+host_ip+'/system')
        domains=[]
        host1 = current.db.host(status=HOST_STATUS_UP)
        for domain_id in conn.listDomainsID():
            domains.append(conn.lookupByID(domain_id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            current.logger.debug("Moving "+str(dom.name())+" to "+host1['host_name'])
            vm_details = current.db.vm_data(vm_identity=dom.name())
            migrate_domain(vm_details['id'], host1['id'])
        current.logger.debug("All the vms moved Successfully. Host is empty")
        current.logger.debug(commands.getstatusoutput("ssh root@"+host_ip+" virsh list --all"))
        domains=None
        names=None
        conn.close()
    except:
        current.logger.exception('Exception: ')
    return

#Save Power, turn off extra hosts and turn on if required
def host_power_operation():
    current.logger.debug("\nIn host power operation function\n-----------------------------------\n")
    livehosts = current.db(current.db.host.status == HOST_STATUS_UP).select()
    masterhost = livehosts[0].ip
    freehosts=[]
    try:
        for host in livehosts:
            if not has_running_vm(host.ip):
                freehosts.append(host.ip)
        freehostscount = len(freehosts)
        if(freehostscount == 2):
            current.logger.debug("Everything is Balanced. Green Cloud :)")
        elif(freehostscount < 2):
            current.logger.debug("Urgently needed "+str(2-freehostscount)+" more live hosts.")
            newhosts = current.db(current.db.host.status==0).select()[0:(2-freehostscount)] #Select only Shutoff hosts
            for host in newhosts:
                current.logger.debug("Sending magic packet to "+host.host_name)
                commands.getstatusoutput("ssh root@"+masterhost+" wakeonlan "+str(host.mac))
        elif(freehosts > 2):
            current.logger.debug("Sending shutdown signal to total "+str(freehostscount-2)+" no. of host(s)")
            extrahosts=freehosts[2:]
            for host in extrahosts:
                current.logger.debug("Moving any dead vms to first running host")
                move_all_dead_vms(host)
                current.logger.debug("Sending kill signal to "+host)
                commands.getstatusoutput("ssh root@"+host+" shutdown -h now")
                host.update_record(status=HOST_STATUS_DOWN)
    except:
        current.logger.exception('Exception: ')
    return

#Put the host in maintenance mode, migrate all running vms and redefine dead ones
def put_host_in_maint_mode(host_id):

    host_data = current.db.host[host_id]
    host_data.update_record(status=HOST_STATUS_MAINTENANCE)

    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+host_data.host_ip+'/system')
        domains=[]
        host1 = current.db.host(status=HOST_STATUS_UP)
        for domain_id in conn.listDomainsID():
            domains.append(conn.lookupByID(domain_id))

        for name in conn.listDefinedDomains():
            domains.append(conn.lookupByName(name))
        
        for dom in domains:
            vm_details = current.db.vm_data(vm_identity=dom.name())
            if vm_details:
                if dom.info()[0] == VIR_DOMAIN_SHUTOFF:    #If the vm is in Off state, move it to host1
                    current.logger.debug("Moving "+str(dom.name())+" to "+host1['host_name'])
                    add_migrate_task_to_queue(vm_details['id'])
                elif dom.info()[0] == VIR_DOMAIN_RUNNING:
                    current.logger.debug("Inserting migrate request for running vm "+str(dom.name())+" to appropriate host in queue")
                    add_migrate_task_to_queue(vm_details['id'], live_migration=True)
        
        move_all_dead_vms(host_data.host_ip)
        conn.close()
    except:
        current.logger.exception('Exception: ')
    return

#Add migrate task to task_queue
def add_migrate_task_to_queue(vm_id, dest_host_id=None, live_migration=False):
    
    params={'vm_id' : vm_id}
    if dest_host_id:
        params.update({'destination_host' : None})
    if live_migration:
        params.update({'live_migration' : True})
    current.db.task_queue.insert(task_type='Migrate VM',
                         vm_id=vm_id, 
                         requester_id=-1,
                         parameters=params, 
                         priority=1,  
                         status=1)

# Delete Orphan VM
def delete_orhan_vm(vm_name, host_id):
    
    host_details = current.db.host[host_id]
    connection_object = libvirt.open("qemu+ssh://root@" + host_details.host_ip + "/system")
    domain = connection_object.lookupByName(vm_name)
    vm_state = domain.info()[0]
    if (vm_state == VIR_DOMAIN_RUNNING or vm_state == VIR_DOMAIN_PAUSED):
        current.logger.debug("VM is not shutoff. Shutting it off first.")
        domain.destroy()

    domain.undefineFlags(
            VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)

    current.logger.debug(vm_name + " is deleted successfully.")
