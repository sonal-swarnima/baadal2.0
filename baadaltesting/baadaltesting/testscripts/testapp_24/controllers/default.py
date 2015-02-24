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
    form = FORM(  TABLE
         (  TR(INPUT(_name='testcase65', _type='checkbox', _value="65"),'All'),
            TR(INPUT(_name='testcase1', _type='checkbox', _value="1"),'Login'),
            TR(INPUT(_name='testcase15', _type='checkbox', _value="15"),'Configure System: Add Host'),
           TR(INPUT(_name='testcase16', _type='checkbox', _value="16"),'Configure System: Add Template'),
           TR(INPUT(_name='testcase17', _type='checkbox', _value="17"),'Configure System: Add Datastore'),
           TR(INPUT(_name='testcase59', _type='checkbox', _value="59"),'Configure System:Add Security Domain'),
            TR(INPUT(_name='testcase2', _type='checkbox', _value="2"),'Request VM'),
            TR(INPUT(_name='testcase3', _type='checkbox', _value="3"),'My VMs'),
            TR(INPUT(_name='testcase4', _type='checkbox', _value="4"),'My Pending Tasks'),
            TR(INPUT(_name='testcase5', _type='checkbox', _value="5"),'My Completed Tasks'),
            TR(INPUT(_name='testcase6', _type='checkbox', _value="6"),'My Failed Taskss'),
            TR(INPUT(_name='testcase7', _type='checkbox', _value="7"),'Pending Faculty-Level VM Approvals(Install VM)'),
            TR(INPUT(_name='testcase46', _type='checkbox', _value="46"),'Pending Faculty-Level VM Approvals(Clone VM)'),
            TR(INPUT(_name='testcase49', _type='checkbox', _value="49"),'Pending Faculty-Level VM Approvals(Attach Disk)'),
            
            TR(INPUT(_name='testcase8', _type='checkbox', _value="8"),'Pending Org-Level VM Approvals(Install VM)'),
            TR(INPUT(_name='testcase51', _type='checkbox', _value="51"),'Pending Org-Level VM Approvals(Clone VM)'),
            TR(INPUT(_name='testcase52', _type='checkbox', _value="52"),'Pending Org-Level VM Approvals(Attach Disk)'),
            
           TR(INPUT(_name='testcase9', _type='checkbox', _value="9"),'List All Org-Level VMs',),
           TR(INPUT(_name='testcase10', _type='checkbox', _value="10"),'All VMs'),
           TR(INPUT(_name='testcase19', _type='checkbox', _value="19"),'Pending Admin VM Requests(Install VM)'),
           TR(INPUT(_name='testcase54', _type='checkbox', _value="54"),'Pending Admin VM Requests(Clone VM)'),
           TR(INPUT(_name='testcase55', _type='checkbox', _value="55"),'Pending Admin VM Requests(Attach Disk)'),
           
           TR(INPUT(_name='testcase62', _type='checkbox', _value="62"),'Pending User VM Requests(Install VM)'),
           TR(INPUT(_name='testcase63', _type='checkbox', _value="63"),'Pending User VM Requests(Clone VM)'),
           TR(INPUT(_name='testcase64', _type='checkbox', _value="64"),'Pending User VM Requests(Attach Disk)'),
           
           TR(INPUT(_name='testcase11', _type='checkbox', _value="11"),'Host and VMs',),
           TR(INPUT(_name='testcase12', _type='checkbox', _value="12"),'Pending Tasks'),
           TR(INPUT(_name='testcase13', _type='checkbox', _value="13"),'Completed Tasks'),
           TR(INPUT(_name='testcase14', _type='checkbox', _value="14"),'Failed Tasks'),
           
           TR(INPUT(_name='testcase18', _type='checkbox', _value="18"),'Take VM snapshot    (Running )'),
           TR(INPUT(_name='testcase20', _type='checkbox', _value="20"),'Pause VM    (Running )'),
           
           TR(INPUT(_name='testcase21', _type='checkbox', _value="21"),'Add User to VM   (Running )'),
           
           TR(INPUT(_name='testcase22', _type='checkbox', _value="22"),'Delete VM    (Running)'),
           TR(INPUT(_name='testcase23', _type='checkbox', _value="23"),'Gracefully shut down VM    (Running )'),
           TR(INPUT(_name='testcase24', _type='checkbox', _value="24"),'Forcefully power off VM   (Running )'),
           TR(INPUT(_name='testcase25', _type='checkbox', _value="25"),'Attach Extra Disk to VM   (Running )'),
           TR(INPUT(_name='testcase57', _type='checkbox', _value="57"),'Migrate VM(Running)'),
           TR(INPUT(_name='testcase26', _type='checkbox', _value="26"),'Take VM snapshot   (Paused )'),
           TR(INPUT(_name='testcase27', _type='checkbox', _value="27"),'Migrate VM(Paused)'),
           TR(INPUT(_name='testcase28', _type='checkbox', _value="28"),'Unpause VM   (Paused )'),
           TR(INPUT(_name='testcase29', _type='checkbox', _value="29"),'Add User to VM  (Paused )'),
           TR(INPUT(_name='testcase30', _type='checkbox', _value="30"),'Delete VM   (Paused )'),
           TR(INPUT(_name='testcase31', _type='checkbox', _value="31"),'Adjust VM Resources Utilization   (Paused )'),
           TR(INPUT(_name='testcase32', _type='checkbox', _value="32"),'Forcefully power off VM   (Paused)'),
           TR(INPUT(_name='testcase33', _type='checkbox', _value="33"),'Delete Addtional User   (Paused )'), 
           TR(INPUT(_name='testcase47', _type='checkbox', _value="47"),'Revert Snapshot    (Paused )'),
           TR(INPUT(_name='testcase42', _type='checkbox', _value="42"),'Delete Snapshot    (Paused )'),
           TR(INPUT(_name='testcase34', _type='checkbox', _value="34"),'Edit VM Config   (Running )'),
           TR(INPUT(_name='testcase35', _type='checkbox', _value="35"),'Turn on VM   (Shutdown )'),
           TR(INPUT(_name='testcase36', _type='checkbox', _value="36"),'Add User to VM  (Shutdown)'),
           TR(INPUT(_name='testcase37', _type='checkbox', _value="37"),'Delete VM   (Shutdown )'),
           TR(INPUT(_name='testcase38', _type='checkbox', _value="38"),'Attach Extra Disk  (Shutdown )'),
           TR(INPUT(_name='testcase39', _type='checkbox', _value="39"),'Request Clone VM   (Shutdown )'),
            TR(INPUT(_name='testcase40', _type='checkbox', _value="40"),'Edit VM Config   (Shutdown )'),
           TR(INPUT(_name='testcase41', _type='checkbox', _value="41"),'Assign VNC   (Shutdown )'),
           TR(INPUT(_name='testcase58', _type='checkbox', _value="58"),'Migrate VM(Shutdown)'),
           TR(INPUT(_name='testcase43', _type='checkbox', _value="43"),'Take VM snapshot   (Shutdown )'),
            
            TR(INPUT(_name='testcase44', _type='checkbox', _value="44"),'Approve VM(Org-admin)'),
           TR(INPUT(_name='testcase45', _type='checkbox', _value="45"),'Reject VM(Org-admin)'), 
            TR(INPUT(_name='testcase60', _type='checkbox', _value="60"),'Approve VM(Faculty)'),
           TR(INPUT(_name='testcase61', _type='checkbox', _value="61"),'Reject VM(Faculty)'), 
               TR(INPUT(_name='testcase62', _type='checkbox', _value="62"),'Approve VM(Admin)'),
           TR(INPUT(_name='testcase63', _type='checkbox', _value="63"),'Reject VM(Admin)'), 
           TR(INPUT(_name='testcase48', _type='checkbox', _value="48"),'Sanity Table'),
           
           BR(),
           TR(INPUT(_type='submit',_value='submit'))
          )
      )
    if form.process().accepted:
        for i in range(1,70):
            test_case_no=request.vars['testcase'+str(i)]
            if test_case_no!=None:
                
                print test_case_no
                if test_case_no=="65":
                    for j in range(1,65):
                        test_case_no=str(j)
                        test_script(test_case_no)
                else:
                    test_script(test_case_no)
        
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    

def index():
    try:
        import commands
        form = FORM( TABLE
                  (  TR(INPUT(_name='testcase1', _type='radio', _value="1"),'Unit Testing'),
                     TR(INPUT(_name='testcase2', _type='radio', _value="2"),'Integration Testing'),
                     TR(INPUT(_name='testcase3', _type='radio', _value="3"),'Stress Testing'),
                     TR(INPUT(_name='testcase4', _type='radio', _value="4"),'Network Testing'),
                     BR(),
                     TR(INPUT(_type='submit',_value='submit'))
                  )
                )        
        if form.process().accepted:
            if request.vars['testcase1']!=None:
                redirect(URL('unit_testing'))
            if request.vars['testcase2']!=None:
                redirect(URL('integration_testing')) 
            if request.vars['testcase3']!=None:
                redirect(URL('stress_testing'))  
            if request.vars['testcase4']!=None:
                redirect(URL('network_testing'))        
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
        return dict(form=form)
    except Exception as e:
        print e


def network_testing():
   
    import commands
    form = FORM(TABLE
             (   
              
    TR(INPUT(_name='testcase79', _type='checkbox', _value="134"),'Packages Install on Host '),
   
     TR(INPUT(_name='testcase78', _type='checkbox', _value="135"),'Packages Install on Baadal '),
    
    TR(INPUT(_name='testcase80', _type='checkbox', _value="80"),'VM status on Host '),
    BR(),
    TR(INPUT(_type='submit',_value='submit'))
            )
            )
    if form.process().accepted:
        if request.vars['testcase78']!=None:
            packages_install_test(134)
        if request.vars['testcase79']!=None:
            packages_install_host(135) 
        if request.vars['testcase80']!=None:
            check_stat_on_host()    
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    
    
def stress_testing(): 

    import commands
    form = FORM(  TABLE
        (   TR(INPUT(_name='testcase0', _type='checkbox', _value="0"),'All'), 
            BR(),
            TR(INPUT(_type='submit',_value='submit'))
        )
        )
              
    if form.process().accepted:
        test_case_no=request.vars['testcase0']
        if test_case_no!=None:
            stress_test_script()
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
    
   
def integration_testing(): 
    import commands
    form = FORM(  TABLE
                  (    TR(INPUT(_name='testcase130', _type='checkbox', _value="130"),'VM Performance(Memory)'),
                       TR(INPUT(_name='testcase131', _type='checkbox', _value="131"),'VM Performance(CPU)'),
                       TR(INPUT(_name='testcase132', _type='checkbox', _value="132"),'VM Performance(Network)'),
                       TR(INPUT(_name='testcase133', _type='checkbox', _value="133"),'VM Performance(Disk)'),
                        TR(INPUT(_name='testcase126', _type='checkbox', _value="126"),'VM Performance   (Shutdown )'),
                    
                    TR(INPUT(_name='testcase72', _type='checkbox', _value="72"),'User Request VM(Approved by Faculty,org-admin,admin)'),
                     TR(INPUT(_name='testcase73', _type='checkbox', _value="73"),'User Request VM(Approved by Faculty and Rejected by org-admin)'),
                      TR(INPUT(_name='testcase74', _type='checkbox', _value="74"),'User Request VM(Approved by Faculty,org-admin and Rejected by admin)'),
                      TR(INPUT(_name='testcase75', _type='checkbox', _value="76"),'User Request VM(Rejected by Faculty )'),
                    TR(INPUT(_name='testcase76', _type='checkbox', _value="76"),'Faculty Request VM(Rejected by org-admin)'),
                    TR(INPUT(_name='testcase77', _type='checkbox', _value="77"),'Faculty Request VM(Approved by org-admin  and Rejected by admin)'),
                    TR(INPUT(_name='testcase78', _type='checkbox', _value="78"),'Faculty Request VM(Approved by org-admin, admin)'),
                    
                    
                   
                    
                    
                  
                    
                    
                    TR(INPUT(_name='testcase79', _type='checkbox', _value="79"),'Take VM snapshot    (Running )'),
                    TR(INPUT(_name='testcase80', _type='checkbox', _value="80"),'Pause VM   (Running )'),
                   TR(INPUT(_name='testcase81', _type='checkbox', _value="81"),'Add User to VM   (Running )'),
                   TR(INPUT(_name='testcase82', _type='checkbox', _value="82"),'Delete VM    (Running)'),
                   TR(INPUT(_name='testcase83', _type='checkbox', _value="83"),'Gracefully shut down VM    (Running )'),
                   TR(INPUT(_name='testcase84', _type='checkbox', _value="84"),'Forcefully power off VM   (Running )'),
                    TR(INPUT(_name='testcase86', _type='checkbox', _value="86") ,'Migrate VM   (Running )'),
                      TR(INPUT(_name='testcase88', _type='checkbox', _value="88"),'Take VM snapshot   (Paused )'),
                      TR(INPUT(_name='testcase89', _type='checkbox', _value="89"),'Unpause VM   (Paused )'),
                      TR(INPUT(_name='testcase90', _type='checkbox', _value="90"),'Add User to VM  (Paused )'),
                      TR(INPUT(_name='testcase91', _type='checkbox', _value="91"),'Delete VM   (Paused )'),
                      TR(INPUT(_name='testcase92', _type='checkbox', _value="92"),'Forcefully power off VM   (Paused)'),
                     TR(INPUT(_name='testcase93', _type='checkbox', _value="93"),'Migrate VM   (Paused )'),
                      TR(INPUT(_name='testcase94', _type='checkbox', _value="94"),'Delete Add User  (Paused )'),
                      TR(INPUT(_name='testcase95', _type='checkbox', _value="95"),'Revert Snapshot  (Paused )'),
                      TR(INPUT(_name='testcase96', _type='checkbox', _value="96"),'Delete snapshot   (Paused )'),
                      TR(INPUT(_name='testcase97', _type='checkbox', _value="97"),'Turn on VM   (Shutdown )'),
                      TR(INPUT(_name='testcase98', _type='checkbox', _value="98"),'Add User to VM  (Shutdown)'),
                      TR(INPUT(_name='testcase99', _type='checkbox', _value="99"),'Delete VM   (Shutdown )'),

                       TR(INPUT(_name='testcase103', _type='checkbox', _value="103"),'Take VM snapshot   (Shutdown )'),
                       TR(INPUT(_name='testcase104', _type='checkbox', _value="104"),'Migrate VM   (Shutdown )'),
                        TR(INPUT(_name='testcase107', _type='checkbox', _value="107"),'User Request Attach Disk(Approved by Faculty,org-admin,admin)'),
                        TR(INPUT(_name='testcase70', _type='checkbox', _value="70"),'Org-Admin Request VM(Approved by admin)'),
                    TR(INPUT(_name='testcase71', _type='checkbox', _value="71"), 'Org-Admin Request VM(Rejected by admin)'),
                     TR(INPUT(_name='testcase109', _type='checkbox', _value="109"),'User Request Attach Disk(Approved by Faculty and Rejected by org-admin)'),
                      TR(INPUT(_name='testcase108', _type='checkbox', _value="108"),'User Request Attach Disk(Approved by Faculty,org-admin and Rejected by admin)'),
                       TR(INPUT(_name='testcase110', _type='checkbox', _value="110"),'User Request Attach Disk(Rejected by Faculty )'),
                       
                      TR(INPUT(_name='testcase105', _type='checkbox', _value="105"),'Org-Admin  Attach Disk(Approved by admin)'),
                    TR(INPUT(_name='testcase106', _type='checkbox', _value="106"), 'Org-Admin Attach Disk(Rejected by admin)'),
                    
                     TR(INPUT(_name='testcase85', _type='checkbox', _value="85"),'Faculty Request Attach Disk(Rejected by org-admin)'),
                    TR(INPUT(_name='testcase87', _type='checkbox', _value="87"),'Faculty Request Attach Disk(Approved by org-admin  and Rejected by admin)'),
                   TR(INPUT(_name='testcase100', _type='checkbox', _value="100"),'Faculty Request Attach Disk(Approved by org-admin, admin)'),
                    TR(INPUT(_name='testcase101', _type='checkbox', _value="101"),'User Request Clone VM(Approved by Faculty,org-admin,admin)'),
                   TR(INPUT(_name='testcase102', _type='checkbox', _value="102"),'User Request Clone VM(Approved by Faculty and Rejected by org-admin)'),
                      TR(INPUT(_name='testcase111', _type='checkbox', _value="111"),'User Request Clone VM(Approved by Faculty,org-admin and Rejected by admin)'),
                      TR(INPUT(_name='testcase112', _type='checkbox', _value="112"),'User Request Clone VM(Rejected by Faculty )'),
                    TR(INPUT(_name='testcase113', _type='checkbox', _value="113"),'Faculty Request Clone VM(Rejected by org-admin)'),
                    TR(INPUT(_name='testcase114', _type='checkbox', _value="114"),'Faculty Request Clone VM(Approved by org-admin  and Rejected by admin)'),
                    TR(INPUT(_name='testcase115', _type='checkbox', _value="115"),'Faculty Request Clone VM(Approved by org-admin, admin)'),
                     TR(INPUT(_name='testcase116', _type='checkbox', _value="116"),'Org-Admin  Request Clone VM(Approved by admin)'),
                    TR(INPUT(_name='testcase117', _type='checkbox', _value="117"), 'Org-Admin Request Clone VM(Rejected by admin)'),
                    
                     TR(INPUT(_name='testcase118', _type='checkbox', _value="118"),'User Request Clone VM(Approved by Faculty,org-admin,admin)'),
                   TR(INPUT(_name='testcase119', _type='checkbox', _value="119"),'User Request Clone VM(Approved by Faculty and Rejected by org-admin)'),
                      TR(INPUT(_name='testcase120', _type='checkbox', _value="120"),'User Request Clone VM(Approved by Faculty,org-admin and Rejected by admin)'),
                      TR(INPUT(_name='testcase121', _type='checkbox', _value="121"),'User Request Edit VM Config(Rejected by Faculty )'),
                    TR(INPUT(_name='testcase122', _type='checkbox', _value="122"),'Faculty Request Clone VM(Rejected by org-admin)'),
                    TR(INPUT(_name='testcase123', _type='checkbox', _value="123"),'Faculty Request Clone VM(Approved by org-admin  and Rejected by admin)'),
                    TR(INPUT(_name='testcase124', _type='checkbox', _value="124"),'Faculty Request Clone VM(Approved by org-admin, admin)'),
                     TR(INPUT(_name='testcase125', _type='checkbox', _value="125"),'Org-Admin  Request Clone VM(Approved by admin)'),
                    TR(INPUT(_name='testcase126', _type='checkbox', _value="136"), 'Org-Admin Request Clone VM(Rejected by admin)'),
                       
                       TR(INPUT(_name='testcase', _type='checkbox', _value=""),'Configure Template'),
                       TR(INPUT(_name='testcase', _type='checkbox', _value=""),'Configure Host'),
                        TR(INPUT(_name='testcase', _type='checkbox', _value=""),'Configure Datastore'),
                      
                      
                      BR(),
                      TR(INPUT(_type='submit',_value='submit'))
            )
     )
    if form.process().accepted:
        for i in range(67,135):
            test_case_no=request.vars['testcase'+str(i)]
            if i<=129:
                if test_case_no!=None:
                    test_script(test_case_no)
            else :
                if test_case_no!=None:
                    graph_test(test_case_no)
            
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)
