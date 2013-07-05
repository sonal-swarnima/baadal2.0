# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import logger
###################################################################################
from gluon import current
from helper import get_config_file

def login_callback(form):
    if current.auth.is_logged_in():
        add_group_test()
    

def login_ldap_callback(form):
    if current.auth.is_logged_in():
        if current.db(current.db.user.username==current.auth.user.username).select(current.db.user.last_name)[0]['last_name'] == "": 
            fetch_ldap_user(current.auth.user.username)

    
def add_group_test():
    member = current.db(current.db.user_membership.user_id==current.auth.user.id).select().first()
    if not member:
        add_membership_db('admin')


def fetch_ldap_user(username):
    config = get_config_file()
    ldap_url=config.get("LDAP_CONF","ldap_url")
    base_dn = config.get("LDAP_CONF","ldap_dn")

    import ldap
    try:
        l = ldap.open(ldap_url)
        l.protocol_version = ldap.VERSION3    
    except ldap.LDAPError, e:
        logger.error(e)

    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter="uid="+username
    _first_name=''
    _last_name=''
    _email=''
    is_faculty=False

    try:
        ldap_result_id = l.search(base_dn, searchScope, searchFilter, retrieveAttributes)
        while 1:
            result_type, result_data = l.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    for name,attrs in result_data:
                        for k,vals in attrs.items():
                            if k == 'cn':
                                name_lst = vals[0].split(' ')
                                _first_name = name_lst[0]
                                if len(name_lst) == 2:
                                    _last_name = name_lst[1]
                                else:
                                    _last_name = vals[0][vals[0].index(' '):].lstrip()
                            if k == 'altEmail':
                                _email=vals[0]
                            if k == 'category':
                                if vals[0] == 'faculty':
                                    is_faculty=True
    except ldap.LDAPError, e:
        logger.error(e)

    if(_first_name != ''):
        current.db(current.db.user.username==current.auth.user.username).update(
                                                                                first_name=_first_name,
                                                                                last_name=_last_name,
                                                                                email=_email)
        add_user_membership(is_faculty, config)
        
def add_user_membership(is_faculty, config):

    admin_users = config.get("GENERAL_CONF","admin_uid")
    if current.auth.user.username in admin_users:
        add_membership_db('admin')
    else:
        if is_faculty:
            add_membership_db('faculty')
        else:
            add_membership_db('user')

def add_membership_db(role):
    _group_id = current.db(current.db.user_group.role==role).select(current.db.user_group.id).first()['id']
    current.db.user_membership.insert(user_id=current.auth.user.id,group_id=_group_id)
    current.auth.user_groups[long(_group_id)]=role
