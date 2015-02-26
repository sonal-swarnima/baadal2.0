import random
import time
import datetime
import os
import thread
import paramiko
import logging
import logging.config
from helper import *
import selenium

#creating a logger for logging the records
logger = logging.getLogger("web2py.app.baadal")
from selenium.common.exceptions import NoSuchElementException
#creating connection to remote system
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

username_list=["Baadal UF","Baadal UA","Baadal UO","Baadal UFA","Baadal UFO","Baadal UOA","Baadal UFOA","Baadal U"]

usrnm_list={"badalUF":"Baadal UF","badalUA":"Baadal UA","badalUO":"Baadal UO","badalUFA":"Baadal UFA","baadalUFO":"Baadal UFO","badalUOA":"Baadal UOA","badalUFOA":"Baadal UFOA","badalU":"Baadal U"}

#list of operation to be performed     
op_list={'revert_to_snapshot':0,'delete_snapshot':1,'snapshot':'Snapshot VM','pause_machine':'Suspend VM','Delete':'Delete VM','shutdown_machine':'Stop VM','destroy_machine':'Destroy VM','start_machine':'Start VM','user_details':'Add User','attach_extra_disk':"Attach Disk",'clone_vm':'Clone VM ','delete_user_vm':'Delete User','adjrunlevel':'Adjust Run Level','edit_vm_config':'Edit VM Config','resume_machine':'Resume VM','migrate_vm':'Migrate VM Between Hosts'}

##############################################################################################################
#  					           functions for various types of input fields  				          	     #
##############################################################################################################

def isInput(driver, xml_sub_child,my_logger):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if xml_sub_child.text!=None:
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
    else:
        if not (xml_sub_child.get("id") in ["user_password","user_username"]):
            field.send_keys(str(current_time))
    return current_time

def isSubmit( driver, xml_parent, xml_child, xml_sub_child,my_logger):
    driver.find_element_by_xpath(xml_sub_child.text).click()
    time.sleep(10)
    if xml_sub_child.get("id")=="check_data":
        xpath=xml_sub_child.get("xpath")
        status=isElementPresent(driver,xml_child,xpath,my_logger)

        if status==1:
            my_logger.debug(str(xml_child.get("value")) +": Correct data")
        else:
            my_logger.debug(str(xml_child.get("value")) +": Incorrect data")
    return

def isScroll(driver,xml_sub_child,my_logger):
        logger.debug("inside is scroll")
	field=driver.find_element_by_tag_name("html")
        logger.debug("field is : " + str(field))
	field.send_keys("Keys.PAGE_DOWN")
        logger.debug("send down key")
	driver.execute_script("window.scrollBy(0,200)", "")
        logger.debug("return ")
	return


def isHref(driver, xml_sub_child,xml_child,my_logger):
    driver.find_element_by_partial_link_text(xml_sub_child.text).click()
    if xml_sub_child.get("id")=="collaborator":
        xpath=xml_sub_child.get("xpath")
        if isElementPresent(driver,xml_child,table_path,my_logger):

            field=driver.find_element_by_xpath(xpath)
            result=xml_sub_child.get("result")
            field_text=field.get_attribute("innerHTML")
            print_result(field_text,result,xml_child,my_logger)
	    logger.error(xml_child.get("value")  + ": corrent enrty in form")
        else:
            logger.error(xml_child.get("value")  + ": Error in the form")
	return

def isInput_add(driver, xml_sub_child,xml_child,my_logger):
    path=xml_sub_child.get("user_id")
    field = driver.find_element_by_id(path)
    field.send_keys(xml_sub_child.get("user_id_data"))
    return


#add extra disk to a VM
def add_extra_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    isInput_add(driver, xml_sub_child,xml_child,my_logger)
    value=xml_sub_child.get("add_button")
    isButton_add(driver, xml_sub_child,value,xml_child,my_logger)

    return

def isButton_add(driver, xml_sub_child,value,xml_child,my_logger):
    logger.debug("inside isButton")
    if isElementPresent(driver,xml_child,value,my_logger):
        logger.debug("inside checking element ")
    	driver.find_element_by_xpath(value).click()    
    return

#add extra disk to a VM
def add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    isInput_add(driver, xml_sub_child,xml_child,my_logger)
    value=xml_sub_child.get("add_button")
    logger.debug("value is : " + str(value))
    isButton_add(driver, xml_sub_child,value,xml_child,my_logger)
    
    return


def isReadOnly(driver, xml_parent,xml_child,xml_sub_child,my_logger):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if field.get_attribute("value")!='':
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
        if field.get_attribute("value")==xml_sub_child.text:
            my_logger.debug(xml_child.get("value")  +': Result:error') #logging the report
        else:
            my_logger.debug(xml_child.get("value")  +': Result:no error') #logging the report
    else:
        my_logger.debug(xml_child.get("value")  +': Result:empty') #logging the report
    return 



def isClear(driver,xml_sub_child,my_logger) :
    driver.find_element_by_id(xml_sub_child.get("id")).clear()	
    return

def isWait( driver, xml_parent, xml_child, xml_sub_child,my_logger):
    if xml_sub_child.get("id")=="wait":
        time.sleep(300)
    else:
        time.sleep(3)
    return

def isselect (driver, xml_sub_child,my_logger):
    option_value=xml_sub_child.get("value")
    path=xml_sub_child.text
    driver.find_element_by_xpath(path + "[text()='" + option_value + "']").click()
    return

def isSelect(driver, xml_sub_child,temp,my_logger):
        logger.debug("inside isSelect")
	list=[]
	if xml_sub_child.get("select_name")=="configuration":
	    
	    path=xml_sub_child.text +str(temp)+ "']/option"
	    print path
	else:	    
            path=xml_sub_child.text   
	field=driver.find_elements_by_xpath(path)
	count=0
	for data in field:
	    value=data.get_attribute("value")
	    list.insert(count,value)
	    count+=1
	
	option_value=random.choice(list)
	logger.debug(option_value)
	driver.find_element_by_xpath(path + "[@value='" + option_value + "']").click()
        
	if xml_sub_child.get("select_name")=="configuration":
	    option_value=1
        logger.debug("op" + str(option_value))
	return option_value





# checking whether an element is present on the webpage without writting it to log
def isPresent(driver,xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return 1
    except:
        return 0

# checking whether an element is present on the webpage
def isElementPresent(driver,xml_child,xpath,my_logger):
    logger.debug("inside isElementPresent")
    try:
        driver.find_element_by_xpath(xpath)
        logger.debug(xml_child.get("value") +': Result:element exists')
        return 1
    except:
        logger.debug(xml_child.get("value") +': Result:no element exists')
        return 0
   


# checking whether a table is present on the webpage
def isTablePresent(driver,xml_child,xpath,my_logger):
    logger.debug("inside isTablePresent")
    try:
        driver.find_element_by_xpath(xpath)
        logger.debug(xml_child.get("value") +': Result:table exists')
        return 1
    except:
        logger.debug(xml_child.get("value") +': Result:no table exists')
        return 0	
   
 

def isTable(driver,xml_parent,xml_child,xml_sub_child,baadal_db,my_logger):
    logger.debug("inside is table : ")
    status_list={0:"Error",1:"failed_tasks",2:"TRY AGAIN | IGNORE",3:"my_pending_vm",4:"admin_pending_attach_disk",5:"pending_user_install_vm",6:"pending_user_clone_vm",7:"pending_user_attach_disk",8:"pending_user_edit_conf",9:"host_and_vm",10:"Configure_host",11:"admin_pending_clone_vm",12:"admin_pending_install_vm" ,13:'Configure_security',14:'pending_fac_install_vm',15:'pending_org_install_vm',16:'pending_org_clone_vm',17:'pending_org_attach_disk',18:'pending_org_edit_conf',19:"admin_pending_edit_conf" ,20:'list_my_vm',21:'fac_pending_attach_disk',22:'list_all_org_vm',23:'setting',24:'list_all_vm'}
    
    table_path=xml_sub_child.text       
    if isTablePresent(driver,xml_child,table_path,my_logger):
        logger.debug(xml_child.get("query3"))
        cur=execute_query(baadal_db,my_logger,xml_child.get("query3"))
        query_result=cur.fetchall()
        logger.debug(query_result)
        cur.close()
        field=driver.find_elements_by_xpath(xml_sub_child.text)#data from gui
        if query_result!=():
            length=len(query_result[0])#calculate number of columns of query
            length_row=len(query_result)#calculate number of columns of query
        else:
            length=0
            length_row=0
        row_count=0 #number of rows in the table
        col_count=0 #number of columns in the table     
        count=0
        for col in field:
            field_text=col.text
           
            if field_text!="":
                count=count+1     
        total=length_row*length
        if ((str(total)==str(count))) :
            for col in field:
                field_text=col.text
                if (field_text!=""):
            
                    if field_text==status_list[0]:
                        text=open_error_page(driver,xml_parent,xml_child,field_text,row_count,my_logger)
                        result=query_result[row_count][col_count]#data form query
                        print_result(text,result,xml_child,my_logger)
                    
                    elif (query_result[row_count][col_count]==4) & (xml_parent.get("name")==status_list[1]):
                        result=status_list[2]
                        print_result(field_text,result,xml_child,my_logger)
                    
                    elif (col_count%int(length)==7) & ( (xml_parent.get("name")==status_list[22]) | (xml_parent.get("name")==status_list[24])|  (xml_parent.get("name")==status_list[20])):
                    	status=query_result[row_count][col_count]
                        result=admin_vm_status(status,my_logger)                        
                        print_result(field_text,result,xml_child,my_logger)
                    
                    elif ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[21]) | (xml_parent.get("name")==status_list[16]) | (xml_parent.get("name")==status_list[17]))) | (col_count%int(length)==4) & ((xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[6]) | (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[11])) | ((col_count%int(length)==5) & (
                    (xml_parent.get("name")==status_list[12]) | (xml_parent.get("name")==status_list[24]) | (xml_parent.get("name")==status_list[22] )))   :
                        ram=query_result[row_count][col_count]
                        result=check_vm_ram(ram,my_logger)
                        print_result(field_text,result,xml_child,my_logger) 
                    
                    elif (col_count%int(length)==4) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) )  | ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[12])) | (col_count%int(length)==5) & (xml_parent.get("name")==status_list[5]) :
                        extra_disk=query_result[row_count][col_count]
                        result=check_extra_disk(extra_disk,my_logger)
                        print_result(field_text,result,xml_child,my_logger)   
                    

                    elif (((col_count%int(length)==4) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) &  (xml_parent.get("name")==status_list[17]) | (xml_parent.get("name")==status_list[21]) ) |  ((col_count%int(length)==4) & (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==5) & ((xml_parent.get("name")==status_list[11]) | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==7) & (xml_parent.get("name")==status_list[4]))  | (((col_count%int(length)==7) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) & ((xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[4]))) | (((col_count%int(length)==1) |  (col_count%int(length)==2)) &  (xml_parent.get("name")==status_list[23])):
                        mem=query_result[row_count][col_count]
                        result=check_mem(mem,my_logger)
                        print_result(field_text,result,xml_child,my_logger)  
                 
                    elif (((col_count%int(length)==8)| (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[4])) | (((col_count%int(length)==7) | (col_count%int(length)==8)) & (xml_parent.get("name")==status_list[11])) | (((col_count%int(length)==8) | (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[12])):
                        my_logger.debug("correct entries")
                    
                    elif (col_count%int(length)==4) & (xml_parent.get("name")==status_list[13]):
                        status=query_result[row_count][col_count]
                        result=check_security_visibilty(status,my_logger)
                        print_result(field_text,result,xml_child,my_logger)
                    
                    elif (col_count%int(length)==2) & (xml_parent.get("name")==status_list[10]):
                        status=query_result[row_count][col_count]
                        result=host_status(status,my_logger)
                        print_result(field_text,result,xml_child,my_logger)   
                     
                    elif (col_count%int(length)==7) & ( (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[6])) | ((col_count%int(length)==8) & ((xml_parent.get("name")==status_list[23]) | (xml_parent.get("name")==status_list[7]))):
                        status=query_result[row_count][col_count]
                        result=user_vm_status(status,my_logger)
                        print_result(field_text,result,xml_child,my_logger)  
                        
                    elif (col_count%int(length)==2) & ( (xml_parent.get("name")==status_list[17]) | (xml_parent.get("name")==status_list[21]) | (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15])) | ((col_count%int(length)==5) &  (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==6) &  ((xml_parent.get("name")==status_list[11])  | (xml_parent.get("name")==status_list[22]) | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[5]))) | ((col_count%int(length)==4) &  (xml_parent.get("name")==status_list[12])) | ( (col_count%int(length)==3)  &  (xml_parent.get("name")==status_list[23])) | ((col_count%int(length)==6) &  (xml_parent.get("name")==status_list[24])):
                        status=query_result[row_count][col_count]
                        result=check_vcpu(status,my_logger)
                        print_result(field_text,result,xml_child,my_logger)  
                        
                    elif ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[14])) | ( (col_count%int(length)==7) & (xml_parent.get("name")==status_list[21])):
                        owner_name_db=query_result[row_count][col_count]
                        owner_name_screen=xml_child[0].text
                        
                        result=faculty_vm_status(owner_name_db,owner_name_screen,xml_child)
                        print_result(field_text,result,xml_child,my_logger)     
                    
                    elif (col_count%int(length)==6) & ((xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[16]) ) | ((col_count%int(length)==7) &  (xml_parent.get("name")==status_list[17])):
                    	status=query_result[row_count][col_count]
                        
                    	result=org_task_status(status,xml_child,my_logger)
                        
                    	print_result(field_text,result,xml_child,my_logger)
                        
                    elif (col_count%int(length)==1) & (xml_parent.get("name")==status_list[12]):
                        vm_name=query_result[row_count][4]
                        query_results=execute_query(baadal_db,xml_sub_child.get("query_collbtr"),(str(vm_name))).fetchall()
                        len_query=len(query_results)
                        if query_results!="None":
                            for m in range(0,len_query):
                                result=query_results[m][0]
                                print_result(field_text,result,xml_child,my_logger)
                        else:
                            my_logger.debug(xml_child.get("value") +': Result:correct input')		
                    else:
                        result=query_result[row_count][col_count]
                        print_result(field_text,result,xml_child,my_logger)
                    col_count+=1
                    if col_count%int(length)==0:
                        row_count+=1
                        col_count=0	
        else:
            my_logger.error(xml_child.get("value")  + "Error:tuple out of index")
    else:
    	my_logger.debug(xml_child.get("value") + ":Table does not exists")
    return
	
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


#checking whether front end data and daatabase entries are equal and printing the result 		
def print_result(field_text,result,xml_child,my_logger):
	
	query_result=str(result)
        logger.debug("screen=  "+str(field_text) )
        logger.debug("db=      "+query_result)
	if str(field_text)==str(query_result):
		my_logger.debug(xml_child.get("value") +': Result:correct input') 
		
	else:
		my_logger.error(xml_child.get("value") +': Result:Incorrect input')

	return 


def total_user(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    logger.debug("total user")
    vm_user_list=[] 
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
    path="//table[@id='vm_users']/tbody/tr/td"
    if isTablePresent(driver,xml_child,path,my_logger):
	field=driver.find_elements_by_xpath(path)
	count=0
	for user in field:
	     vm_user_list.insert(count,user.text)
	     count+=1
    logger.debug(vm_user_list)
    return vm_user_list


def time_to_check_in_tasktable(my_logger):
    current_time=datetime.datetime.now()
    break_pt_time=current_time + datetime.timedelta(seconds=220) 
    print datetime.datetime.now()
    print break_pt_time 
    time.sleep(60)
    return 

def check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list,my_logger):
    logger.debug("inside check_pendingtasks_table")
    task_table_name="Pending Task"
    driver.find_element_by_partial_link_text("Tasks").click()
    path_row="//table[@id='pendingtasks']/tbody/tr"
    path_col="//table[@id='pendingtasks']/tbody/tr/td"
    path_header="//table[@id='pendingtasks']/tbody/tr/th"
    data1=[]
    logger.debug("inside check_pendingtasks_table")
     
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countp=0
        c_count=0
        vm_name_s=""
        select_row=0
        field_header=driver.find_elements_by_xpath(path_header)
        counth=0
        for h_data in field_header:
            if h_data.text=="Task":
                task_f_no=counth
            if h_data.text=="VM":
                vm_f_no=counth
            if h_data.text=="Requested By":
                requester_f_no=counth
            if h_data.text=="Request Time":
                request_f_no=counth
            counth+=1
        col_count=counth	
        field=driver.find_elements_by_xpath(path_col)	
        for data in field:	    
            if c_count%col_count==task_f_no:
                op_name_sc=data.text
		
            if c_count%col_count==vm_f_no:
                vm_name_s=data.text
		
            if c_count%col_count==requester_f_no:
		 if data.text in vm_user_list:
		     user_name_s=data.text
		     select_row=1            	    
            if (c_count%col_count==request_f_no):
                start_time_s=data.text	    
            if (select_row) & (c_count%col_count==(col_count-1)):
                if (str(vm_name)==str(vm_name_s)) & (str(operation_name)==str(op_name_sc)):
                    data1.append([])
		    data1[-1].append(start_time_s)
                    data1[-1].append(user_name_s)
		    data1[-1].append(task_table_name)		    
                    countp+=1
            c_count+=1	    
    else:
        countp=0  
    logger.debug(data1)
    return data1


def get_vm_info_frm_setting(xml_child,xml_sub_child,driver,vm_name,my_logger):
    vm_info={}
    path_col="//table[@id='configuration']/tbody/tr/td"
    path_row="//table[@id='configuration']/tbody/tr"
    path_header="//table[@id='configuration']/tbody/tr/th"
    
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
   	    
	    if hdata.text=="Operating System":
                operating_sys_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
	    if c_count%col_count==operating_sys_no:
		vm_info['operating_sys']=data.text
	    if c_count%col_count==security_domain_no:
		vm_info['security_domain']=data.text
	    if c_count%col_count==hdd_no:
		vm_info['hdd']=data.text
            if c_count%col_count==status_no:
		vm_info['status']=data.text
	    if c_count%col_count==private_ip_no:
		vm_info['private_ip']=data.text
	    if c_count%col_count==public_ip_no:
		vm_info['public_ip']=data.text
	    if c_count%col_count==vcpu_no:
		vm_info['vcpu']=data.text
	    if c_count%col_count==ram_no:
		vm_info['ram']=data.text
            c_count+=1
    
    else:
	    logger.debug("No VM exists")
    logger.debug(vm_info)
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
	logger.debug("No VM exists")
    return vm_info


def get_vm_info_frm_mylist(xml_child,xml_sub_child,driver,vm_name,my_logger):
    logger.debug("Getting VM details !!")
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
        logger.debug("collected header info")
        for data in field:
            if c_count%col_count==vm_name_no:
		logger.debug(vm_name)
		logger.debug(data.text)
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
		    logger.debug("VM selected!!!!!!!!")
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
	logger.debug("No VM exists")
    logger.debug(vm_info)
    return vm_info

def select_testing_user(driver,my_logger):
    logger.debug("Searching Baadal in ALL VMs")
    driver.find_element_by_id("search").send_keys("Baadal")
    
    return


def my_vm_list(xml_child,xml_sub_child,driver,my_logger):
    vm_info={}
    path_col="//table[@id='myvms']/tbody/tr/td"
    path_row="//table[@id='myvms']/tbody/tr"
    path_header="//table[@id='myvms']/thead/tr/th"
    #select_testing_user(driver,my_logger)
    if isTablePresent(driver,xml_child,path_col,my_logger):
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
                logger.debug("data text" + str(data.text))
                user_name=data.text
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

def vm_list(xml_child,xml_sub_child,driver,my_logger):
    vm_info={}
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    #select_testing_user(driver,my_logger)
    if isTablePresent(driver,xml_child,path_col,my_logger):
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
                logger.debug("data text" + str(data.text))
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

def vm_list_all_vm(xml_child,xml_sub_child,driver,my_logger):
    logger.debug("Inside vm_list")
    data1=[]
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"	
    if isTablePresent(driver,xml_child,path_col,my_logger):
        logger.debug("vm_list table present")
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
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Host":
                host_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            logger.debug(data.text)
            if c_count%col_count==vm_name_no:
                vm_name=data.text
                
            if c_count%col_count==user_name_no:
                logger.debug("inside"+ data.text)
                for username in username_list:
                    if username in data.text:
                        user_name=data.text
                        logger.debug("username" + str(data.text))
                        select_row=1
                        break
            if c_count%col_count==status_no:
                status=data.text
            if c_count%col_count==host_no:
                host=data.text   
            if (c_count%col_count==col_count-1):
                logger.debug("select row : "+str(select_row))
                if select_row:
                    logger.debug("inside select row")
                    field_data=driver.find_elements_by_xpath(path_row)
                    vm_id=data.get_attribute("id")
                    print vm_id
                    countc+=1
                    break       
            c_count+=1       
    if countc==0:
        print "No user of testing User.Please Create a VM!!!!"
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_name=""
        vm_id=""
        host=""
    data1.insert(0,vm_id)
    data1.insert(1,vm_name)
    data1.insert(2,host)
    logger.debug(data1)
    return data1

# Function to find VM id of a given VM with name
def find_vm_id(driver,xml_child,xml_sub_child,vm_name1,my_logger):
    logger.debug("Inside find_vm_id function ")
    data1=[]
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    logger.debug("vm_name :"+str(vm_name1))	
    if isTablePresent(driver,xml_child,path_col,my_logger):
        print "vm_list table present"
        countc=0
        c_count=0
        r_count=0
        select_row=0
        select=0
        col_count=0
        count=0
        header_field=driver.find_elements_by_xpath(path_header)
        for hdata in header_field:
            if hdata.text=="Name":
                vm_name_no=count
            if hdata.text=="Owner":
                user_name_no=count
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Host":
                host_no=count
            if hdata.text=="Organisation":
                org_no=count
            count+=1
        col_count=count
        logger.debug("org no : "+str(org_no))
        logger.debug("count:"+str(count))
        logger.debug("colcount :"+str(col_count))
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            logger.debug("data in field :"+str(field))
            if c_count%col_count==vm_name_no:
                vm_name=data.text
                if vm_name == vm_name1:
                    select=1
                
            if c_count%col_count==user_name_no:
                logger.debug("inside"+str(data.text))
                for username in username_list:
                    if username==data.text:
                        user_name=data.text
                        print "username" + str(data.text)
                        select_row=1
                        break
            if c_count%col_count==host_no:
                host=data.text   
            if c_count%col_count==org_no:
                org_name=data.text
            if c_count%col_count==status_no:
                status=data.text 
            if (c_count%col_count==col_count-1):
                print "select row : "+str(select_row)
                if select_row and select:
                    print "inside select row"
                    field_data=driver.find_elements_by_xpath(path_row)
                    vm_id=data.get_attribute("id")
                    print vm_id
                    countc+=1
                    break       
            c_count+=1       
    if countc==0:
        vm_name=""
        vm_id=""
        host=""
        
    data1.insert(0,vm_id)
    data1.insert(1,vm_name)
    data1.insert(2,host)
    data1.insert(3,org_name)
    data1.insert(4,user_name)
    data1.insert(5,status)
    logger.debug("value returned from function find_vm_id :" +str(data1))
    return data1


#perform action on setting button of vm's
def click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    logger.debug("Clicking on setting button...")
    logger.debug("vm_id : " + str(vm_id))
    vmid="vm_"+ str(vm_id)
    logger.debug("vmid : " + str(vmid))
    path="//*[@id='" +str(vm_id)+"']"
    #path="//*[@href='/baadal/user/settings/"+ str(vm_id) +"']"
    logger.debug(path)
    if isElementPresent(driver,xml_child,path,my_logger):
       driver.find_element_by_id(vmid).click()
       logger.debug("Clicked on setting button...")
    else:
       logger.debug("Clicking on setting button..Failed as setting button does not exist...")
    return


#perform action on setting button of vm's
def click_on_setting1(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    logger.debug("Clicking on setting button...")
    path="//*[@id='" +str(vm_id)+"']"
    vmid="vm_"+ str(vm_id)
    logger.debug("fetching VM id : " + str(vmid))
    try:
       driver.find_element_by_id(vmid).click().perform()
    except AttributeError:
       
       i=1
       while (i):
           try:
              driver.find_element_by_id(vmid).click().perform()
	      driver.refresh()
	      isScroll(driver, xml_sub_child,my_logger)

           except AttributeError:
              i=1
              print "dsfg"
           except NoSuchElementException:
              i=0



    return


#open dialogbox when error occurs in falied tasks
def click_on_dialogbox(driver):
    try:
        alert = driver.switch_to_alert()
        alert.accept()
        return 1
    except:
        return 0

    
#for executing sql-query			
def execute_query(baadal_db,my_logger,sql_query,arg=None):
    my_logger.debug("Executing query : ")
    cursor=baadal_db.cursor()    
    if arg==None:
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query,arg)

    return cursor 
		
##############################################################################################################
#                              Function for checking wether pending task list is Empty or not                #
##############################################################################################################
def checkPendingTask(driver):
    flag=0
    start=time.time()
    end=start+300
    xpath="//div[@id='pendTab']/h3"
    driver.find_element_by_xpath("//a[@href='/baadal/admin/task_list']").click()
    while start<end:
        time.sleep(10)
        driver.refresh()
        time.sleep(10)
        if isPresent(driver,xpath):
            flag=1
            break
        start=time.time()
    return flag



################################################################################################################





def isWait( driver, xml_parent, xml_child, xml_sub_child,my_logger):
    if xml_sub_child.get("id")=="wait":
        time.sleep(300)
    else:
        time.sleep(3)
    return

def isInput_add(driver, xml_sub_child,xml_child,my_logger):
    logger.debug(xml_sub_child.get("user_id"))
    path=xml_sub_child.get("user_id")   
    field = driver.find_element_by_id(path) 
    logger.debug(xml_sub_child.get("user_id_data"))  
    field.send_keys(xml_sub_child.get("user_id_data"))
    return

def isButton_add(driver, xml_sub_child,value,xml_child,my_logger):
    logger.debug("inside isButton")
    if isElementPresent(driver,xml_child,value,my_logger):
        logger.debug("inside checking element ")
    	driver.find_element_by_xpath(value).click()    
    return

#add extra disk to a VM
def add_value(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    isInput_add(driver, xml_sub_child,xml_child,my_logger)
    value=xml_sub_child.get("add_button")
    logger.debug("value is : " + str(value))
    isButton_add(driver, xml_sub_child,value,xml_child,my_logger)
    
    return
###############################################################################################################

#message display on screen
def message_in_db(xml_sub_child,my_logger):
    print "inside msg_in_db"
    print op_list
    op_name=xml_sub_child.get("op")
    print op_name
    if op_name=="user_details":
        result="User is added to vm" 
    else:
        print "inside msg in db else"
    	result=op_list[op_name] +" request added to queue."
    	
	return result

#retreiving message from given xpath
def message_flash(driver,xml_sub_child,xml_child,my_logger):
    logger.debug("fetching message from GUI...")
    path='//flash[@id="flash_message"]'
    logger.debug(path)
    if isElementPresent(driver,xml_child,path,my_logger):
        data=driver.find_element_by_id("flash_message")
        field_text=data.text
        logger.debug("Message:" + str(field_text))
    else:
	logger.debug("didn't get the element")
    logger.debug("fetched message from GUI...")
    return field_text

def task_path_vm(xml_sub_child,op_name,my_logger):
    logger.debug("inside task path vm")
    #op_name=xml_sub_child.get("op")
    logger.debug("op name is : " + str(op_name))
    if op_name=="pause_machine":
        path='Suspend this Virtual Machine'    
    if op_name=="shutdown_machine":
        path='Gracefully shut down this virtual machine'
    if op_name=="start_machine":
        path='Turn on this virtual machine'    
    if op_name=="destroy_machine":
    	path='Forcefully power off this virtual machine'        
    if op_name=="resume_machine":
        path='Unpause this virtual machine'
    if op_name=="attach_extra_disk":
       path='Attach Extra Disk'
    if op_name=="clone_vm":
       path='Request VM Clone'
    return path

def task_path(xml_sub_child):
    op_name=xml_sub_child.get("op")
    if op_name=="pause_machine":
        path='Suspend this Virtual Machine'
    if op_name=="shutdown_machine":
        path='Gracefully shut down this virtual machine'
    if op_name=="start_machine":
        path='Turn on this virtual machine'
    if op_name=="destroy_machine":
    	path='Forcefully power off this virtual machine'
    if op_name=="resume_machine":
        path='Unpause this virtual machine'
    return path

    

#open error link on differnet page
def open_error_page(driver,xml_parent,xml_child,row_count,my_logger):
    logger.debug("Fetching error message from failed task table")
    logger.debug("row count is  : " + str(row_count))
    (driver.find_elements_by_link_text("Error"))[row_count].click()
    time.sleep(5)
    error_page="//span[@id='overlayblock']/div" 
    error_page_close_text="CLOSE WINDOW"
    xpath=error_page
    if isTablePresent(driver,xml_child,xpath,my_logger):
        field=driver.find_element_by_xpath(xpath)
        error_message=field.text
        driver.find_element_by_link_text("CLOSE WINDOW").click()
        my_logger.debug("fetched error message :" + str(error_message))
    else:
        error_message="None"
	logger.debug("Does not get location path")
    return error_message



def perform_vm_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    print "inside perform_vm_operation"
    failed_task=check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    logger.debug("failed tasks : " + str(failed_task))
    return failed_task

####################################################################################################################################################
#Checking in task table                                                                                                                            #
####################################################################################################################################################

def perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):   
    logger.debug("Checking data in completed and failed task table after performing operation....")
    task_value=[]
    logger.debug("operation name is : " + str(operation_name))
    p_count=check_pendingtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    if str(p_count)==str(0):
        logger.debug("p_count check")
	c_count=check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
	task_value.append(c_count)
        f_count=check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
	task_value.append(f_count)
    else:
         logger.debug("Its in pending task table!!!!!!!!")
    
    logger.debug("Checked data in completed and failed task table after performing operation....")
    return task_value



def send_bug_on_bugzilla(error_message,xml_child):
    message="Hello Team,\n\n"\
              +str(error_message)+ " .For further details check the logs on https://baadaltesting.cse.iitd.ernet.in\n\n Thanks,\n ...."
    subject="Bug in "+ str(xml_child.get("value"))
    import os
    path=os.popen('pwd').read()
    path=path.strip('\n')
    os.system("python " +str(path)+ "/applications/baadal/bugzilla.py " +str(subject)+" " + str(message))
    return

def check_vm_in_failed_task(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_start_time,my_logger):
    vm_in_failed=0
    logger.debug("Data is in failed Task table..Fetching error......")
    path="//table[@id='failedtasks']/tbody/tr"
    if isTablePresent(driver,xml_child,path,my_logger):
        
        driver.find_element_by_partial_link_text("Failed Tasks").click()
        field=driver.find_elements_by_xpath("//table[@id='failedtasks']/tbody/tr")
        vm_in_failed=0
        row_count=0
        for x in field:
            if (vm_name in x.text) & (operation_name in x.text)  & (str(task_start_time) in x.text):
                logger.error( "Your request is Failed!!!!")
		r=row_count-1
                error_message=open_error_page(driver,xml_parent,xml_child,r,my_logger)
                logger.debug("Error:"+str( error_message))
		send_bug_on_bugzilla(error_message,xml_child)
		#send_mail(xml_child.get("value") + " This testcase has failed due to the following reason.." + str(error_message))
	    row_count+=1
    return


def compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger):
    logger.debug("Comparing Task table........")
    flag=2
    if len(task_value[0])!=len(task_n_value[0]):
	start_time=task_n_value[0][0]
	value=0
    else:
	start_time=task_n_value[1][0]
	value=1
    
    table={0:'complete task table',1:'failed task table'}
    
    my_logger.debug("Your task is in " + str(table[value]))
    if table[value]=='failed task table':
        
	check_vm_in_failed_task(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,start_time,my_logger)
	flag=1
    logger.debug("Compared Task table..")
    return flag





import time
def check_pendingtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("Checking data in pending task table............")
    task_table_name="Pending Task"
    driver.refresh()
    time.sleep(5)
    flag=1
    path_row="//table[@id='pendingtasks']/tbody/tr"
    path_col="//table[@id='pendingtasks']/tbody/tr/td"
    path_header="//table[@id='pendingtasks']/tbody/tr/th"
    pcount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header,my_logger)
    
    p_count=len(pcount)
    logger.debug(p_count)
    start_time=datetime.datetime.now()
    limit_time=start_time + datetime.timedelta(seconds=3600)
    
    if (p_count!=0): 
        if (limit_time>datetime.datetime.now()):
            logger.debug("checking")
            check_pendingtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
	    flag=0
	else:
            my_logger.debug( "Testcase is still in pending task table.Either there are too many task to perform or scheduler is not working.check scheduler status!!!!!!")
            flag=0
    else :
       flag=0
       my_logger.debug( "Pending Task Table is empty.Task is either in Failed or in Complate task table !!!")
    logger.debug("Checking data in pending task table")
    logger.debug("flag value is : " + str(flag))
    return flag



def check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header,my_logger):
    logger.debug("inside check_task_table operation name is : " + str(operation_name))
    logger.debug("vm_name is : " + str(vm_name))
    task_data=[]
    if isTablePresent(driver,xml_child,path_col,my_logger):
        countp=0
        c_count=0
        vm_name_s=""
        select_row=0
        field_header=driver.find_elements_by_xpath(path_header)
        counth=0
        for h_data in field_header:
	    
            if h_data.text=="Task":
                task_f_no=counth
		
            if h_data.text=="VM":
                vm_f_no=counth
            if h_data.text=="Requested By":
                requester_f_no=counth
            if h_data.text=="Request Time":
                request_f_no=counth
            counth+=1
        col_count=counth
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==task_f_no:
                op_name_sc=data.text 
                logger.debug("op_name_sc is : " + str(op_name_sc))               
            if c_count%col_count==vm_f_no:
                vm_name_s=data.text
                logger.debug("vm_name is : " + str(vm_name))                
            if c_count%col_count==requester_f_no:
		 usernm=usrnm_list[xml_child[0].text]
            	 if str(usernm)==str(data.text):
		     user_name_s=data.text
		     select_row=1                     
            if (c_count%col_count==request_f_no):
                start_time_s=data.text
            if (select_row) & (c_count%col_count==(col_count-1)):
                logger.debug("vm_name is : " + str(vm_name))
                logger.debug("vm_name_s is : " + str(vm_name_s))
                logger.debug("op_name_sc is : " + str(op_name_sc))
                logger.debug("operation_name is : " + str(operation_name))
                if (str(vm_name)==str(vm_name_s)) & (str(operation_name)==str(op_name_sc)):	
		    logger.debug("vm is still in pending task table")	    
		    task_data.append(start_time_s)
                    countp+=1
            c_count+=1
    else:
        countp=0
    logger.debug("task_data is : " + str(task_data))
    return task_data



def check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("Checking data in completed task table operation name is : " +str(operation_name))
    task_table_name="Completed Task"
    time.sleep(20)
    driver.find_element_by_partial_link_text("Tasks").click()
    driver.find_element_by_partial_link_text("Completed Tasks").click()
    path_row="//table[@id='completedtasks']/tbody/tr"
    path_col="//table[@id='completedtasks']/tbody/tr/td"
    path_header="//table[@id='completedtasks']/tbody/tr/th"
    ccount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header,my_logger)
    logger.debug("Checking data in completed task table")
    logger.debug("ccount is : " + str(ccount))
    return ccount


def check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("Checking data in failed task table operation name is : " + str(operation_name))
    task_table_name="Failed Task"
    driver.find_element_by_partial_link_text("Failed Tasks").click()
    path_row="//table[@id='failedtasks']/tbody/tr"
    path_col="//table[@id='failedtasks']/tbody/tr/td"
    path_header="//table[@id='failedtasks']/tbody/tr/th"
    fcount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header,my_logger)
    logger.debug("Checked data in failed task table")
    logger.debug("fcount is : " +str(fcount))
   
    return fcount




def check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("Checking data in completed and failed task table before performing operation....")
    task_value=[]
    c_count=check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    task_value.append(c_count)
    f_count=check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    task_value.append(f_count)    
    logger.debug("Checked data in completed and failed task table before performing operation....")
    return task_value


#Checking data in task table

def check_data_in_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,my_logger):
    logger.debug("Checking data in task table......")
    value=0
    driver.find_element_by_link_text("Tasks").click()
    task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    driver.find_element_by_partial_link_text("Pending Tasks").click()
    task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
    logger.debug("Before operations:"+str(task_value))
    logger.debug("After operations:"+str(task_n_value))
    if task_n_value!=[]:
        value=compare_task_table(driver,xml_sub_child,xml_child,xml_parent,vm_name,operation_name,task_value,task_n_value,my_logger)
    logger.debug("Checked data in task table......")
    return value
   


############################################################################################################################################################################################################

def check_status_of_vm(driver,xml_sub_child,xml_child,my_logger):
    logger.debug("inside check_status_of_vm")
    c_count=0
    path_col="//table[@id='configuration']/tbody/tr/td"
    path_header="//table[@id='configuration']/tbody/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
        field_header=driver.find_elements_by_xpath(path_header)
        counth=0
        for h_data in field_header:
            if h_data.text=="Status":
                status_f_no=counth
            counth+=1
        col_count=counth
        field=driver.find_elements_by_xpath(path_col)
	
        for data in field:
	    if c_count%col_count==status_f_no:
                status=data.text
	    c_count+=1
	
    return status

        
#getting user id of a user access to a VM                        
def get_user_id(driver,xml_sub_child,xml_child,vm_name,baadal_db,my_logger):
    query_result=execute_query( xml_sub_child.get("query_user_id"),(str(vm_name))).fetchone()
    baadal_db.commit()
    field=driver.find_elements_by_xpath(xml_sub_child.get("xpath_user"))
    for t in field:
        if str(query_result[1]) in t.text:
            user_id=query_result[0]
            logger.debug("user_id :" + " " + str(user_id))
    return user_id



#Checking data in Snapshot table  
                                                
def check_snapshot(vm_name,driver,xml_child,xml_sub_child,baadal_db,my_logger):
    logger.debug("Checking for entries in current snapshot table")
    path=xml_sub_child.get("xpath_snap")
    if isElementPresent(driver,xml_child,path,my_logger):
        query_result=execute_query(xml_sub_child.get("query4"),(str(vm_name))).fetchall()
        baadal_db.commit()
        total_snap=len(query_result)
        field=driver.find_elements_by_xpath(path)
        result_setting_page(field,query_result,driver,xml_child,xml_sub_child,my_logger)
        return total_snap
    else :
        total_snap=""
        return total_snap





def check_task_task_report(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("inside check task task report")
    logger.debug("operation name is : " + str(operation_name))
    i=1
    j=0
    #driver.find_element_by_link_text("Tasks").click()
    k=20
    print i
    while i and k:
       local_list=check_pendingtask_table_status(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger)
       i=len(local_list)
       logger.debug("still in pending task")
       time.sleep(30)
       k=k-1
       print i
    local_list=check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name, my_logger)
    i=len(local_list)
    logger.debug("i is : " + str(i))
    logger.debug("j is : " + str(j))
    if i>j:
       return True
    else:
       return False

def check_pendingtask_table_status(driver,xml_sub_child,xml_child,vm_name,operation_name,my_logger):
    logger.debug("Inside check_pendingtask_table")
    task_table_name="Pending Task"
    driver.refresh()
    time.sleep(5)
    path_row="//table[@id='pendingtasks']/tbody/tr"
    path_col="//table[@id='pendingtasks']/tbody/tr/td"
    path_header="//table[@id='pendingtasks']/tbody/tr/th"
    pcount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header,my_logger)
    return pcount


def vm_list_host_detail(xml_child,xml_sub_child,driver,my_logger):
    logger.debug("inside vm_list_host : ")
    data1=[]
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    if isTablePresent(driver,xml_child,path_col,my_logger):
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
            if hdata.text=="Status":
                status_no=count
            if hdata.text=="Host":
                host_no=count
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_name=data.text
            if c_count%col_count==user_name_no:
                if data.text in username_list:
                    user_name=data.text
                    select_row=1
            if c_count%col_count==status_no:
                status=data.text
            if c_count%col_count==host_no:
                host=data.text
            if (c_count%col_count==col_count-1):
                logger.debug("select_row is :" + str(select_row))
	        if select_row:
                    if (str(status)==xml_sub_child.get("status")):
                        field_data=driver.find_elements_by_xpath(path_row)
                        vm_id=data.get_attribute("id")
                        countc+=1
                        break
            c_count+=1
    if countc==0:
        my_logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_name=""
        vm_id=""
	user_name=""
    data1.insert(0,vm_id)
    data1.insert(1,vm_name)
    data1.insert(2,user_name)
    data1.insert(4,host)
    logger.debug(data1)
    return data1





#approving or rejecting vm operations
def isCheckdata(driver,xml_parent, xml_child, xml_sub_child,vm_name,baadal_db,my_logger):
    logger.debug("Finding row to approve VM.....")
    table_path=xml_sub_child.text
    driver.refresh()
    if isTablePresent(driver,xml_child,table_path,my_logger):
    	flag=0
        field=driver.find_elements_by_xpath(xml_sub_child.text)#data from gui
        if  xml_sub_child.get("data")=="integeration":
            path_col="//table[@id='sortTable1']/tbody/tr/td"
    path_row="//table[@id='sortTable1']/tbody/tr"
    path_header="//table[@id='sortTable1']/thead/tr/th"
    path_col="//table[@id='sortTable1']/tbody/tr/td"

    if isTablePresent(driver,xml_child,path_col,my_logger):
        logger.debug("vm_list table present")
        logger.debug(vm_name)
        countc=0
        c_count=0
        r_count=0
        select_row=0
	select_r=0
        header_field=driver.find_elements_by_xpath(path_header)
        count=0
        for hdata in header_field:
            if hdata.text=="Requested By":
                user_name_no=count
            if hdata.text=="VM Name":
                vm_name_no=count
            count+=1
        col_count=count
        driver.refresh()
        field=driver.find_elements_by_xpath(path_col)
        for data in field:
            if c_count%col_count==vm_name_no:
                vm_nam=data.text
                if str(vm_nam)==str(vm_name):
		    select_r=1
                    
            if c_count%col_count==user_name_no:
		i=xml_child[0].text
		username=usrnm_list[i]
		if str(data.text)==str(username):
                    select_row=1
            if (c_count%col_count==col_count-1):
	        if (select_row and select_r):
                    logger.debug( "Got row to approve vm")
                    path=data.get_attribute("id")
                    vm_id="accept_" + str(path)
                    logger.debug(vm_id)
		    vmid=str(vm_id)
                    driver.find_element_by_xpath("//*[@href='/baadal/admin/approve_request/"+ str(path) +"']").click()
		    '''f_data=driver.find_element_by_xpath("//a[@id='"+str(vm_id)+"']")
		    get_href=f_data.get_attribute("href")
                    logger.debug(get_href)
		    logger.debug("//*[@href='"+str(href)+"']")
                    #driver.find_element_by_xpath("//*[@href='"+str(href)+"']").click()
		    try:
		        driver.find_element_by_id(vmid).click().perform()
		    except AttributeError:
		
                       
                        paths='//*[@id="accept_'+str(path)+'"]'
			logger.debug(paths)
                        while isElementPresent(driver,xml_child,paths,my_logger):			   			   
			   try:
                               logger.debug("inside try block")
		               driver.find_element_by_id(vmid).click().perform()
		    	   except AttributeError:                                  
		               logger.debug("inside except block")
                           except NoSuchElementException:
                               i=0'''
		    countc+=1
                    break
            c_count+=1
    logger.debug("return back after approving vm")
    return

#performing delete operation on vm

def op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
    limit=0
    logger.debug("Deleting testing user VM....")  
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

def delete_specific_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger):
   my_logger.debug("Deleting VM.............")
   driver.find_element_by_link_text("All VMs").click()
   click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
   op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,my_logger)
   my_logger.debug("Deleted VM.............")
   return
 
 
def change_vm_paswd(vm_ip):
    time.sleep(30)
    logger.debug("inside change_vm_passwd")
    import os
    path=os.popen('pwd').read()
    path=path.strip('\n')
    logger.debug("path is : " + str(path))
    logger.debug("expect " + str(path)+ "/new_test.expect yes baadal baadal123 " + str(vm_ip) + " root exit")
    try :
        os.system("expect " + str(path)+ "/new_test.expect yes baadal baadal123 " + str(vm_ip) + " root exit")       
    except : 
        os.system("exit")
    time.sleep(120)
    return

#################################################################################################################
#                         Function for mailing
                                           #
#################################################################################################################
def send_mail(error_message):
    from gluon.tools import Mail
    mail = Mail()
    mail.settings.server = 'smtp.iitd.ernet.in:25'
    mail.settings.sender = 'jyoti690.visitor@cse.iitd.ernet.in'
    mail.settings.login = 'jyoti690.visitor@cse.iitd.ernet.in:jyoti_saini'
    mail.send(to=['sonal.swarnima@gmail.com','kanikashridhar@gmail.com ','keerti.agr@gmail.com','nalini.varshney22@gmail.com','jyoti690saini@gmail.com'],
          subject='Bug in baadal',
          # If reply_to is omitted, then mail.settings.sender is used
          message="Hello Team,\n\n"
              +str(error_message)+ " .For further details check the logs on https://baadaltesting.cse.iitd.ernet.in\n\n"
              "Thanks,\n"
              "....")
