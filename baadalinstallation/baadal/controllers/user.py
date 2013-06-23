# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global session; session = gluon.globals.Session()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

def request_vm():

    form = get_request_vm_form()
    
    if form.accepts(request.vars, session, onvalidation=set_configuration_elem):
        add_user_to_vm(form.vars.id)
        logger.debug('VM requested successfully')
        
        #TODO:Approve functionality to be implemented
        approve_vm_request(form.vars.id)
        redirect(URL(c='default', f='index'))
    return dict(form=form)


def list_my_vm():
    vm_list = get_my_vm_list()
    return dict(vmlist=vm_list)

