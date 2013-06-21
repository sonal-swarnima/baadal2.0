# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global db; db = gluon.sql.DAL()
    global session; session = gluon.globals.Session()
###################################################################################
import os

def is_moderator():
    if 'admin' in auth.user_groups.values():
        return True
    return False    

def is_faculty():
    if 'faculty' in auth.user_groups.values():
        return True
    return False    

def get_fullname(_user_id):
    user  = db(db.user.id==_user_id).select()[0]
    return user.first_name + ' ' + user.last_name;

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/config-db.cfg'));
    return config

def get_vm_template_config():
    from xml.dom import minidom

    xmldoc = minidom.parse(os.path.join(get_context_path(), 'static/vm_template_config.xml'))
    return xmldoc
    
def get_context_path():

    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path
