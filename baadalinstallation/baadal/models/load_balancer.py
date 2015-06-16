# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db,request, cache
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

from helper import get_datetime, log_exception, is_pingable, execute_remote_cmd, config
from vm_utilization import get_host_resources_usage,get_host_mem_usage,get_dom_mem_usage
from log_handler import logger, rrd_logger
from vm_helper import migrate_domain

from gluon import current
current.cache = cache

from operator import itemgetter

import os


def loadbalance_vm(host_list=[],vm_list=[]):
    if (host_list == [] and vm_list == []):
       logger.debug("host list or vm list is empty")
       return False
    else:
        try:
            shutdown_vm_list={} 
            guests_map={}
            for guest in vm_list:
                guests_map[guest] = False
  
            for vm_details in guests_map:
                if (vm_details.status == VM_STATUS_SHUTDOWN or vm_details.status == VM_STATUS_SUSPENDED):
                    logger.debug("VM: "+vm_details.vm_name+" is shutoff, no need to migrate VM")
                    shutdown_vm_list[vm_details] = False
                elif (vm_details.status == VM_STATUS_RUNNING):
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

        except:
            logger.exception('Exception in process_schedule_vm') 
            return False

def check_affinity(vm_details,host):
    try:
        logger.debug("host is : " + str(host))
        flag=vm_details.affinity_flag
        logger.debug("affinity flag value is : " + str(flag))
        if flag == 1:
           logger.debug("host value is : " + str(vm_details.vm_identity))
           host_list=get_host_details(vm_details.vm_identity)
           for key in host_list['available_hosts']:
                if host['host_name'] in host_list['available_hosts'][key]:
                   return True 
                else :
                   return False 
        else:
          return True
    except:
        logger.exception('Exception in check_affinity') 
        return False
        

def schedule_vm(vm_details,host,live_migration):
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


def find_host_and_guest_list():

    logger.debug("Entering into find_host_and_guest_list")
    host_usage = {}
    host_usage_map = {}
    host_ram_usage_map = {}
    host_list = []
    hosts = db(db.host.id>0).select(db.host.ALL)
    #call memhog to retreive the memory back
    #overload_memory()
    for host in hosts:
        logger.debug(host.host_ip.private_ip)
        host_usage = get_host_resources_usage(host.host_ip.private_ip)
        host_usage_map[host] = host_usage
        host_ram_usage_map[host] = (host['RAM']*1024*1024*1024) - host_usage['ram']

    sorted(host_ram_usage_map.items(), key=itemgetter(1),reverse=True)

    guest_list = db(db.vm_data.id>0).select(db.vm_data.ALL)
        #logger.debug("Guest_list is"+str(guest_list))
    logger.debug(host_ram_usage_map)

    return (host_ram_usage_map.keys(),guest_list)

def is_same_host(guest_info,host_info):
    try:
        logger.debug("Entering into is_same_host")
        host_ip = host_info['host_ip'].private_ip
        guest_present_host = guest_info['host_id'].host_ip.private_ip
 
        if(host_ip == guest_present_host): 
            return False
        else:
	    return True
          
    except:
        logger.exception('Exception in is_same_host')
        return False

def is_migration_possible(guest_info,host_info):
    try:
        logger.debug("Entering into is_migration_possible")
        #host mem usage used_mem_in_kb
        host_ip = host_info['host_ip'].private_ip
        host_mem_utilization = get_host_mem_usage(host_ip)
        host_mem_utilization = host_mem_utilization * 1024

        # guest mem usage
        guest_present_host = guest_info['host_id'].host_ip.private_ip
        guest_mem_utilization = get_dom_mem_usage(guest_info['vm_identity'], guest_present_host)
        host_utilization_if_migrated = (host_mem_utilization + guest_mem_utilization)/(host_info['RAM']*1024*1024*1024)

        host_utilization_if_migrated = host_utilization_if_migrated * 100
        logger.debug("host_mem_utilization is " +str(host_mem_utilization))
        logger.debug("guest_mem_utilization is " +str(guest_mem_utilization))
        logger.debug("host_utilization_if_migrated is " +str(host_utilization_if_migrated))
   
        if(host_utilization_if_migrated > 90):
            return False
        else:
            return True
    except:
        logger.exception('Exception in is_migration_possible')
        return False

