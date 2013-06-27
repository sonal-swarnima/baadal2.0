# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    from common_model import *  # @UnusedWildImport
###################################################################################

def get_add_template_form():
    
    form_fields = ['name','os_type','arch','hdd','hdfile','type','datastore_id']
    form_labels = {'name':'Name of Template','hdd':'Harddisk(GB)','os_type':'Operating System','arch':'Architecture', 'hdfile':'HD File','type':'Template Type', 'datastore_id':'Datastore'}

    form =SQLFORM(db.template, fields = form_fields, labels = form_labels, submit_button='Add Template')
    return form

def get_add_host_form():
    form_fields = ['host_ip','host_name','mac_addr','HDD']
    form_labels = {'name':'Name of Template','hdd':'Harddisk(GB)','os_type':'Operating System','arch':'Architecture'}

    form =SQLFORM(db.host, fields = form_fields, labels = form_labels, submit_button='Add Host')
    return form
    
def get_add_datastore_form():
    form_fields = ['ds_name', 'ds_ip', 'capacity', 'username', 'password', 'path']
    form_labels = {'ds_name':'Name', 'ds_ip':'Mount IP', 'capacity':'Capacity (GB)', 'username':'Username', 'password':'Password', 'path':'Path'}

    form = SQLFORM(db.datastore, fields=form_fields, labels=form_labels, submit_button='Add Datastore')
    return form

def get_all_vm_list():

    vms = db(db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)).select()
    vmlist=[]
    for vm in vms:
        total_cost = add_to_cost(vm.vm_name)
        element = {'name':vm.vm_name,'ip':vm.vm_ip, 'owner':vm.user_id, 'ip':vm.vm_ip, 'hostip':'hostip','RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
        vmlist.append(element)

    return vmlist
