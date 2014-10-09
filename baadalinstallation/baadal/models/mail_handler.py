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
                    "1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nDefault credentials for VM:\nUsername:root/baadalservervm/baadaldesktopvm\nPassword:baadal\n\n"\
                    "To access VM using assigned private IP; SSH to baadal gateway machine using your GCL credential.\n"\
                    "username@baadalgateway.cse.iitd.ernet.in\n"\
                    "For other details, Please login to baadal WEB interface.\n\nRegards,\nBaadal Admin"

TASK_COMPLETE_SUBJECT="{0[taskType]} task successful"

TASK_COMPLETE_BODY="Dear {0[userName]},\n\nThe '{0[taskType]}' task for VM({0[vmName]}) requested on {0[requestTime]} is complete."\
                    "\n\nRegards,\nBaadal Admin "

VNC_ACCESS_SUBJECT="VNC Access to your VM activated"

VNC_ACCESS_BODY="Dear {0[userName]},\n\nVNC Access to your VM {0[vmName]} was activated on {0[requestTime]}. Details follow:\n"\
                "1. VNC IP : {0[vncIP]}\n2. VNC Port : {0[vncPort]}\n\nVNC Access will be active for 30 minutes only.\n\n"\
                "For other details, Please login to baadal WEB interface.\n\nRegards,\nBaadal Admin"

BAADAL_SHUTDOWN_SUBJECT="VM Shutdown"

BAADAL_SHUTDOWN_BODY="Dear {0[userName]},\n\nIn view of planned server migration tomorrow, Baadal team will shutdown your VM {0[vmName]}({0[vmIp]}) at 3:00 PM.\n"\
             "Please save your work accordingly.\n\nVM will be brought up as soon as possible.\n\nRegards,\nBaadal Admin"

MAIL_FOOTER = "\n\n\nNOTE: Please do not reply to this email. It corresponds to an unmonitored mailbox. "\
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

    cc_addresses = []
    cc_addresses.append(config.get("MAIL_CONF","mail_admin_request"))
    for vm_user in vm_users:
        user_info = get_user_details(vm_user)
        if user_info[1] != None:
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
    vms = db(db.vm_data.status.belongs(VM_STATUS_RUNNING, VM_STATUS_PAUSED)).select()
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

