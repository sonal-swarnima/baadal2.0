# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request,session
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

@check_orgadmin
@handle_exception
def list_all_orglevel_vm():
    vm_list = get_all_orglevel_vm_list()
    return dict(vmlist=vm_list)

        
@check_orgadmin
@handle_exception
def pending_approvals():
    pending_approvals = get_verified_requests()
    requests = get_segregated_requests(pending_approvals)

    return dict(install_requests = requests[0], 
                clone_requests = requests[1], 
                disk_requests = requests[2], 
                edit_requests= requests[3])
    
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
    vm_id=request.args[0]
    send_remind_faculty_email(vm_id)
    session.flash = 'Faculty Reminded'
    redirect(URL(c='faculty', f='pending_requests'))
