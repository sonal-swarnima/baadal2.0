# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from datetime import timedelta
from helper import get_datetime, log_exception, config
from log_handler import logger
from vm_utilization import compare_rrd_data_with_threshold


def process_sendwarning_shutdownvm():

    logger.info("Entering Process send warning mail to shutdown vm........")

    try:
        vmShutDownDays = config.get("GENERAL_CONF", "shutdown_vm_days")
        send_email=0

        for vm_id in db().select(db.vm_event_log.vm_id, distinct=True):
            for vm_details in db(db.vm_event_log.vm_id==vm_id['vm_id']).select(db.vm_event_log.ALL,orderby = ~db.vm_event_log.id,limitby=(0,1)):
                daysDiff=(get_datetime()-vm_details.timestamp).days
                vm_shutdown_time=vm_details.timestamp

                logger.info("VM details are VM_ID:" + str(vm_details['vm_id'])+ "|ID:"+str(vm_details['id'])+"|new_values is:"+str(vm_details['new_value'])+"|daysDiff:" + str(daysDiff)+"|vmShutDownDays:"+vmShutDownDays+"|vm_shutdown_time :"+str(vm_shutdown_time))

                if (vm_details.new_value == "Shutdown" and int(daysDiff)>=int(vmShutDownDays)):
                    vm_users = []
                    vm_name  = ""

                    for user in db((db.user_vm_map.vm_id == vm_details.vm_id) & (db.user_vm_map.vm_id == db.vm_data.id) & (db.vm_data.locked != True) & (db.vm_data.delete_warning_date == None )).select(db.user_vm_map.user_id,db.vm_data.vm_name):
                        send_email=1
                        vm_users.append(user.user_vm_map.user_id)
                        vm_name=user.vm_data.vm_name

                    if (send_email == 1):
                        vm_delete_time=send_email_vm_warning(VM_TASK_WARNING_DELETE,vm_users,vm_name,vm_shutdown_time)
                        logger.debug("Mail sent for vm_id:"+str(vm_details.vm_id)+"|vm_name:"+str(vm_name)+"|delete time:"+ str(vm_delete_time))
                        db(db.vm_data.id == vm_details.vm_id).update(locked=True, delete_warning_date=vm_delete_time) 
                        send_email=0
                    else:
                        logger.debug("Email has already been sent to VM_ID:"+str(vm_details.vm_id))

                else:
                    logger.info("VM:"+str(vm_details.vm_id)+" is not shutdown for: "+str(vmShutDownDays)+"(configured) days")


    except:
        log_exception()
        pass
    finally:
        db.commit()
        logger.debug("EXITING Send warning to shutdown vm........")


def process_sendwarning_unusedvm():

    logger.info("Entering send warning to unused VM........")

    try:
        ''' performing daily checks for network usage '''
        vmCPUThreshold  = config.get("GENERAL_CONF", "cpu_threshold_limit")
        vmreadThreshold = config.get("GENERAL_CONF", "nwRead_threshold_limit")
        vmwriteThreshold = config.get("GENERAL_CONF", "nwWrite_threshold_limit")

        thresholdcontext = dict(CPUThreshold=vmCPUThreshold,
                                ReadThreshold=vmreadThreshold,
                                WriteThreshold=vmwriteThreshold)

        logger.info("checking network usage with threshold values as CPUThreshold is:"+str(thresholdcontext['CPUThreshold'])+" WriteThreshold is :"+str(thresholdcontext['WriteThreshold'])+" ReadThreshold is :"+ str(thresholdcontext['ReadThreshold']))

        vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED) & (db.vm_data.shutdown_warning_date == None) & (db.vm_data.start_time < (get_datetime() - timedelta(days=20)))).select()
        '''check vm should have been created 20days back'''

        for vm in vms:
            logger.info("comparing threshold for the vm "+ str(vm.vm_identity))
            send_email=0
            retVal=compare_rrd_data_with_threshold(vm.vm_identity,thresholdcontext)
            if(retVal == True): 
                vm_users = []
                vm_name  = ""
                for user in db((db.user_vm_map.vm_id == vm.id) & (db.user_vm_map.vm_id == db.vm_data.id) & (db.vm_data.shutdown_warning_date == None )).select(db.user_vm_map.user_id,db.vm_data.vm_name):
                    send_email=1
                    vm_users.append(user.user_vm_map.user_id)
                    vm_name=user.vm_data.vm_name

                if (send_email == 1):
                    vm_shutdown_time=send_email_vm_warning(VM_TASK_WARNING_SHUTDOWN,vm_users,vm_name,'')
                    logger.debug("Mail sent for vm_name:"+str(vm_name)+"|shutdown time returned from the function:"+ str(vm_shutdown_time))
                    db(db.vm_data.id == vm.id).update(shutdown_warning_date=vm_shutdown_time)
                    db.commit()
                else:
                    logger.debug("Warning Email to use the VM has already been sent to VM_ID:"+str(vm.id))
            else:
                logger.info("VM:"+str(vm.id)+" is in use.. no need to send shutdown warning mail ...")
    except:
        log_exception()
        pass
    finally:
        db.commit()
        logger.debug("EXITING send warning to unused VM........")

def process_shutdown_unusedvm():
   
    logger.info("ENTERING SHUTDOWN UNUSED VM ........")

    try:
        # Fetch all the VM's which are locked and whose shutdown_warning_date=today. 
        vmCPUThreshold  = config.get("GENERAL_CONF", "cpu_threshold_limit")
        vmreadThreshold = config.get("GENERAL_CONF", "nwRead_threshold_limit")
        vmwriteThreshold = config.get("GENERAL_CONF", "nwWrite_threshold_limit")

        thresholdcontext = dict(CPUThreshold=vmCPUThreshold,
                                ReadThreshold=vmreadThreshold,
                                WriteThreshold=vmwriteThreshold)

        for vmData in db(db.vm_data.shutdown_warning_date!=None).select(db.vm_data.ALL):
            daysDiff=(get_datetime()-vmData.shutdown_warning_date).days
            if(daysDiff >= 0):
                '''Again compare the data for last 20 days from rrd logs '''
                retVal=compare_rrd_data_with_threshold(vmData.vm_identity,thresholdcontext) 
                logger.info(" DaysDiff are "+str(daysDiff)+" return value is "+str(retVal))
                if(retVal == True):
                    logger.info("Need to shutdown the VM ID:"+str(vmData.id))
                    add_vm_task_to_queue(vmData.id,VM_TASK_DESTROY)
                    # make an entry in task queue so that scheduler can pick up and shutdown the VM.
                else:
                    logger.info("No Need to shutdown the VM ID:"+str(vmData.id)+" as VM is in use now. ")
             
                #update db to clean the shutdown warning date 
                db(db.vm_data.id == vmData.id).update(shutdown_warning_date=None)
            else:
                logger.info("No need to process purge for the VM:"+str(vmData.id))
    except:
        log_exception()
        pass
    finally:
        db.commit()
        logger.debug("EXITING SHUTDOWN UNUSED VM ........")


def process_purge_shutdownvm():

    logger.info("ENTERING PURGE SHUTDOWN VM ........") 
    vmShutDownDays = config.get("GENERAL_CONF", "shutdown_vm_days")

    try:
        # Fetch all the VM's which are locked and whose delete warning date is not null. 
        for vm_data in db(db.vm_data.locked == True and db.vm_data.delete_warning_date!=None).select(db.vm_data.ALL):
            daysDiff=0
            daysDiff=(get_datetime()-vm_data.delete_warning_date).days
            if(daysDiff >=0 ):
                for vm_details in db(db.vm_event_log.vm_id==vm_data.id).select(db.vm_event_log.ALL,orderby = ~db.vm_event_log.id,limitby=(0,1)):
                    daysDiff=(get_datetime()-vm_details.timestamp).days
                    if(vm_details.new_value == "Shutdown" and int(daysDiff)>=int(vmShutDownDays)):
                        logger.info("Need to delete the VM ID:"+str(vm_data.id)) 
                        add_vm_task_to_queue(vm_data.id,VM_TASK_DELETE)
                        # make an entry in task queue so that scheduler can pick up and delete the VM.
                    else:
                        logger.info("No need to delete the VM ID:"+str(vm_data.id)+" as it is in use now. ")
                        db(db.vm_data.id == vm_details.vm_id).update(locked='F',delete_warning_date=None)
            else:
                logger.info("No need to process shutdown VM :"+str(vm_data.id))
    except:
        log_exception()
        pass
    finally:
        db.commit()
        logger.debug("EXITING PURGE SHUTDOWN VM ........")

