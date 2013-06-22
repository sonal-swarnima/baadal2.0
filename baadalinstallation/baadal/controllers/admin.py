# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global request; request = gluon.globals.Request
    global response; request = gluon.globals.Response
    global session; session = gluon.globals.Session()
    global db; db = gluon.sql.DAL()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################


def list_all_vm():
    vm_list = get_all_vm_list()
    return dict(vmlist=vm_list)


def add_template():

    form = get_add_template_form()
    
    if form.accepts(request.vars, session):
        logger.debug('New Template Created')
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)


def host_details():

    hosts = db(db.host.id >= 0).select()
    results = []
    for host in hosts:
        results.append({'ip':host.host_ip, 'id':host.id, 'name':host.host_name, 'status':host.status})

    return dict(hosts=results)

def add_host():
    form = get_add_host_form()

    if form.accepts(request.vars, session):
        db(db.host.id == form.vars.id).update(status=HOST_STATUS_DOWN)  # @UndefinedVariable
        logger.debug('New Host Added')
        response.flash = 'New Host Added'
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)
    
def add_datastore():

    form = get_add_datastore_form()

    if form.accepts(request.vars, session):
        logger.debug('New datastore added')
        redirect(URL(c='default', f='index'))
    elif form.errors:
        logger.error('Error in form')
    return dict(form=form)
