# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global mail; mail = gluon.tools.Mail()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import config, logger

#Email templates and subject constants
REGISTRATION_SUCCESSFUL_SUBJECT = "Baadal Registration Successful"

REGISTRATION_SUCCESSFUL_BODY = "Dear {0[userName]},\n\nYour account with username {0[loginName]} has been activated."\
                                "\n\nWelcome to Baadal!\n\nRegards,\nBaadal Admin"
                                
REGISTRATION_DENIED_SUBJECT = "Baadal Registration Denied"

REGISTRATION_DENIED_BODY = "Dear {0[userName]},\n\nYour registration to Baadal has been denied. "\
                            "For any query, send an email to {0[supportMail]}\n\nRegards,\nBaadal Admin"
                            
VM_REQUEST_SUBJECT = "VM request successful"

VM_REQUEST_BODY="Dear {0[userName]},\n\nYour request for VM({0[vmName]}) creation has been successfully registered. "\
                    "Please note that you will be getting a separate email on successful VM creation.\n\nRegards,\nBaadal Admin"
                    
APPROVAL_REMINDER_SUBJECT = "Request waiting for your approval"

APPROVAL_REMINDER_BODY ="Dear {0[approverName]},\n\n{0[userName]} has made a '{0[requestType]}' request on {0[requestTime]}. "\
                            "It is waiting for your approval.\n\nRegards,\nBaadal Admin"
                    
VM_CREATION_SUBJECT = "VM created successfully"

VM_CREATION_BODY="Dear {0[userName]},\n\nThe VM {0[vmName]} requested on {0[requestTime]} is "\
                    "successfully created and is now available for use. The following operations are allowed on the VM:\n"\
                    "1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nDefault credentials for VM:\nUsername:root/baadalvm\nPassword:baadal\n\n"\
		    "For other details, Please login to baadal WEB interface.\n\nRegards,\nBaadal Admin"

TASK_COMPLETE_SUBJECT="{0[taskType]} task successful"

TASK_COMPLETE_BODY="Dear {0[userName]},\n\nThe '{0[taskType]}' task for VM({0[vmName]}) requested on {0[requestTime]} is complete."\
                    "\n\nRegards,\nBaadal Admin "

MAIL_FOOTER = "\n\n\nDisclaimer:: Please do not reply to this email. It corresponds to an unmonitored mailbox. "\
             "If you have any queries, send an email to {0[adminEmail]}."

def push_email(to_address, email_subject, email_message, reply_to_address, cc_addresses=[]):
    if config.getboolean("MAIL_CONF","mail_active"):
        rtn = mail.send(to=to_address, subject=email_subject, message = email_message, reply_to=reply_to_address, cc=cc_addresses)
        logger.error("ERROR:: " + str(mail.error))
        logger.info("EMAIL STATUS:: " + str(rtn))


def send_email(to_address, email_subject, email_template, context, cc_addresses=[]):

    email_template += MAIL_FOOTER
    context['adminEmail'] = config.get("MAIL_CONF","mail_admin_request")
    if to_address != None:
        email_message = email_template.format(context)
    
        push_email(to_address, email_subject, email_message, [], cc_addresses)


def send_email_to_approver(approver_id, requester_id, request_type, request_time):

    approver_info = get_user_details(approver_id)
    requester_name = get_full_name(requester_id)
    context = dict(approverName = approver_info[0], 
                   userName = requester_name, 
                   requestType = request_type, 
                   requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
    send_email(approver_info[1], APPROVAL_REMINDER_SUBJECT, APPROVAL_REMINDER_BODY, context)


def send_email_to_requester(vm_name):

    user_info = get_user_details(auth.user.id)
    context = dict(vmName = vm_name, 
                   userName = user_info[0])

    send_email(user_info[1], VM_REQUEST_SUBJECT, VM_REQUEST_BODY, context)
    
def send_email_to_vm_user(task_type, vm_name, request_time, vm_users):

    cc_addresses = []
    cc_addresses.append(config.get("MAIL_CONF","mail_admin_request"))
    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        context = dict(vmName = vm_name, 
                       userName = user_info[0],
                       taskType = task_type,
                       requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
        if task_type == TASK_TYPE_CREATE_VM:
            cc_addresses = []
            send_email(user_info[1], VM_CREATION_SUBJECT, VM_CREATION_BODY, context, cc_addresses)
        else:
            subject = TASK_COMPLETE_SUBJECT.format(dict(taskType=task_type))
            send_email(user_info[1], subject, TASK_COMPLETE_BODY, context, cc_addresses)
        

def send_email_to_admin(email_subject, email_message, email_type):
    if email_type == 'report_bug':
        email_address = config.get("MAIL_CONF","mail_admin_bug_report")
    if email_type == 'request':
        email_address = config.get("MAIL_CONF","mail_admin_request")
    if email_type == 'complaint':
        email_address = config.get("MAIL_CONF","mail_admin_complaint")
    user_email_address = auth.user.email
    logger.info("MAIL ADMIN: type:"+email_type+", subject:"+email_subject+", message:"+email_message+", from:"+user_email_address)
    push_email(email_address, email_subject, email_message, user_email_address)

def send_email_on_successful_registration(user_id):
    user_info = get_user_details(user_id)
    context = dict(userName = user_info[0],
                    loginName = user_info[2])
    send_email(user_info[1], REGISTRATION_SUCCESSFUL_SUBJECT, REGISTRATION_SUCCESSFUL_BODY, context)
    
def send_email_on_registration_denied(user_id):
    user_info = get_user_details(user_id)
    context = dict(userName = user_info[0],
                    supportMail = config.get("MAIL_CONF","mail_admin_request"))
    send_email(user_info[1], REGISTRATION_DENIED_SUBJECT, REGISTRATION_DENIED_BODY, context)
