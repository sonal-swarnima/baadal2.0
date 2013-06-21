# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
###################################################################################

def get_add_template_form():
    
    form_fields = ['name','os_type','arch','hdd','hdfile']
    form_labels = {'name':'Name of Template','hdd':'Harddisk(GB)','os_type':'Operating System','arch':'Architecture', 'hdfile':'HD File'}

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