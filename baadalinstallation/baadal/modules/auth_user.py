# -*- coding: utf-8 -*-
###################################################################################
from gluon import current
from helper import config, logger

AUTH_TYPE_LDAP = 'ldap'
AUTH_TYPE_DB = 'db'

def register_callback(form):
    add_membership_db(current.auth.user.id, current.USER, True)
    
    
def login_callback(form):
    if current.auth.is_logged_in():
        member = current.db(current.db.user_membership.user_id == current.auth.user.id).select().first()
        if not member:
            roles = fetch_user_role(current.auth.user.username)
            for role in roles:
                add_membership_db(current.auth.user.id, role, True)
    

def login_ldap_callback(form):
    if current.auth.is_logged_in():
        user_name = current.auth.user.username
        if current.db.user(username = user_name)['last_name'] == "":
            user_info = fetch_ldap_user(user_name)
            if user_info:
                create_or_update_user(user_info, True)
            else:
                logger.error('Unable To Update User Info!!!')

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

def fetch_ldap_user(username):
    ldap_url = config.get("LDAP_CONF","ldap_url")
    base_dn = config.get("LDAP_CONF","ldap_dn")

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
#                             if k == 'altEmail':
#                                 if vals[0] != 'none':
#                                     user_info['email'] = vals[0]
 
#TODO: find role and organisation from ldap and set in db accordingly (current iitd ldap does not support this feature entirely) 
        user_info['email'] = username + config.get("MAIL_CONF", "email_domain")                                    
        user_info['roles'] = fetch_user_role(username)
        # If user has super admin rights; it is added to separate organization
        if current.ADMIN in user_info['roles']:
            user_info['organisation'] = 'ADMIN'
        else:
            user_info['organisation'] = 'IITD'

    except ldap.LDAPError, e:
        logger.error(e)

    logger.info(user_info)
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
    
    org_id = current.db(current.db.organisation.name == user_info['organisation']).select(current.db.organisation.id).first()   
    current.db(current.db.user.username==user_name).update(first_name = user_info['first_name'], 
                                                           last_name = user_info['last_name'], 
                                                           email = user_info['email'], 
                                                           organisation_id = org_id)
    if update_session:
        current.auth.user.organisation_id = org_id.id
                                                     
    add_or_update_user_memberships(user.id, user_info['roles'], update_session)


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
    
