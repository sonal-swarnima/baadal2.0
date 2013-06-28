# -*- coding: utf-8 -*-

from gluon import current
from helper import get_config_file

def login_callback(form):
    if current.auth.is_logged_in():
        add_group_test()
    

def login_ldap_callback(form):
    if current.auth.is_logged_in():
        if current.db(current.db.user.username==current.auth.user.username).select(current.db.user.last_name)[0]['last_name'] == "": 
#             fetch_ldap_user()
            current.db(current.db.user.username==current.auth.user.username).update(first_name=str(current.auth.user.username),last_name='test',email=str(current.auth.user.username)+"@cse.iitd.ernet.in")

    
def add_group_test():
    member = current.db(current.db.user_membership.user_id==current.auth.user.id).select().first()
    if not member:
        admin_group_id = current.db(current.db.user_group.role=='admin').select(current.db.user_group.id).first()['id']
        current.db.user_membership.insert(user_id=current.auth.user.id,group_id=admin_group_id)
        current.auth.user_groups[long(admin_group_id)]='admin'


def fetch_ldap_user():
    config = get_config_file()
    ldap_url=config.get("LDAP_CONF","ldap_url")
    ldap_dn = config.get("LDAP_CONF","ldap_dn")

    import ldap
    l = ldap.initialize(ldap_url)
    l.bind_s("", "", ldap.AUTH_SIMPLE);

    for name,attrs in l.search_s(ldap_dn, ldap.SCOPE_SUBTREE,"uid="+name):
        for k,vals in attrs.items():
            print k
            print vals[0]
    l.unbind()
