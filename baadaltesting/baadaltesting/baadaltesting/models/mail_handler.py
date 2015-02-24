# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global mail; mail = gluon.tools.Mail()
    from applications.new_baadal_testing.models import *  # @UnusedWildImport
###################################################################################
#from helper import config, logger
RUNNING_SUBJECT="Running state of testing scripts"
RUNNING_BODY="Your Testing Scripts are now Running"

QUEUED_SUBJECT="QUEUED our request"
QUEUED_BODY="Your testing request is queued"

COMPLETE_SUBJECT="Complete your request"
COMPLETE_BODY="all your testing request are complete successfully"


def push_email(email_id,email_subject, email_message, reply_to_address):
    logger.debug("inside push email ")
    if config.getboolean("MAIL_CONF","mail_active"):
        logger.debug("inside config")
        rtn = mail.send(to=email_id,subject=email_subject, message = email_message, reply_to=reply_to_address)
        logger.error("ERROR:: " + str(mail.error))
        logger.info("EMAIL STATUS:: " + str(rtn))


def send_email(email_id,email_subject, email_template):
    logger.debug("inside send email ")
    #context['adminEmail'] = config.get("MAIL_CONF","mail_admin_request")
    if email_id != None:
        #email_message = email_template.format(context)
    
        push_email(email_id,email_subject, email_template, [])


def send_email_to_testing_user(task_type, request_time,status,email_id):
    logger.debug("inside send email to testing user")
    status=str(status)
    logger.debug(status)
    cc_addresses = []
    if status == "RUNNING":
          logger.debug("inside running ")
          send_email(email_id,RUNNING_SUBJECT, RUNNING_BODY)
    if status == "QUEUED":
          logger.debug("inside queued ")
          send_email(email_id,QUEUED_SUBJECT, QUEUED_BODY) 
    if status == "COMPLETED":
          logger.debug("inside complete ")
          send_email(email_id,COMPLETE_SUBJECT, COMPLETE_BODY)
