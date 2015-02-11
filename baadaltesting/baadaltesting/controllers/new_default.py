# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
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

#@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
    
    
    
def unit_testing():
    import commands
    print request.vars
    ip_addr=request.vars['ip_addr'][0]
    print ip_addr
    form = FORM(  TABLE
        (  TR(INPUT(_name='testcase54', _type='checkbox', _value="54"),'All'),
           TR(INPUT(_name='testcase1', _type='checkbox', _value="1"),'Login'),
           TR(INPUT(_name='testcase2', _type='checkbox', _value="2"),'Configure System: Add Host'),
           TR(INPUT(_name='testcase3', _type='checkbox', _value="3"),'Configure System: Add Template'),
           TR(INPUT(_name='testcase4', _type='checkbox', _value="4"),'Configure System: Add Datastore'),
           TR(INPUT(_name='testcase5', _type='checkbox', _value="5"),'Configure System:Add Security Domain'),
           TR(INPUT(_name='testcase6', _type='checkbox', _value="6"),'Request VM'),
           TR(INPUT(_name='testcase7', _type='checkbox', _value="7"),'My VMs'),
           TR(INPUT(_name='testcase8', _type='checkbox', _value="8"),'My Pending Tasks'),
           TR(INPUT(_name='testcase9', _type='checkbox', _value="9"),'My Completed Tasks'),
           TR(INPUT(_name='testcase10', _type='checkbox', _value="10"),'My Failed Taskss'),
           TR(INPUT(_name='testcase11', _type='checkbox', _value="11"),'Pending Faculty-Level VM Approvals(Install VM)'),
           TR(INPUT(_name='testcase12', _type='checkbox', _value="12"),'Pending Faculty-Level VM Approvals(Clone VM)'),
           TR(INPUT(_name='testcase13', _type='checkbox', _value="13"),'Pending Faculty-Level VM Approvals(Attach Disk)'), 
           TR(INPUT(_name='testcase14', _type='checkbox', _value="14"),'Pending Org-Level VM Approvals(Install VM)'),
           TR(INPUT(_name='testcase15', _type='checkbox', _value="15"),'Pending Org-Level VM Approvals(Clone VM)'),
           TR(INPUT(_name='testcase16', _type='checkbox', _value="16"),'Pending Org-Level VM Approvals(Attach Disk)'), 
           TR(INPUT(_name='testcase17', _type='checkbox', _value="17"),'List All Org-Level VMs',),
           TR(INPUT(_name='testcase18', _type='checkbox', _value="18"),'All VMs'),
           TR(INPUT(_name='testcase19', _type='checkbox', _value="19"),'Host and VMs',),
           TR(INPUT(_name='testcase20', _type='checkbox', _value="20"),'Pending Tasks'),
           TR(INPUT(_name='testcase21', _type='checkbox', _value="21"),'Completed Tasks'),
           TR(INPUT(_name='testcase22', _type='checkbox', _value="22"),'Failed Tasks'),
           TR(INPUT(_name='testcase23', _type='checkbox', _value="23"),'Take VM snapshot    (Running )'),
           TR(INPUT(_name='testcase24', _type='checkbox', _value="24"),'Pause VM    (Running )'),
           TR(INPUT(_name='testcase25', _type='checkbox', _value="25"),'Add User to VM   (Running )'),
           TR(INPUT(_name='testcase26', _type='checkbox', _value="26"),'Gracefully shut down VM    (Running )'),
           TR(INPUT(_name='testcase27', _type='checkbox', _value="27"),'Forcefully power off VM   (Running )'),
           TR(INPUT(_name='testcase28', _type='checkbox', _value="28"),'Migrate VM(Running)'),
           TR(INPUT(_name='testcase29', _type='checkbox', _value="29"),'Delete VM    (Running)'),
           TR(INPUT(_name='testcase30', _type='checkbox', _value="30"),'Take VM snapshot   (Paused )'),
           TR(INPUT(_name='testcase32', _type='checkbox', _value="31"),'Migrate VM(Paused)'),
           TR(INPUT(_name='testcase32', _type='checkbox', _value="32"),'Unpause VM   (Paused )'),
           TR(INPUT(_name='testcase33', _type='checkbox', _value="33"),'Add User to VM  (Paused )'), 
	       TR(INPUT(_name='testcase34', _type='checkbox', _value="34"),'Delete Addtional User   (Paused )'),
           TR(INPUT(_name='testcase35', _type='checkbox', _value="35"),'Forcefully power off VM   (Paused)'),
           TR(INPUT(_name='testcase36', _type='checkbox', _value="36"),'Delete Snapshot    (Paused )'),
           TR(INPUT(_name='testcase37', _type='checkbox', _value="37"),'Revert Snapshot    (Paused )'),
           TR(INPUT(_name='testcase38', _type='checkbox', _value="38"),'Delete VM   (Paused )'),
           TR(INPUT(_name='testcase39', _type='checkbox', _value="39"),'Turn on VM   (Shutdown )'),
           TR(INPUT(_name='testcase40', _type='checkbox', _value="40"),'Add User to VM  (Shutdown)'),
           TR(INPUT(_name='testcase41', _type='checkbox', _value="41"),'Migrate VM(Shutdown)'),
           TR(INPUT(_name='testcase42', _type='checkbox', _value="42"),'Take VM snapshot   (Shutdown )'),
           TR(INPUT(_name='testcase43', _type='checkbox', _value="43"),'Delete VM   (Shutdown )'),
           TR(INPUT(_name='testcase44', _type='checkbox', _value="44"),'Sanity Table'), 
           TR(INPUT(_name='testcase45', _type='checkbox', _value="45"),'Pending User VM Requests(Install VM)'),
           TR(INPUT(_name='testcase46', _type='checkbox', _value="46"),'Pending User VM Requests(Clone VM)'),
           TR(INPUT(_name='testcase47', _type='checkbox', _value="47"),'Pending User VM Requests(Attach Disk)'),
           TR(INPUT(_name='testcase93', _type='checkbox', _value="93"),'Maintain Idompotency'),
           
           
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    if form.process().accepted:
        for i in range(1,95):
            test_case_no=request.vars['testcase'+str(i)]
            if test_case_no!=None:
                
                print test_case_no
                if test_case_no=="54":
                    for j in range(1,55):
                        test_case_no=str(j)
                        test_script(test_case_no,ip_addr)
                else:
                    test_script(test_case_no,ip_addr)
        
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)


def system_testing():
    import commands
    print request.vars
    ip_addr=request.vars['ip_addr'][0]
    print ip_addr
    form = FORM(  TABLE
        (  
	   TR(INPUT(_name='testcase54', _type='checkbox', _value="1"),'All'),
           TR(INPUT(_name='testcase1', _type='checkbox', _value="2"),'Migrate'),
           TR(INPUT(_name='testcase2', _type='checkbox', _value="3"),'Shutdown'),
           TR(INPUT(_name='testcase3', _type='checkbox', _value="4"),'Paused'),
           TR(INPUT(_name='testcase4', _type='checkbox', _value="5"),'Delete'),
           TR(INPUT(_name='testcase5', _type='checkbox', _value="6"),'Force Shutdown'),
           TR(INPUT(_name='testcase6', _type='checkbox', _value="7"),'Attach Disk'),
           TR(INPUT(_name='testcase7', _type='checkbox', _value="8"),'Baadal Shutdown'),
           TR(INPUT(_name='testcase8', _type='checkbox', _value="9"),'Clone VM'),
           TR(INPUT(_name='testcase9', _type='checkbox', _value="10"),'Edit VM Configuration'),
           TR(INPUT(_name='testcase10', _type='checkbox', _value="11"),'VNC Access'),
           TR(INPUT(_name='testcase11', _type='checkbox', _value="12"),'Sanity Check'),
           TR(INPUT(_name='testcase11', _type='checkbox', _value="13"),'VM Snapshot '),
           
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    if form.process().accepted:
        for i in range(1,13):
            test_case_no=request.vars['testcase'+str(i)]
            if test_case_no!=None:
                
                print test_case_no
                if test_case_no=="1":
                    for j in range(2,13):
                        test_case_no=str(j)
                        sys_test_script(test_case_no,addr_ip)
                else:
                    print test_case_no
                    sys_test_script(test_case_no,addr_ip)
        
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)


def index():
	import commands
        form = FORM( TABLE
                  (  TR(INPUT(_name='testcase1', _type='radio', _value="10.208.21.67"),'Main Server'),
                     TR(INPUT(_name='testcase2', _type='radio', _value="10.208.21.66"),'Nalini Sandbox'),
                     TR(INPUT(_name='testcase3', _type='radio', _value="10.208.23.80"),'Prateek Sandbox'),
                     TR(INPUT(_name='testcase4', _type='radio', _value="4"),'Paritosh Sandbox'),
                     TR(INPUT(_name='testcase5', _type='radio', _value="5"),'Suvojit Sandbox'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )
        if form.process().accepted:
            if request.vars['testcase1']!=None:         
                redirect(URL(r=request, f='main_page',vars=request.vars))
            if request.vars['testcase2']!=None:
                redirect(URL(r=request, f='main_page',vars=request.vars))
	    if request.vars['testcase3']!=None:
                redirect(URL(r=request, f='main_page',vars=request.vars))
            if request.vars['testcase4']!=None:
                redirect(URL(r=request, f='main_page',vars=request.vars))
	    if request.vars['testcase5']!=None:
                redirect(URL(r=request, f='main_page',vars=request.vars))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)


def main_page():
        print request.vars
        ip_addr=request.vars['testcase1']
            
        import commands
        form = FORM( TABLE
                  (  TR(INPUT(_name='testcase1', _type='radio', _value="1"),'All'),
		     TR(INPUT(_name='testcase2', _type='radio', _value="2"),'Unit Testing'),
		     TR(INPUT(_name='testcase3', _type='radio', _value="3"),'System Testing'),                     
                     TR(INPUT(_name='testcase4', _type='radio', _value="4"),'Network Testing'),
                     TR(INPUT(_name='testcase5', _type='radio', _value="5"),'Integration Testing'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )
        if form.process().accepted:
            if request.vars['testcase2']!=None:
                print "unit testing"
                redirect(URL(r=request, f='unit_testing',vars=dict(ip_addr=ip_addr)))
            if request.vars['testcase5']!=None:
                redirect(URL(r=request, f='integration_testing',vars=dict(ip_addr=ip_addr)))
            if request.vars['testcase1']!=None:
                 for j in range(1,94):
                        test_case_no=str(j)
                        test_script(test_case_no)
            if request.vars['testcase4']!=None:
                redirect(URL(r=request, f='network_testing',vars=dict(ip_addr=ip_addr)))
            if request.vars['testcase3']!=None:
                print "system testing"
                redirect(URL(r=request, f='system_testing',vars=dict(ip_addr=ip_addr)))
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)

def network_testing():
   
    import commands
    ip_addr=request.vars['ip_addr'][0]
    form = FORM(TABLE
             (   
              
    TR(INPUT(_name='testcase98', _type='checkbox', _value="98"),'Packages Install on Host '),
   
     TR(INPUT(_name='testcase99', _type='checkbox', _value="99"),'Packages Install on Baadal '),
    
    TR(INPUT(_name='testcase80', _type='checkbox', _value="80"),'VM status on Host '),
    BR(),
    TR(INPUT(_type='submit',_value='submit'))
            )
            )
    if form.process().accepted:
        if request.vars['testcase98']!=None:
            packages_install_test(98,ip_addr)
        if request.vars['testcase99']!=None:
            packages_install_host(99,ip_addr) 
        if request.vars['testcase80']!=None:
            check_stat_on_host(ip_addr)    
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    
    
def stress_testing(): 

    import commands
    ip_addr=request.vars['ip_addr'][0]
    form = FORM(  TABLE
        (   TR(INPUT(_name='testcase0', _type='checkbox', _value="0"),'All'), 
            BR(),
            TR(INPUT(_type='submit',_value='submit'))
        )
        )
              
    if form.process().accepted:
        test_case_no=request.vars['testcase0']
        if test_case_no!=None:
            stress_test_script(ip_addr)
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    
   
def integration_testing(): 
    import commands
    ip_addr=request.vars['ip_addr'][0]
    form = FORM(  TABLE
                  
                  (    TR(INPUT(_name='testcase93', _type='checkbox', _value="93"),'Maintain Idompotency'),
                       TR(INPUT(_name='testcase95', _type='checkbox', _value="95"),'VM Performance(Memory)'),
                       TR(INPUT(_name='testcase96', _type='checkbox', _value="96"),'VM Performance(CPU)'),
                       TR(INPUT(_name='testcase97', _type='checkbox', _value="97"),'VM Performance(Network)'),
                       TR(INPUT(_name='testcase98', _type='checkbox', _value="98"),'VM Performance(Disk)'),
                       TR(INPUT(_name='testcase99', _type='checkbox', _value="99"),'VM Performance   (Shutdown )'),
                       TR(INPUT(_name='testcase56', _type='checkbox', _value="56"),'User Request VM(Approved by Faculty,org-admin,admin)'),
                       TR(INPUT(_name='testcase57', _type='checkbox', _value="57"),'User Request VM(Approved by Faculty and Rejected by org-admin)'),
                       TR(INPUT(_name='testcase58', _type='checkbox', _value="58"),'User Request VM(Approved by Faculty,org-admin and Rejected by admin)'),
                       TR(INPUT(_name='testcase59', _type='checkbox', _value="59"),'User Request VM(Rejected by Faculty )'),
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
    if form.process().accepted:
        for i in range(56,100):
            test_case_no=request.vars['testcase'+str(i)]
            if i<=94:
                if test_case_no!=None:
                    test_script(test_case_no,ip_addr)
            else :
                if test_case_no!=None:
                    graph_test(test_case_no,ip_addr)
            
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
