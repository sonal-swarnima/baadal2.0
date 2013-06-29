# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global db; db = gluon.sql.DAL()
    from user_model import add_to_cost
###################################################################################
from helper import get_fullname

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
		hostip=gethostinfo_fromhostid(vm.host_id).host_ip        
		element = {'name':vm.vm_name,'ip':vm.vm_ip, 'owner':get_fullname(vm.user_id), 'ip':vm.vm_ip, 'hostip':hostip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
		vmlist.append(element)

	return vmlist

def get_all_vm_ofhost(hostid):
	vms = db((db.vm_data.status != (VM_STATUS_REQUESTED|VM_STATUS_APPROVED)) & (db.vm_data.host_id == hostid )).select()
	vmlist=[]
	for vm in vms:
		total_cost = add_to_cost(vm.vm_name)
		hostip=gethostinfo_fromhostid(vm.host_id).host_ip        
		element = {'name':vm.vm_name,'ip':vm.vm_ip, 'owner':get_fullname(vm.user_id), 'ip':vm.vm_ip, 'hostip':hostip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.current_run_level,'cost':total_cost}
		vmlist.append(element)

	return vmlist

def deleteuser_accesstovm(vmid,uid) :	
	db((db.user_vm_map.vm_id==vmid) & (db.user_vm_map.user_id==uid)).delete()		

def lockandunlockvm(flag) :
	#if flag == True lock the vm else unlock
	if flag == True :
		db(db.vm_data.id==vminfo.id).update(locked=True)
	else :
		 db(db.vm_data.id==vminfo.id).update(locked=False)

def check_moderator() :
	if not is_moderator() :
		response.flash="You don't have admin privileges"
		redirect_listvm() # @ user_models.py
def getallhosts() :
	return db().select(db.host.ALL) 

def getvm_groupbyhosts() :
		hosts = getallhosts()              
		hostvmlist=[]
		for host in hosts:    # for each host get all the vm's that runs on it and add them to list              			
			vmlist=get_all_vm_ofhost(host.id)
			hostvms={'hostIP':host.host_ip,'details':vmlist,'ram':host.RAM,'cpus':host.CPUs}
			hostvmlist.append(hostvms)	
		return (hostvmlist)
