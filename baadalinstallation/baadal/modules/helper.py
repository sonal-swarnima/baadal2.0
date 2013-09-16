# -*- coding: utf-8 -*-
###################################################################################

import os
from gluon import current

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

def get_fullname(user_id):
    user = current.db.user[user_id]
    if user :
        return user.first_name + ' ' + user.last_name
        
def get_email(user_id):
    user = current.db.user[user_id]
    if user:
        return user.email

def send_email_for_vm_creation(requester_id, vm_name, vm_request_time):
    user_name = get_fullname(requester_id)
    user_email = get_email(requester_id)
    context = dict(userName=user_name, vmName=vm_name, vmRequestTime=vm_request_time)
    send_mail(user_email, current.VM_CREATION_SUBJECT, current.VM_CREATION_TEMPLATE, context, None)

def send_email_to_faculty(faculty_id, vm_name, sender_user_name, vm_request_time, faculty_info):
    config = get_config_file()
    if faculty_info:
        faculty_name = get_fullname(faculty_id)
        email_address = faculty_info.email
        context = dict(facultyName = faculty_name, vmName = vm_name, userName = sender_user_name, vmRequestTime=vm_request_time)
        noreply_email = config.get("MAIL_CONF","mail_noreply")
        send_mail(email_address, current.VM_APPROVAL_SUBJECT_FOR_FACULTY, current.VM_APPROVAL_TEMPLATE_FOR_FACULTY, context, noreply_email)

def send_mail(to_address, email_subject, email_template, context, reply_to_address):
    email_message = email_template.format(context)
    push_email(to_address, email_subject, email_message, reply_to_address)
    
def push_email(to_address, email_subject, email_message, reply_to_address):
    if not reply_to_address:
        current.mail.send(to=to_address, subject=email_subject, message = email_message)
    else:
        current.mail.send(to=to_address, subject=email_subject, message = email_message, reply_to=reply_to_address)

