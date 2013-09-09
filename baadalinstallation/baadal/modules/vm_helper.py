# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

import re, os, ast, sys, math, time, commands, shutil, paramiko, traceback, random, libvirt
import xml.etree.ElementTree as etree
from libvirt import *
from helper import *

def install(parameters):
 
    vmid = parameters['vm_id']
    current.logger.debug(vmid)
    try:
        current.db(current.db.vm_data.id == vmid).update( host_id = 1, \
                                      datastore_id = 1, \
                                      public_ip = '10.20.18.56', \
                                      private_ip = '127.0.0.1', \
                                      vnc_port = 5656, \
                                      mac_addr = '10:20:30:40:50:60', \
                                      start_time = get_datetime(), \
                                      current_run_level = 3, \
                                      last_run_level = 3,\
                                      total_cost = 0, \
                                      status = current.VM_STATUS_RUNNING)
        message = "VM is installed successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)


# Function to start a vm
def start(parameters):
    
    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING)  
        message = vm_details.vm_name + " is started successfully."
        current.logger.debug(message) 
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to suspend a vm
def suspend(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SUSPENDED)       
        message = vm_details.vm_name + " is suspended successfully." 
        current.logger.debug(message)       
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to resume a vm
def resume(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    try:
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_RUNNING) 
        message = vm_details.vm_name + " is resumed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to destroy a vm forcefully
def destroy(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        current.db(current.db.vm_data.id == vmid).update(status = current.VM_STATUS_SHUTDOWN) 
        message = vm_details.vm_name + " is destroyed successfully."
        current.logger.debug(message)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to delete a vm
def delete(parameters):

    vmid = parameters['vm_id']
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        current.logger.debug(str(vm_details.status))
        if (vm_details.status == current.VM_STATUS_RUNNING or vm_details.status == current.VM_STATUS_SUSPENDED):
            current.logger.debug("Vm is not shutoff. Shutting it off first.")
        current.logger.debug("Starting to delete it...")
        message = vm_details.vm_name + " is deleted successfully."
        current.logger.debug(message)
        current.db(current.db.vm_data.id == vmid).delete()
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)

# Function to migrate a vm to a new host
def migrate(parameters):

    vmid = parameters['vm_id']
    current.logger.debug("vmid :" + str(vmid))
    destination_host_id = parameters['destination_host']
    current.logger.debug("destination host id :" + str(destination_host_id))
    destination_host_ip = current.db(current.db.host.id == destination_host_id).select(current.db.host.host_ip).first()['host_ip']
    current.logger.debug("destination_host_ip " + str(destination_host_ip))

    if 'live_migration' in parameters:
        flags = current.MIGRATE_LIVE|current.MIGRATE_PEER2PEER|current.MIGRATE_TUNNELLED|current.MIGRATE_PERSIST_DEST|current.MIGRATE_UNDEFINE_SOURCE
    else:
        flags = current.MIGRATE_PEER2PEER|current.MIGRATE_TUNNELLED|current.MIGRATE_PERSIST_DEST|current.MIGRATE_UNDEFINE_SOURCE
    current.logger.debug("Flags: " + str(flags))       
    vm_details = current.db(current.db.vm_data.id == vmid).select().first()
    current.logger.debug(str(vm_details))
    try:
        current.logger.debug("Migrated successfully..")
        current.db(current.db.vm_data.id == vmid).update(host_id = destination_host_id)
        vm_count_on_old_host = current.db(current.db.host.id == vm_details.host_id).select().first()['vm_count']
        current.logger.debug("vm count on old host : " + str(vm_count_on_old_host))
        current.db(current.db.host.id == vm_details.host_id).update(vm_count = vm_count_on_old_host - 1)
        vm_count_on_new_host = current.db(current.db.host.id == destination_host_id).select().first()['vm_count']
        current.logger.debug("vm count on new host : " + str(vm_count_on_new_host))
        current.db(current.db.host.id == destination_host_id).update(vm_count = vm_count_on_new_host + 1) 
        message = vm_details.vm_name + " is migrated successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)
    except Exception as e:
        message = e.get_error_message()
        return(current.TASK_QUEUE_STATUS_FAILED, message)
    
def snapshot(parameters):
    return resume(parameters)

    
def revert(parameters):
    return resume(parameters)

    
def delete_snapshot(parameters):
    return resume(parameters)

    
def edit_vm_config(parameters):
    return resume(parameters)

def clone(vmid):

    try:
        current.logger.debug("Updating db")
#         return (current.TASK_QUEUE_STATUS_SUCCESS) 
        return (current.TASK_QUEUE_STATUS_FAILED, "Exception") 
    except:
        current.logger.error("Exception")
        return (current.TASK_QUEUE_STATUS_FAILED, "Exception") 

