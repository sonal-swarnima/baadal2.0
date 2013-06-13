# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.

if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global session; session = gluon.globals.Session()
    from vm_helper import get_create_vm_form,set_configuration_elem
    import logger
###################################################################################

def request_vm():

    form = get_create_vm_form()
    
    if form.accepts(request.vars, session, onvalidation=set_configuration_elem):
        set_configuration_elem(form)
        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)
