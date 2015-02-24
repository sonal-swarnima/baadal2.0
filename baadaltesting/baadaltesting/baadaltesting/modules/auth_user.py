# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from applications.new_baadal_testing.models import *  # @UnusedWildImport
###################################################################################
from gluon import current
import os
import logging
import logging.config
from gluon.tools import Auth, Service, PluginManager

AUTH_TYPE_LDAP = 'ldap'
AUTH_TYPE_DB = 'db'


def get_context_path():
    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/baadalapp.cfg'))
    return config

config = get_config_file()

def register_callback(form):
    add_membership_db(current.auth.user.id, current.USER, True)

def login_callback(form):
    if current.auth.is_logged_in():
        member = current.db(current.db.user_membership.user_id == current.auth.user.id).select().first()
        if not member:
            roles = fetch_user_role(current.auth.user.username)
            for role in roles:
                add_membership_db(current.auth.user.id, role, True)


def fetch_user_role(username):

    _role_list = [current.USER]
    username_qt = '\'' + username +'\''
    
    if username_qt in config.get("GENERAL_CONF","admin_uid"):
        _role_list.append(current.ADMIN)
    if username_qt in config.get("GENERAL_CONF","orgadmin_uid"):
        _role_list.append(current.ORGADMIN)
    if username_qt in config.get("GENERAL_CONF","faculty_uid"):
        _role_list.append(current.FACULTY)
            
    return _role_list    

def login_ldap_callback(form):
    print "inside login ldap callback"
    if current.auth.is_logged_in():
        user_name = current.auth.user.username
        print user_name
        if current.db.user(username = user_name)['last_name'] == "":
            user_info = fetch_ldap_user(user_name)
            if user_info:
                create_or_update_user(user_info, True)
            else:
                logger.error('Unable To Update User Info!!!')

def fetch_ldap_user(username):
    print "inside fetch_ldap_user"
    ldap_url = config.get("LDAP_CONF","ldap_url")
    base_dn = config.get("LDAP_CONF","ldap_dn")
    print ldap_url
    print base_dn
    import ldap
    try:
        l = ldap.open(ldap_url)
        l.protocol_version = ldap.VERSION3    
    except ldap.LDAPError, e:
        logger.error(e)
        return None

    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = None
    searchFilter = "uid="+username
    user_info={'user_name':username}
    user_info['email'] = None
    user_info['last_name'] = ''

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
                                user_info['first_name'] = name_lst[0]
                                if len(name_lst) == 2:
                                    user_info['last_name'] = name_lst[1]
                                elif len(name_lst) > 2:
                                    user_info['last_name'] = vals[0][vals[0].index(' '):].lstrip()
        user_info['email'] = username + config.get("MAIL_CONF", "email_domain")                                    
    except ldap.LDAPError, e:
        logger.error(e)
    if 'first_name' in user_info:
        return user_info
    else: 
        return None

#This method is called only when user logs in for the first time or when faculty name is verified on 'request VM' screen
def create_or_update_user(user_info, update_session):

    user_name = user_info['user_name']
    user = current.db(current.db.user.username == user_name).select().first()
    
    if not user:
        #create user
        user = current.db.user.insert(username=user_name, registration_id=user_name)   
    current.db(current.db.user.username==user_name).update(first_name = user_info['first_name'], 
                                                           last_name = user_info['last_name'], 
                                                           email = user_info['email'])


def add_or_update_user_memberships(user_id, roles, update_session):

    current_roles = current.db((user_id == current.db.user_membership.user_id) 
                               & (current.db.user_membership.group_id == current.db.user_group.id)).select(current.db.user_group.role).as_list()

    logger.info("users current roles: %s", current_roles)
    if current_roles != roles:
        current.db(current.db.user_membership.user_id == user_id).delete()
        for role in roles:
            add_membership_db(user_id, role, update_session)


def add_membership_db(_user_id, role, update_session):
    #Find the group_id for the given role
    _group_id = current.db.user_group(role=role)['id']
    if _group_id !=0:
        current.db.user_membership.insert(user_id=_user_id,group_id=_group_id)
        if update_session:
            # add role to the current session
            current.auth.user_groups[long(_group_id)] = role

def is_auth_type_db():

    auth_type = config.get("AUTH_CONF","auth_type")
    return (auth_type == AUTH_TYPE_DB)
    
