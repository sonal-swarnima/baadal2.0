# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db, request, session
    from gluon import *  # @UnusedWildImport
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_context_path
import sys
import logging
import logging.config
logger = logging.getLogger("web2py.app.baadal")


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in 
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def index():
     if auth.is_logged_in():
        user_id=auth._get_user_id()
   	print user_id
    	new_db=mdb.connect("127.0.0.1","root","baadal","baadal")
    	cursor=new_db.cursor()
    	cursor.execute("select first_name,last_name,email from user where id= %s",user_id)
    	user_email_id=cursor.fetchall()
    	print user_email_id
    	print type(user_email_id)
    	#user_email_id=user_email_id.split(',')
    	first_name=user_email_id[0][0]
    	last_name=user_email_id[0][1]
    	email_id=user_email_id[0][2]
    	cursor.close()
   	user_name= first_name+ " " + last_name
   	print user_name
        print email_id
        redirect(URL(r=request, f='testing',vars=dict(email_id=email_id,user_name=user_name)))
     return dict(request=request)




def add_sandbox():
    print "inside add sandbox"
    form=FORM(DIV('Sandbox Name: ',INPUT(_name='server_name',requires=IS_NOT_EMPTY())),
     DIV('Ip address : ',INPUT(_name='name',requires=IS_NOT_EMPTY())),
     DIV(INPUT(_type='submit',_value='submit')))
    if form.process().accepted:
           redirect(URL(r=request, f='main_page',vars=request.vars))
    return dict(form=form)

def task():
    file_name=request.args[0]
    print "dfghjk"
    file_name=file_name.replace('_',' ')
    print file_name
    #print file_name1
    log_dir = os.path.join(get_context_path(),'logs/' + file_name + '.log')
    logger.debug(type(log_dir))
    logger.debug("log path is : " + str(log_dir))
    logger.debug("chown -R www-data:www-data " + str(log_dir))
    os.system("chown -R www-data:www-data " + str(log_dir))
    log_dir="<br />".join(log_dir.split("\n"))
    print log_dir
    fp=open(log_dir,'rU')             
    text=fp.read()                     
    text="<br />".join(text.split("\n"))
    fp.close()  
    #redirect(URL(r=request,c='default',f='task_list',args=text))         
    return text
    

def task_list():
    form = get_task_num_form()
    task_num = 20
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_task_by_status([TASK_QUEUE_STATUS_PENDING], task_num)
    success = get_task_by_status([TASK_QUEUE_STATUS_SUCCESS], task_num)
    failed = get_task_by_status([TASK_QUEUE_STATUS_FAILED, TASK_QUEUE_STATUS_PARTIAL_SUCCESS], task_num)
    return dict(pending=pending, success=success, failed=failed, form=form)
   
def page():
    form= FORM()
    return dict(form=form)

def testing():
	import commands
        if auth.is_logged_in():
           user_id=auth._get_user_id()
    	   new_db=mdb.connect("127.0.0.1","root","baadal","baadal")
    	   cursor=new_db.cursor()
    	   cursor.execute("select first_name,last_name,email from user where id= %s",user_id)
    	   user_email_id=cursor.fetchall()
    	   first_name=user_email_id[0][0]
    	   last_name=user_email_id[0][1]
    	   email_id=user_email_id[0][2]
    	   cursor.close()
   	   user_name= first_name+ " " + last_name
           user_name=user_name
           email_id=email_id
        form = FORM( TABLE
                  (  TR(INPUT(_name='testcase1', _type='checkbox', _value="10.237.20.155"),'Main Server'),
                     TR(INPUT(_name='testcase2', _type='checkbox', _value="14.139.13.4"),'NIC Server'),
                     TR(INPUT(_name='testcase3', _type='checkbox', _value="10.237.20.250"),'Nalini Sandbox'),
                     TR(INPUT(_name='testcase4', _type='checkbox',_value=""),'Add Sandbox'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )
        server_name={'10.237.20.155':'Main Server','14.139.13.4':'NIC Server','10.237.20.250':'Nalini Sandbox'}
        name=request.vars['name']
        if name == None :
           new_list=request.vars
           ip_addr = [v for k,v in new_list.iteritems() if 'testcase' in k]             
       	else :
           ip_addr=name[1]  
           print ip_addr
        if form.process().accepted:
            if request.vars['testcase1']!=None: 
                print "inside testcase1 in index page"        
                #redirect(URL(r=request, f='main_page',vars=request.vars))
                
                redirect(URL(r=request, f='main_page',vars=dict(email_id=email_id,user_name=user_name,ip_addr=ip_addr,server_name=server_name['10.237.20.155'])))
            if request.vars['testcase2']!=None: 
                print "inside testcase2 in index page"        
                #redirect(URL(r=request, f='main_page',vars=request.vars))
                
                redirect(URL(r=request, f='main_server',vars=dict(email_id=email_id,user_name=user_name,ip_addr=ip_addr,server_name=server_name['14.139.13.4'])))

            if request.vars['testcase3']!=None:
                print "inside testcase3 in index page"
                #redirect(URL(r=request, f='main_page',vars=request.vars))
		redirect(URL(r=request, f='main_page',vars=dict(email_id=email_id,user_name=user_name,ip_addr=ip_addr,server_name=server_name['10.237.20.250'])))
	    if request.vars['testcase4']!=None:
                print "inside testcase3 in index page"
                #redirect(URL(r=request, f='add_sandbox',vars=request.vars))
                redirect(URL(r=request, f='add_sandbox',vars=dict(email_id=email_id,user_name=user_name,ip_addr=ip_addr)))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)


def main_server():
        import commands
        print "inside main_page"
        print request.vars
        name=request.vars['name']
        if name == None :
                ip_addr=request.vars['ip_addr']            
        else :
                ip_addr=name               
        email_id=request.vars['email_id']
        user_name=request.vars['user_name']
        server_name=request.vars['server_name']
        print "server name is " + str(server_name)
        print "ip address is : " + str(ip_addr)
        print email_id
        form = FORM( TABLE
                  (  
                     TR(INPUT(_name='case3', _type='checkbox', _value="3"),'System Testing'),
                     TR(INPUT(_name='case5', _type='checkbox', _value="5"),'Integration Testing'),
		     #TR(INPUT(_name='case2', _type='checkbox', _value="2"),'Performance Testing'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )
        if form.process().accepted:
	    if request.vars['case3']!=None:
                redirect(URL(r=request, f='main_system_testing',vars=request.vars))
	    if request.vars['case2']!=None:
                redirect(URL(r=request, f='Performance Testing',vars=request.vars))
            if request.vars['case5']!=None:
                redirect(URL(r=request, f='integration_testing',vars=request.vars))

        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)


def main_page():
        import commands
        print "inside main_page"
        print request.vars
        name=request.vars['name']
        if name == None :
                ip_addr=request.vars['ip_addr']            
        else :
                ip_addr=name               
        email_id=request.vars['email_id']
        user_name=request.vars['user_name']
        server_name=request.vars['server_name']
        print "server name is " + str(server_name)
        print "ip address is : " + str(ip_addr)
        print email_id
        form = FORM( TABLE
                  (  TR(INPUT(_name='case1', _type='checkbox', _value="1"),'Unit Testing'),
                     TR(INPUT(_name='case3', _type='checkbox', _value="3"),'System Testing'),
                     TR(INPUT(_name='case5', _type='checkbox', _value="5"),'Integration Testing'),
		     #TR(INPUT(_name='case2', _type='checkbox', _value="2"),'Performance Testing'),
		     TR(INPUT(_name='case4', _type='checkbox', _value="4"),'Database Dependent Testing'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )
        if form.process().accepted:
            if request.vars['case1']!=None:
                redirect(URL(r=request, f='unit_testing',vars=request.vars))
	    if request.vars['case3']!=None:
                redirect(URL(r=request, f='system_testing',vars=request.vars))
	    if request.vars['case2']!=None:
                redirect(URL(r=request, f='Performance Testing',vars=request.vars))
            if request.vars['case4']!=None:
                redirect(URL(r=request, f='database_dependent_testing',vars=request.vars))
            if request.vars['case5']!=None:
                redirect(URL(r=request, f='integration_testing',vars=request.vars))

        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)
     
def unit_testing():
    print "inside unit testing"
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    print "ip address of the testing system is : "
    print ip_address
    form = FORM(  TABLE
        (  TR(INPUT(_name='testcase54', _type='checkbox', _value="54"),'All'),
           TR(INPUT(_name='testcase1', _type='checkbox', _value="1"),'Login'),
           TR(INPUT(_name='testcase2', _type='checkbox', _value="2"),'Configure System: Add Host'),
           TR(INPUT(_name='testcase3', _type='checkbox', _value="3"),'Configure System: Add Template'),
           TR(INPUT(_name='testcase4', _type='checkbox', _value="4"),'Configure System: Add Datastore'),
           TR(INPUT(_name='testcase6', _type='checkbox', _value="6"),'Request VM'), 
           TR(INPUT(_name='testcase23', _type='checkbox', _value="23"),'Take VM snapshot(Running )'),    
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
        )
           #TR(INPUT(_name='testcases5', _type='checkbox', _value="5"),'Configure System:Add Security Domain'),  
           #TR(INPUT(_name='testcase23', _type='checkbox', _value="23"),'Take VM snapshot(Running )'),
           #TR(INPUT(_name='testcase24', _type='checkbox', _value="24"),'Pause VM(Running )'),
           #TR(INPUT(_name='testcase25', _type='checkbox', _value="25"),'Add User to VM   (Running )'),
           #TR(INPUT(_name='testcase26', _type='checkbox', _value="26"),'Gracefully shut down VM    (Running )'),
           #TR(INPUT(_name='testcase27', _type='checkbox', _value="27"),'Forcefully power off VM   (Running )'),
           #TR(INPUT(_name='testcase28', _type='checkbox', _value="28"),'Migrate VM(Running)'),
           #TR(INPUT(_name='testcase29', _type='checkbox', _value="29"),'Delete VM    (Running)'),
           #TR(INPUT(_name='testcase30', _type='checkbox', _value="30"),'Take VM snapshot   (Paused )'),
           #TR(INPUT(_name='testcase32', _type='checkbox', _value="31"),'Migrate VM(Paused)'),
           #TR(INPUT(_name='testcase32', _type='checkbox', _value="32"),'Unpause VM   (Paused )'),
          # TR(INPUT(_name='testcase33', _type='checkbox', _value="33"),'Add User to VM  (Paused )'),
          # TR(INPUT(_name='testcase34', _type='checkbox', _value="34"),'Delete Addtional User   (Paused )'),
           #TR(INPUT(_name='testcase35', _type='checkbox', _value="35"),'Forcefully power off VM   (Paused)'),
          # TR(INPUT(_name='testcase36', _type='checkbox', _value="36"),'Delete Snapshot    (Paused )'),
           #TR(INPUT(_name='testcase37', _type='checkbox', _value="37"),'Revert Snapshot    (Paused )'),
           #TR(INPUT(_name='testcase38', _type='checkbox', _value="38"),'Delete VM   (Paused )'),
          # TR(INPUT(_name='testcase39', _type='checkbox', _value="39"),'Turn on VM   (Shutdown )'),
           #TR(INPUT(_name='testcase40', _type='checkbox', _value="40"),'Add User to VM  (Shutdown)'),
          # TR(INPUT(_name='testcase41', _type='checkbox', _value="41"),'Migrate VM(Shutdown)'),
          # TR(INPUT(_name='testcase42', _type='checkbox', _value="42"),'Take VM snapshot   (Shutdown )'),
           #TR(INPUT(_name='testcase43', _type='checkbox', _value="43"),'Delete VM   (Shutdown )'),
           #TR(INPUT(_name='testcase44', _type='checkbox', _value="44"),'Sanity Table'),
          # TR(INPUT(_name='testcase45', _type='checkbox', _value="45"),'Pending User VM Requests(Install VM)'),
          # TR(INPUT(_name='testcase46', _type='checkbox', _value="46"),'Pending User VM Requests(Clone VM)'),
          # TR(INPUT(_name='testcase47', _type='checkbox', _value="47"),'Pending User VM Requests(Attach Disk)'),
           
           
     
    test_list={'54':'All','1':'Login','2':'Configure System: Add Host','3':'Configure System: Add Template','4':'Configure System: Add Datastore','5':'Configure System:Add Security Domain','6':'Request VM','23':'Take VM snapshot(Running )','24':'Pause VM(Running )','25':'Add User to VM   (Running )','26':'Gracefully shut down VM(Running )','4':'Configure System: Add Datastore','5':'Configure System:Add Security Domain','6':'Request VM'}   
    if form.process().accepted:
        testcase_list=[]
        test_case_list=[]
        j=0
        for i in range(1,95):
            test_case_no=request.vars['testcase'+str(i)]
            logger.debug(type(test_case_no))
            logger.debug("test case no is : " + str(test_case_no))            
            if test_case_no == None or test_case_no == "" :
                continue              
            else:
                testcase_list.insert(j,i)
                test_case_list.append(test_list[str(i)])
            j+=1
        logger.debug(testcase_list)
        task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='Unit Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
        db.commit()
        task_type='Unit Testing' 
        print task_event_id 
        schedule_task(task_type,task_event_id,email_id,user_name,server_name,test_case_list)     
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)


def main_system_testing():
    print "inside main system testing"
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    print "ip address of the testing system is : "
    print ip_address
    form = FORM(  TABLE
        (  
	   
           TR(INPUT(_name='testcases13', _type='checkbox', _value="16"),'All'),
           TR(INPUT(_name='testcases1', _type='checkbox', _value="1"),'Migrate'),
           TR(INPUT(_name='testcases2', _type='checkbox', _value="2"),'Gracefully shutdown'),
           TR(INPUT(_name='testcases3', _type='checkbox', _value="3"),'Paused'),
           TR(INPUT(_name='testcases4', _type='checkbox', _value="4"),'Delete'),
           TR(INPUT(_name='testcases5', _type='checkbox', _value="5"),'Force Shutdown'),
           TR(INPUT(_name='testcases6', _type='checkbox', _value="6"),'Attach Disk'),
           TR(INPUT(_name='testcases8', _type='checkbox', _value="8"),'Clone VM'),
           TR(INPUT(_name='testcases9', _type='checkbox', _value="9"),'Edit VM Configuration'),
           #TR(INPUT(_name='testcases10', _type='checkbox', _value="10"),'VNC Access'),
           #TR(INPUT(_name='testcases11', _type='checkbox', _value="11"),'Sanity Check'),
           TR(INPUT(_name='testcases12', _type='checkbox', _value="12"),'VM Snapshot '),
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    test_list={'16':'All','1':'Migrate','2':'Gracefully shutdown','3':'Paused','4':'Delete','5':'Force Shutdown','6':'Attach Disk','7':'Baadal Shutdown','8':'Clone VM','9':'Edit VM Configuration','10':'VNC Access','11':'Sanity Check','12':'VM Snapshot','13':'Launch VM','14':'Wake On LAN','15':'Check Host Load Capacity'}   
    if form.process().accepted:
        testcase_list=[]
        test_case_list=[]
        j=0
        for i in range(1,17): 
            print i
            test_case_no=request.vars['testcases'+str(i)]    
            print "test case no  : " +str(test_case_no)       
            if test_case_no==None:                
                	continue
	    elif test_case_no=='16':
		for i in range(1,16): 
		    testcase_list.insert(j,i)
                    test_case_list.append(test_list[str(i)])
            else:
                        testcase_list.insert(j,i)
                        test_case_list.append(test_list[str(i)])
            j+=1
        print "test case list : " + str(testcase_list)
        print test_case_list
        task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='System Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
        db.commit()
        task_type='System Testing'  
        schedule_task(task_type,task_event_id,email_id,user_name,server_name,test_case_list) 
   
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

def system_testing():
    logger.debug("inside system testing")
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    logger.debug("ip address of the testing system is : " + str(ip_address))
    form = FORM(  TABLE
        (  
           TR(INPUT(_name='testcases16', _type='checkbox', _value="16"),'All'),
           TR(INPUT(_name='testcases1', _type='checkbox', _value="1"),'Migrate'),
           TR(INPUT(_name='testcases2', _type='checkbox', _value="2"),'Gracefully shutdown'),
           TR(INPUT(_name='testcases3', _type='checkbox', _value="3"),'Paused'),
           TR(INPUT(_name='testcases4', _type='checkbox', _value="4"),'Delete'),
           TR(INPUT(_name='testcases5', _type='checkbox', _value="5"),'Force Shutdown'),
           TR(INPUT(_name='testcases6', _type='checkbox', _value="6"),'Attach Disk'),
           #TR(INPUT(_name='testcases7', _type='checkbox', _value="7"),'Baadal Shutdown'),
           TR(INPUT(_name='testcases8', _type='checkbox', _value="8"),'Clone VM'),
           TR(INPUT(_name='testcases9', _type='checkbox', _value="9"),'Edit VM Configuration'),
           #TR(INPUT(_name='testcases10', _type='checkbox', _value="10"),'VNC Access'),
           #TR(INPUT(_name='testcases11', _type='checkbox', _value="11"),'Sanity Check'),
           #TR(INPUT(_name='testcases12', _type='checkbox', _value="12"),'VM Snapshot '),
           #TR(INPUT(_name='testcases13', _type='checkbox', _value="13"),'Launch VM '),
           #TR(INPUT(_name='testcases14', _type='checkbox', _value="14"),'Wake On LAN '),
           #TR(INPUT(_name='testcases15', _type='checkbox', _value="15"),'Check Host Load Capacity (100 min)'),
           
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    test_list={'16':'All','1':'Migrate','2':'Gracefully shutdown','3':'Paused','4':'Delete','5':'Force Shutdown','6':'Attach Disk','7':'Baadal Shutdown','8':'Clone VM','9':'Edit VM Configuration','10':'VNC Access','11':'Sanity Check','12':'VM Snapshot','13':'Launch VM','14':'Wake On LAN','15':'Check Host Load Capacity'}   
    if form.process().accepted:
        testcase_list=[]
        test_case_list=[]
        j=0
        for i in range(1,18): 
            logger.debug(i)
            test_case_no=request.vars['testcases'+str(i)]    
            logger.debug("test case no  : " +str(test_case_no))       
            if test_case_no==None:                
                	continue
	   
            else:
                        testcase_list.insert(j,i)
                        test_case_list.append(test_list[str(i)])
            j+=1
        logger.debug("test case list : " + str(testcase_list))
        task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='System Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
        db.commit()
        task_type='System Testing'  
        schedule_task(task_type,task_event_id,email_id,user_name,server_name,test_case_list) 
   
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)




def database_dependent_testing():
    print "database_dependent testing"
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    print "ip address of the testing system is : "
    print ip_address
    form = FORM(  TABLE
        (  
           TR(INPUT(_name='testcases7', _type='checkbox', _value="7"),'My VMs'),
           TR(INPUT(_name='testcases8', _type='checkbox', _value="8"),'My Pending Tasks'),
           TR(INPUT(_name='testcases9', _type='checkbox', _value="9"),'My Completed Tasks'),
           TR(INPUT(_name='testcases10', _type='checkbox', _value="10"),'My Failed Tasks'),
           TR(INPUT(_name='testcases18', _type='checkbox', _value="18"),'All VMs'),
           TR(INPUT(_name='testcases19', _type='checkbox', _value="19"),'Host and VMs',),
           TR(INPUT(_name='testcases20', _type='checkbox', _value="20"),'Pending Tasks'),
           TR(INPUT(_name='testcases21', _type='checkbox', _value="21"),'Completed Tasks'),
           TR(INPUT(_name='testcases22', _type='checkbox', _value="22"),'Failed Tasks'),
           TR(INPUT(_name='testcases44', _type='checkbox', _value="44"),'Sanity Table'), 
           TR(INPUT(_name='testcases17', _type='checkbox', _value="17"),'List All Org-Level VMs',),
           TR(INPUT(_name='testcases45', _type='checkbox', _value="45"),'Pending User VM Requests(Install VM)'),
           TR(INPUT(_name='testcases46', _type='checkbox', _value="46"),'Pending User VM Requests(Clone VM)'),
           TR(INPUT(_name='testcases47', _type='checkbox', _value="47"),'Pending User VM Requests(Attach Disk)'), 
           TR(INPUT(_name='testcases11', _type='checkbox', _value="11"),'Pending Faculty-Level VM Approvals(Install VM)'),
           TR(INPUT(_name='testcases12', _type='checkbox', _value="12"),'Pending Faculty-Level VM Approvals(Clone VM)'),
           TR(INPUT(_name='testcases13', _type='checkbox', _value="13"),'Pending Faculty-Level VM Approvals(Attach Disk)'), 
           TR(INPUT(_name='testcases14', _type='checkbox', _value="14"),'Pending Org-Level VM Approvals(Install VM)'),
           TR(INPUT(_name='testcases15', _type='checkbox', _value="15"),'Pending Org-Level VM Approvals(Clone VM)'),
           TR(INPUT(_name='testcases16', _type='checkbox', _value="16"),'Pending Org-Level VM Approvals(Attach Disk)'),          
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    test_list={'7':'My VMs','8':'My Pending Tasks','9':'My Completed Tasks','10':'My Failed Tasks','11':'Pending Faculty-Level VM Approvals(Install VM)','12':'Pending Faculty-Level VM Approvals(Clone VM)','13':'Pending Faculty-Level VM Approvals(Attach Disk)','14':'Pending Org-Level VM Approvals(Install VM)','15':'Pending Org-Level VM Approvals(Clone VM)','16':'Pending Org-Level VM Approvals(Attach Disk)','17':'List All Org-Level VMs','18':'All VMs','19':'Host and VMs','20':'Pending Tasks','21':'Completed Tasks','22':'Failed Tasks','44':'Completed Tasks','22':'Sanity Table','47':'Pending User VM Requests(Attach Disk)','45':'Pending User VM Requests(Install VM)','46':'Pending User VM Requests(Clone VM)'}   
    if form.process().accepted:
        testcase_list=[]
        test_case_list=[]
        j=0
        for i in range(6,49): 
            print i
            test_case_no=request.vars['testcases'+str(i)]    
            print "test case no  : " +str(test_case_no)       
            if test_case_no==None:                
                	continue
            else:
                        testcase_list.insert(j,i)
                        test_case_list.append(test_list[str(i)])
            j+=1
        print "test case list : " + str(testcase_list)
        print test_case_list
        task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='Database Dependent Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
        db.commit()
        task_type='Database Dependent Testing'  
        schedule_task(task_type,task_event_id,email_id,user_name,server_name,test_case_list) 
   
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

'''def network_testing():
   
    print "inside unit testing"
    import commands
    email_id=request.vars['email_id']
    print type(email_id)
    user_name=request.vars['user_name']
    ip_address=request.vars['ip_addr']
    name=request.vars['name']
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name[1]         
    form = FORM(TABLE
             (                 
    TR(INPUT(_name='testcases98', _type='checkbox', _value="98"),'Packages Install on Host '),
   
     TR(INPUT(_name='testcases99', _type='checkbox', _value="99"),'Packages Install on Baadal '),
    
    TR(INPUT(_name='testcases80', _type='checkbox', _value="80"),'VM status on Host '),
    BR(),
    TR(INPUT(_type='submit',_value='submit'))
            )
            )
    task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='Network Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name) 
    if form.process().accepted:
        if request.vars['testcases98']!=None:
            packages_install_test(98,ip_address)
        if request.vars['testcases99']!=None:
            packages_install_host(99,ip_address) 
        if request.vars['testcases80']!=None:
            check_stat_on_host(ip_address)    
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)'''
    
    
def stress_testing(): 

    print "inside stress testing"
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    print "ip address of the testing system is : "
    print ip_address
    form = FORM(  TABLE
        (   TR(INPUT(_name='testcases0', _type='checkbox', _value="1"),'All'), 
            BR(),
            TR(INPUT(_type='submit',_value='submit'))
        )
        )
              
    if form.process().accepted:
        test_case_no=request.vars['testcases0']   
       	print "test case list : " + str(test_case_no)
        if test_case_no!=None:                
                testcase_list=test_case_no
    	task_event_id = db.task_queue.insert(ip_addr=ip_address,task_type ='Stress Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
    	db.commit()
    	task_type='Stress Testing'  
    	schedule_task(task_type,task_event_id,email_id,user_name,server_name)
        
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    
   
def integration_testing(): 
    print "inside integration testing"
    import commands
    print request.vars
    email_id=request.vars['email_id']
    user_name=request.vars['user_name']
    name=request.vars['name']
    server_name=request.vars['server_name']
    print "server name is " + str(server_name)
    if name == None :
       print "inside name checking "
       ip_address=request.vars['ip_addr'] 
    else :
       print "else part of name checking"
       ip_address=name         
    print "ip address of the testing system is : "
    print ip_address
    form = FORM(  TABLE
                  
                  (    TR(INPUT(_name='testcase114', _type='checkbox', _value="114"),'All'),
			TR(INPUT(_name='testcase49', _type='checkbox', _value="49"),'Maintain Idompotency'),
                       TR(INPUT(_name='testcase50', _type='checkbox', _value="50"),'VM Graph(Memory)'),
                       TR(INPUT(_name='testcase51', _type='checkbox', _value="51"),'VM Graph(CPU)'),
                       TR(INPUT(_name='testcase52', _type='checkbox', _value="52"),'VM Graph(Network)'),
                       TR(INPUT(_name='testcase53', _type='checkbox', _value="53"),'VM Graph(Disk)'),
                       #TR(INPUT(_name='testcase54', _type='checkbox', _value="54"),'VM Performance   (Shutdown )'),
                       #TR(INPUT(_name='testcase56', _type='checkbox', _value="56"),'User Request VM(Approved by Faculty,org-admin,admin)'),
                       #TR(INPUT(_name='testcase57', _type='checkbox', _value="57"),'User Request VM(Approved by Faculty and Rejected by org-admin)'),
                      # TR(INPUT(_name='testcase58', _type='checkbox', _value="58"),'User Request VM(Approved by Faculty,org-admin and Rejected by admin)'),
                      # TR(INPUT(_name='testcase59', _type='checkbox', _value="59"),'User Request VM(Rejected by Faculty )'),
                       TR(INPUT(_name='testcase54', _type='checkbox', _value="54"),'Performance Testing(1CPU,80GB HDD,256MB RAM)'),
			TR(INPUT(_name='testcase55', _type='checkbox', _value="55"),'Performance Testing(1CPU,80GB HDD,512MB RAM)'),
			TR(INPUT(_name='testcase56', _type='checkbox', _value="56"),'Performance Testing(1CPU,80GB HDD,1GB RAM)'),
			TR(INPUT(_name='testcase57', _type='checkbox', _value="57"),'Performance Testing(1CPU,80GB HDD,2GB RAM)'),
			TR(INPUT(_name='testcase58', _type='checkbox', _value="58"),'Performance Testing(2CPU,80GB HDD,2GB RAM)'),
			TR(INPUT(_name='testcase59', _type='checkbox', _value="59"),'Performance Testing(2CPU,80GB HDD,4GB RAM)'),
			TR(INPUT(_name='testcase60', _type='checkbox', _value="60"),'Performance Testing(4CPU,80GB HDD,4GB RAM)'),
			TR(INPUT(_name='testcase61', _type='checkbox', _value="61"),'Performance Testing(4CPU,80GB HDD,8GB RAM)'),
			TR(INPUT(_name='testcase62', _type='checkbox', _value="62"),'Performance Testing(8CPU,80GB HDD,8GB RAM)'),
			TR(INPUT(_name='testcase63', _type='checkbox', _value="63"),'Performance Testing(8CPU,80GB HDD,16GB RAM)'),
#                             
                  #     TR(INPUT(_name='testcase60', _type='checkbox', _value="60"),'Take VM snapshot    (Running )'),
                   #    TR(INPUT(_name='testcase61', _type='checkbox', _value="61"),'Pause VM   (Running )'),
                    #   TR(INPUT(_name='testcase62', _type='checkbox', _value="62"),'Add User to VM   (Running )'),
                     #  TR(INPUT(_name='testcase65', _type='checkbox', _value="65"),'Delete VM    (Running)'),
                      # TR(INPUT(_name='testcase64', _type='checkbox', _value="64"),'Gracefully shut down VM    (Running )'),
                      # TR(INPUT(_name='testcase63', _type='checkbox', _value="63"),'Forcefully power off VM   (Running )'),
                      # TR(INPUT(_name='testcase66', _type='checkbox', _value="66") ,'Migrate VM   (Running )'),
                       #TR(INPUT(_name='testcase67', _type='checkbox', _value="67"),'Take VM snapshot   (Paused )'),
                       #TR(INPUT(_name='testcase68', _type='checkbox', _value="68"),'Unpause VM   (Paused )'),
                       #TR(INPUT(_name='testcase69', _type='checkbox', _value="69"),'Add User to VM  (Paused )'),
                       #TR(INPUT(_name='testcase75', _type='checkbox', _value="75"),'Delete VM   (Paused )'),
                       #TR(INPUT(_name='testcase71', _type='checkbox', _value="71"),'Forcefully power off VM   (Paused)'),
                       #TR(INPUT(_name='testcase70', _type='checkbox', _value="70"),'Migrate VM   (Paused )'),
                       #TR(INPUT(_name='testcase72', _type='checkbox', _value="72"),'Delete Add User  (Paused )'),
                       #TR(INPUT(_name='testcase73', _type='checkbox', _value="73"),'Revert Snapshot  (Paused )'),
                      # TR(INPUT(_name='testcase74', _type='checkbox', _value="74"),'Delete snapshot   (Paused )'),
                      # TR(INPUT(_name='testcase76', _type='checkbox', _value="76"),'Turn on VM   (Shutdown )'),
                      # TR(INPUT(_name='testcase77', _type='checkbox', _value="77"),'Add User to VM  (Shutdown)'),
                       #TR(INPUT(_name='testcase80', _type='checkbox', _value="80"),'Delete VM   (Shutdown )'),
                      # TR(INPUT(_name='testcase78', _type='checkbox', _value="78"),'Take VM snapshot   (Shutdown )'),
                       #TR(INPUT(_name='testcase79', _type='checkbox', _value="79"),'Migrate VM   (Shutdown )'),
                       #TR(INPUT(_name='testcase107', _type='checkbox', _value="107"),'User Request Attach Disk(Approved by Faculty,org-admin,admin)'),
                       # TR(INPUT(_name='testcase71', _type='checkbox', _value="71"), 'Org-Admin Request VM(Rejected by admin)'),
                       #TR(INPUT(_name='testcase109', _type='checkbox', _value="109"),'User Request Attach Disk(Approved by Faculty and Rejected by org-admin)'),
                      #TR(INPUT(_name='testcase108', _type='checkbox', _value="108"),'User Request Attach Disk(Approved by Faculty,org-admin and Rejected by admin)'),
                      # TR(INPUT(_name='testcase110', _type='checkbox', _value="110"),'User Request Attach Disk(Rejected by Faculty )'),            
                     # TR(INPUT(_name='testcase105', _type='checkbox', _value="105"),'Org-Admin  Attach Disk(Approved by admin)'),
                   # TR(INPUT(_name='testcase106', _type='checkbox', _value="106"), 'Org-Admin Attach Disk(Rejected by admin)'),                    
                     
                   # TR(INPUT(_name='testcase102', _type='checkbox', _value="102"),'User Request Clone VM(Approved by Faculty and Rejected by org-admin)'),
                   #   TR(INPUT(_name='testcase112', _type='checkbox', _value="112"),'User Request Clone VM(Rejected by Faculty )'),
                   
                  #   TR(INPUT(_name='testcase118', _type='checkbox', _value="118"),'User Request Clone VM(Approved by Faculty,org-admin,admin)'),
                #   TR(INPUT(_name='testcase119', _type='checkbox', _value="119"),'User Request Clone VM(Approved by Faculty and Rejected by org-admin)'),
                 #     TR(INPUT(_name='testcase120', _type='checkbox', _value="120"),'User Request Clone VM(Approved by Faculty,org-admin and Rejected by admin)'),
                  #    TR(INPUT(_name='testcase121', _type='checkbox', _value="121"),'User Request Edit VM Config(Rejected by Faculty )'),
                   
                      BR(),
                      TR(INPUT(_type='submit',_value='submit'))
            )
     ) 
    test_list={'114':'All','49':'Maintain Idompotency','50':'VM Graph(Memory)','51':'VM Graph(CPU)','52':'VM Graph(Network)','53':'VM Graph(Disk)','54':'Performance Testing(1CPU,80GB HDD,256MB RAM)','55':'Performance Testing(1CPU,80GB HDD,512MB RAM)','56':'Performance Testing(1CPU,80GB HDD,1GB RAM)','57':'Performance Testing(1CPU,80GB HDD,2GB RAM)','58':'Performance Testing(2CPU,80GB HDD,2GB RAM)','59':'Performance Testing(2CPU,80GB HDD,4GB RAM)','60':'Performance Testing(4CPU,80GB HDD,4GB RAM)','61':'Performance Testing(4CPU,80GB HDD,8GB RAM)','62':'Performance Testing(8CPU,80GB HDD,8GB RAM)','63':'Performance Testing(8CPU,80GB HDD,16GB RAM)'}  
    if form.process().accepted:
        testcase_list=[]
        test_case_list=[]
        j=0
        for i in range(49,116):
            print "inside for loop"
            test_case_no=request.vars['testcase'+str(i)]
            logger.debug("i is : " + str(i))
            logger.debug("j is : " + str(j))
            logger.debug("test case no : " + str(test_case_no))
	    if test_case_no == None :
                continue            
            else:
                testcase_list.insert(j,i)
                test_case_list.append(test_list[str(i)])
            j+=1
        logger.debug("test cases are : " + str(testcase_list))
        task_event_id=db.task_queue.insert(ip_addr=ip_address,task_type='Integration Testing',requester_type=testcase_list,email_id=email_id,user_name=user_name)
        db.commit()
        task_type='Integration Testing'  
        schedule_task(task_type,task_event_id,email_id,user_name,server_name,test_case_list)
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

import time

def network_graph():
     
              
    return 


def test():
    form = FORM(  TABLE
        (  
           TR(INPUT(_name='testcase1', _type='checkbox', _value="1"),'All'),
           TR(INPUT(_name='testcase2', _type='checkbox', _value="2"),'Migrate'),
           TR(INPUT(_name='testcase3', _type='checkbox', _value="3"),'Shutdown'),
           
           
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    return dict(form=form)
