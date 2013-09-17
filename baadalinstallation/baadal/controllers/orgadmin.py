# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import datetime

@check_orgadmin
@handle_exception
def list_all_orglevel_vm():
    vm_list = get_all_orglevel_vm_list()
    return dict(vmlist=vm_list)

        
@check_orgadmin
@handle_exception
def pending_approvals():
    pending_approvals = get_verified_vm_list()
    return dict(pending_approvals=pending_approvals)
    
@check_orgadmin
@handle_exception
def approve_request():
    vm_id=request.args[0] 
    approve_vm_request(vm_id);
    session.flash = 'Request approved.'
    redirect(URL(c='orgadmin', f='pending_approvals'))

@check_orgadmin
@handle_exception
def reject_request():
    vm_id=request.args[0]
    reject_vm_request(vm_id);
    session.flash = 'Request Rejected'
    redirect(URL(c='orgadmin', f='pending_approvals'))

@check_orgadmin
@handle_exception
def remind_faculty():
    vm_owner_id=request.args[0]
    vm_name = request.args[1]
    
    request_time = datetime.datetime.fromtimestamp(float(request.args[2])/1000.0).strftime("%A %d %B %Y %I:%M:%S %p")
    
    send_email_to_faculty(vm_owner_id, vm_name, request_time)
    session.flash = 'Faculty Reminded'
    redirect(URL(c='orgadmin', f='pending_approvals'))
