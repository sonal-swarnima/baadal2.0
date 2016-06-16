# -*- coding: utf-8 -*-
###################################################################################
""" load_balancer.py: This module manages periodic load balancing of hosts on the
    basis of the recorded resource utilization by VMs.
"""
from gluon import current
from libvirt import *
from helper import execute_remote_cmd
from host_helper import HOST_STATUS_UP
from log_handler import logger, rrd_logger
from operator import itemgetter
from vm_helper import migrate_domain,getVirshDomain
import libvirt, os
from vm_utilization import get_host_resources_usage, get_host_mem_usage, \
    get_dom_mem_usage



def loadbalance_vm(host_list=[],vm_list=[]):
    if (host_list == [] and vm_list == []):
        logger.debug("host list or vm list is empty")
        return False
    else:
        host_list_for_host_status = host_list[:]
        try:
            shutdown_vm_list={} 
            guests_map={}
            for guest in vm_list:
                guests_map[guest] = False
  
            for vm_details in guests_map:
                if (vm_details.status == current.VM_STATUS_SHUTDOWN or vm_details.status == current.VM_STATUS_SUSPENDED):
                    logger.debug("VM: "+vm_details.vm_name+" is shutoff, no need to migrate VM")
                    shutdown_vm_list[vm_details] = False
                elif (vm_details.status == current.VM_STATUS_RUNNING):
                    logger.debug("VM:"+vm_details.vm_name+" is running, need live migration")
                    for host in host_list:
                        if (check_affinity(vm_details,host) and schedule_vm(vm_details,host,1)):
                            logger.debug(host)
                            logger.debug("VM:"+vm_details.vm_name+" migration is successful on the host "+ str(host['host_ip'].private_ip))  
                            guests_map[vm_details] = True
                            break
                        else: 
                            logger.debug("VM:"+vm_details.vm_name+" failed to migrate on the host "+str(host['host_ip'].private_ip)) 

            #move the shutdown VM to the least loaded host.
            for shutdown_vm in shutdown_vm_list:
                for host in host_list:
                    if (check_affinity(shutdown_vm,host) and schedule_vm(shutdown_vm,host,0)):
                        logger.debug(host)
                        logger.debug("VM migration successful on the host "+ str(host['host_ip'].private_ip))
                        shutdown_vm_list[shutdown_vm]= True 
                        break
                    else:
                        logger.debug("VM failed to migrate on the host "+ str(host['host_ip'].private_ip)) 


            logger.debug("loadbalance_vm is done....")
            shutdown_nonactive_hosts(host_list_for_host_status)
        except:
            logger.exception('Exception in process_schedule_vm') 
            return False

def check_affinity(vm_details,host):
    """
    Check affinity of vm with host. Affinity gives list of host on which vm can be migrated.
    """
    try:
        logger.debug("Entering into check_affinity for vm:"+str(vm_details.vm_name)) 
        if(vm_details.vm_name in ('superopt','largevm','NeuroImaging2','sniper-big','csl788-1','NeuroImaging','sniper-large', 'mooc_6')):
            return False 
        else:
            return True 
    except:
        logger.exception('Exception in check_affinity') 
        return False
        

def schedule_vm(vm_details,host,live_migration):
    """
    Migrate a vm on host if affinity is correct and migration is possible.
    """
    try:
        logger.debug("Entering into scheduleVM")
        retVal=True
       
        retVal=is_same_host(vm_details,host)
        if (retVal == False):
            logger.debug("VM is on the same host")
            return False

        if (live_migration == 1):
            retVal=is_migration_possible(vm_details,host)
         
        if (retVal == True):
            logger.debug("Going to migrate VM:"+vm_details.vm_name+ " on host: "+ str(host['host_ip'].private_ip))
            ret=migrate_domain(vm_details.id,host.id,live_migration) 
            #ret=(TASK_QUEUE_STATUS_SUCCESS,'msg') #when uncomment this, comment the line above
            logger.debug("Value returned from migrate_domain is:"+str(ret[0]))
            if(ret[0] == TASK_QUEUE_STATUS_SUCCESS):
                return True
            else:
                return False
        else:
            logger.debug("VM:"+vm_details.vm_name+" cannot be migrated to host:"+str(host['host_ip'].private_ip))  
            return False
    except:
        logger.exception('Exception in scheduleVM')         
        return False

def get_memhog_usage(host_ip):
    """
    Returns memory used by memhog process so that it can be added to available memory.
    """
    logger.debug("Entering into getmemhog_usage") 
    cmd = "output=`ps -ef --sort=start_time | grep 'memhog' | grep -v grep | awk '{print $2}'`;smem -c 'pid pss'| grep $output | awk '{print $2}'"
    output = execute_remote_cmd(host_ip, "root", cmd, None, True) 
    if not output : 
        return 0
    else:
        #logger.debug("For host:"+str(host_ip)+" PSS Value from memhog="+str(output))
        return (int(output[0])*1024)


def find_host_and_guest_list():
    """
    Returns host list in descending order of available memory and guest list.
    """
    logger.debug("Entering into find_host_and_guest_list")

    host_usage = {}
    host_ram_usage_map = {}

    hosts = current.db(current.db.host.id>0 and current.db.host.status == HOST_STATUS_UP).select(current.db.host.ALL)
    for host in hosts:
        logger.debug("host_private_ip is "+ str(host.host_ip.private_ip))
        host_usage = get_host_resources_usage(host.host_ip.private_ip)
        memhog_usage = get_memhog_usage(host.host_ip.private_ip)
        logger.debug("memhog_usage and host_usage are:"+str(memhog_usage)+"::"+str(host_usage))
        host_ram_usage_map[host] =(( (host['RAM']*1024*1024*1024) - host_usage['ram']) + memhog_usage )

    sorted_host_list=sorted(host_ram_usage_map.items(),key=itemgetter(1),reverse=True)

    guest_list = current.db(current.db.vm_data.id>0).select(current.db.vm_data.ALL)
    logger.debug("Guest_list is :"+str(guest_list))
    logger.debug("sorted list is :" + str(sorted_host_list))

    return (map(itemgetter(0),sorted_host_list),guest_list)


def is_same_host(guest_info,host_info):
    """
    Checks guest_present_host and selected host are same or not.
    """
    try:
        logger.debug("Entering into is_same_host")
        host_ip = host_info['host_ip'].private_ip
        guest_present_host = guest_info['host_id'].host_ip.private_ip
 
        return False if(host_ip == guest_present_host) else True
          
    except:
        logger.exception('Exception in is_same_host')
        return False

def is_migration_possible(guest_info,host_info):
    """
    Checks whether migration on the host is possible or not and criteria is host utilization should not 
    go above 90% after migration.
    """
    try:
        logger.debug("Entering into is_migration_possible")
        #host mem usage used_mem_in_kb

        host_ip = host_info['host_ip'].private_ip
        host_mem_utilization = get_host_mem_usage(host_ip)
        memhog_usage = get_memhog_usage(host_ip)

        logger.debug("For host:"+str(host_ip)+" PSS Value from memhog="+str(memhog_usage))
        host_mem_utilization=((host_mem_utilization * 1024 ) - memhog_usage) 

        logger.debug("For host:"+str(host_ip)+" host_mem_utilization="+str(host_mem_utilization))

        # guest mem usage
        guest_present_host = guest_info['host_id'].host_ip.private_ip 
        guest_domain = getVirshDomain(guest_info)  # @UndefinedVariable
        guest_mem_utilization = get_dom_mem_usage(guest_domain, guest_present_host)
        host_utilization_if_migrated = (host_mem_utilization + guest_mem_utilization)/(host_info['RAM']*1024*1024*1024)

        host_utilization_if_migrated = host_utilization_if_migrated * 100
        logger.debug("host_mem_utilization is " +str(host_mem_utilization))
        logger.debug("guest_mem_utilization is " +str(guest_mem_utilization))
        logger.debug("host_info['RAM']*1024*1024*1024 is " +str(host_info['RAM']*1024*1024*1024))
        logger.debug("host_utilization_if_migrated is " +str(host_utilization_if_migrated))
   
        if(host_utilization_if_migrated > 90):
            return False
        else:
            return True
    except:
        logger.exception('Exception in is_migration_possible')
        return False

def shutdown_nonactive_hosts(host_list):
    """
    Shutdown the host with no vm.
    """
    logger.debug(host_list)

    for host in host_list:
        host_ip = host.host_ip.private_ip
        logger.debug("host_ip %s" %host_ip)
        hypervisor_conn = libvirt.openReadOnly("qemu+ssh://root@" + host_ip + "/system")  # @UndefinedVariable
        rrd_logger.debug(hypervisor_conn.getHostname())

        active_dom_ids  = hypervisor_conn.listDomainsID()
        rrd_logger.info(active_dom_ids)
        all_dom_objs    = hypervisor_conn.listAllDomains()
        rrd_logger.info(all_dom_objs)
        rrd_logger.info(type(all_dom_objs))
        if not all_dom_objs:
            logger.debug("Host1 %s is free...Shutting it down " %str(host.host_ip.private_ip))
