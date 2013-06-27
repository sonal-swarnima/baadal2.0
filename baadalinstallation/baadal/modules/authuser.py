# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    global db; db = gluon.sql.DAL()
###################################################################################
from gluon import current

def login_callback(form):
#TODO: fetch details from ldap/db depending on the auth type and enter in database    
    if current.auth.is_logged_in():
        if current.db(current.db.user.username==current.auth.user.username).select(current.db.user.last_name)[0]['last_name'] == "": 
            current.db(current.db.user.username==current.auth.user.username).update(first_name=str(current.auth.user.username),last_name='test',email=str(current.auth.user.username)+"@cse.iitd.ernet.in")

        member = current.db(current.db.user_membership.user_id==current.auth.user.id).select().first()
        if not member: 
            admin_group_id = current.db(current.db.user_group.role=='admin').select().first()
            current.db.user_membership.insert(user_id=current.auth.user.id,group_id=admin_group_id)
