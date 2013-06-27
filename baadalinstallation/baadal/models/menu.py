# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    import gluon.languages.translator as T
    global request; request = gluon.globals.Request
    global response; request = gluon.globals.Response
    global session; session = gluon.globals.Session()
###################################################################################

response.title = request.application
response.google_analytics_id = None

response.top_menu = [
    (T('About'), False, URL('default','index')),
    (T('Blog'), False, URL('default','index')),
    (T('Photos'), False, URL('default','index')),
    (T('Team Baadal'), False, URL('default','index')),
    (T('Contact'), False, URL('default','index'))
    ]
if current.auth.is_logged_in():
    response.user_menu = [
        (H2('USER MENU'),False,URL('None','None')),
        (T('Home'), False, URL('default','index')),
        (T('Request VM'), False, URL('user','request_vm')),
        (T('List My VMs'), False, URL('user','list_my_vm')),
        (T('Pending Requests'), False, URL('default','index')),
        (T('Mail Admin'), False, URL('default','index')),
        (T('Report Bug'), False, URL('default','index'))
        ]
    
    if ('faculty' in current.auth.user_groups.values() or 'admin' in current.auth.user_groups.values()):
        response.faculty_menu = [
            (H2('FACULTY MENU'),False,URL('None','None')),
            (T('Add User to VM'), False, URL('default','index'))
            ]
        
        if ('admin' in current.auth.user_groups.values()):
            response.admin_menu = [
                (H2('ADMIN MENU'),False,URL('None','None')),
                (T('All VM''s'), False, URL('admin','list_all_vm')),
                (T('Host and VMs'), False, URL('default','index')),
                (T('Tasks'), False, URL('default','index')),
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
