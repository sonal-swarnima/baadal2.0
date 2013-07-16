# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import T,request,response
    import gluon
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import is_moderator,is_faculty,is_orgadmin,get_pending_req_count,get_pending_approval_count

response.title = request.application
response.google_analytics_id = None

response.top_menu = [
    (T('About'), False, URL('default','index')),
    (T('Blog'), False, URL('default','test')),
    (T('Photos'), False, URL('default','page_under_construction.html')),
    (T('Team Baadal'), False, URL('default','page_under_construction.html')),
    (T('Contact'), False, URL('default','page_under_construction.html'))
    ]
if auth.is_logged_in():
    response.user_menu = [
        (H2('USER MENU'),False,None),
        (T('Home'), False, URL('default','index')),
        (T('Request VM'), False, URL('user','request_vm')),
        (T('List My VMs'), False, URL('user','list_my_vm')),
        (T('Mail Admin'), False, URL('default','page_under_construction.html')),
        (T('My Tasks'), False, URL('default','page_under_construction.html')),
        (T('Report Bug'), False, URL('default','page_under_construction.html'))
        ]
    
    if (is_moderator() | is_faculty()):
        response.faculty_menu = [
            (H2('FACULTY MENU'),False,None),
            (T('Pending Requests {'+str(get_pending_req_count())+'} '), False, URL('default','page_under_construction.html')),
            (T('Add User to VM'), False, URL('default','page_under_construction.html'))
            ]
            
        if (is_moderator() | is_orgadmin()):
            response.orgadmin_menu = [
                (H2('ORG-ADMIN MENU'),False,None),
                (T('List All Org-Level VMs'), False, URL('orgadmin','list_all_orglevel_vm.html')),
                (T('Pending Org-Level VM Approvals {'+str(0)+'}'), False, URL('default','page_under_construction.html'))
                ]
        
            if is_moderator():
                response.admin_menu = [
                    (H2('ADMIN MENU'),False,None),
                    (T('All VM''s'), False, URL('admin','list_all_vm')),
                    (T('Approve VM''s'), False, URL('admin','pending_requests')),
                    (T('Host and VMs'), False, URL('admin','hosts_vms')),
                    (T('Tasks'), False, URL('admin','task_list')),
                    (T('Sanity Check'), False, URL('default','page_under_construction.html')),
                    (T('Emergency'), False, URL('default','page_under_construction.html')),
                    (T('Configure System'), False,dict(_href='#', _id='configure'),[
                        (T('Add Host'), False, URL('admin','host_details')),
                        (T('Add Disk'), False, URL('admin','add_disk')),
                        (T('Add Template'), False, URL('admin','add_template')),
                        (T('Add Datastore'), False, URL('admin','add_datastore'))
                        ])
                    ]
