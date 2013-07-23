# -*- coding: utf-8 -*-
###################################################################################

import os
from gluon import current  # @Reimport

def is_moderator():
    if current.ADMIN in current.auth.user_groups.values():
        return True
    return False    

def is_faculty():
    if current.FACULTY in current.auth.user_groups.values():
        return True
    return False 
    
def is_orgadmin():
    if current.ORGADMIN in current.auth.user_groups.values():
        return True
    return False        

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/config-db.cfg'));
    return config

def get_context_path():

    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_datetime():
    import datetime
    return datetime.datetime.now()


def get_vm_template_config():
    from xml.dom import minidom

    xmldoc = minidom.parse(os.path.join(get_context_path(), 'static/vm_template_config.xml'))
    return xmldoc

def get_constant(constant_name):
    constant = current.db(current.db.constants.name == constant_name).select().first()['value']
    return constant

def update_value(constant_name, constant_value):
    current.db(current.db.constants.name == constant_name).update(value = constant_value)
    return 

def get_fullname(_user_id):
    row = current.db(current.db.user.id==_user_id).select()
    if row :
        row=row.first()
        return row['first_name'] + ' ' + row['last_name']
        
def get_pending_approval_count():

    users_of_same_org = current.db(current.auth.user.organisation_id == current.db.user.organisation_id).select(current.db.user.id)

    return current.db((current.db.vm_data.status == current.VM_STATUS_VERIFIED)
            & (current.db.vm_data.requester_id.belongs(users_of_same_org))).count()
             

