# -*- coding: utf-8 -*-
###################################################################################

import os
import re
from gluon import current
from gluon.validators import Validator

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
    config.read(os.path.join(get_context_path(), 'static/baadalapp.cfg'));
    return config

def get_context_path():

    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_datetime():
    import datetime
    return datetime.datetime.now()


def get_constant(constant_name):
    constant = current.db(current.db.constants.name == constant_name).select().first()['value']
    return constant

def update_value(constant_name, constant_value):
    current.db(current.db.constants.name == constant_name).update(value = constant_value)
    return 

def get_fullname(user_id):
    user = current.db.user[user_id]
    if user :
        return user.first_name + ' ' + user.last_name
        
def get_email(user_id):
    user = current.db.user[user_id]
    if user:
        return user.email
    
def is_valid_ipv4(value):
    regex = re.compile(
        '^(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])$')
    return regex.match(value)

def validate_ip_range(ipFrom, ipTo):
    
    if is_valid_ipv4(ipFrom) and is_valid_ipv4(ipTo):
        ip1 = ipFrom.split('.')
        ip2 = ipTo.split('.')
        if ip1[0] == ip2[0] and ip1[1] == ip2[1] and ip1[2] == ip2[2] and int(ip1[3]) < int(ip2[3]):
            return True

    return False
    
class IS_MAC_ADDRESS(Validator):
    
    regex = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    
    def __init__(self, error_message='enter valid MAC address'):
        self.error_message = error_message

    def __call__(self, value):
        if self.regex.match(value):
            return (value, None)
        else:
            return (value, self.error_message)
