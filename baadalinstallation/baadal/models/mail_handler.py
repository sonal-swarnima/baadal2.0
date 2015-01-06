# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    import gluon
    global auth; auth = gluon.tools.Auth()
    global mail; mail = gluon.tools.Mail()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import config, logger, get_datetime
from datetime import timedelta

#Email templates and subject constants
REGISTRATION_SUCCESSFUL_SUBJECT = "Baadal Registration Successful"

REGISTRATION_SUCCESSFUL_BODY = "Dear {0[userName]},\n\n"\
    "Your account with username {0[loginName]} has been activated.\n\n"\
    "Welcome to Baadal!"
                                
REGISTRATION_DENIED_SUBJECT = "Baadal Registration Denied"

REGISTRATION_DENIED_BODY = "Dear {0[userName]},\n\n"\
    "Your registration to Baadal has been denied. "\
    "For any query, send an email to {0[supportMail]}"
                            
VM_REQUEST_SUBJECT = "VM request successful"

VM_REQUEST_BODY="Dear {0[userName]},\n\n"\
    "Your request for VM({0[vmName]}) creation has been successfully registered. "\
    "Please note that you will be getting a separate email on successful VM creation."
                    
APPROVAL_REMINDER_SUBJECT = "Request waiting for your approval"

APPROVAL_REMINDER_BODY = "Dear {0[approverName]},\n\n"\
    "{0[userName]} has made a '{0[requestType]}' request on {0[requestTime]}. "\
    "It is waiting for your approval."
                    
VM_CREATION_SUBJECT = "VM created successfully"

VM_CREATION_BODY="Dear {0[userName]},\n\n"\
    "The VM {0[vmName]} requested on {0[requestTime]} is "\
    "successfully created and is now available for use. Following operations are allowed on the VM:\n"\
    "1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\n"\
    "Default credentials for VM is as follows:\nUsername:root/baadalservervm/baadaldesktopvm\nPassword:baadal\n\n"\
    "To access VM using assigned private IP; SSH to baadal gateway machine using your GCL credential.\n"\
    "username@{0[gatewayVM]}\n"\
    "For other details, Please login to baadal WEB interface."

TASK_COMPLETE_SUBJECT="{0[taskType]} task successful"

TASK_COMPLETE_BODY="Dear {0[userName]},\n\n"\
    "The '{0[taskType]}' task for VM({0[vmName]}) requested on {0[requestTime]} is complete."

VNC_ACCESS_SUBJECT="VNC Access to your VM activated"

VNC_ACCESS_BODY="Dear {0[userName]},\n\n"\
    "VNC Access to your VM {0[vmName]} was activated on {0[requestTime]}. Details follow:\n"\
    "1. VNC IP : {0[vncIP]}\n2. VNC Port : {0[vncPort]}\n\nVNC Access will be active for 30 minutes only.\n\n"\
    "For other details, Please login to baadal WEB interface."

DELETE_WARNING_SUBJECT="Delete Warning to the Shutdown VM" 

DELETE_WARNING_BODY="Dear {0[userName]},\n\n"\
    "It has been noticed that your VM {0[vmName]} is being shutdown from {0[vmShutdownDate]}.\n"\
    "Kindly use the VM/delete the VM if not required. \n" \
    "If no action is taken on the VM, the VM will be automatically deleted on {0[vmDeleteDate]}. \n\n"\
    "For other details, Please login to baadal WEB interface." 

BAADAL_SHUTDOWN_SUBJECT="VM Shutdown notice"

BAADAL_SHUTDOWN_BODY="Dear {0[userName]},\n\n"\
    "Baadal services will be shutting down tomorrow at 3:00 PM for planned maintenance."\
    "We will shutdown your VM {0[vmName]}({0[vmIp]}) to avoid any corruption of data.\n"\
    "Please save your work accordingly.\n\nVM will be brought up as soon as possible."

MAIL_FOOTER = "\n\nRegards,\nBaadal Admin\n\n\n"\
    "NOTE: Please do not reply to this email. It corresponds to an unmonitored mailbox. "\
    "If you have any queries, send an email to {0[adminEmail]}."

def push_email(to_address, email_subject, email_message, reply_to_address, cc_addresses=[]):
    if config.getboolean("MAIL_CONF","mail_active"):
        logger.debug("Sending mail to %s with subject %s" %(to_address, email_subject))
        rtn = mail.send(to=to_address, subject=email_subject, message = email_message, reply_to=reply_to_address, cc=cc_addresses)
        logger.error("ERROR:: " + str(mail.error))
        logger.info("EMAIL STATUS:: " + str(rtn))


def send_email(to_address, email_subject, email_template, context, cc_addresses=[]):

    if to_address != None:
        email_template += MAIL_FOOTER
        context['adminEmail'] = config.get("MAIL_CONF","mail_admin_request")
        email_message = email_template.format(context)
        cc_addresses.append(config.get("MAIL_CONF","mail_sender"))
        push_email(to_address, email_subject, email_message, [], cc_addresses)


def send_email_to_approver(approver_id, requester_id, request_type, request_time):

    approver_info = get_user_details(approver_id)
    if approver_info[1] != None:
        requester_name = get_full_name(requester_id)
        context = dict(approverName = approver_info[0], 
                       userName = requester_name, 
                       requestType = request_type, 
                       requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
        send_email(approver_info[1], APPROVAL_REMINDER_SUBJECT, APPROVAL_REMINDER_BODY, context)


def send_email_to_requester(vm_name):

    user_info = get_user_details(auth.user.id)
    if user_info[1] != None:
        context = dict(vmName = vm_name, 
                       userName = user_info[0])
    
        send_email(user_info[1], VM_REQUEST_SUBJECT, VM_REQUEST_BODY, context)
    
def send_email_to_vm_user(task_type, vm_name, request_time, vm_users):

    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        if user_info[1] != None:
            context = dict(vmName = vm_name, 
                           userName = user_info[0],
                           taskType = task_type,
                           requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
            if task_type == VM_TASK_CREATE:
                context.update({'gatewayVM':config.get("GENERAL_CONF","gateway_vm")})
                send_email(user_info[1], VM_CREATION_SUBJECT, VM_CREATION_BODY, context)
            else:
                subject = TASK_COMPLETE_SUBJECT.format(dict(taskType=task_type))
                send_email(user_info[1], subject, TASK_COMPLETE_BODY, context)
        

def send_email_vnc_access_granted(vm_users, vnc_ip, vnc_port, vm_name, request_time):
    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        if user_info[1] != None:
            context = dict(vmName = vm_name, 
                           userName = user_info[0],
                           vncIP = vnc_ip,
                           vncPort = vnc_port,
                           requestTime=request_time.strftime("%A %d %B %Y %I:%M:%S %p"))
            send_email(user_info[1], VNC_ACCESS_SUBJECT, VNC_ACCESS_BODY, context)
    

""""Send VM delete warning mail to VM users"""
def send_email_delete_vm_warning(vm_users,vm_name,vm_shutdown_time):
    vm_delete_time= get_datetime() + timedelta(days=15)   
    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        if user_info[1] != None:
            context = dict(vmName = vm_name, 
                           userName = user_info[0],
                           vmShutdownDate=vm_shutdown_time,
                           vmDeleteDate=vm_delete_time)
            logger.debug("Inside send mail delete vm warning function:" +vm_name+ ", userName:" +user_info[0]+ ", vmShutdownDate:" + str(vm_shutdown_time) + ", vmDeleteDate:" + str(vm_delete_time))
        send_email(user_info[1],DELETE_WARNING_SUBJECT,DELETE_WARNING_BODY,context) 
        return vm_delete_time

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

def send_email_to_user_manual(email_subject, email_message, vm_id):
    vm_users = []
    context = dict(adminEmail = config.get("MAIL_CONF","mail_admin_request"))

    for user in db(db.user_vm_map.vm_id == vm_id).select(db.user_vm_map.user_id):
        vm_users.append(user['user_id'])
    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        if user_info[1] != None:
            logger.info("MAIL USER: User Name: "+ user_info[0])
            send_email(user_info[1], email_subject, email_message, context)

def send_email_on_successful_registration(user_id):
    user_info = get_user_details(user_id)
    if user_info[1] != None:
        context = dict(userName = user_info[0],
                        loginName = user_info[2])
        send_email(user_info[1], REGISTRATION_SUCCESSFUL_SUBJECT, REGISTRATION_SUCCESSFUL_BODY, context)
    
def send_email_on_registration_denied(user_id):
    user_info = get_user_details(user_id)
    if user_info[1] != None:
        context = dict(userName = user_info[0],
                        supportMail = config.get("MAIL_CONF","mail_admin_request"))
        send_email(user_info[1], REGISTRATION_DENIED_SUBJECT, REGISTRATION_DENIED_BODY, context)


def send_shutdown_email_to_all():
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_SUSPENDED)).select()
    for vm_data in vms:
        owner_info = get_user_details(vm_data.owner_id)
        context = dict(vmName = vm_data.vm_name,
                       userName = owner_info[0],
                       vmIp = vm_data.private_ip)
        
        cc_user_list = []
        for user in db(db.user_vm_map.vm_id == vm_data.id).select(db.user_vm_map.user_id):
            if user.user_id != vm_data.owner_id:
                user_info = get_user_details(user.user_id)
                cc_user_list.append(user_info[1])

        logger.info("Sending mail to:: " + str(owner_info[1]))
        send_email(owner_info[1], BAADAL_SHUTDOWN_SUBJECT, BAADAL_SHUTDOWN_BODY, context, cc_user_list)
        import time
        time.sleep(30)

