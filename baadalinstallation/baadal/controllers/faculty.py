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

@check_faculty
@handle_exception
def pending_requests():
    pending_requests = get_pending_requests()
    requests = get_segregated_requests(pending_requests)

    return dict(install_requests = requests[0], 
                clone_requests = requests[1], 
                disk_requests = requests[2], 
                edit_requests= requests[3])
        
@check_faculty
@handle_exception
def approve_request():
    request_id=request.args[0]
    verify_vm_owner(request_id)  
    verify_vm_request(request_id);
    session.flash = 'Request Approved'
    redirect(URL(c='faculty', f='pending_requests'))
    
@check_faculty
@handle_exception
def reject_request():
    request_id=request.args[0]
    verify_vm_owner(request_id)
    reject_vm_request(request_id);
    session.flash = 'Request Rejected'
    redirect(URL(c='faculty', f='pending_requests'))

@check_faculty
@handle_exception
def edit_pending_request():
    
    if session.back:
        redirect_url = session.back
    else:
        redirect_url = URL()
    request_id=request.args[0]
    verify_vm_owner(request_id)

    form = get_edit_pending_request_form(request_id)
    if form.accepts(request.vars, session):
        session.flash = "Request is successfully edited."
        session.back = None
        redirect(redirect_url)
    elif not form.errors:
        session.back = request.env.http_referer

    return dict(form=form)

def verify_vm_owner(request_id):
    request_info = get_request_info(request_id)
    if request_info != None:
        if is_moderator() or (
            is_orgadmin() and request_info.owner_id.organisation_id == auth.user.organisation_id) or (
            request_info.owner_id == auth.user.id):
            return
        
    session.flash="Not authorized"
    redirect(URL(c='default', f='index'))
    
