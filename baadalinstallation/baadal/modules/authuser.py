# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
#if 0:
#    from gluon import *  # @UnusedWildImport
#    import gluon
#    global auth; auth = gluon.tools.Auth()
#    global db; db = gluon.sql.DAL()
###################################################################################
from gluon import *

def login_callback(form):
    if current.auth.is_logged_in():
        if current.db(current.db.user.username==current.auth.user.username).select(current.db.user.last_name)[0]['last_name'] == "": 
#TODO: fetch details from ldap/db depending on the auth type and enter in database
            current.db(current.db.user.username==current.auth.user.username).update(first_name=str(current.auth.user.username),last_name='test',email=str(current.auth.user.username)+"@cse.iitd.ernet.in")

