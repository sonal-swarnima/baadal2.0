# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global mail; auth = gluon.tools.Mail()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_fullname, get_config_file, get_email

config = get_config_file()

def send_email_for_vm_creation(requester_id, vm_name, vm_request_time):
    user_email = get_email(requester_id)
    context = dict(vmName=vm_name, vmRequestTime=vm_request_time)
    send_mail(user_email, VM_CREATION_SUBJECT, VM_CREATION_TEMPLATE, context, None)


def send_mail(to_address, email_subject, email_template, context, reply_to_address):
    
    context['userName'] = (auth.user.first_name + ' ' + auth.user.last_name) 
    email_message = email_template.format(context)
    push_email(to_address, email_subject, email_message, reply_to_address)
    
def push_email(to_address, email_subject, email_message, reply_to_address):
    if not reply_to_address:
        mail.send(to=to_address, subject=email_subject, message = email_message)
    else:
        mail.send(to=to_address, subject=email_subject, message = email_message, reply_to=reply_to_address)


def send_email_to_faculty(faculty_id, vm_name, vm_request_time):

    faculty_email = get_email(faculty_id)
    if faculty_email:
        faculty_name = get_fullname(faculty_id)
        context = dict(facultyName = faculty_name, vmName = vm_name, 
                       vmRequestTime=vm_request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
        noreply_email = config.get("MAIL_CONF","mail_noreply")
        send_mail(faculty_email, VM_APPROVAL_SUBJECT_FOR_FACULTY, VM_APPROVAL_TEMPLATE_FOR_FACULTY, context, noreply_email)


def send_email_to_user(vm_name):

    email_address = get_email(auth.user.id)
    context = dict(vmName = vm_name)
    noreply_email = config.get("MAIL_CONF","mail_noreply")
    send_mail(email_address, VM_REQUEST_SUBJECT_FOR_USER, VM_REQUEST_TEMPLATE_FOR_USER, context, noreply_email)
    

def send_email_to_admin(email_subject, email_message, email_type):
    if email_type == 'request':
        email_address = config.get("MAIL_CONF","mail_admin_bug_report")
    if email_type == 'report_bug':
        email_address = config.get("MAIL_CONF","mail_admin_request")
    if email_type == 'complaint':
        email_address = config.get("MAIL_CONF","mail_admin_complaint")
    user_email_address = get_email(auth.user.id)
    logger.info("MAIL ADMIN: type:"+email_type+", subject:"+email_subject+", message:"+email_message+", from:"+user_email_address)
    push_email(email_address, email_subject, email_message,user_email_address)

