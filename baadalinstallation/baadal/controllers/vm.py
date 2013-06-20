# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.

if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global session; session = gluon.globals.Session()
    from vm_model import get_create_vm_form,set_configuration_elem,add_request_vm_queue
    import logger
###################################################################################

def request_vm():

    form = get_create_vm_form()
    
    if form.accepts(request.vars, session, onvalidation=set_configuration_elem):
        logger.debug('VM requested successfully')
        add_request_vm_queue(form.vars.id)
        redirect(URL(c='default', f='index'))
    return dict(form=form)

