# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import request, session
    from applications.baadal.models import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import is_moderator

@check_faculty
def add_user_to_vm():
    return dict()

@check_faculty
@handle_exception
def pending_requests():
    pending_requests = get_pending_requests()
    return dict(pending_requests=pending_requests,is_moderator=is_moderator())
        
@check_faculty
@handle_exception
def approve_request():
    vm_id=request.args[0]
    verify_vm_owner(vm_id)  
    verify_vm_request(vm_id);
    session.flash = 'Request Approved'
    redirect(URL(c='faculty', f='pending_requests'))
    
@check_faculty
@handle_exception
def reject_request():
    vm_id=request.args[0]
    verify_vm_owner(vm_id)
    reject_vm_request(vm_id);
    session.flash = 'Request Rejected'
    redirect(URL(c='faculty', f='pending_requests'))

def verify_vm_owner(vm_id):
    vm_info = get_vm_info(vm_id)
    if vm_info != None:
        if is_moderator() or (vm_info.owner_id == auth.user.id):
            return
        
    session.flash="Not authorized"
    redirect(URL(c='default', f='index'))
    
