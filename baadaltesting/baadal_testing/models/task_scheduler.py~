# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db,request, cache
    from applications.new_baadal_testing.models import *  # @UnusedWildImport
###################################################################################
import logging
import logging.config
logger = logging.getLogger("web2py.app.baadal")
from log_handler import _get_configured_logger
MINUTES=60
import os


def get_datetime():
    import datetime
    logger.debug(datetime.datetime.now())
    return datetime.datetime.now()

def send_task_complete_mail(task_event,status): 
       logger.debug("inside send task complete mail function")
       send_email_to_testing_user(task_event.task_type, task_event.start_time,status,task_event.email_id)
    

def process_task_queue(task_event_id):
    logger.debug("\n ENTERING Testing Task........")    
    logger.debug(task_event_id)    
    task_event_data = db.task_queue_event[task_event_id]
    task_event = db.task_queue[task_event_id]
    logger.debug(task_event_data)
    logger.debug(" ..................... ")
    logger.debug(task_event)
    new_db=mdb.connect("127.0.0.1","root","baadal","baadal")
    cursor1=new_db.cursor()
    cursor1.execute("select task_type,requester_type,ip_addr from task_queue where id= %s",task_event_data.task_id)
    task_queue_data=cursor1.fetchall()
    cursor1.execute("select file_name from task_queue_event where id= %s",task_event_data.id)
    file_name=cursor1.fetchall()
    new_db.commit()
    cursor1.close() 
    logger.debug(task_queue_data)
    task_queue_data=task_queue_data[0]
    logger.debug(task_queue_data)
    attention_time=get_datetime()
    logger.debug(file_name[0][0])
    try:
      attention_time=get_datetime()
      task_event_data.update_record(attention_time=attention_time,status=TASK_QUEUE_STATUS_PROCESSING)
      logger.debug("Starting TASK processing...")
      file_name=file_name[0][0]
      my_logger=_get_configured_logger(file_name)
      task_type=task_queue_data[0]
      ip_address=task_queue_data[2]
      request_type=task_queue_data[1]
      if task_type in "Unit Testing":
         unit_testing(task_event_data.task_id,request_type,ip_address,my_logger)
         end_time=get_datetime()
         my_logger.debug(end_time)
         task_event_data.update_record(end_time=end_time,status=TASK_QUEUE_STATUS_SUCCESS)
         db.commit() 
      if task_type in "System Testing":
         system_testing(request_type,ip_address,my_logger)
         end_time=get_datetime()
         task_event_data.update_record(end_time=end_time,status=TASK_QUEUE_STATUS_SUCCESS)
      if task_type in "Integration Testing":
         integration_testing(request_type,ip_address,my_logger)
         end_time=get_datetime()
         task_event_data.update_record(end_time=end_time,status=TASK_QUEUE_STATUS_SUCCESS)
      if task_type in "Database Dependent Testing":
         database_dependent_testing(request_type,ip_address,my_logger)
         end_time=get_datetime()
         task_event_data.update_record(end_time=end_time,status=TASK_QUEUE_STATUS_SUCCESS)
    except:        
        end_time=get_datetime()
        task_event_data.update_record(end_time=end_time,status=TASK_QUEUE_STATUS_FAILED)
        #send_task_complete_mail(task_event_data,status)
    finally:
        db.commit()



from gluon.scheduler import Scheduler
task_scheduler = Scheduler(db, dict(testing_task=process_task_queue))


def schedule_task(task_type,task_event_id,email_id,requester_id,server_name,test_case_list):
    print "inside schedule_task"
    print test_case_list
    file_name=str(task_event_id) + str(requester_id)
    task_event_id = db.task_queue_event.insert(task_type=task_type,status=TASK_QUEUE_STATUS_PENDING,task_id=task_event_id,email_id=email_id,requester_id=requester_id,file_name=file_name,server_name=server_name,test_case_list=test_case_list)                            
    task_scheduler.queue_task('testing_task', pvars = dict(task_event_id = task_event_id),start_time = request.now,timeout=120*MINUTES)
    task_event_data = db.task_queue_event[task_event_id]
    

def unit_testing(task_id,request_type,ip_address,my_logger):
    my_logger.debug("inside unit testing...")
    request_type=request_type.replace('|',',')
    request_type=request_type[1:]
    request_type=request_type[:-1]
    request_type=request_type.split(",")
    for test_case_no in request_type:
    		if test_case_no=="54":
               		for j in range(1,55):
                        	test_case_no=str(j)
                        	test_script(test_case_no,ip_address,my_logger)
    		else:
              		test_script(test_case_no,ip_address,my_logger)
    return                    
    

def system_testing(request_type,ip_address,my_logger):
    my_logger.debug("inside system testing...")
    request_type=request_type.replace('|',',')
    request_type=request_type[1:]
    request_type=request_type[:-1]
    my_logger.debug(request_type)
    request_type=request_type.split(",")
    for test_case_no in request_type:
      	if test_case_no=="16":
           for j in range(2,13):
               test_case_no=str(j)
               sys_test_script(test_case_no,ip_address,my_logger)
      	else:
           sys_test_script(test_case_no,ip_address,my_logger)
    return 	



def integration_testing(request_type,ip_address,my_logger):
    my_logger.debug("inside integration testing...")
    request_type=request_type.replace('|',',')
    request_type=request_type[1:]
    request_type=request_type[:-1]
    my_logger.debug(request_type)
    request_type=request_type.split(",")
    my_logger.debug(type(request_type))
    for test_case_no in request_type:
      	my_logger.debug(test_case_no)
        if test_case_no=='114':
	   for i in range(55,113):  
               test_case_no=str(i)
      	       test_script(test_case_no,ip_address,my_logger)
        else:
          test_script(test_case_no,ip_address,my_logger)
      	
    return


def database_dependent_testing(request_type,ip_address,my_logger):
    my_logger.debug("inside idatabase_dependent testing...")
    request_type=request_type.replace('|',',')
    request_type=request_type[1:]
    request_type=request_type[:-1]
    my_logger.debug(request_type)
    request_type=request_type.split(",")
    for test_case_no in request_type:
        test_script(test_case_no,ip_address,my_logger)
    return
