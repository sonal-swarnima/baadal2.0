# coding: utf8
import os
import thread
import paramiko
import logging
import datetime
import logging.config
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from helper import *
from function import *
from function import check_task_task_report
import libvirt
import commands
import MySQLdb as mdb
from selenium.webdriver.common.keys import Keys
import sys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from log_handler import logger

#creating a my_logger for logging the records
#my_logger = logging.getmy_logger("web2py.app.baadal")

#creating connection to remote system
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

########################### DB connection ############################
def db_connection(host_ip,my_logger):
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(get_context_path(),'static/db.conf'))
    database_user_name=Config.get("db_info","database_user_name")
    database_name=Config.get("db_info","database_name")
    password=Config.get("db_info","password")
    db=mdb.connect(host_ip,database_user_name,password,database_name)
    my_logger.debug(db)
    return db

#################################################################################################################
#                                       The main test function  for unit testing                                            #
#################################################################################################################
vm_status=2		
def test_script(test_case_no,host_ip,my_logger):
    
    baadal_path="https://"+str(host_ip)+"/baadal"
    my_logger.debug("Teesting has been started and test case no is : "+ str(test_case_no))
    baadal_db=db_connection(host_ip,my_logger)
    my_logger.debug(baadal_db)    
    root = xml_connect()
    num=int(test_case_no)
    vm_status=2
    
    if root[num-1].get("id")==test_case_no:

        i=num-1
        vm_name=""
        for j in xrange(0,len(root[i])):
            temp_value=1
            driver = webdriver.Firefox()#connect to selenium server
            driver.implicitly_wait(10)
            page_present=driver.get(baadal_path) #url of the page to be hit 
            if page_present!="None":
            	driver.find_element_by_link_text(root.get("href")).click()
            	image=0
            	for k in xrange(0,len(root[i][j])):
                    if vm_status>1:
                        
                        xml_parent=root[i]
                        xml_child=root[i][j]
                        xml_sub_child=root[i][j][k]
                        
                    	if field_type=="input": #checking for text fields
                        	vm_name1=isInput(driver,xml_sub_child,my_logger)
                      
                    	elif field_type=="read_only": #checking for submit button
                        	isReadOnly(driver, xml_parent,xml_child,xml_sub_child,my_logger)
						
                    	elif field_type=="submit": #checking for submit button
                        	time.sleep(3)
                        
                        	isSubmit(driver, xml_parent,xml_child,xml_sub_child,my_logger)

                    	elif field_type=="scroll":#scrolling the page up/down
                        	isScroll(driver,xml_sub_child,my_logger)
                            
                    	elif field_type=="clear":#Clearing text from textarea 
                        	isClear(driver,xml_sub_child,my_logger)  
                        	
                        elif field_type=="href":
                            isHref(driver,xml_sub_child,xml_child,my_logger)#clicking on the hyper link
                    
                    	elif field_type=="select":
                        	temp=isSelect(driver,xml_sub_child,temp_value,my_logger)# selecting from dropdown menu
                    
                    	elif field_type=="sanity_table":
                        	isSanityCheck(driver, xml_parent, xml_child, xml_sub_child,baadal_db,my_logger)# checking for data in  sanity table
			 	
                    	elif field_type=="table":
                            my_logger.debug("field type is table")
                            isTable(driver,xml_parent,xml_child,xml_sub_child,baadal_db,my_logger)#checking for data in table
                         
                    	elif field_type=="img":#checking for setting image
                        	table_path=xml_sub_child.get("path")
                        	vm_name2=isImage(driver,xml_child,xml_sub_child,table_path,baadal_db,my_logger)
				
                    	elif field_type=="check_tables":#cheking for host table
                        	isCheckTable(driver,xml_parent,xml_child,xml_sub_child,baadal_db,my_logger)
                
                    	elif field_type=="wait":
                        	isWait(driver,xml_parent,xml_child,xml_sub_child,my_logger)#checking for data in table
                        elif field_type=="vm_perf":
			        my_logger.debug("qwerty")
			        vm_check_host(driver,xml_child,xml_sub_child,xml_parent,vm_name,my_logger)

			elif field_type=="graph_perf":
			        print "qwerty"
			        #graph_perf(driver,xml_child,xml_sub_child,vm_name,my_logger)
                                vm_ip=1
			        graph_test(driver,vm_ip,vm_name,xml_sub_child,xml_child,my_logger)
                    	elif field_type=="check_data":
                        	isCheckdata(driver,xml_parent,xml_child,xml_sub_child,vm_name,baadal_db,my_logger)#checking for data in table
                 
                    	elif field_type=="task_table":
                                my_logger.debug("task table checking ")
                         	operation_name=xml_sub_child.text
                                my_logger.debug("operation name is : " + str(operation_name))
                         	vm_status=check_data_in_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,my_logger)#checking for data in table
                
                    	elif field_type=="attach_disk":
                        	operation_name=xml_sub_child.text
                        	attack_disk(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)#checking for data in table
                        
                        elif field_type=="idompotent":
                            maintain_idompotency(driver,xml_sub_child,xml_child,my_logger)				          				          				
                    	else:
                        	logging.debug("report problem") #logging the report
                    	
                    	if k==5:
                        	vm_name=vm_name1
            	driver.close()#disconnect from server        
                if vm_status==0:
                
                    my_logger.debug("Your VM has not created.Please Check it!!!Its in pending task table!!!Either Scheduler is not working or Host is down!!!")
                if vm_status==1:
                	my_logger.debug("Your VM has not created.Please Check it!!!Its in failed task table!!!")
                	
            else:
                my_logger.debug("Cannot connect to controller.Please check controller")


#performing   operation on vm        
def other_operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    operation_name
    xpath=task_path(xml_sub_child)
    
    path="//*[@title='" + str(xpath) + "']"
    if isElementPresent(driver,xml_child,path):
	#vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
	#total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger)
	driver.find_element_by_link_text("All VMs").click()
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
        driver.find_element_by_xpath(path).click()
        field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
	
        result=message_in_db(xml_sub_child,my_logger)
	limit=1
	
        print_result(field_text,result,xml_child,my_logger)
    else:
        my_logger.debug(":This VM has been deleted and its in pending task table,So this functionality has been disabled !!!!!!") 
	limit=0	
    return limit

#selecting operation to be perform    
def click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name,baadal_db,my_logger): 
    my_logger.debug("Clicking on operation perform on a VM")   
    op_name=xml_sub_child.get("op") 
    my_logger.debug("op_name is : " + str(op_name))      
    if op_name=="user_details":
        limit=op_user(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger)
    elif op_name=="Delete":
        limit=op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name in {"revert_to_snapshot","delete_snapshot","snapshot"}:         
        limit=op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="delete_user_vm": 
        limit=op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name,baadal_db,my_logger)
    elif op_name in {"attach_extra_disk","clone_vm"}:
        op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="edit_vm_config":
        op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    elif op_name=="migrate_vm":
        limit=op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)     
    else:
        limit=other_operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    return limit   


def vm_mode(xml_child,xml_sub_child,xml_parent,driver,my_logger):
    vm_info=vm_list(xml_child,xml_sub_child,driver,my_logger)
    my_logger.debug(vm_info)
    if vm_info!={}:
        vm_id=vm_info['vm_id']
        vm_name=vm_info['vm_name']
        owner_name=vm_info['user_name']
	my_logger.debug("VM info" + str(vm_info))   
        vm_mode_op(xml_child,xml_sub_child,xml_parent,driver,vm_name,vm_id,owner_name,my_logger)
    else:
        my_logger.debug(xml_sub_child.get("print_mode"))
	test_script(48)
    return

def vm_list(xml_child,xml_sub_child,driver,my_logger):
    vm_info={}
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    select_testing_user(driver,my_logger)
    if isTablePresent(driver,xml_child,path_col):
        countc=0
        c_count=0
        r_count=0
        select_row=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Host":
                host_no=count
	    if hdata.text=="Private IP":
                private_ip_no=count
	    if hdata.text=="vCPUs":
                vcpu_no=count
	    if hdata.text=="Status":
                status_no=count
            if hdata.text=="RAM":
                ram_no=count
   	    if hdata.text=="Organisation":
                organisation_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_name=data.text
            if c_count%col_count==user_name_no:
                my_logger.debug("data text" + str(data.text))
                if data.text in username_list:
                    user_name=data.text
                    select_row=1
            if c_count%col_count==status_no:
                status=data.text
            if c_count%col_count==host_no:
		host=data.text
	    if c_count%col_count==private_ip_no:
		private_ip=data.text
	    
	    if c_count%col_count==vcpu_no:
		vcpu=data.text
	    if c_count%col_count==ram_no:
		ram=data.text
            if (c_count%col_count==col_count-1):
	        if select_row:
                    if (str(status)==xml_sub_child.get("status")):
                        field_data=driver.find_elements_by_xpath(path_row)
                        vm_id=data.get_attribute("id")
			vm_info['vm_id']=vm_id
    			vm_info['vm_name']=vm_name
    			vm_info['user_name']=user_name
    			vm_info['host']=host
    			vm_info['private_ip']=private_ip
    			vm_info['vcpu']=vcpu
    			vm_info['ram']=ram
                        countc+=1
                        break
            c_count+=1
    if countc==0:
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        
    
    print vm_info
    return vm_info

def get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger):
    time.sleep(10)
    driver.find_element_by_link_text("My VMs").click()
    vm_info={}
    vm_id=0
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    driver.refresh()
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countc=0
        c_count=0
        r_count=0
        select_vm=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Host":
                host_no=count
	    if hdata.text=="Public IP":
                public_ip_no=count
            if hdata.text=="Private IP":
                private_ip_no=count
	    if hdata.text=="vCPUs":
                vcpu_no=count
            if hdata.text=="RAM":
                ram_no=count
   
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        my_logger.debug("collected header info")
        for data in field:
            if c_count%col_count==vm_name_no:
		my_logger.debug(vm_name)
		my_logger.debug(data.text)
                if str(vm_name)==str(data.text):
		    select_vm=1
		    
            if c_count%col_count==public_ip_no:
		public_ip=data.text
	    if c_count%col_count==private_ip_no:
		private_ip=data.text
	    if c_count%col_count==status_no:
		status=data.text
	    if c_count%col_count==vcpu_no:
		vcpu=data.text
	    if c_count%col_count==ram_no:
		ram=data.text
	    if c_count%col_count==host_no:
		host=data.text
            if (c_count%col_count==col_count-1):
	        if select_vm:
		    my_logger.debug("VM selected!!!!!!!!")
                    vm_id=data.get_attribute("id")
		    vm_info['vm_id']=vm_id
		    vm_info['public_ip']=public_ip
		    vm_info['private_ip']=private_ip
		    vm_info['vcpu']=vcpu
		    vm_info['ram']=ram
		    vm_info['host']=host
		    vm_info['status']=status
		    
                    
            c_count+=1
      
    else:
	my_logger.debug("No VM exists")
    my_logger.debug("FEtched VM info from MY VMs"+str(vm_info))
    return vm_info

def get_vm_info_frm_alllist(xml_child,xml_sub_child,driver,vm_name,my_logger):
  
    driver.find_element_by_link_text("All VMs").click()
    vm_info={}
    vm_id=0
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countc=0
        c_count=0
        r_count=0
        select_vm=0
	select_user=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Host":
                host_no=count
	    if hdata.text=="Private IP":
                private_ip_no=count
	    if hdata.text=="vCPUs":
                vcpu_no=count
	    if hdata.text=="Status":
                status_no=count
            if hdata.text=="RAM":
                ram_no=count
   	    if hdata.text=="Organisation":
                organisation_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
		
                if str(vm_name)==str(data.text):
		    select_vm=1
	    if c_count%col_count==user_name_no:
		i=xml_child[0].text
		username=usrnm_list[i]
		
                if str(username)==str(data.text):
		    select_user=1
            if c_count%col_count==host_no:
		host=data.text
	    if c_count%col_count==private_ip_no:
		private_ip=data.text
	    if c_count%col_count==vcpu_no:
		vcpu=data.text
	    if c_count%col_count==ram_no:
		ram=data.text
            if (c_count%col_count==col_count-1):
	        if (select_vm) & (select_user):
                    vm_id=data.get_attribute("id")
		    vm_info['vm_id']=vm_id
		    vm_info['private_ip']=private_ip
		    vm_info['vcpu']=vcpu
		    vm_info['ram']=ram
                    vm_info['organisation']=organisation
		    vm_info['host']=host
		    vm_info['public_ip']=host
            c_count+=1
    else:
	my_logger.debug("No VM exists")
    my_logger.debug("FEtched VM info from All VMs"+str(vm_info))
    return vm_info


def get_vm_info_frm_setting(xml_child,xml_sub_child,driver,vm_name,my_logger):
    vm_info={}
    path_col="//table[@id='configuration']/tbody/tr/td"
    path_row="//table[@id='configuration']/tbody/tr"
    path_header="//table[@id='configuration']/thead/tr/th"
    
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countc=0
        c_count=0
        r_count=0
        select_vm=0
	select_user=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="HDD":
                hdd_no=count
            if hdata.text=="Security Domain":
                security_domain_no=count
	    if hdata.text=="Private IP":
                private_ip_no=count
	    if hdata.text=="Public IP":
                public_ip_no=count
	    if hdata.text=="VCPUs":
                vcpu_no=count
	    if hdata.text=="Status":
                status_no=count
            if hdata.text=="RAM":
                ram_no=count
   	    if hdata.text=="Organisation":
                organisation_no=count 
	    if hdata.text=="Operating System":
                operating_sys_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==organisation_no:
		organisation=data.text
	    if c_count%col_count==operating_sys_no:
		operating_sys=data.text
	    if c_count%col_count==security_domain_no:
		security_domain=data.text
	    if c_count%col_count==hdd_no:
		hdd=data.text
            if c_count%col_count==status_no:
		status=data.text
	    if c_count%col_count==private_ip_no:
		private_ip=data.text
	    if c_count%col_count==public_ip_no:
		public_ip=data.text
	    if c_count%col_count==vcpu_no:
		vcpu=data.text
	    if c_count%col_count==ram_no:
		ram=data.text
            if (c_count%col_count==col_count-1):
	        vm_info['security_domain']=security_domain
                vm_info['public_ip']=public_ip
		vm_info['status']=status
		vm_info['private_ip']=private_ip
		vm_info['vcpu']=vcpu
		vm_info['ram']=ram
		vm_info['organisation']=organisation
		vm_info['host']=host
		vm_info['operating_sys']=operating_sys
            c_count+=1
    
    else:
	    my_logger.debug("No VM exists")
    my_logger.debug("FEtched VM info from setting page"+str(vm_info))
    return vm_info


def change_vm_paswd(vm_ip):
    os.system("expect /home/nalini/Desktop/web2py/applications/baadal_11feb/test.expect yes baadal baadal123 "+ str(vm_ip)+ " root exit")
    os.system("exit")
    return

def graph_perf(driver,xml_child,xml_sub_child,vm_name,my_logger):
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger)
    public_ip=vm_info['public_ip']
    
    change_vm_paswd(public_ip)
    graph_test(driver,public_ip,vm_name,xml_sub_child,xml_child,my_logger)
   
def total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    vm_user_list=[]
    path="//table[@id='vm_users']/tbody/tr/td"
    if isTablePresent(driver,xml_child,path,my_logger):
	field=driver.find_elements_by_xpath(path)
	count=0
	for user in field:
	     vm_user_list.insert(count,user.text)
	     count+=1
    my_logger.debug("Total user of this VM is "+ str(vm_user_list))
    return vm_user_list

def select_testing_user(driver):
    my_logger.debug("Searching Baadal in ALL VMs")
    driver.find_element_by_id("search").send_keys("Baadal")
    
    return



def vm_mode_op(xml_child,xml_sub_child,driver,vm_name,vm_id,owner_name,baadal_db,my_logger):
    my_logger.debug("inside vm_mode_op")
    if xml_sub_child.get("task")=="graph":
        graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id,my_logger)
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    else:
        my_logger.debug("inside else")
        op_name=xml_sub_child.get("op")    
        operation_name=op_list[op_name]
        my_logger.debug("operation name is : " + str(operation_name))
        if vm_id!="":
            task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
            driver.find_element_by_link_text("All VMs").click()
            click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
            limit=click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name,baadal_db,my_logger)
            time.sleep(10)
            if limit:
                driver.find_element_by_link_text("Tasks").click()
		task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
		my_logger.debug("Before operations:"+str(task_value))
    		my_logger.debug("After operations:"+str(task_n_value))
	        compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
        else:
            logger.debug(xml_sub_child.get("print_mode"))
    return

def get_snapshot_id(driver,xml_sub_child,xml_child,vm_name,my_logger):
    snap_data=driver.find_elements_by_xpath("//table[@id='vm_snaps']/tbody/tr")
    select_row=0
    snap_id=0
    total_count=3
    for row in snap_data:
	row_data=row.text.split()
        if "User"==row_data[0]:
	    snap_id=row.get_attribute("id")
    my_logger.debug("Snapshot id for this VM is "+ str(snap_id))    
    return snap_id
#Checking data in task table

def check_data_in_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,my_logger):
    my_logger.debug("Checking data in task table......")
    value=0
    driver.find_element_by_link_text("Tasks").click()
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_partial_link_text("Pending Tasks").click()
    task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    my_logger.debug("Before operations:"+str(task_value))
    my_logger.debug("After operations:"+str(task_n_value))
    if task_n_value!=[]:
        value=compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    my_logger.debug("Checked data in task table......")
    return value
   


#performing  edit vm configuration
def op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op")
    driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    driver.find_element_by_xpath("//input[@type='submit']").click()
    result="Your request has been queued!!!"
    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    result=message_in_db(xml_sub_child)
    print_result(field_text,result,xml_child,my_logger)
    return
          

        
#getting user id of a user access to a VM                        
def get_user_id(driver,xml_sub_child,xml_child,vm_name,owner_name,my_logger):
    path="//table[@id='vm_users']/tbody/tr/td"    
    if isElementPresent(driver,xml_child,path,my_logger):   
        user_data=driver.find_elements_by_xpath(path)
    	select_row=0
    	user_id=0
    	for col in user_data:
	    if owner_name==col.text:
	        user_id=col.get_attribute("id")
	    
	        break
    my_logger.debug("User id for this VM is "+ str(user_id))        
    return user_id




#performing add_user operation on vm
def op_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op")
    my_logger.debug("Performing operation on user field........")    
    path="//a[@title='Add User to VM']"

    limit=0
    if isElementPresent(driver,xml_child,path,my_logger):   
        
        time.sleep(20)
        driver.find_element_by_xpath(path).click()
        time.sleep(10)
        if add_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
            if xml_sub_child.get("op_typ")!="cancel_user":
		
                field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
                result=message_in_db(xml_sub_child)
                print_result(field_text,result,xml_child,my_logger)
            	if xml_sub_child.get("name") in vm_mode_type:
              		check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger)
    return limit

#performing delete operation on vm

def op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    limit=0
    my_logger.debug("Deleting testing user VM....")  
    op_name=xml_sub_child.get("op")
    path=xml_sub_child.get("title")
    if isTablePresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
    	click_on_dialogbox(driver,my_logger)
    	click_on_dialogbox(driver,my_logger)
    	field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    	result=message_in_db(xml_sub_child)
    	print_result(field_text,result,xml_child,my_logger)

    else:
	my_logger.debug("This functionality is disabled as the VM has been deleted!!!!!!!!!!")

    return limit

#add additional user to a VM
def add_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    my_logger.debug("Adding user for this VM........")
    isInput_add(driver, xml_sub_child,xml_child,my_logger)
    value=xml_sub_child.get("add_submit")
    isButton_add(driver, xml_sub_child,value,xml_child,my_logger)
    time.sleep(3)
    status=isElementPresent(driver,xml_child,value,my_logger)
    
    if status==1:
        my_logger.error(xml_child.get("value")  + " :User is already VM user")
        
    else:
        val=xml_sub_child.get("add_button")
        isButton_add(driver, xml_sub_child,val,xml_child,my_logger)
       
   
    return status

#performing snapshot operation on vm
def op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    limit=0
    snap=1
    op_name=xml_sub_child.get("op")
    if op_name=="snapshot":
        path="//a[@title='Take VM snapshot']"
    else:
        path=xml_sub_child.get("xpath_snap")
    if isElementPresent(driver,xml_child,path,my_logger):
	result=snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger)
        if op_name=="snapshot":
            driver.find_element_by_xpath(path).click()
        else:
             snapshot_id=get_snapshot_id(driver,xml_sub_child,xml_child,vm_name,my_logger)
	     if snapshot_id:
		     if op_name=="revert_to_snapshot":
		         path="//table[@id='vm_snaps']/tbody/tr/td[@id='"+ str(snapshot_id) + "']/a[@title='Revert to this snapshot']"
		     if op_name=="delete_snapshot":
		     
		         path="//table[@id='vm_snaps']/tbody/tr/td[@id='"+ str(snapshot_id) + "']/a[@title='Delete this snapshot']"
		         print path
		     if isElementPresent(driver,xml_child,path,my_logger):
		        print "in"
                        driver.find_element_by_xpath(path).click()
             else:
		my_logger.debug("No snapshot present")
		snap=0	
        if  (result=="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot.") | (result=="Snapshot request already in queue.") | (result=="") | (snap==0):
            my_logger.debug(result )
	    limit=0
        else:
            limit=1
    else:
    	my_logger.debug(xml_child.get("value") + ":This functioality is Disabled")        
    return limit

#checking snapshot
def snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger):
    op_name=xml_sub_child.get("op")   
    operation_name=op_list[op_name]
    #vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
    #l_snap=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list)
    #length_snap=len(l_snap)

    #driver.find_element_by_link_text("All VMs").click()
    #click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    total_user_snap=total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger)
    result=snap_db_result(xml_sub_child,op_name, total_user_snap,my_logger)
    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    print_result(field_text,result,xml_child,my_logger)
    
    driver.find_element_by_link_text("All VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)    
    total_user_snap=total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger)
    result=snap_db_result(xml_sub_child,op_name, total_user_snap,my_logger)
    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    print_result(field_text,result,xml_child,my_logger)
    return result

def total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name,my_logger):
    total_user_snap=0
    total_snap=0
    total=0
    path="//table[@id='vm_snaps']/tbody/tr"
    if isTablePresent(driver,xml_child,path,my_logger):
	snap_data=driver.find_elements_by_xpath(path)
	print snap_data
	for row in snap_data:
	    print row
            if "User" in row.text:
                total_user_snap+=1
	    

        if op_name=="Migrate VM":
	    total=total_snap
        else:
	     total=total_user_snap

    my_logger.debug("Total snapshot for this VM is :" + str(total))
    return total

#printing result correspondence to snapshot
def snap_db_result(xml_sub_child,op_name, total_user_snap,my_logger):
    print "total_user_snap:" + str(total_user_snap)
    print "max:" + str(xml_sub_child.get("max"))	
    if op_name=="delete_snapshot":
        result="Your delete snapshot request has been queued"
    else:
        if str(total_user_snap)==str(xml_sub_child.get("max")):
            result="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
	elif (op_name=="revert_to_snapshot") & (str(total_user_snap)==str(0)):
	     result="No VM snapshot exists to perform this operation"
        elif (op_name=="revert_to_snapshot") & (total_user_snap>0):
		result="Your revert to snapshot request has been queued"
        else :
            
            result="Your request to snapshot VM has been queued"
    print result
    return result
#list of operation to be performed
op_list={'revert_to_snapshot':'Revert to Snapshot','delete_snapshot':'Delete Snapshot','snapshot':'Snapshot VM','pause_machine':'Suspend VM','Delete':'Delete VM','shutdown_machine':'Stop VM','destroy_machine':'Destroy VM','start_machine':'Start VM','user_details':'Add User','attach_extra_disk':"Attach Disk",'clone_vm':'Clone ','delete_user_vm':'Delete User','adjrunlevel':'Adjust Run Level','edit_vm_config':'Edit VM Config','resume_machine':'Resume VM','migrate_vm':'Migrate VM'}

#performing attach disk operation on vm
def op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    op_name=xml_sub_child.get("op")   
    path="//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"']" 
    if isElementPresent(driver,xml_child,path,my_logger):
    	driver.find_element_by_xpath(path).click()
    	add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    	field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    	result=xml_sub_child.get("print")
    	print_result(field_text,result,xml_child,my_logger)
    	if xml_sub_child.get("name")in vm_mode_type:
        	operation_name=op_list[op_name]
        	check_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,operation_name,my_logger)
    else:
	my_logger.debug("No element exist")

def op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    my_logger.debug("Performing Migrate operation on this VM..............")
    op_name=xml_sub_child.get("op")
    limit=0
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    operation_name
    path="//a[@title='Migrate this virtual machine']"
    if isElementPresent(driver,xml_child,path,my_logger):
        vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
	total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger)
        driver.find_element_by_link_text("All VMs").click()
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger) 
	status=check_status_of_vm(driver,xml_sub_child,xml_child,my_logger)
	driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
	driver.find_element_by_xpath("//input[@value='Migrate']").click()
	if status=="Running":
	    result="Your VM is already running. Kindly turn it off and then retry!!!"
	    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
            print_result(field_text,result,xml_child,my_logger)
	elif total:
	    result="Your request already in the queue"
	    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
            print_result(field_text,result,xml_child,my_logger)
	else:
           result="Your task has been queued. please check your task list for status. "
           field_text=message_flash(driver,xml_sub_child,xml_child)
           print_result(field_text,result,xml_child,my_logger)
           limit=1
    else:
        my_logger.debug("Migrate operation could not performed because no host is available.Please do host up then again try this operation")
    return limit

#performing  delete add_user operation on vm
def op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name,baadal_db,my_logger):
    limit=0
    op_name=xml_sub_child.get("op")
    my_logger.debug("Deleting addtional user from user list on setting page........")
    path=xml_sub_child.get("xpath_user")
    if isElementPresent(driver,xml_child,path,my_logger):
        user_id=get_user_id(driver,xml_sub_child,xml_child,vm_name,owner_name)
	path="//a[@id='"+str(user_id)+"']"

	driver.find_element_by_xpath(path).click()
        #driver.find_element_by_xpath("//*[@href='/baadal/admin/"+ tr(op_name) +"/"+ str(vm_id) +"/"+ str(user_id) + "']").click()
        result="User access is eradicated."
        field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
        print_result(field_text,result,xml_child,my_logger)
        check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child,my_logger)
	#check_owner_of_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name,my_logger)
    else:
    	my_logger.debug(xml_child.get("value") + ":This VM has been deleted and its in pending task table,So this functionality has been disabled !!!!!!") 
    return limit

        
#################################################################################################################
#                                       The main test function  for graph testing                                       #
#################################################################################################################

def graph_test(driver,vm_ip,vm_name,xml_sub_child,xml_child,my_logger):
#Checking memory utilizations
    my_logger.debug("Performing graph testing by fetching rrd data from controller before executing program on VM.........")
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))
    
    #vm_full_name='IITD_badalUFA_'+ str(vm_name) + '.rrd'
    #stdin, stdout, stderr =ssh.exec_command('cd /mnt/datastore/vm_rrds/;rrdtool fetch' +str(vm_full_name)+' MIN -s -600s -e now')
    stdin, stdout, stderr =ssh.exec_command('cd /mnt/datastore/vm_rrds/;rrdtool fetch IITD_sjyoti_graph_testing.rrd MIN -s -600s -e now')
    initial_data=stdout.readlines()
    
    current_time=datetime.datetime.now()

    ini_data=str(initial_data[2])
    init_data=ini_data.split()
    my_logger.debug("Fetched data from rrd before performing operations:"+ str(init_data))
    #os.system('sshpass -p "baadal123" scp -r root@'+str(vm_ip)+':/home /home/jyoti/Desktop/data')
    ssh.connect("10.237.20.221", username="root", password="baadal123")
    my_logger.debug("Executing program on graph testing VM.....")
    stdin, stdout, stderr =ssh.exec_command(xml_child.get("cmd_run_prgrm"))
    data=stdout.readlines()
    time.sleep(300)
    my_logger.debug("Executed program on graph testing VM")
    my_logger.debug("Performing graph testing by fetching rrd data from controller after executing program on VM.........")
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))
    #stdin, stdout, stderr =ssh.exec_command('cd /mnt/datastore/vm_rrds/;rrdtool fetch' +str(vm_full_name)+'.rrd MIN -s -600s -e now')
    stdin, stdout, stderr =ssh.exec_command('cd /mnt/datastore/vm_rrds/;rrdtool fetch IITD_sjyoti_graph_testing.rrd MIN -s -600s -e now')
    final_data=stdout.readlines()
   
    fin_data=str(final_data[2])
    finl_data=fin_data.split()
    my_logger.debug("Fetched data from rrd after performing operations:"+ str(finl_data))
    print_graph_result(finl_data,init_data,xml_child,my_logger)
    
    


    
def print_graph_result(finl_data,init_data,xml_child,my_logger):
    my_logger.debug(xml_child.get("value") +" Initial_data:"+ str(init_data))
    my_logger.debug(xml_child.get("value") +" Final_data:"+ str(finl_data))
    for i in range(1,7):
        if init_data[i]=="-nan":
            i_data=0
        else:
            i_data=init_data[i]
        diff=float(finl_data[i])-float(i_data)
        print diff
	fin_data=finl_data[i]
        my_logger.debug(xml_child.get("value") +": Differnce "+ str(diff))
        '''if finl_data[i]=="-nan":
            my_logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
            print "no"
        else :
            if diff<=0:
                my_logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
		print "no"
            else:
                my_logger.debug(xml_child.get("value") +':  '+"Correct Data")
		print "yes"'''
	print i
        if  i==1:
	    my_logger.debug("Checking data for CPU performance")
            
            check_type_of_graph(i,diff,xml_child,fin_data,my_logger)
            break
        if i==2:
            my_logger.debug("Checking data for RAM performance")
            check_type_of_graph(i,diff,xml_child,fin_data,my_logger)
	    
            break
        if i==4| i==3:
	    my_logger.debug("Checking data for DISK performance")
            check_type_of_graph(i,diff,xml_child,fin_data,my_logger)
	    
            break
        if i==5 | i==6:
            my_logger.debug("Checking data for NETWORK performance")
            check_type_of_graph(i,diff,xml_child,fin_data,my_logger)
     	    
            break     
            
    return

def check_type_of_graph(i,diff,xml_child,fin_data,my_logger):
    
    my_logger.debug(xml_child.get("value") +": Differnce "+ str(diff)) 
    if fin_data=="-nan":
	my_logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
    else :
	if diff<=0:
	    my_logger.debug(xml_child.get("value") +':  '+"Incorrect Data") 
	else:
	    my_logger.debug(xml_child.get("value") +':  '+"Correct Data") 
    return

def print_graph(finl_data,xml_child,my_logger):
    for i in range(1,7):
        if finl_data[i]=="-nan":
            my_logger.debug(xml_child.get("value") +':  '+"Correct Data")
        else :
            my_logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
#################################################################################################################
#                                        Function  for Network testing                                            #
#################################################################################################################
def packages_install_test(test_case_no,my_logger):
    root = xml_connect()
    xml_sub_child=root[test_case_no-1][0][0]

    xml_child=root[test_case_no-1][0]
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_flush"))
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_pkg"))
    pkg_list=xml_sub_child.get("pkg_lst").split()
    for pkg in  pkg_list:
        cmd=xml_sub_child.get("cmd_srch") + " " +str(pkg)
        stdin, stdout, stderr =ssh.exec_command(cmd)
        data=stdout.readlines()
        if data:
            my_logger.debug(xml_child.get("value") +': '+pkg +" :software has installed properly")

        else:
            my_logger.debug(xml_child.get("value") +': '+pkg +" :software has not installed properly")


def check_stat_on_host():
    conn = libvirt.open("qemu+ssh://root@" + '10.208.21.70' + "/system")
    db=mdb.connect("10.208.21.111","baadaltesting","test_baadal","baadal")
    cursor1=db.cursor()
    cursor1.execute("select vm_name,vm_data.status,host_id from vm_data join host where host.id=vm_data.host_id and host_ip='10.208.21.70'")
    output=cursor1.fetchall()
    datas=str(output)
    lists=datas.split("), (")
    col_count=len(lists)
    for i in range(0,col_count):
        datass=lists[i].split(",")
        newstr = datass[0].replace("'", "")
        if i==0:
            newstr=newstr.replace("((","")
        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            infos = dom.info()
            if newstr==dom.name():
                print newstr
                print 'Name =  %s' % dom.name()
                print 'State = %d' % infos[0]
                print datass[1]
                if (((datass[1]==" 5L") & (infos[0]==1)) | ((datass[1]==" 6L") & (infos[0]==3))):
                    print "yes"

#################################################################################################################
#                         Function for mailing
                                           #
#################################################################################################################
def send_mail():
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.server = 'smtp.iitd.ernet.in:25'
    mail.settings.sender = 'monika28.visitor@cse.iitd.ernet.in'
    mail.settings.login = 'jyoti11.visitor@cse.iitd.ernet.in:jyoti_saini'
    mail.send(to=['monika71990@gmail.com'],
          subject='hello',
          # If reply_to is omitted, then mail.settings.sender is used
          message="Error")
###############################################################################################################
#                             Functions used by the input field functions                                     #
###############################################################################################################


#open error link on differnet page
def open_error_page(driver,xml_parent,xml_child,row_count,my_logger):
    (driver.find_elements_by_link_text("Error"))[row_count].click()
    time.sleep(5)
    xpath=xml_parent.get("error_page")
    if isTablePresent(driver,xml_child,xpath,my_logger):
        field=driver.find_element_by_xpath(xpath)	
        error_message=field.text
        driver.find_element_by_link_text("CLOSE WINDOW").click()
    else:
        error_message="None"
    my_logger.debug("Eroor message is :" + str(error_message))
    return error_message

	
#converting vm status bits into status text			
def admin_vm_status(status,my_logger):
    vm_status=["Running","Paused","Shutdown"]
    if status==2:
        result=vm_status[0]
    if status==3:
        result=vm_status[1]
    if status==4:
        result=vm_status[2]
    return result 

    	
#converting host status bits into status text    	    	    	
def host_status(status,my_logger):
	host_status={0:"Down",1:"Up",2:"Maintenance"}	
	if status==0:
		result=host_status[0]
	if status==1:
		result=host_status[1]
	if status==2:
		result=host_status[2]
	return result

		
#converting  status bits into status text	
def org_task_status(status,xml_child,my_logger):
    user_name=xml_child[0].get("value")

    task_status={0:"Approve  |  Reject | Edit",1:"Waiting for admin approval",2:"Remind Faculty"}
    if (status==0) | (status==2):
        result=task_status[0]
    if (status==3) :
        result=task_status[0]
    if (status==4) :
        result=task_status[1]
    if (status==1) :
        result=task_status[2]
    return result



#checking whether username is in vm_users table or not
def check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id,baadal_db,my_logger):
    username=xml_sub_child.get("user_id_data")
    ry( xml_sub_child.get("query5"),(str(vm_name))).fetchone()
    baadal_db.commit()
    length=len(query_length)
    
    query_result=execute_query(baadal_db,"select concat(user.first_name,' ',user.last_name) as user_name from user where username=%s",(str(username))).fetchone()
    baadal_db.commit()
    path="//table[@id='vm_users']/tbody/tr"
    field=driver.find_elements_by_xpath(path)
    count=0
    a=0
    for data in field:
        if query_result[0] in data.text:
            
            my_logger.debug("User name is added to VM")
            count=1
        a=a+1
    if a==length:
    	if count==0:
    		my_logger.errot(xml_child.get("value")  + "Error ")    
    return
    
#list of vm mode 
vm_mode_type=['vm_running_Setting_intgrtn','vm_paused_Setting_integrtn','vm_shutdown_Setting_integrtn']

#checking whether user access removed for a vm or not
def check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child,my_logger):
    my_logger.debug("Checking whether user has been deleted or not... ")
    path="//a[@id='"+str(user_id)+"']"
    if isTablePresent(driver,xml_child,path,my_logger):
	    my_logger.debug(xml_child.get("value")  +"User access is eradicated and its working ")
        
    else:
        my_logger.error(xml_child.get("value")  + "User has not been deleted!!!!!!!Check ")
    return

def graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id,my_logger):
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    initial_data=stdout.readlines()

    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    time.sleep(900)
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    final_data=stdout.readlines()
    fin_data=str(final_data[2])
    finl_data=fin_data.split()
    
    print_graph(finl_data,xml_child,my_logger)
                                           
                                               
def result_setting_page(field,query_result,driver,xml_child,xml_sub_child,my_logger):
    i=0
    for t in field:
        print "screen=" + str(t.text)
        print "db=" + str(query_result[i][0])
        if str(query_result[i][0]) in t.text:
            my_logger.debug("correct inputs")
        else :
            my_logger.debug("Incorrect inputs")
        i+=1 
    return

    
# providing connection to all host exists
def conn_host(host_name,vm_status,vm_name,message,total_vm,baadal_db,my_logger):
    
    query_result=execute_query(baadal_db,"select host_name,host_ip from host").fetchall()
    no_of_cols=len(query_result)#calculate number of columns of query
    baadal_db.commit()
    for host in range(0,no_of_cols):
        host_nam=query_result[host][0]
        host_ip=query_result[host][1]
        
        conn = libvirt.open("qemu+ssh://root@" +str(host_ip)+ "/system")
        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            infos = dom.info()
            status=infos[0]
            status_vm=check_vm_status_on_host(status,my_logger)
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam,baadal_db,my_logger)
        for vm in conn.listDefinedDomains():
            status_vm="Off"
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam,baadal_db,my_logger)	   



#checking data in sanity table
def print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam,baadal_db,my_logger):
    for i in range(0,total_vm):
        vm_nm=vm_name[i]
        if ((vm_nm==vm_name[i]) & (host_nam==host_name[i])):
            messg=check_messg_in_db(vm_nm,host_ip,host_nam,baadal_db)
            if vm_nm==vm_name[i]:
                my_logger.debug('host='+vm_nm)
                my_logger.debug('screen='+vm_name[i])
                my_logger.debug('Result:correct input')
            else:
                my_logger.debug('host='+vm_nm)
                my_logger.debug('screen='+vm_name[i])
                my_logger.debug('Result:Incorrect input')
                
            if status_vm==vm_status[i]:
                my_logger.debug('host='+status_vm)
                my_logger.debug('screen='+vm_status[i])
                my_logger.debug('Result:correct input')
            else:
                my_logger.debug('host='+status_vm)
                my_logger.debug('screen='+vm_status[i])
                my_logger.debug('Result:Incorrect input')
                	
            if messg==message[i]:
                my_logger.debug('host='+messg)
                my_logger.debug('screen='+message[i])
                my_logger.debug('Result:correct input')
            else:
                my_logger.debug('host='+messg)
                my_logger.debug('screen='+message[i])
                my_logger.debug('Result:Incorrect input')
                
            if host_nam==host_name[i]:
                my_logger.debug('host='+host_nam)
                my_logger.debug('screen='+host_name[i])
                my_logger.debug('Result:correct input')
            else:
                my_logger.debug('host='+host_nam)
                my_logger.debug('screen='+host_name[i])
                my_logger.debug('Result:Incorrect input')



#converting vm status bits on host into status text		
def check_vm_status_on_host(status,my_logger):
	if status==1:
		status_vm="Running"
	if status==3:
		status_vm="Paused"
	return status_vm

	
#checking whether data in sanity table is correct or incorrect    
def check_messg_in_db(vm_nm,host_ip,host_nam,baadal_db):    
    fetch_result=execute_query(baadal_db," select vm_name,vm_data.status from vm_data,host where vm_data.host_id=host.id and host_ip=%s",(str(host_ip))).fetchall()
    
    no_vm_in_db=len(fetch_result)
    baadal_db.commit()
    if fetch_result!=():
        for j in range(0,no_vm_in_db):
            if vm_nm==fetch_result[j][0]:
                vm_in_db="True"
                messg="VM is on expected host "+host_nam
            else:
                vm_in_db="False"
                messg="Orphan, VM is not in database"
       
    else:
        messg="Orphan, VM is not in database"                
    return messg
##############################################################################################################
#  					           functions for various types of input fields  				          	     #
##############################################################################################################

def faculty_vm_status(owner_name_db,owner_name_screen,xml_child,my_logger):
	user_name=xml_child[0].text
	print user_name
	if owner_name_screen==str(owner_name_db):
		result="Approve  |  Reject | Edit"
	else:
		result="Remind Faculty"
	return result

def user_vm_status(status,my_logger):
	if (status==1) | (status==4):
		result="Waiting for admin approval"
	if status==2:
		result="Approved. In Queue."
	if status==3:
		result=" Waiting for org admin approval"
	if status==-1:
		result='Task failed. Contact administrator.'
	return result
	
	
#converting port status bits into status text
def check_port_enabled(vm_name,baadal_db,my_logger):
    query_result=execute_query(baadal_db,"select enable_ssh,enable_http from request_queue where vm_name=%s",(str(vm_name))).fetchall()
    baadal_db.autocommit(True)
    enable_ssh=query_result[0][0]
    enable_http=query_result[0][1]
    if (enable_ssh=="F") & (enable_http=="F"):
        result="-"
    if (enable_ssh=="T") & (enable_http=="F"):
        result="SSH"
    if (enable_ssh=="F") & (enable_http=="T"):
        result="HTTP"
    if (enable_ssh=="T") & (enable_http=="T"):
        result="SSH,HTTP"
    return result




#converting security visibility status bits into status text
def check_security_visibilty(status,my_logger):
    if status=="T":
        result="ALL"
    else:
        result="NO"
    return result


#converting vCPU status bits into status text
def check_vcpu(status,my_logger):
	status=str(status) + " CPU"
	return status



#converting memory bits into  text
def check_mem(mem,my_logger):
    if mem==0:
        result="-"
    else:
        result=str(mem)+"GB"
    return result
    

#converting extra disk bits into  text
def check_extra_disk(extra_disk,my_logger):
    if extra_disk==0:
        result="10GB"
    else:
        result="10GB + " + str(extra_disk) + "GB" 
    return result

#converting ram bits into  text
def check_vm_ram(ram,my_logger):
    if ram==256:
        result="0.25GB"
    if ram==512:
        result="0.50GB"
    if ram==1024:
        result="1.0GB"
    if ram==2048:
        result="2.0GB"
    if ram==4096:
        result="4.0GB"
    if ram==8192:
        result="8.0GB"
    if ram==16384:
        result="16.0GB"
    return result



#checking data into host table
def isCheckTable(driver, xml_parent, xml_child, xml_sub_child,baadal_db,my_logger):
    field=driver.find_elements_by_xpath(xml_sub_child.get("path"))
    query_result=execute_query(baadal_db,xml_parent.get("query3")).fetchall()
    baadal_db.autocommit(True)    
    length=len(query_result[0])#calculate number of columns of query
    length_row=len(query_result)#calculate number of columns of query
    table=0
    count=0
    for col in field:
		field_text=col.text 
		print field_text  
		if field_text!="":
			count=count+1			
    total=length_row*length
    print total
    if (str(total)==str(count)):
        for header in field:
            host_ip=query_result[table][0]
            if query_result[table][0] in header.text:
                table_path=xml_sub_child.text
                if isTablePresent(driver,xml_child,table_path,my_logger):
                    result_fetch=execute_query(baadal_db,xml_parent.get("query4"),str(host_ip)).fetchall()
                    baadal_db.autocommit(True)
                    if result_fetch!=():
                        field=driver.find_elements_by_xpath(xml_sub_child.text)   
                    	no_of_rows=len(result_fetch)#calculate number of rows of query
                    	no_of_cols=len(result_fetch[0])#calculate number of columns of query	
                    	cont=0
                    	for col in field:
			   field_text=col.text 							
			   if field_text!="":
				cont=cont+1                       
                        total=no_of_cols
                    	row_count=0
                    	col_count=0
                    	if (str(total)==str(cont)):                    		
                    		for col in field:
                        	    field_text=col.text                               
                                    if field_text!="":                                    
                                      if col_count%int(no_of_cols)==5:
                                        status=result_fetch[row_count][col_count]
                                        result=admin_vm_status(status,my_logger)
                                      else:
                                	result=result_fetch[row_count][col_count]
                                    print_result(field_text,result,xml_child,my_logger)
                                    col_count+=1
                                    if col_count%int(no_of_cols)==0:
                                		row_count+=1
                                		col_count=0                                
                        else:
                            my_logger.error(xml_child.get("value") +":tuple out of index")                            
                else:
                    my_logger.debug("No VM Exists on "+str(host_ip))
                table=table+1
    else:
        my_logger.error(xml_child.get("value") + ":incorrect data")
    return




def check_operation(driver,xml_parent, xml_child, xml_sub_child,op_id,result,my_logger):
    request=xml_sub_child.get("click")        
    print "//*[@href='/baadal/" + str(op_id) + "/" +str(request)+ "/" + str(result) + "']"
    driver.find_element_by_xpath("//*[@href='/baadal/"+ str(op_id) +"/"+str(request)+"/"+str(result) +"']").click()
    result=xml_sub_child.get("print_data")
    field_text=message_flash(driver,xml_sub_child,xml_child,my_logger)
    print_result(field_text,result,xml_child,my_logger)
    return


def isSanityCheck(driver, xml_parent, xml_child, xml_sub_child,baadal_db,my_logger):
    field=driver.find_elements_by_xpath("//div[@id='sanity_check_table']/table/tbody/tr/td")
#print field.text
    row_count=0
    col_count=0
    host_name=[]
    vm_status=[]
    vm_name=[]
    message=[]
    operation=[]
    for col in field:
        field_text=col.text
        if col_count%5==0:
            host_name.insert(row_count,field_text)
           
        if col_count%5==1:
            vm_status.insert(row_count,field_text)
           
        if col_count%5==2:
            vm_name.insert(row_count,field_text)
           
        if col_count%5==3:
            message.insert(row_count,field_text)
           
        if col_count%5==4:
            operation.insert(row_count,field_text)
           
        if col_count%5==0:
            
            row_count+=1
            col_count=0	
        col_count+=1
       
    total_vm=len(vm_name)  
    
    conn_host(host_name,vm_status,vm_name,message,total_vm,baadal_db,my_logger)
   

def maintain_idompotency(driver,xml_sub_child,xml_child,my_logger):
    my_logger.debug("Deleting VM for maintaing idompotency.......")
    deletevm_from_pending_request_table(driver,xml_sub_child,xml_child,my_logger)
    delete_vm_from_allvms(driver,xml_sub_child,xml_child,my_logger)
    return


def deletevm_from_pending_request_table(driver,xml_sub_child,xml_child,my_logger):
    my_logger.debug("Deleting VM from pending request table.............")
    data1=[]
    path_col="//table[@id='sortTable1']/tbody/tr/td"
    path_row="//table[@id='sortTable1']/tbody/tr"
    path_header="//table[@id='sortTable1']/thead/tr/th"

    driver.find_element_by_partial_link_text("All Pending Requests").click()
    if isTablePresent(driver,xml_child,path_col,my_logger):
        print "vm_list table present"
        countc=0
        c_count=0
        r_count=0
        select_row=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Requested By":
                user_name_no=count
          
            if hdata.text=="Action":
                action_no=count
        
            count+=1
        col_count=count
    count_u=0 
    vm_id_list=[]	    	      
    field=driver.find_elements_by_xpath(path_col)
    for data in field:
	print data.text
	if c_count%col_count==user_name_no:	    
	    for username in username_list:
		if str(username)==str(data.text):
		    user_name=data.text		    
		    select_row=1
		    break            
	if (c_count%col_count==col_count-1):	    
	    if select_row:
		vm_id=data.get_attribute("id")
		path='//a[@id="reject_'+str(vm_id)+'"]'
		vid='reject_'+str(vm_id)
		vm_id_list.append(vid)
		select_row=0
	c_count+=1    
    for vm_id in vm_id_list:
        my_logger.debug("DEleting VM having id" :str(vm_id))
        driver.refresh()
	path="//a[@id='"+str(vm_id)+"']"
	if isElementPresent(driver,xml_child,path,my_logger):	    
	    driver.find_element_by_xpath(path).click()
	    time.sleep(15)
    return


def delete_vm_from_allvms(driver,xml_sub_child,xml_child):
    vm_exist=0
    my_logger.debug("Deleting VM from all VMs..........")
    driver.find_element_by_link_text("All VMs").click()
    path="//table[@id='listallvm']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0
    col_count=0
    user_present=0
    if isElementPresent(driver,xml_child,path,my_logger):
        field=driver.find_elements_by_xpath("//table[@id='listallvm']/thead/tr/th")
        for data in field:
            if data.text=="Owner":
		requester_col_no=counth
		
            counth+=1
        
        total_col=counth
        field=driver.find_elements_by_xpath("//table[@id='listallvm']/tbody/tr/td[2]")
        for data in field:
	         for username in username_list:
		         if username==data.text:
		             
   		             user_present+=1
		
       
        for x in range(0,user_present):
            driver.refresh()	    
            field_data=driver.find_elements_by_xpath("//table[@id='listallvm']/tbody/tr/td")
	   
            for user in field_data:
	        if (col_count%total_col==requester_col_no):
                    for username in username_list:
                        if username==user.text:
                            user_name=user.text
                            select_row=1
                if col_count%total_col==(total_col-1) :
                    if select_row:
                        vm_id=user.get_attribute("id")                     
                        time.sleep(30)
			path="//*[@id='" +str(vm_id)+"']/a"
    			vmid="vm_"+ str(vm_id)
			if isElementPresent(driver,xml_child,path,my_logger):
	    			driver.find_element_by_xpath(path).click()
	    			time.sleep(15)
                        if isElementPresent(driver,xml_child,path):
                        	try:
                                    driver.find_element_by_xpath(path).click()
                                    e_present=1
                                except:
                                    e_present=0
                                if e_present:
                                    click_on_dialogbox(driver,my_logger)
                                    click_on_dialogbox(driver,my_logger)
                                    my_logger.debug(str(user_name) + " VM (" + str(vm_id[3:]) + ") has been deleted from All VMs table") 
                                    select_row=0
                                    col_count=0
                                    vm_exist=1
                                    driver.find_element_by_link_text("All VMs").click()
                                    driver.refresh()
                                    time.sleep(10)
                                    break		
                                else:
                                    my_logger.debug("This VM already has been   deleted!!!")                    		   
                col_count+=1
	if vm_exist==0:
	    my_logger.debug("No VM exists to perform Delete Pending request!!!")
    return



####### performane testing #########


def vm_list_host(driver,xml_child,xml_sub_child,my_logger):
    my_logger.debug("inside vm_list_host")
    data_host=[]
    path_col="//table[@id='hostdetails']/tbody/tr/td"
    path_row="//table[@id='hostdetails']/tbody/tr"
    path_header="//table[@id='hostdetails']/tbody/tr/th"
    driver.find_element_by_partial_link_text("Configure System").click()
    driver.find_element_by_partial_link_text("Configure Host").click()
    #path=driver.find_element_by_id("menu_user").click()
    #path=driver.find_element_by_xpath("//a[@href='/baadal/user/list_my_vm']").click()
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="IP":
                vm_ip_no=count
            if hdata.text=="Status":
                status_no=count
            count+=1
        col_count=count
        my_logger.debug(count)
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_ip_no:
                vm_ip=data.text
            if c_count%col_count==status_no:
                          host_status=data.text
                          if host_status=="Up":
                            data_host.append(vm_ip)
                           # host_status= Down
            c_count+=1
    my_logger.debug("data_host : " + str(data_host))
    return data_host




def vm_check_host(driver,xml_child,xml_sub_child,xml_parent,vm_name,my_logger):
    my_logger.debug("Finding suitable host........")
    data= vm_list_host(driver,xml_child,xml_sub_child,my_logger)
    print data
    i= len(data)
    j=i
    host_num=[0]*j
    driver.find_element_by_partial_link_text("All VMs").click()
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Host":
                vm_host_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        my_logger.debug("vm_host_no is : " + str(vm_host_no))
        for datum in field:
            if c_count%col_count==vm_host_no:
                host=datum.text
                vm_per_host_count(j,data,host_num,host,my_logger)
            c_count+=1
    my_logger.debug(host_num)
    min_host= select_mini_host(j,data,host_num,my_logger)
    my_logger.debug(min_host)
    my_logger.debug(vm_name)
    vm_info=get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger)
    
    vm_host=vm_info['host']
    my_logger.debug(vm_info)
    vm_ip=vm_info['public_ip']
    my_logger.debug(vm_host)
    my_logger.debug(min_host)
    vm_id=vm_info['vm_id']
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    vm_data=get_vm_info_frm_setting(xml_child,xml_sub_child,driver,vm_name,my_logger)
    vm_hdd=vm_data['hdd']
    if str(vm_host)==str(min_host):
      my_logger.debug(vm_host)
      my_logger.debug("VM already running on host having minimum utilizations..No need to migrate this VM..")
    else :
      my_logger.debug("Checking for min host")
      migrate_on_specific_host_test(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id, min_host,my_logger)
    performance(vm_info,my_logger,vm_hdd)
    return


def vm_per_host_count( j,data,host_num,host,my_logger):
    my_logger.debug("inside vm_per_host_count")
    i=0
    while(i<j):
      my_logger.debug(data[0:])
      my_logger.debug(host)
      if(data[i]==host):
        my_logger.debug("Counting host")
        host_num[i]=host_num[i]+1
      i=i+1
    return



def select_mini_host(j,data,host_num,my_logger):
    min = 0
    while (j-1):
      if host_num[j-1]<host_num[min]:
        min=j-1
      j=j-1
    return data[min]


def get_vm_id_by_vmname(driver,vmname,xml_child,xml_sub_child,my_logger):
    my_logger.debug("inside get_vm_id_by_vmname")
    data2=[]
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    #path=driver.find_element_by_id("menu_user").click()
    countc=0
    if isTablePresent(driver,xml_child,path_col,my_logger):
        c_count=0
        r_count=0
        select_row=0
	select=0
	select_status=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Host":
                user_host_no=count
            if hdata.text =="Public IP":
                public_ip_no= count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_name=data.text
                
            if c_count%col_count==user_host_no:
                host=data.text
            if c_count%col_count==public_ip_no:
                public_ip= data.text
            if (c_count%col_count==col_count-1):
                    if (vm_name==vmname):
                        field_data=driver.find_elements_by_xpath(path_row)
                        data1=data.find_element_by_tag_name("a")
			vm_id=data1.get_attribute("id")
                        
              		countc+=1
                        break
            c_count+=1
    if countc==0:
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_id=""
        host=""
        public_ip=""

    data2.insert(0,vm_id)
    data2.insert(1,host)
    data2.insert(2,public_ip)
    my_logger.debug(data2)
    return data2


def migrate_on_specific_host_test(driver,xml_sub_child,xml_child,xml_parent,vm_name,vm_id, host,my_logger):
    my_logger.debug("Migrating VM on host having min utilizations....")
    driver.find_element_by_link_text("My Tasks").click()
    operation_name="Migrate VM"
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_link_text("My VMs").click()
    my_logger.debug("vm_name is : " + str(vm_name))
    my_logger.debug("vm_is id : " + str(vm_id))
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
    my_logger.debug("Doing live migration")
    message=message_flash(driver,xml_sub_child,xml_child,my_logger)
    my_logger.debug(message)
    message=str(message)
    if message=="No host available right now":
         sys.exit()
    else:
	driver.find_element_by_xpath("//input[@name='live_migration']").click()
	my_logger.debug("//table/tbody/tr/td/select/option[text()='"+str(host)+"]'")
	driver.find_element_by_xpath("//table/tbody/tr/td/select/option[text()='"+str(host)+"']").click()
	driver.find_element_by_xpath("//input[@value='Migrate']").click()
    	my_logger.debug("migration done")
    	time.sleep(10)
    	driver.find_element_by_link_text("Tasks").click()
    	task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
        my_logger.debug("Before performing operations data in failed and completed task table:"+str(task_value))
        my_logger.debug("After performing operations data in failed and completed task table:"+str(task_n_value))
    	compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    my_logger.debug("Migrated VM on host having min utilizations....")
    return



'''def migrate_on_specific_host(driver,xml_sub_child,xml_child,vm_name,vm_id, host):
    print "inside operation_on_migrate_vm"
    limit =0
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
    path="//a[@title='Migrate this virtual machine']"
    if isElementPresent(driver,xml_child,path):
	print "vm exist"
	driver.find_element_by_partial_link_text("All VMs").click()
        vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
        operation_name="Migrate VM"
	total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name, vm_user_list)
        driver.find_element_by_partial_link_text("All VMs").click()
	print "again clicked all vms"
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
	status=check_status_of_vm(driver,xml_sub_child,xml_child)
	print status+" status"
	driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
	print "live migration"
        message=message_flash(driver,xml_sub_child,xml_child)
        print message
        message=str(message)
        if message=="No host available right now":
                sys.exit()
        else:
            driver.find_element_by_xpath("//input[@name='live_migration']").click()
            print "//table/tbody/tr/td/select/option[text()='"+str(host)+"]'"
            driver.find_element_by_xpath("//table/tbody/tr/td/select/option[text()='"+str(host)+"']").click()

            driver.find_element_by_xpath("//input[@value='Migrate']").click()
	if total:
	    result="Your request already in the queue"
	    field_text=message_flash(driver,xml_sub_child,xml_child)
            print_result(field_text,result,xml_child)
	else:
           result="Your task has been queued. please check your task list for status. "
           field_text=message_flash(driver,xml_sub_child,xml_child)
           print field_text
           print_result(field_text,result,xml_child)
           print print_result
           limit=1
	print "migration done"
    else:
	print "Migrate operation could not performed because no host is available.Please do host up then again try this operation"
        logger.debug("Migrate operation could not performed because no host is available.Please do host up then again try this operation")

    return limit'''


def convert_into_float(data,my_logger):
    logger.debug(data)
    m=str(data)
    q=m.replace("['",' ')    
    qa=q.replace("']",' ')    
    a=qa.strip()
    l=len(a)
    output=a[:(l-3)]    
    my_logger.debug(output)
    return output



def performance(vm_info,my_logger,vm_hdd):
    my_logger.debug("Checking performance.....")
    my_logger.debug("VM info:"+ str(vm_info))
    vm_ip=vm_info['public_ip']
    hdd=vm_hdd
    ram=vm_info['ram']
    cpu=vm_info['vcpu']
    
    perf_root = xml_connect_perf()
    my_logger.debug(len(perf_root))
    for i in xrange(0,len(perf_root)):
        my_logger.debug(i)
        if (cpu==perf_root[i].get("cpu")) & (ram==perf_root[i].get("ram")) & (hdd==perf_root[i].get("hdd")):
            my_logger.debug("yes")
	    for j in xrange(0,len(perf_root[i])):
		my_logger.debug(j)
                pxml_parent=perf_root[i]
                pxml_child=perf_root[i][j]
	        upper_limit=pxml_child.get("ulimit")
	        lower_limit=pxml_child.get("llimit")
	        if pxml_child.get("type")=="cpu":
		    check_cpu_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="seqr":
		    check_seqr_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="seqrd":
		    check_seqw_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="rndrd":
		    check_ranr_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="rndwr":
   		    check_ranw_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="net":
		    check_net_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="memr":
		    check_memr_performance(upper_limit,lower_limit,vm_ip,my_logger)
		elif pxml_child.get("type")=="memw":
		    check_memw_performance(upper_limit,lower_limit,vm_ip,my_logger)
		else:
		     my_logger.debug("..................")
    return  1



def check_cpu_performance(upper_limit,lower_limit,vm_ip,my_logger):
    time.sleep(300)
    import os 
    
    change_vm_paswd(vm_ip)
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking CPU performance ....")
    
    stdin, stdout, stderr =ssh.exec_command("echo 'is it working?'")
    
    stdin, stdout, stderr =ssh.exec_command("apt-get update")
    time.sleep(60)
    stdin, stdout, stderr =ssh.exec_command("apt-get -y install sysbench --force-yes")
   
    my_logger.debug(stdout.readlines())
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=cpu --num-threads=4 --cpu-max-prime=20000 run | grep 'total time:' | cut  -d  ':'  -f   '2'")

    data=stdout.readlines()
    
    
    cpu_output=convert_into_float(data,my_logger)

    my_logger.debug( "time to run"+ str(cpu_output))

    my_logger.debug(cpu_output)
    if lower_limit <= float(cpu_output) <= upper_limit:
       my_logger.debug( "CPU performance is upto the mark!!!!!!!!!!")
    else:
       my_logger.debug( "CPU performance is not upto the mark!!!!!!!!!!")
    ssh.close()
    return

def check_seqr_performance(upper_limit,lower_limit,vm_ip,my_logger):
    my_logger.debug(upper_limit)
    my_logger.debug(lower_limit)
    my_logger.debug(vm_ip)
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking sequential read file performance ....")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqrd prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqrd run | grep 'total time:' | cut  -d  ':'  -f   '2'")
    data=stdout.readlines()
    fseqr_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(fseqr_output))

    if lower_limit <= float(fseqr_output) <= upper_limit:
	my_logger.debug( "File Sequential Read performance is upto the mark!!!!!!!!!!")
    else:
         my_logger.debug( "File Sequential Read performance is not upto the mark!!!!!!!!!!")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqrd cleanup")
    ssh.close()
    return

import time
def check_seqw_performance(upper_limit,lower_limit,vm_ip,my_logger):

    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking sequential write file performance ....")
    ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqwr prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqwr run | grep 'total time:' | cut  -d  ':'  -f   '2'")

    time.sleep(10)
    data=stdout.readlines()
    
    fseqrd_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(fseqrd_output))

    if lower_limit <= float(fseqrd_output) <= upper_limit:
	my_logger.debug( "File Sequential Write performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "File Sequential Write performance is not upto the mark!!!!!!!!!!")

    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=seqwr cleanup")
    ssh.close()
    return

def check_ranr_performance(upper_limit,lower_limit,vm_ip,my_logger):
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking random read file performance ....")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndrd prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndrd run | grep 'total time:' | cut  -d  ':'  -f   '2'")
    data=stdout.readlines()
    
    frndrd_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(frndrd_output))
    if lower_limit <= float(frndrd_output) <= upper_limit:
	my_logger.debug( "File Random Read performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "File Random Read performance is not upto the mark!!!!!!!!!!")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndrd cleanup")
    ssh.close()

    return

def check_ranw_performance(upper_limit,lower_limit,vm_ip,my_logger):
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking random write file performance ....")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndwr prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndwr run | grep 'total time:' | cut  -d  ':'  -f   '2'")
    data=stdout.readlines()
    
    frndwr_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(frndwr_output))

    if lower_limit <= float(frndwr_output) <= upper_limit:
	my_logger.debug( "File Randon Write performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "File Randon Write performance is not upto the mark!!!!!!!!!!")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=fileio --num-threads=1 --file-total-size=2G --file-test-mode=rndwr cleanup")
    ssh.close()
    return

def check_net_performance(upper_limit,lower_limit,vm_ip,my_logger):
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking network performance ....")
    stdin, stdout, stderr =ssh.exec_command("apt-get -y install netperf --force-yes")
    print stdout.readlines()
    stdin, stdout, stderr =ssh.exec_command('netperf | grep "^ " | tr -s " "  | cut -f"6" -d" "')
    data=stdout.readlines()
    print data
    net_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(net_output))
    if lower_limit <= float(net_output) <= upper_limit:
	my_logger.debug( "Network performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "Network performance is not upto the mark!!!!!!!!!!")
    ssh.close()
    return



def check_memr_performance(upper_limit,lower_limit,vm_ip,my_logger):
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking memory read performance ....")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=read prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=read run | grep 'total time:' | cut  -d  ':'  -f   '2'")
    data=stdout.readlines()
    print data
    my_logger.debug(data)
    memr_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(memr_output))

    if lower_limit <= float(memr_output) <= upper_limit:
	my_logger.debug( "Memory Read performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "Memory Read performance is not upto the mark!!!!!!!!!!")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=read cleanup")
    ssh.close()
    return

def check_memw_performance(upper_limit,lower_limit,vm_ip,my_logger):
    ssh.connect(vm_ip,username="root", password="baadal123")
    my_logger.debug( "checking memory write performance ....")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=write prepare")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=write run | grep 'total time:' | cut  -d  ':'  -f   '2'")
    data=stdout.readlines()
    print data
    memw_output=convert_into_float(data,my_logger)
    my_logger.debug( "time to run"+ str(memw_output))

    if lower_limit <= float(memw_output) <= upper_limit:
	my_logger.debug( "Memroy Write performance is upto the mark!!!!!!!!!!")
    else:
	my_logger.debug( "Memroy Write performance is not upto the mark!!!!!!!!!!")
    stdin, stdout, stderr =ssh.exec_command("sysbench --test=mutex --memory-total-size=1G --memory-oper=write cleanup")
    ssh.close()
    return





