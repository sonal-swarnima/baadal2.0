# coding: utf8
import os
import thread
import paramiko
import logging
import datetime
import random
import logging.config
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import TimeoutException
from helper import *
import libvirt
import commands
import MySQLdb as mdb
from selenium.webdriver.common.keys import Keys
import sys
import time

from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()


#creating a logger for logging the records
logger = logging.getLogger("web2py.app.testapp")

#creating connection to remote database
baadal_db=db_connection() 


#creating connection to remote system
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#getting path of baadal
host_ip=get_app_name()
baadal_path="https://"+str(host_ip)+"/baadal"

#################################################################################################################
#                                       The main test function  for unit testing                                            #
#################################################################################################################



def test_script(test_case_no):
    root = xml_connect()
    num=int(test_case_no)
    vm_status=1
    vm_status1=1
    
    if root[num-1].get("id")==test_case_no:
        temp=1
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
		  
                    if vm_status:
                        field_type=root[i][j][k].get("type")
                        xml_parent=root[i]
                        xml_child=root[i][j]
                        xml_sub_child=root[i][j][k]
                	
                    	if field_type=="input": #checking for text fields
                        	vm_name1=isInput(driver,xml_sub_child)
                      		
                    	elif field_type=="read_only": #checking for submit button
                        	isReadOnly(driver, xml_parent,xml_child,xml_sub_child)
						
                    	elif field_type=="submit": #checking for submit button
                        	time.sleep(3)
                        
                        	isSubmit(driver, xml_parent,xml_child,xml_sub_child)
                        
	
                    	elif field_type=="scroll":#scrolling the page up/down
                        	isScroll(driver,xml_sub_child)
				 	
                    	elif field_type=="clear":#Clearing text from textarea 
                        	isClear(driver,xml_sub_child)  
                        	
                        elif field_type=="href":
                            isHref(driver,xml_sub_child,xml_child)#clicking on the hyper link
                    
                    	elif field_type=="select":
				
                        	temp=isSelect(driver,xml_sub_child,temp_value)# selecting from dropdown menu
                    		
                    	elif field_type=="sanity_table":
                        	isSanityCheck(driver, xml_parent, xml_child, xml_sub_child)# checking for data in  sanity table
			 	
                    	elif field_type=="table":
                        	isTable(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                         
                    	elif field_type=="img":#checking for setting image
                        	table_path=xml_sub_child.get("path")
                        	vm_name2=isImage(driver,xml_child,xml_sub_child,table_path)
				
                    	elif field_type=="check_tables":#cheking for host table
                        	isCheckTable(driver,xml_parent,xml_child,xml_sub_child)
                
                    	elif field_type=="wait":
                        	isWait(driver,xml_parent,xml_child,xml_sub_child)#checking for data in table
                    
                    	elif field_type=="check_data":
				
                        	isCheckdata(driver,xml_parent,xml_child,xml_sub_child,vm_name)#checking for data in table
                 
                    	elif field_type=="task_table":
                         	operation_name=xml_sub_child.text
				time.sleep(30)
                         	vm_status1=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)#checking for data in table
                
                    	elif field_type=="attach_disk":
                        	operation_name=xml_sub_child.text
                        	attack_disk(driver,xml_sub_child,xml_child,vm_name,operation_name)#checking for data in table
                        elif field_type=="idompotent":
                             maintain_idompotency(driver,xml_sub_child,xml_child)				          				          				
			     #vm_list(driver)
                    	else:
                        	logging.debug("report problem") #logging the report
                    	if k==39:
                            vm_status=vm_status1
                    	if k==5:
                        	vm_name=vm_name1
			if k==5:
			    temp_value=temp
			    

            	driver.close()#disconnect from server        

            else:
                logger.debug("Cannot connect to controller.Please check controller")

        
#################################################################################################################
#                                       The main test function  for graph testing                                       #
#################################################################################################################

def graph_test(test_case_no):
#Checking memory utilizations
    
    root = xml_connect()
    i=int(test_case_no)
    
    xml_sub_child=root[i-1][0][0]
    xml_child=root[i-1][0]   
    
    ssh.connect("10.208.21.67", username="root", password="baadalcse_blade_FEB2014")   
    stdin, stdout, stderr =ssh.exec_command("cd /mnt/datastore/vm_rrds/;rrdtool fetch IITD_badalUFA_test1.rrd MIN -s -600s -e now")
	
    initial_data=stdout.readlines()
   
    current_time=datetime.datetime.now()
    ini_data=str(initial_data[2])
    init_data=ini_data.split()
    
    ssh.connect("10.208.23.56", username="root", password="baadal")   
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_run_prgrm"))
    data=stdout.readlines()
    time.sleep(100)   
    ssh.connect("10.208.21.67", username="root", password="baadalcse_blade_FEB2014")   
    stdin, stdout, stderr =ssh.exec_command("cd /mnt/datastore/vm_rrds/;rrdtool fetch IITD_badalUFA_test1.rrd MIN -s -600s -e now")
    final_data=stdout.readlines()
    fin_data=str(final_data[2])
    finl_data=fin_data.split()

    print "finl_data" + str(finl_data)
    print "init_data" + str(init_data)
    print_graph_result(finl_data,init_data,xml_child)
    
    
def print_graph_result(finl_data,init_data,xml_child):
    logger.debug(xml_child.get("value") +" Initial_data:"+ str(init_data))
    logger.debug(xml_child.get("value") +" Final_data:"+ str(finl_data))
    for i in range(1,7):
        if init_data[i]=="-nan":
        	i_data=0
    	else:
       		 i_data=init_data[i]      
    	diff=float(finl_data[i])-float(i_data)
    	logger.debug(xml_child.get("value") +": Differnce "+ str(diff)) 
    	if finl_data[i]=="-nan":
       		 logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
        else :
      	     if diff<=0:
            	logger.debug(xml_child.get("value") +':  '+"Incorrect Data") 
       	     else:
                 logger.debug(xml_child.get("value") +':  '+"Correct Data") 
	'''print xml_child.get("type")
	print i
        if (xml_child.get("type")=="CPU") & (i==1):
	    print "CPU"
            check_type_of_graph(i)
            break
        if (xml_child.get("type")=="RAM") & (i==2 ):
            check_type_of_graph(i)
	    print "RAM"
            break
        if (xml_child.get("type")=="DISK") & (i==4| i==3):
            check_type_of_graph(i)
	    print "DISK"
            break
        if (xml_child.get("type")=="NETWORK") & (i==5 | i==6):
            check_type_of_graph(i)
     	    print "NETWORK"
            break     '''
            
    return

'''def check_type_of_graph(i):
    	if init_data[i]=="-nan":
        	i_data=0
    	else:
       		 i_data=init_data[i]      
    	diff=float(finl_data[i])-float(i_data)
    	logger.debug(xml_child.get("value") +": Differnce "+ str(diff)) 
    	if finl_data[i]=="-nan":
       		 logger.debug(xml_child.get("value") +':  '+"Incorrect Data")
        else :
      	     if diff<=0:
            	logger.debug(xml_child.get("value") +':  '+"Incorrect Data") 
       	     else:
                 logger.debug(xml_child.get("value") +':  '+"Correct Data") 
    return'''

def print_graph(finl_data,xml_child):
    for i in range(1,7):
        if finl_data[i]=="-nan":
            logger.debug(xml_child.get("value") +':  '+"Correct Data")
        else :
            logger.debug(xml_child.get("value") +':  '+"Incorrect Data")  
#################################################################################################################
#                                        Function  for Network testing                                            #
#################################################################################################################           
def packages_install_test(test_case_no): 
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
            logger.debug(xml_child.get("value") +': '+pkg +" :software has installed properly") 
            
        else:
            logger.debug(xml_child.get("value") +': '+pkg +" :software has not installed properly") 
 
    return
                                                                                                                                                                        

                                         
def check_stat_on_host():
    
    conn = libvirt.open("qemu+ssh://root@" + '10.208.21.70' + "/system")
    
    db=mdb.connect("10.208.21.111","baadaltesting","test_baadal","baadal")
    cursor1=db.cursor()
    cursor1.execute("select vm_name,vm_data.status,host_id from vm_data join host where host.id=vm_data.host_id and host_ip='10.208.21.70'")
    output=cursor1.fetchall()
    data1=str(output)
    lists=data1.split("), (")
    col_count=len(lists)
    
    for i in range(0,col_count):
        data1s=lists[i].split(",")
        newstr = data1s[0].replace("'", "")
        if i==0:
            newstr=newstr.replace("((","")
        for id in conn.listDomainsID():
            dom = conn.lookupByID(id)
            infos = dom.info()
            if newstr==dom.name():
                if (((data1s[1]==" 5L") & (infos[0]==1)) | ((data1s[1]==" 6L") & (infos[0]==3))):
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

# checking whether a table is present on the webpage
def isElementPresent(driver,xml_child,xpath):
    try:
        driver.find_element_by_xpath(xpath)
   
        return 1
    except :
        logger.debug(xml_child.get("value") +': Result:no element exists')
        return 0
   
        	


# checking whether an element is present on the webpage
def isTablePresent(driver,xml_child,xpath):
    try:
        driver.find_element_by_xpath(xpath)
        
        return 1
    except:
        logger.debug(xml_child.get("value") +': Result:no table exists')
        return 0	
   

				
#checking whether front end data and daatabase entries are equal and printing the result 		
def print_result(field_text,result,xml_child):
	
	query_result=str(result)
        logger.debug("screen=  "+str(field_text) )
        logger.debug("db=      "+query_result)
	if str(field_text)==str(query_result):
		logger.debug(xml_child.get("value") +': Result:correct input') 
		
	else:
		logger.error(xml_child.get("value") +': Result:Incorrect input')

	return 

	
#open error link on differnet page			
def open_error_page(driver,xml_parent,xml_child,text,row_count):
    (driver.find_elements_by_link_text(text))[row_count].click()
    time.sleep(5)
    xpath=xml_parent.get("error_page")
    if isTablePresent(driver,xml_child,xpath):
        field=driver.find_element_by_xpath(xpath)	
        error_message=field.text
        driver.find_element_by_link_text(xml_parent.get("error_page_close_text")).click()
    else:
        error_message="None"
    return error_message

	
#converting vm status bits into status text			
def admin_vm_status(status):
    vm_status=["Running","Paused","Shutdown"]
    if status==2:
        result=vm_status[0]
    if status==3:
        result=vm_status[1]
    if status==4:
        result=vm_status[2]
    return result 

    	
#converting host status bits into status text    	    	    	
def host_status(status):
	host_status={0:"Down",1:"Up",2:"Maintenance"}	
	if status==0:
		result=host_status[0]
	if status==1:
		result=host_status[1]
	if status==2:
		result=host_status[2]
	return result

		
#converting  status bits into status text	
def org_task_status(status,xml_child):
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
    

        
    
#for executing sql-query			
def execute_query(sql_query,arg=None):
    cursor=baadal_db.cursor()    
    if arg==None:
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query,arg)

    return cursor

def total_element(driver,xml_sub_child,xml_child,path):
     field=driver.find_elements_by_xpath(path)
     count=0
     for element in field:
	count+=1
     
     return count
  
def extract_col_no(driver,xml_sub_child,xml_child,path_header,headerlist,arg=None):
    header_field=driver.find_elements_by_xpath(path_header)
    count=0
    for hdata in header_field:
        for data in headerlist:
            if hdata.text==data.text:
    		header_list.append([])
		header_list[-1].append(data)
                header_list[-1].append(count)
		
        count+=1
    col_count=count
    if arg==None:
        header_list.append([])
        header_list[-1].append("total_col")
        header_list[-1].append(col_count)

    return header_list
    
    
def check_owner_name_in_allvm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name):
    data1=[]
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    
	
    if isTablePresent(driver,xml_child,path_col):
        countc=0
        c_count=0
        row_present=0	
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
            count+=1
        col_count=count
        field=driver.find_elements_by_xpath(path_col)
        
        
        for data in field:
            
            if c_count%col_count==vm_name_no:
                vm_name=data.text
            if c_count%col_count==user_name_no:
		ownername=data.text
    
            if c_count%col_count==status_no:
                status=data.text
                
            
            if (c_count%col_count==col_count-1):
		if (str(status)==xml_sub_child.get("status")):
		    vmid=data.get_attribute("id")
		    
                    if str(vm_id)==str(vmid[3:]):
			if ownername=="Admin":
			    logger.debug("Correct data")
			else:
			    logger.debug("Incorrect Data")
		        row_present=1
			break
                        
                  
            c_count+=1
    if row_present:
	    logger.debug("Row present in the table")
    else:
	    logger.error("VM has been deleted")
    return    


def vm_list(xml_child,xml_sub_child,driver):
   
    data1=[]
    path_col="//table[@id='listallvm']/tbody/tr/td"
    path_row="//table[@id='listallvm']/tbody/tr"
    path_header="//table[@id='listallvm']/thead/tr/th"
    
	
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
            if hdata.text=="Status":
                status_no=count
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
                
            
            if (c_count%col_count==col_count-1):
                
	        if select_row:
		
                    if (str(status)==xml_sub_child.get("status")):
                        field_data=driver.find_elements_by_xpath(path_row)

                        vm_id=data.get_attribute("id")
                        
                        countc+=1
                        break
                        
                    
            c_count+=1
            
           
    if countc==0:
        logger.debug("No user of testing User.Please Create a VM!!!!")
        vm_name=""
        vm_id=""
	user_name=""
    data1.insert(0,vm_id)
    data1.insert(1,vm_name)
    data1.insert(2,user_name)
    
    return data1

def total_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
    vm_user_list=[]
    
    
    path="//table[@id='vm_users']/tbody/tr/td"
    if isTablePresent(driver,xml_child,path):
	field=driver.find_elements_by_xpath(path)
	count=0
	for user in field:
	     vm_user_list.insert(count,user.text)
	     count+=1
    
    return vm_user_list



#perform action on setting button of vm's
def click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id):
    
	
    path="//table/tbody/tr/td[@id='vm_"+str(vm_id)+"']"
    
    field=driver.find_element_by_xpath(path)
    ref=field.get_attribute("href")
    #path="//*[@href='/user/settings/"+ str(vm_id) +"']"
    time.sleep(30)
   
    
    if isElementPresent(driver,xml_child,path):
       
	path=path + "/a"
        q=driver.find_element_by_xpath(path).click()
	
        time.sleep(30)
        logger.debug(xml_child.get("value") +': Result:Setting button is working properly') 
        
    else:
        logger.debug(xml_child.get("value") +': Result:Setting button is not working properly')
        
    return 
    
    
    
#open dialogbox when error occurs in falied tasks            
def click_on_dialogbox(driver):
	
    alert = driver.switch_to_alert()
    alert.accept()
    return
    
#add extra disk to a VM
def add_extra_disk(driver,xml_sub_child,xml_child,vm_name,vm_id):
    isInput_add(driver, xml_sub_child,xml_child)
    value=xml_sub_child.get("add_button")
    isButton_add(driver, xml_sub_child,value,child,xml_child)
    
    return
    
#add additional user to a VM
def add_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
    isInput_add(driver, xml_sub_child,xml_child)
    value=xml_sub_child.get("add_submit")
    isButton_add(driver, xml_sub_child,value,xml_child)
    time.sleep(3)
    status=isElementPresent(driver,xml_child,value)
    
    if status==1:
        logger.error(xml_child.get("value")  + " :User is already VM user")
        
    else:
        val=xml_sub_child.get("add_button")
        isButton_add(driver, xml_sub_child,val,xml_child)
       
   
    return status

       


#getting snapshot id of a VM

def get_snapshot_id(driver,xml_sub_child,xml_child,vm_name):
    snap_data=driver.find_elements_by_xpath("//table[@id='vm_snaps']/tbody/tr")
    select_row=0
    snap_id=0
    total_count=3
    for row in snap_data:
	row_data=row.text.split()
        if "User"==row_data[0]:
	    snap_id=row.get_attribute("id")
	    
    return snap_id


# performing  attach disk operation on vm 
def attack_disk(driver,xml_sub_child,xml_child,vm_name,operation_name):
    
    query_result=execute_query("select id,status from request_queue where vm_name=%s",(str(vm_name))).fetchone()
    baadal_db.commit()
    query_result=execute_query("select id from vm_data where vm_name=%s",(str(vm_name))).fetchone()
    baadal_db.commit()
    if query_result!=():
        query_result=execute_query("select id from vm_data where vm_name=%s",(str(vm_name))).fetchone()
        
        vm_id=query_result[0]
        
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
        click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return
          

        
#getting user id of a user access to a VM                        
def get_user_id(driver,xml_sub_child,xml_child,vm_name,owner_name):
    path="//table[@id='vm_users']/tbody/tr/td"    
    if isElementPresent(driver,xml_child,path):   
        user_data=driver.find_elements_by_xpath(path)
    	select_row=0
    	user_id=0
    	for col in user_data:
	    if owner_name==col.text:
	        user_id=col.get_attribute("id")
	    
	        break
	    
    return user_id




#performing add_user operation on vm
def op_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")  
    path="//table[@id='vm_ops']/tbody/tr/td/a[@title='Add User to VM']"
    
    limit=0
    if isElementPresent(driver,xml_child,path):   
        
        time.sleep(20)
        driver.find_element_by_xpath(path).click()
        time.sleep(10)
        if add_user(driver,xml_sub_child,xml_child,vm_name,vm_id):
            if xml_sub_child.get("op_typ")!="cancel_user":
		
                field_text=message_flash(driver,xml_sub_child,xml_child)
                result=message_in_db(xml_sub_child)
                print_result(field_text,result,xml_child)
            	if xml_sub_child.get("name") in vm_mode_type:
              		check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return limit



#checking whether username is in vm_users table or not
def  check_user_table(driver,xml_sub_child,xml_child,vm_name,vm_id):
    username=xml_sub_child.get("user_name")
    path="//table[@id='vm_users']/tbody/tr"
    if isElementPresent(driver,xml_child,path):
        field=driver.find_elements_by_xpath(path)
	check_len=0
	total_col=driver.find_elements_by_xpath("//table[@id='vm_users']/tbody/tr/td")
	
	for data in field:
	    if username in data.text:
		logger.debug("User name is added to VM")
		check_len=1
    	if check_len==0:
	    logger.error(xml_child.get("value")  + "Error ")    
    return


    
#list of vm mode 
vm_mode_type=['vm_running_Setting_intgrtn','vm_paused_Setting_integrtn','vm_shutdown_Setting_integrtn']





#performing delete operation on vm

def op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):   
    limit=0
    
    op_name=xml_sub_child.get("op")  
    path=xml_sub_child.get("title")  
    if isTablePresent(driver,xml_child,path):         
    	driver.find_element_by_xpath(path).click()
    	click_on_dialogbox(driver)
    	click_on_dialogbox(driver)
    	field_text=message_flash(driver,xml_sub_child,xml_child)
    	result=message_in_db(xml_sub_child)
    	print_result(field_text,result,xml_child)
 
    else:
	logger.debug("This functionality is disabled")          

    return limit



#performing snapshot operation on vm
def op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    limit=0
    snap=1
    op_name=xml_sub_child.get("op") 
    if op_name=="snapshot": 
        path="//a[@title='Take VM snapshot']"
    else:
        path=xml_sub_child.get("xpath_snap")
        
    if isElementPresent(driver,xml_child,path): 
	result=snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name)
	
        if op_name=="snapshot":
            driver.find_element_by_xpath(path).click()
        else:
            snapshot_id=get_snapshot_id(driver,xml_sub_child,xml_child,vm_name) 
	    if snapshot_id:
                 driver.find_element_by_xpath("//*[@href='/user/"+ str(op_name) +"/"+ str(vm_id) +"/"+ str(snapshot_id) + "']").click()
            else:
		logger.debug("No snapshot present")
		snap=0
	
        if  (result=="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot.") | (result=="Snapshot request already in queue.") | (result=="") | (snap==0):
            logger.debug(result )
	    limit=0
        else:
            limit=1
    else:
    	logger.debug(xml_child.get("value") + ":This functioality is Disabled")  

      
    return limit


def check_owner_of_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name):
      driver.find_element_by_partial_link_text("All VMs").click()
      check_owner_name_in_allvm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name)

#performing  delete add_user operation on vm
def op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name):
    limit=0
    op_name=xml_sub_child.get("op") 
    
    path=xml_sub_child.get("xpath_user")
    if isElementPresent(driver,xml_child,path):  
        user_id=get_user_id(driver,xml_sub_child,xml_child,vm_name,owner_name) 
	path="//table[@id='vm_users']/tbody/tr/td[@id='"+ str(user_id)+"']/a/b"
	
	driver.find_element_by_xpath(path).click()
        #driver.find_element_by_xpath("//*[@href='/baadal/admin/"+ tr(op_name) +"/"+ str(vm_id) +"/"+ str(user_id) + "']").click()
        result="User access is eradicated."
        field_text=message_flash(driver,xml_sub_child,xml_child)
        print_result(field_text,result,xml_child)   
        check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child)
	check_owner_of_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name)
    else:
    	logger.debug(xml_child.get("value") + ":This VM has been deleted and its in pending task table,So this functionality has been disabled !!!!!!") 
    return limit
            


#checking whether user access removed for a vm or not                        
def check_delete_user(driver,user_id,op_name,xml_child,xml_sub_child):
    operation_name=op_list[op_name]
    path=xml_sub_child.get("xpath_user")
    user_absent=1
    if isTablePresent(driver,xml_child,path):
        user_table=driver.find_elements_by_xpath("//table[@id='vm_users']/tbody/tr/td")
	for user in user_table:
            if user.get_attribute("id")==user_id:
                logger.error(xml_child.get("value")  + "User has not been deleted")
	        user_absent=0
        if user_absent:
            logger.debug(xml_child.get("value")  + "User access is eradicated")
    else:
        logger.debug("User access is eradicated")
    return


#performing attach disk operation on vm
def op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")   
    path="//*[@href='/baadal/user/"+ str(op_name) +"/"+ str(vm_id) +"']" 
    if isElementPresent(driver,xml_child,path):
    	driver.find_element_by_xpath(path).click()
    	add_extra_disk(driver,xml_sub_child,xml_child,vm_name,vm_id)
    	field_text=message_flash(driver,xml_sub_child,xml_child)
    	result=xml_sub_child.get("print")
    	print_result(field_text,result,xml_child)
    	if xml_sub_child.get("name")in vm_mode_type:
        	operation_name=op_list[op_name]
        	check_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,operation_name)
    else:
	logger.debug("No element exist")


def check_status_of_vm(driver,xml_sub_child,xml_child):
    c_count=0
    path_col="//table[@id='configuration']/tbody/tr/td"
    path_header="//table[@id='configuration']/tbody/tr/th"
    if isTablePresent(driver,xml_child,path_col):
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



#performing migrate operation on vm
def op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    limit=0
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    operation_name
    path="//a[@title='Migrate this virtual machine']"
    if isElementPresent(driver,xml_child,path):
        vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
	total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list)
        driver.find_element_by_link_text("All VMs").click()
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id) 
	status=check_status_of_vm(driver,xml_sub_child,xml_child)
	driver.find_element_by_xpath("//a[@title='Migrate this virtual machine']").click()
	driver.find_element_by_xpath("//input[@value='Migrate']").click()
	
        
            
	if status=="Running":
	    result="Your VM is already running. Kindly turn it off and then retry!!!"
	    field_text=message_flash(driver,xml_sub_child,xml_child)
            print_result(field_text,result,xml_child)
	elif total:
	    result="Your request already in the queue"
	    field_text=message_flash(driver,xml_sub_child,xml_child)
            print_result(field_text,result,xml_child)
	else:
           result="Your task has been queued. please check your task list for status. "
           field_text=message_flash(driver,xml_sub_child,xml_child)
           print_result(field_text,result,xml_child)
           limit=1
    else:
        logger.debug("Migrate operation could not performed because no host is available.Please do host up then again try this operation")
    return limit
        
#performing   operation on vm        
def other_operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    operation_name=op_list[op_name]
    operation_name
    
    xpath=task_path(xml_sub_child)
    
    path="//*[@title='" + str(xpath) + "']"
    
    if isElementPresent(driver,xml_child,path):
	vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
	total=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list)
	driver.find_element_by_link_text("All VMs").click()
	click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id) 
        driver.find_element_by_xpath(path).click()
        field_text=message_flash(driver,xml_sub_child,xml_child)
	
	if total==[]:
            result=message_in_db(xml_sub_child)
	    limit=1
	else:
	    result="Your request already in the queue"
	    limit=0
        print_result(field_text,result,xml_child)
	
        
    else:
        logger.debug(xml_child.get("value") + ":This VM has been deleted and its in pending task table,So this functionality has been disabled !!!!!!") 
	limit=0
	
    return limit

#performing  edit vm configuration
def op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id):
    op_name=xml_sub_child.get("op")
    driver.find_element_by_xpath("//*[@href='/baadal/user/"+ str(op_name) +"/"+ str(vm_id) +"']").click()
    driver.find_element_by_xpath("//input[@type='submit']").click()
    result="Your request has been queued!!!"
    field_text=message_flash(driver,xml_sub_child,xml_child)
    result=message_in_db(xml_sub_child)
    print_result(field_text,result,xml_child)
    return


def task_path(xml_sub_child):
    op_name=xml_sub_child.get("op")
    if op_name=="pause_machine":
        path='Pause this virtual machine'    
    if op_name=="shutdown_machine":
        path='Gracefully shut down this virtual machine'
    if op_name=="start_machine":
        path='Turn on this virtual machine'    
    if op_name=="destroy_machine":
    	path='Forcefully power off this virtual machine'
        
    if op_name=="resume_machine":
        path='Unpause this virtual machine'
    return path
        
        
	
	
#selecting operation to be perform    
def click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name): 
    
    
    op_name=xml_sub_child.get("op")    
    
   
    if op_name=="user_details":
        limit=op_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="Delete":
        limit=op_delete_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name in {"revert_to_snapshot","delete_snapshot","snapshot"}:         
        limit=op_snap_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="delete_user_vm": 
        limit=op_del_user_vm(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name)
    elif op_name in {"attach_extra_disk","clone_vm"}:
        op_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="edit_vm_config":
        op_edit_vm_conf(driver,xml_sub_child,xml_child,vm_name,vm_id)
    elif op_name=="migrate_vm":
        limit=op_migrate_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)  
   
    else:
        limit=other_operation_on_vm(driver,xml_sub_child,xml_child,vm_name,vm_id)
    return limit




# list of operation to be performed     
op_list={'revert_to_snapshot':0,'delete_snapshot':1,'snapshot':'Snapshot VM','pause_machine':'Suspend VM','Delete':'Delete VM','shutdown_machine':'Stop VM','destroy_machine':'Destroy VM','start_machine':'Start VM','user_details':'Add User','attach_extra_disk':"Attach Disk",'clone_vm':'Clone ','delete_user_vm':'Delete User','adjrunlevel':'Adjust Run Level','edit_vm_config':'Edit VM Config','resume_machine':'Resume VM','migrate_vm':'Migrate VM'}

#message display on screen
def message_in_db(xml_sub_child):
    op_name=xml_sub_child.get("op")
    if op_name=="user_details":
        result="User is added to vm" 
    else:
    	result=op_list[op_name] +" request added to queue."
    	
	return result
    
    

#retreiving message from given xpath        
def message_flash(driver,xml_sub_child,xml_child):
    path=driver.find_element_by_xpath('//flash[@id="flash_message"]')
    field_text=path.text
    return field_text

def total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name):
    total_user_snap=0
    total_snap=0
    snap_data=driver.find_elements_by_xpath("//table[@id='vm_snaps']/tbody/tr")
    for row in snap_data:
        s_row=row.text.split()
        user=s_row[0]
        if "User"==user:
            total_user_snap+=1
	total_snap+=1
    
    if op_name=="Migrate VM":
	total=total_snap
    else:
	total=total_user_snap
    return total


#checking snapshot
def snap_result(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name):
    op_name=xml_sub_child.get("op")   
    operation_name=op_list[op_name]
    vm_user_list=total_user(driver,xml_sub_child,xml_child,vm_name,vm_id)
    l_snap=check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list)  
    length_snap=len(l_snap)
    
    driver.find_element_by_link_text("All VMs").click()
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)    
    total_user_snap=total_snap(driver,xml_sub_child,xml_child,vm_name,vm_id,op_name)
    
    result=snap_db_result(xml_sub_child,op_name,length_snap, total_user_snap)
    field_text=message_flash(driver,xml_sub_child,xml_child)
    print_result(field_text,result,xml_child)
    return result



def check_pendingtasks_table(driver,xml_sub_child,xml_child,vm_name,operation_name,vm_user_list):
    task_table_name="Pending Task"
    driver.find_element_by_link_text("Tasks").click()
    path_row="//table[@id='pendingtasks']/tbody/tr"
    path_col="//table[@id='pendingtasks']/tbody/tr/td"
    path_header="//table[@id='pendingtasks']/tbody/tr/th"

    data1=[]


    if isTablePresent(driver,xml_child,path_col):
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
                    #user_name_s=data.text
		 #usernm=usrnm_list[xml_child[0].text]
            	 #if usernm==data.text:
		    
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
	 
    
    
    return data1


#printing result correspondence to snapshot
def snap_db_result(xml_sub_child,op_name,length_snap, total_user_snap):
    
    if op_name=="delete_snapshot":
        result="Your delete snapshot request has been queued"
    else:
        if str(total_user_snap)==xml_sub_child.get("max"):
            result="Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
        elif length_snap:
            result="Snapshot request already in queue."
	if str(total_user_snap)==str(0):
	     result="No VM snapshot exists to perform this operation"
        else :
            if (op_name=="revert_to_snapshot") & (total_user_snap>0):
		result="Your revert to snapshot request has been queued"
            else:
                result="Your request to snapshot VM has been queued"
    return result



def graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id):
    ssh.connect(xml_child.get("ip_add"), username=xml_child.get("usrnam"), password=xml_child.get("password"))   
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    initial_data=stdout.readlines()
    
    click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
    click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id)
    time.sleep(900)
    stdin, stdout, stderr =ssh.exec_command(xml_sub_child.get("cmd_finl_data")+vm_name +xml_sub_child.get("cmd"))
    final_data=stdout.readlines()
    fin_data=str(final_data[2])
    finl_data=fin_data.split()
    
    print_graph(finl_data,xml_child)

#username_list=["BadalUF UF","Badal UA","Badal UO","Badal UFA","Badal UFO","Badal UOA","BadalUFOA UFOA","BadalU U"]
usrnm_list={"badalUF":"BadalUF UF","badalUA":"Badal UA","badalUO":"Badal UO","badalUFA":"Badal UFA","badalUFO":"Badal UFO","badalUOA":"Badal UOA","badalUFOA":"BadalUFOA UFOA","badalU":"BadalU U"}

username_list=["BadalUF UF","Badal UA","Badal UO","Badal UFO","Badal UOA","BadalUFOA UFOA","BadalU U"]
#usrnm_list={"badalUA":"Badal UA","badalUO":"Badal UO","badalUFO":"Badal UFO","badalUOA":"Badal UOA","badalUFOA":"BadalUFOA UFOA","badalU":"BadalU U"}

def total_vm(driver,xml_sub_child,xml_child):
    counth=0
    user_vm=0
    field=driver.find_elements_by_xpath("//table[@id='listallvm']/thead/tr/th")
    for data in field:
	
	if data.text=="Owner":
	    requester_no=counth
	counth+=1
   
    path="//table[@id='listallvm']/tbody/tr/td"+ "["+ str(requester_no+1) +"]"
   
    field=driver.find_elements_by_xpath(path)
    for user in field:
	for username in username_list:
	    if username==user.text:
		             
   	        user_vm+=1
    return user_vm


def maintain_idompotency(driver,xml_sub_child,xml_child):
    execute_query("FLUSH QUERY CACHE")
    deletevm_from_pending_request_table(driver,xml_sub_child,xml_child)
    delete_vm_from_allvms(driver,xml_sub_child,xml_child)
    return


    

def delete_vm_from_allvms(driver,xml_sub_child,xml_child):
    vm_exist=0
    driver.find_element_by_link_text("All VMs").click()
    path="//table[@id='listallvm']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    user_present=0
    if isElementPresent(driver,xml_child,path):
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
         	        
                        path="//*[@href='/user/settings/"+ str(vm_id[3:]) +"']"
    	
                        time.sleep(30)
                        if isElementPresent(driver,xml_child,path):
                            q=driver.find_element_by_xpath(path).click()
                            path="//a[@title='Delete this virtual machine']"
			  
                            if isElementPresent(driver,xml_child,path): 
                                try:
                                    driver.find_element_by_xpath(path).click() 
                                    e_present=1
                                except:
                                    e_present=0
                                if e_present:
				 
                                    click_on_dialogbox(driver)
                                    click_on_dialogbox(driver)
                                    logger.debug(str(user_name) + " VM (" + str(vm_id[3:]) + ") has been deleted from All VMs table") 
                                    select_row=0
                                    col_count=0
                                    vm_exist=1
                                    driver.find_element_by_link_text("All VMs").click()
                                    driver.refresh()
                                    time.sleep(10)
                                    break
		
                                else:
                                    logger.debug("This VM already has been deleted!!!")
			
                    
		   
                col_count+=1
	if vm_exist==0:
	    logger.debug("No VM exists to perform Delete Pending request!!!")
    return

 



def deletevm_from_pending_request_table(driver,xml_sub_child,xml_child):    
    vm_exist=0
    driver.find_element_by_partial_link_text("All Pending Requests").click()
    path="//table[@id='sortTable1']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    user_present=0
    if isElementPresent(driver,xml_child,path):
        field=driver.find_elements_by_xpath("//table[@id='sortTable1']/thead/tr/th")  
        for data in field:
            if data.text=="Requested By":
		         requester_col_no=counth
		
            counth+=1
        
        total_col=counth
        field=driver.find_elements_by_xpath("//table[@id='sortTable1']/tbody/tr/td[1]")  
        for data in field:
	         for username in username_list:
		         if username==data.text:
		             
   		             user_present+=1
		
       
        for x in range(0,user_present):
	    
            driver.refresh()
	    
            field_data=driver.find_elements_by_xpath("//table[@id='sortTable1']/tbody/tr/td")
	    
            for user in field_data:
                
                if (col_count%total_col==requester_col_no):
                    for username in username_list:
                        if username==user.text:
                            user_name=user.text
                            select_row=1   
			 
	    
                if col_count%total_col==(total_col-1) :
                    if select_row:
                        vm_id=user.get_attribute("id")
         	      
                        path="//a[@href='/baadal/admin/reject_request/"+ str(vm_id[7:]) + "']"
                        if isElementPresent(driver,xml_child,path):
                            driver.find_element_by_xpath(path).click()
                            logger.debug(str(user_name) + " VM (" + str(vm_id[7:]) + ") has been deleted from Pending request")
			    select_row=0
			    col_count=0
			    vm_exist=1
			    break
                col_count+=1
	if vm_exist==0:
	    logger.debug("No VM exists to perform Delete Pending request!!!")
    return

     
def vm_mode(xml_child,xml_sub_child,driver):
    data=vm_list(xml_child,xml_sub_child,driver)
   
    if data!=['', '']:
        vm_id=data[0][3:]
        vm_name=data[1][0:]
        owner_name=data[2][0:]
        vm_mode_op(xml_child,xml_sub_child,driver,vm_name,vm_id,owner_name)
    else:       
        logger.debug(xml_sub_child.get("print_mode")) 
	test_script(48)
    return
    
def perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name):
    check_pendingtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name)
    task_value=check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name)
    check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name)
    return task_value


def vm_mode_op(xml_child,xml_sub_child,driver,vm_name,vm_id,owner_name):
    if xml_sub_child.get("task")=="graph":
        graph_test_mode(xml_child,xml_sub_child,driver,vm_name,vm_id)
        click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
    else:
        op_name=xml_sub_child.get("op")    
        operation_name=op_list[op_name]
        if vm_id!="":
            task_value=check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name)
            if task_value!=["No"]:
                driver.find_element_by_partial_link_text("All VMs").click()
                click_on_setting(driver,xml_sub_child,xml_child,vm_name,vm_id)
                limit=click_on_operation(driver,xml_sub_child,xml_child,vm_name,vm_id,owner_name)
                if limit:
                    time_to_check_in_tasktable()
                    task_n_value=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name)
                    compare_task_table(driver,xml_sub_child,xml_child,vm_name,operation_name,task_value,task_n_value)
        else:       
            logger.debug(xml_sub_child.get("print_mode")) 
	
	    
    return



def time_to_check_in_tasktable():
    current_time=datetime.datetime.now()
    break_pt_time=current_time + datetime.timedelta(seconds=220) 
    print datetime.datetime.now()
    print break_pt_time 
    time.sleep(60)
    return 

 

def compare_task_table(driver,xml_sub_child,xml_child,vm_name,operation_name,task_value,task_n_value):
	
	value_present=1
	for value in task_n_value:
	    
	    
	    for value1 in task_value:
		
		if (value[0]==value1[0]) & (value[1]==value1[1]):
		    value_present=0
		    break
	    if value_present:
			print value
            print value[2]
	
		
	logger.debug("Your Request is in "+ str(value[2]))
	if value[2]=="Failed Tasks":
	    start_time=value[0]
	   
	    check_in_failed_task_table(driver,xml_sub_child,xml_child,vm_name,operation_name,start_time)     
   



def check_in_failed_task_table(driver,xml_sub_child,xml_child,vm_name,operation_name,start_time):
    path_col="//table[@id='failedtasks']/tbody/tr/td"
    path_header="//table[@id='failedtasks']/tbody/tr/th"
    field_header=field=driver.find_elements_by_xpath(path_header)
    for h_data in path_header:
        if h_data.text=="Task":
            task_f_no=counth
        if h_data.text=="VM":
            vm_f_no=counth
        if h_data.text=="Requested By":
            requester_f_no=counth
        if h_data.text=="Request Time":
            request_f_no=counth
        if h_data.text=="Error":
            error_f_no=counth
        counth+=1
    col_count=counth
    field=driver.find_elements_by_xpath(path_col)
	
    row_count=0       
    for data in field:
        if c_count%col_count==task_f_no:
            op_name_sc=data.text
        if c_count%col_count==vm_f_no:
            vm_name_s=data.text
        if c_count%col_count==requester_f_no:
            if xml_child[0].text==data.text:
               
                user_name_s=data.text 	    
        if (c_count%col_count==request_f_no):
            start_time_s=data.text
        if (c_count%col_count==(col_count-1)) & (vm_name==vm_name_sc) & (operation_name==op_name_sc) & (start_time_s==start_time):
            
            error_message=open_error_page(driver,xml_parent,xml_child,"Error",row_count)
            
            break
        if (c_count%col_count==(col_count-1)):
            row_count+=1   
            
        
        c_count+=1

    return
# Checking data on front end and in back end                                            


                                               
def result_setting_page(field,query_result,driver,xml_child,xml_sub_child):
    i=0
    for t in field:
        print "screen=" + str(t.text)
        print "db=" + str(query_result[i][0])
        if str(query_result[i][0]) in t.text:
            logger.debug("correct inputs")
        else :
            logger.debug("Incorrect inputs")
        i+=1 
    return

#Checking data in Snapshot table  
                                                
def check_snapshot(vm_name,driver,xml_child,xml_sub_child):
    logger.debug("Checking for entries in current snapshot table")
    path=xml_sub_child.get("xpath_snap")
    if isElementPresent(driver,xml_child,path):
    	vm_nam=str(vm_name)
        query_result=execute_query(xml_sub_child.get("query4"),(vm_nam)).fetchall()
        baadal_db.commit()
        total_user_snap=len(query_result)
        field=driver.find_elements_by_xpath(path)
        result_setting_page(field,query_result,driver,xml_child,xml_sub_child)
        return total_user_snap
    else :
        total_user_snap=""
        return total_user_snap
        
 
#Checking data in User table         
       
def check_user(driver,xml_child,xml_sub_child,vm_name):
    logger.debug("Checking for entries in user table")
    path=xml_sub_child.get("xpath_user")
    
    if isElementPresent(driver,xml_child,path):
        query_result=execute_query( xml_sub_child.get("query5"),(str(vm_name))).fetchall()
        baadal_db.commit()
       
        field=driver.find_elements_by_xpath(path)
        logger.debug("Checking for entries in Additional user table")
        result_setting_page(field,query_result,driver,xml_child,xml_sub_child)
    else:
    	logger.debug(xml_child.get("value") + ":Table does not exists") 

      
'''check_security_domain():
   driver.find_element_by_link_text("Configure System").click()
        driver.find_element_by_link_text("Configure Security Domain").click()
        field=driver.find_elements_by_xpath("//table/thead/tr/th")
        counth=0
	
        for data in field:
            if data.text=="Name":
                s_domain_no=counth
            if data.text=="Vlan":
                vlan_no=counth
            counth+=1
        t_col=counth
	
        field=driver.find_elements_by_xpath("//table/tbody/tr/td")
        
        select_row=0
        col_count=0
        for data in field:            
            
            if data.text=="Research":
                select_row=1
            if col_count%t_col==vlan_no:
               
                vlan_name=data.text
            if col_count%t_col==t_col-1:
                if select_row:
                    print vlan_name
                    break   
            col_count+=1  

       
        driver.find_element_by_link_text("Configure Private IP Pool").click()
        field=driver.find_elements_by_xpath("//table/thead/tr/th")
        counth=0
        for data in field:
            if data.text=="Assigned to":
                IP_assgn=counth
            if data.text=="Vlan":
                vlan_no=counth
            counth+=1
        t_col=counth
        total_row=driver.find_elements_by_xpath("//div[@class='web2py_paginator  ']/ul/li")
        count=0
	for data in total_row:
	   
	    count+=1
	
	ip_available=0
        for i in range(0,count):
            field=driver.find_elements_by_xpath("//table/tbody/tr/td")
            col_count=0
            select_row=0
	    
            for data in field:
            	
                if col_count%t_col==vlan_no:
                    if data.text==xml_child[5].text:
                        d_name=data.text
                        select_row=1
                if col_count%t_col==IP_assgn:
                    ip_assign=data.text
                if col_count%t_col==t_col-1:
                    if select_row:
                        if ip_assign=="Unassigned":
                            logger.debug("Availabe")
                            ip_available=1
                            break
                col_count+=1  
            if ip_available:
                print ip_available
                break
	    else:
		print i
		print count
		if i<count-1:
		    page_no=i+2
		    
		    driver.find_element_by_link_text(str(page_no)).click()
           
        if ip_available:
            
            data1=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name)
        else:
           
            logger.debug(xml_child.get("value")  + ": No Private IP available in " + str(d_name) + ".")
            data1=["NO"]
   '''

#Checking data in task table

def check_vm_task(driver,xml_sub_child,xml_child,vm_name,operation_name):

    data1=perform_task_operation(driver,xml_sub_child,xml_child,vm_name,operation_name)
 
    return data1



def check_pendingtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name):
    task_table_name="Pending Task"
    driver.refresh()
    time.sleep(15)
    driver.find_element_by_link_text("Tasks").click()
    path_row="//table[@id='pendingtasks']/tbody/tr"
    path_col="//table[@id='pendingtasks']/tbody/tr/td"
    path_header="//table[@id='pendingtasks']/tbody/tr/th"
    pcount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header)
    return pcount

task_data=[]

def check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header):

    if isTablePresent(driver,xml_child,path_col):
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
		
		
                #if data.text in vm_user_list:
                 #   user_name_s=data.text
                
                usernm=usrnm_list[xml_child[0].text]
		
                if usernm==data.text:
		    
                    user_name_s=data.text
                    select_row=1
	    
            	    
            if (c_count%col_count==request_f_no):
                start_time_s=data.text
	    
            if (select_row) & (c_count%col_count==(col_count-1)):
		
                if (str(vm_name)==str(vm_name_s)) & (str(operation_name)==str(op_name_sc)):
                    task_data.append([])
		    task_data[-1].append(start_time_s)
                    task_data[-1].append(user_name_s)
		    task_data[-1].append(task_table_name)
		    
                    countp+=1
            c_count+=1
	    
    else:
        countp=0
    if xml_sub_child.get("task_type")=="checking":
	
        if countp==0:
            logger.debug("Operation does not exist" +str(task_table_name) +" table!!!!!")
        else:
            logger.debug( "Operation exists in " +str(task_table_name) +"  table!!!")
            if task_table_name=="Failed Task":

                start_time=task_data[0]
	   
                check_in_failed_task_table(driver,xml_sub_child,xml_child,vm_name,operation_name,start_time) 
	    
		    
    else:
        if countp==0:
            logger.debug("Operation does not exist" +str(task_table_name) +" table!!!!!")
        else:
            logger.debug(str(countp) + "number of same operation already exists in " +str(task_table_name) +"  table!!!")
  
    return task_data

def check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name):
   
    path="//table[@id='sortTable1']/tbody/tr/td"
    counth=0
    user_vm=0
    select_row=0 
    col_count=0
    s_row=0
    ref=0
    if isElementPresent(driver,xml_child,path):
        field=driver.find_elements_by_xpath("//table[@id='sortTable1']/thead/tr/th")  
        for data in field:
	    if data.text=="VM Name":
		vm_no=counth
	    if data.text=="Requested By":
		user_no=counth
            counth+=1
        
        total_col=counth
        
        field=driver.find_elements_by_xpath(path)
        for data in field:
            
            if col_count%total_col==vm_no:
		
                if str(data.text)==str(vm_name):
                   
                    s_row=1
	      
            if col_count%total_col==user_no:
                
                usernm=usrnm_list[xml_child[0].text]
                 
                if str(data.text)==usernm:
                    
                    select_row=1   
		    
			
		   
            if col_count%total_col==(total_col-1) :
		
 	        if select_row :
		    if s_row:
			
                        value=data.get_attribute("id")
				
			
		        vm_id=value[7:]
			
		
		        field=driver.find_element_by_xpath("//table/tbody/tr/td/a[@id='accept_"+str(vm_id)+"']").click()
		        ref=1
			time.sleep(10)
			
		        break
            col_count+=1
   
    return ref


def check_completedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name):
    task_table_name="Completed Task"
   
    driver.find_element_by_link_text("Completed Tasks").click()
    path_row="//table[@id='completedtasks']/tbody/tr"
    path_col="//table[@id='completedtasks']/tbody/tr/td"
    path_header="//table[@id='completedtasks']/tbody/tr/th"
    ccount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header)
    return ccount





def check_failedtask_table(driver,xml_sub_child,xml_child,vm_name,operation_name):
    task_table_name="Failed Task"
    driver.find_element_by_link_text("Failed Tasks").click()
    path_row="//table[@id='failedtasks']/tbody/tr"
    path_col="//table[@id='failedtasks']/tbody/tr/td"
    path_header="//table[@id='failedtasks']/tbody/tr/th"
    fcount=check_tasktable(driver,xml_sub_child,xml_child,vm_name,operation_name,task_table_name,path_row,path_col,path_header)
    return fcount
    
       
 
     

#checking data in attach_disk table

def check_attach_disk(driver,xml_sub_child,xml_child,vm_name,vm_id,operation_name):  
    driver.find_element_by_link_text("Pending Requests").click()
    driver.find_element_by_link_text("Attach Disk").click()
    field=driver.find_elements_by_xpath("//table[@id='sortTable2']/tbody/tr")
    qery_result=execute_query('select id,vm_name from request_queue where status=4 and vm_name=%s order by start_time desc',(str(vm_name))).fetchone()
    baadal_db.commit()
    if qery_result!=():
        query_result=execute_query('select id,vm_name from request_queue where status=4 and vm_name=%s order by start_time desc',(str(vm_name))).fetchone() 
        baadal_db.commit()
        vm_ids= query_result[0]
        if xml_sub_child.get("action")=="approve_request":    
            driver.find_element_by_xpath("//*[@href='/admin/approve_request/"+ str(vm_ids) +"']").click()        
    else:
        
        driver.find_element_by_xpath("//*a[@href='/admin/reject_request/"+ str(vm_ids) +"']").click()
       
    return
    
# providing connection to all host exists
def conn_host(host_name,vm_status,vm_name,message,total_vm):
    
    query_result=execute_query("select host_name,host_ip from host").fetchall()
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
            status_vm=check_vm_status_on_host(status)
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam)
        for vm in conn.listDefinedDomains():
            status_vm="Off"
            print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam)	   



#checking data in sanity table
def print_sanity_result(status_vm,host_name,vm_status,vm_name,message,total_vm,host_ip,host_nam):
    for i in range(0,total_vm):
        vm_nm=vm_name[i]
        if ((vm_nm==vm_name[i]) & (host_nam==host_name[i])):
            messg=check_messg_in_db(vm_nm,host_ip,host_nam)
            if vm_nm==vm_name[i]:
                logger.debug('host='+vm_nm)
                logger.debug('screen='+vm_name[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+vm_nm)
                logger.debug('screen='+vm_name[i])
                logger.debug('Result:Incorrect input')
                
            if status_vm==vm_status[i]:
                logger.debug('host='+status_vm)
                logger.debug('screen='+vm_status[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+status_vm)
                logger.debug('screen='+vm_status[i])
                logger.debug('Result:Incorrect input')
                	
            if messg==message[i]:
                logger.debug('host='+messg)
                logger.debug('screen='+message[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+messg)
                logger.debug('screen='+message[i])
                logger.debug('Result:Incorrect input')
                
            if host_nam==host_name[i]:
                logger.debug('host='+host_nam)
                logger.debug('screen='+host_name[i])
                logger.debug('Result:correct input')
            else:
                logger.debug('host='+host_nam)
                logger.debug('screen='+host_name[i])
                logger.debug('Result:Incorrect input')



#converting vm status bits on host into status text		
def check_vm_status_on_host(status):
	if status==1:
		status_vm="Running"
	if status==3:
		status_vm="Paused"
	return status_vm

	
#checking whether data in sanity table is correct or incorrect    
def check_messg_in_db(vm_nm,host_ip,host_nam):    
    fetch_result=execute_query(" select vm_name,vm_data.status from vm_data,host where vm_data.host_id=host.id and host_ip=%s",(str(host_ip))).fetchall()
    
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
		
def isInput(driver, xml_sub_child):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if xml_sub_child.text!=None:
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
    else:
        if not (xml_sub_child.get("id") in ["user_password","user_username"]):
            field.send_keys(str(current_time))	
    return current_time


def	isInput_add(driver, xml_sub_child,xml_child):
    path=xml_sub_child.get("user_id")
    
    field = driver.find_element_by_id(path)
    
    field.send_keys(xml_sub_child.get("user_id_data"))
    return



def isReadOnly(driver, xml_parent,xml_child,xml_sub_child):
    current_time=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    field = driver.find_element_by_id(xml_sub_child.get("id"))
    if field.get_attribute("value")!='':
        field.send_keys(xml_sub_child.text) # sending the user name/password/vm name/purpose etc
        if field.get_attribute("value")==xml_sub_child.text:
            logger.debug(xml_child.get("value")  +': Result:error') #logging the report
        else:
            logger.debug(xml_child.get("value")  +': Result:no error') #logging the report
    else:
        logger.debug(xml_child.get("value")  +': Result:empty') #logging the report
    return 



def isWait( driver, xml_parent, xml_child, xml_sub_child):
    if xml_sub_child.get("id")=="wait":
        time.sleep(300)
    else:
        time.sleep(3)
    return



def isSubmit( driver, xml_parent, xml_child, xml_sub_child):
    driver.find_element_by_xpath(xml_sub_child.text).click()
    time.sleep(10)    
    if xml_sub_child.get("id")=="check_data":
        xpath=xml_sub_child.get("xpath")
        status=isElementPresent(driver,xml_child,xpath)

        if status==1:
            logger.debug(str(xml_child.get("value")) +": Correct data")
        else:
            logger.debug(str(xml_child.get("value")) +": Incorrect data")
    return
	

    
def isButton_add(driver, xml_sub_child,value,xml_child):
    if isElementPresent(driver,xml_child,value):
    	driver.find_element_by_xpath(value).click()
    
    return



def isClear(driver,xml_sub_child) :
    driver.find_element_by_id(xml_sub_child.get("id")).clear()	
    return
	
def isScroll(driver, xml_sub_child):
	field=driver.find_element_by_tag_name("html")
	field.send_keys(xml_sub_child.text)
	driver.execute_script("window.scrollBy(0,200)", "")
	return



def isHref(driver, xml_sub_child,xml_child):
    driver.find_element_by_partial_link_text(xml_sub_child.text).click()
    if xml_sub_child.get("id")=="collaborator":
        xpath=xml_sub_child.get("xpath")
        if isElementPresent(driver,xml_child,table_path):
         
            field=driver.find_element_by_xpath(xpath)    
            result=xml_sub_child.get("result")
            field_text=field.get_attribute("innerHTML")
            print_result(field_text,result,xml_child)
        else:
            logger.error(xml_child.get("value")  + ": Error in the form")
	return



def isSelect(driver, xml_sub_child,temp):
	list=[]
	if xml_sub_child.get("select_name")=="configuration":
	    
	    path=xml_sub_child.text +str(temp)+ "']/option"
	   
	else:
	    
            path=xml_sub_child.text   
	field=driver.find_elements_by_xpath(path)
	count=0
	for data in field:
	    value=data.get_attribute("value")
	    list.insert(count,value)
	    count+=1
	
	option_value=random.choice(list)
	driver.find_element_by_xpath(path + "[@value='" + option_value + "']").click()
        
	if xml_sub_child.get("select_name")=="configuration":
	    option_value=1
	return option_value


def isImage(driver,xml_child,xml_sub_child,a):	
    if isElementPresent(driver,xml_child,a):
        vm_mode(xml_child,xml_sub_child,driver)
    else:
    	logger.debug(xml_child.get("value") + ":No VM exists.So,to perform this operation please create a VM.")
    return 


def isTable(driver,xml_parent,xml_child,xml_sub_child):
    status_list={0:"Error",1:"failed_tasks",2:"TRY AGAIN | IGNORE",3:"my_pending_vm",4:"admin_pending_attach_disk",5:"pending_user_install_vm",6:"pending_user_clone_vm",7:"pending_user_attach_disk",8:"pending_user_edit_conf",9:"host_and_vm",10:"Configure_host",11:"admin_pending_clone_vm",12:"admin_pending_install_vm" ,13:'Configure_security',14:'pending_fac_install_vm',15:'pending_org_install_vm',16:'pending_org_clone_vm',17:'pending_org_attach_disk',18:'pending_org_edit_conf',19:"admin_pending_edit_conf" ,20:'list_my_vm',21:'fac_pending_attach_disk',22:'list_all_org_vm',23:'setting',24:'list_all_vm'}
    
    table_path=xml_sub_child.text       
    if isTablePresent(driver,xml_child,table_path):
        
        cur=execute_query( xml_child.get("query3"))
        query_result=cur.fetchall()
        
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
        print total
	print count
        if ((str(total)==str(count))) :
            for col in field:
                field_text=col.text
                if (field_text!=""):
            
                    if field_text==status_list[0]:
                        text=open_error_page(driver,xml_parent,xml_child,field_text,row_count)
                        result=query_result[row_count][col_count]#data form query
                        print_result(text,result,xml_child)
                    
                    elif (query_result[row_count][col_count]==4) & (xml_parent.get("name")==status_list[1]):
                        result=status_list[2]
                        print_result(field_text,result,xml_child)
                    
                    elif (col_count%int(length)==7) & ( (xml_parent.get("name")==status_list[22]) | (xml_parent.get("name")==status_list[24])|  (xml_parent.get("name")==status_list[20])):
                    	status=query_result[row_count][col_count]
                        result=admin_vm_status(status)
                        
                        print_result(field_text,result,xml_child)
                    
                    elif ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[21]) | (xml_parent.get("name")==status_list[16]) | (xml_parent.get("name")==status_list[17]))) | (col_count%int(length)==4) & ((xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[6]) | (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[11])) | ((col_count%int(length)==5) & (
                    (xml_parent.get("name")==status_list[12]) | (xml_parent.get("name")==status_list[24]) | (xml_parent.get("name")==status_list[22] )))   :
                        ram=query_result[row_count][col_count]
                        result=check_vm_ram(ram)
                        print_result(field_text,result,xml_child) 
                    
                    elif (col_count%int(length)==4) & ( (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15]) )  | ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[12])) | (col_count%int(length)==5) & (xml_parent.get("name")==status_list[5]) :
                        extra_disk=query_result[row_count][col_count]
                        result=check_extra_disk(extra_disk)
                        print_result(field_text,result,xml_child)   
                    

                    elif (((col_count%int(length)==4) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) &  (xml_parent.get("name")==status_list[17]) | (xml_parent.get("name")==status_list[21]) ) |  ((col_count%int(length)==4) & (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==5) & ((xml_parent.get("name")==status_list[11]) | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==7) & (xml_parent.get("name")==status_list[4]))  | (((col_count%int(length)==7) |  (col_count%int(length)==5) | (col_count%int(length)==6 )) & ((xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[4]))) | (((col_count%int(length)==1) |  (col_count%int(length)==2)) &  (xml_parent.get("name")==status_list[23])):
                        mem=query_result[row_count][col_count]
                        result=check_mem(mem)
                        print_result(field_text,result,xml_child)  
                 
                    elif (((col_count%int(length)==8)| (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[4])) | (((col_count%int(length)==7) | (col_count%int(length)==8)) & (xml_parent.get("name")==status_list[11])) | (((col_count%int(length)==8) | (col_count%int(length)==9)) & (xml_parent.get("name")==status_list[12])):
                        logger.debug("correct entries")
                    
                    elif (col_count%int(length)==4) & (xml_parent.get("name")==status_list[13]):
                        status=query_result[row_count][col_count]
                        result=check_security_visibilty(status)
                        print_result(field_text,result,xml_child)
                    
                    elif (col_count%int(length)==2) & (xml_parent.get("name")==status_list[10]):
                        status=query_result[row_count][col_count]
                        result=host_status(status)
                        print_result(field_text,result,xml_child)   
                     
                    elif (col_count%int(length)==7) & ( (xml_parent.get("name")==status_list[5]) | (xml_parent.get("name")==status_list[6])) | ((col_count%int(length)==8) & ((xml_parent.get("name")==status_list[23]) | (xml_parent.get("name")==status_list[7]))):
                        status=query_result[row_count][col_count]
                        result=user_vm_status(status)
                        print_result(field_text,result,xml_child)  
                        
                    elif (col_count%int(length)==2) & ( (xml_parent.get("name")==status_list[17]) | (xml_parent.get("name")==status_list[21]) | (xml_parent.get("name")==status_list[14]) | (xml_parent.get("name")==status_list[15])) | ((col_count%int(length)==5) &  (xml_parent.get("name")==status_list[16])) | ((col_count%int(length)==6) &  ((xml_parent.get("name")==status_list[11])  | (xml_parent.get("name")==status_list[22]) | (xml_parent.get("name")==status_list[6]))) | ((col_count%int(length)==3) & ( (xml_parent.get("name")==status_list[4]) | (xml_parent.get("name")==status_list[7]) | (xml_parent.get("name")==status_list[5]))) | ((col_count%int(length)==4) &  (xml_parent.get("name")==status_list[12])) | ( (col_count%int(length)==3)  &  (xml_parent.get("name")==status_list[23])) | ((col_count%int(length)==6) &  (xml_parent.get("name")==status_list[24])):
                        status=query_result[row_count][col_count]
                        result=check_vcpu(status)
                        print_result(field_text,result,xml_child)  
                        
                    elif ((col_count%int(length)==6) & (xml_parent.get("name")==status_list[14])) | ( (col_count%int(length)==7) & (xml_parent.get("name")==status_list[21])):
                        owner_name_db=query_result[row_count][col_count]
                        owner_name_screen=xml_child[0].text
                        
                        result=faculty_vm_status(owner_name_db,owner_name_screen,xml_child)
                        print_result(field_text,result,xml_child)     
                    
                    elif (col_count%int(length)==6) & ((xml_parent.get("name")==status_list[15]) | (xml_parent.get("name")==status_list[16]) ) | ((col_count%int(length)==7) &  (xml_parent.get("name")==status_list[17])):
                    	status=query_result[row_count][col_count]
                        
                    	result=org_task_status(status,xml_child)
                        
                    	print_result(field_text,result,xml_child)
                        
                    elif (col_count%int(length)==1) & (xml_parent.get("name")==status_list[12]):
                        vm_name=query_result[row_count][4]
                        query_results=execute_query( xml_sub_child.get("query_collbtr"),(str(vm_name))).fetchall()
                        len_query=len(query_results)
                        if query_results!="None":
                            for m in range(0,len_query):
                                result=query_results[m][0]
                                print_result(field_text,result,xml_child)
                        else:
                            logger.debug(xml_child.get("value") +': Result:correct input')		
                    else:
                        result=query_result[row_count][col_count]
                        print_result(field_text,result,xml_child)
                    col_count+=1
                    if col_count%int(length)==0:
                        row_count+=1
                        col_count=0	
        else:
            logger.error(xml_child.get("value")  + "Error:tuple out of index")
    else:
    	logger.debug(xml_child.get("value") + ":Table does not exists")
    return

def faculty_vm_status(owner_name_db,owner_name_screen,xml_child):
	user_name=xml_child[0].text
	
	if owner_name_screen==str(owner_name_db):
		result="Approve  |  Reject | Edit"
	else:
		result="Remind Faculty"
	return result


def faculty_vm_status(owner_name_db,owner_name_screen,xml_child):
	user_name=xml_child[0].text
	
	if owner_name_screen==str(owner_name_db):
		result="Approve  |  Reject | Edit"
	else:
		result="Remind Faculty"
	return result

def user_vm_status(status):
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
def check_port_enabled(vm_name):
    query_result=execute_query("select enable_ssh,enable_http from request_queue where vm_name=%s",(str(vm_name))).fetchall()
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
def check_security_visibilty(status):
    if status=="T":
        result="ALL"
    else:
        result="NO"
    return result


#converting vCPU status bits into status text
def check_vcpu(status):
	status=str(status) + " CPU"
	return status



#converting memory bits into  text
def check_mem(mem):
    if mem==0:
        result="-"
    else:
        result=str(mem)+"GB"
    return result
    

#converting extra disk bits into  text
def check_extra_disk(extra_disk):
    if extra_disk==0:
        result="80GB"
    else:
        result="80GB + " + str(extra_disk) + "GB" 
    return result

#converting ram bits into  text
def check_vm_ram(ram):
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
def isCheckTable(driver, xml_parent, xml_child, xml_sub_child):
    field=driver.find_elements_by_xpath(xml_sub_child.get("path"))
    query_result=execute_query(xml_parent.get("query3")).fetchall()
    baadal_db.autocommit(True)
    
    length=len(query_result[0])#calculate number of columns of query
    length_row=len(query_result)#calculate number of columns of query
    table=0
    count=0
    for col in field:
		field_text=col.text 
		
		if field_text!="":
			count=count+1
			
    total=length_row*length
    if (str(total)==str(count)):
        for header in field:
            host_ip=query_result[table][0]
            if query_result[table][0] in header.text:
                table_path=xml_sub_child.text
                if isTablePresent(driver,xml_child,table_path):
                    result_fetch=execute_query(xml_parent.get("query4"),str(host_ip)).fetchall()
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
                                        result=admin_vm_status(status)
                                    else:
                                		result=result_fetch[row_count][col_count]
                                    print_result(field_text,result,xml_child)
                                    col_count+=1
                                    if col_count%int(no_of_cols)==0:
                                		row_count+=1
                                		col_count=0	
                                
                        else:
                            logger.error(xml_child.get("value") +":tuple out of index")
                            
                else:
                    logger.debug("No VM Exists on "+str(host_ip))
                table=table+1
    else:
        logger.error(xml_child.get("value") + ":incorrect data")
    return





#approving or rejecting vm operations   
def isCheckdata(driver,xml_parent, xml_child, xml_sub_child,vm_name):
    
    table_path=xml_sub_child.text
    if isTablePresent(driver,xml_child,table_path):
        ref=check_vm_in_pending_request_table(driver,xml_sub_child,xml_child,vm_name)
	
    	if ref:
	     logger.debug("Requst Approved!!!!!")
                       
        else:
	    logger.debug("No VM requests available to perform this testing.So,please create a VM before doing this testing.")
    return


def check_operation(driver,xml_parent, xml_child, xml_sub_child,op_id,vm_id):
    
    driver.find_element_by_xpath(ref).click()
    result=xml_sub_child.get("print_data")
    field_text=message_flash(driver,xml_sub_child,xml_child)
    print_result(field_text,result,xml_child)
    return



def isSanityCheck(driver, xml_parent, xml_child, xml_sub_child):
  
    field=driver.find_elements_by_xpath("//div[@id='sanity_check_table']/table/tbody/tr/td")

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
    
    conn_host(host_name,vm_status,vm_name,message,total_vm)


display.stop()
