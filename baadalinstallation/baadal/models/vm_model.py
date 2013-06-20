# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
from applications.baadal.modules.helper import get_vm_template_config
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################


def get_configuration_elem(form):
    
    xmldoc = get_vm_template_config()
    itemlist = xmldoc.getElementsByTagName('template')
    _id=0
    for item in itemlist:
        if item.attributes['default'].value != 'true':
            _id=item.attributes['id'].value
        select=SELECT(_name='configuration_'+str(_id))
        cfglist = item.getElementsByTagName('config')
        i=0
        for cfg in cfglist:
            select.insert(i,OPTION(cfg.attributes['display'].value,_value=cfg.attributes['value'].value))
            i+=1
        
        config_elem = TR(LABEL('Configuration:'),select,_id='config_row__'+str(_id))
        form[0].insert(2,config_elem)

def set_configuration_elem(form):

    configVal = form.vars.configuration_0
    template = form.vars.template_id
    
    if eval('form.vars.configuration_'+str(template)) != None:
        configVal = eval('form.vars.configuration_'+str(template))

    configVal = configVal.split(',')
    
    form.vars.vCPU = int(configVal[0])
    form.vars.RAM = int(configVal[1])*1024
    form.vars.HDD = int(configVal[2])
    return


def get_create_vm_form():
    
    form_fields = ['vm_name','template_id','HDD','purpose']
    form_labels = {'vm_name':'Name of VM','HDD':'Optional Additional Harddisk(GB)','template_id':'Template Image','purpose':'Purpose of this VM'}

    form =SQLFORM(db.vm_data, fields = form_fields, labels = form_labels)
    get_configuration_elem(form)
    return form

def add_request_vm_queue(_vm_id):
    
    db.task_queue.insert(task_type=TASK_TYPE_REQUEST_VM, vm_id=_vm_id, priority=TASK_QUEUE_PRIORITY_NORMAL, status=TASK_QUEUE_STATUS_PENDING)  # @UndefinedVariable
    