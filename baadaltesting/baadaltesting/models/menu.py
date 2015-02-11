# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import T,request,response,URL,H2
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.google_analytics_id = None

if auth.is_logged_in():
    response.main_menu = [
        (H2('MAIN MENU'),False, dict(_href='#', _id='menu')),
        (T('Task'), False, URL('default','task_list')),
        (T('Testing'), False, URL('default','testing'))
        ]
