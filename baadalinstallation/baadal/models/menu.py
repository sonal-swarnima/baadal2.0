# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import T,request,response,URL,H2
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import is_moderator,is_faculty,is_orgadmin

response.title = request.application
response.google_analytics_id = None

response.top_menu = [
    (T('About'), False, URL('default','index')),
    (T('Blog'), False, URL('default','page_under_construction')),
    (T('Photos'), False, URL('default','page_under_construction')),
    (T('Team Baadal'), False, URL('default','page_under_construction')),
    (T('Contact'), False, URL('default','page_under_construction'))
    ]
if auth.is_logged_in():
    response.user_menu = [
        (H2('USER MENU'),False,None),
        (T('Home'), False, URL('default','index')),
        (T('Request VM'), False, URL('user','request_vm')),
        (T('My VMs'), False, URL('user','list_my_vm')),
        (T('My Tasks'), False, URL('user','list_my_task')),
        (T('Mail Admin'), False, URL('default','page_under_construction')),
        (T('Report Bug'), False, URL('default','page_under_construction'))
        ]
    
    if (is_moderator() | is_faculty()):
        response.faculty_menu = [
            (H2('FACULTY MENU'),False,None),
            (T('Pending Requests {'+str(len(get_pending_requests()))+'} '), False, URL('faculty','pending_requests'))
            ]
            
        if (is_moderator() | is_orgadmin()):
            response.orgadmin_menu = [
                (H2('ORG-ADMIN MENU'),False,None),
                (T('List All Org-Level VMs'), False, URL('orgadmin','list_all_orglevel_vm')),
                (T('Pending Org-Level VM Approvals {'+str(0)+'}'), False, URL('orgadmin','pending_approvals'))
                ]
        
            if is_moderator():
                response.admin_menu = [
                    (H2('ADMIN MENU'),False,None),
                    (T('All VM''s'), False, URL('admin','list_all_vm')),
                    (T('Host and VMs'), False, URL('admin','hosts_vms')),
                    (T('Tasks'), False, URL('admin','task_list')),
                    (T('Sanity Check'), False, URL('default','page_under_construction')),
                    (T('Emergency'), False, URL('default','page_under_construction')),
                    (T('Configure System'), False,dict(_href='#', _id='configure'),[
                        (T('Add Host'), False, URL('admin','host_details')),
                        (T('Add Disk'), False, URL('default','page_under_construction')),
                        (T('Add Template'), False, URL('admin','add_template')),
                        (T('Add Datastore'), False, URL('admin','add_datastore'))
                        ])
                    ]
