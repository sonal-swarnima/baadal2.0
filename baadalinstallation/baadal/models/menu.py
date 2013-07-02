# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import T,request,response
    import gluon
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import is_moderator,is_faculty

response.title = request.application
response.google_analytics_id = None

response.top_menu = [
    (T('About'), False, URL('default','index')),
    (T('Blog'), False, URL('default','index')),
    (T('Photos'), False, URL('default','index')),
    (T('Team Baadal'), False, URL('default','index')),
    (T('Contact'), False, URL('default','index'))
    ]
if auth.is_logged_in():
    response.user_menu = [
        (H2('USER MENU'),False,None),
        (T('Home'), False, URL('default','index')),
        (T('Request VM'), False, URL('user','request_vm')),
        (T('List My VMs'), False, URL('user','list_my_vm')),
        (T('Mail Admin'), False, URL('default','index')),
        (T('Report Bug'), False, URL('default','index'))
        ]
    
    if (is_moderator() | is_faculty()):
        response.faculty_menu = [
            (H2('FACULTY MENU'),False,None),
            (T('Pending Requests'), False, URL('default','index')),
            (T('Add User to VM'), False, URL('default','index'))
            ]
        
        if is_moderator():
            response.admin_menu = [
                (H2('ADMIN MENU'),False,None),
                (T('All VM''s'), False, URL('admin','list_all_vm')),
                (T('Host and VMs'), False, URL('admin','hosts_vms')),
                (T('Tasks'), False, URL('admin','task_list')),
                (T('Sanity Check'), False, URL('default','index')),
                (T('Emergency'), False, URL('default','index')),
                (T('Configure System'), False,dict(_href='#', _id='configure'),[
                    (T('Add Host'), False, URL('admin','add_host')),
                    (T('Add Disk'), False, URL('admin','add_disk')),
                    (T('Add Template'), False, URL('admin','add_template')),
                    (T('Add Datastore'), False, URL('admin','add_datastore')),
                    (T('Add ISO'), False, URL('admin','add_iso'))
                    ])
                ]
