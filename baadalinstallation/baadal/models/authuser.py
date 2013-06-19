# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global db; db = gluon.sql.DAL()
###################################################################################

def login_callback(form):
    if auth.is_logged_in():
        if db(db.user.username==auth.user.username).select(db.user.last_name)[0]['last_name'] == "": 
#TODO: fetch details from ldap/db depending on the auth type and enter in database
            db(db.user.username==auth.user.username).update(first_name='test',last_name='test')

