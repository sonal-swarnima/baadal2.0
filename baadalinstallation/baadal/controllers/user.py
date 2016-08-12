# -*- coding: utf-8 -*-
"""
user.py: This controller has functions that corresponds to the requested actions 
by users with role of 'user'.
"""
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import auth,request,session,response
    import gluon
    global auth; auth = gluon.tools.Auth()
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import config, get_file_stream, get_context_path
from log_handler import logger
from vm_utilization import check_graph_type, check_graph_period, \
    fetch_info_graph
import os


def request_object_store():
    form = get_request_object_store_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_object_store_validation):
        
        send_email_to_object_requester(form.vars.ob_name)
        if is_general_user():
            send_remind_faculty_email(form.vars.id)

        logger.debug('Object Store requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def request_vm():
    form = get_request_vm_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_vm_validation):
        
        send_email_to_requester(form.vars.vm_name)
        if is_general_user():
            send_remind_faculty_email(form.vars.id)

        logger.debug('VM requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def request_container():
    form = get_request_container_form()
    
    # After validation, read selected configuration and set RAM, CPU and HDD accordingly
    if form.accepts(request.vars, session, onvalidation=request_container_validation):
#         print "dfsklj"
        #send_email_to_requester(form.vars.vm_name)
        if is_general_user():
            #send_remind_faculty_email(form.vars.id)
            print "sdfklsd"
        logger.debug('Container requested successfully')
        redirect(URL(c='default', f='index'))
    return dict(form=form)

@auth.requires_login()
@handle_exception
def verify_faculty():

    username = request.vars['keywords']
    faculty_info = get_user_info(username, [FACULTY])
    if faculty_info != None:
        return faculty_info[1]

@auth.requires_login()
@handle_exception
def add_collaborator():

    username = request.vars['keywords']
    user_info = get_user_info(username)
    if user_info != None:
        return user_info[1]

@auth.requires_login()
@handle_exception
def list_my_vm():
    hosted_vm = get_my_hosted_vm()
    saved_templates = get_my_saved_templates()   
    return dict(hosted_vm = hosted_vm, saved_templates = saved_templates)

def list_my_object_store():
    my_object_store = get_my_object_store()
    return dict(my_object_store = my_object_store)


def list_my_container():
    my_container = get_my_container()
    return dict(my_container = my_container)

def download_sample_obect_program():
    file_name = 's3_object_key.txt'
    file_path = os.path.join(get_context_path(), 'private/Object_keys/' + file_name)
    logger.debug(file_path+"\n")
    response.headers['Content-Type'] = "text"
    response.headers['Content-Disposition']="attachment; filename=" +file_name
    try:
        return response.stream(get_file_stream(file_path),chunk_size=4096)
    except Exception:
        session.flash = "Unable to download your Keys."
    redirect(URL(r = request, c = 'user', f = 'list_my_object_store'))

@check_vm_owner
@handle_exception

def download_object_keys():
    #user_info=get_user_details()
    #user_name=user_info['username'].title()
    logger.debug(request.args[1])
#     if '_' in request.args[1]:
#         user_name,b=request.args[1].split('_', 1)
#     else:
#         user_name=request.args[1]
    object_store_name=request.args[0]
    logger.debug(object_store_name)
    file_name = object_store_name+'_key.txt'
    file_path = os.path.join(get_context_path(), 'private/Object_keys/' + file_name)
    logger.debug(file_path+"\n")
    response.headers['Content-Type'] = "text"
    response.headers['Content-Disposition']="attachment; filename=" +file_name
    try:
        return response.stream(get_file_stream(file_path),chunk_size=4096)
    except Exception:
        session.flash = "Unable to download your Keys."
    redirect(URL(r = request, c = 'user', f = 'list_my_object_store'))
   


def vpn():
    return dict()

def vpn_setup_guide():
    return dict()

@auth.requires_login()
@handle_exception
def request_user_vpn():
    var = request_vpn()
    logger.debug("request user vpn var value "+str(var))
    if var== 1 :
        session.flash = "Get your baadalVPN key's  tar file from the Download link given below "

    elif var == 2 :
        session.flash = "Unable to process  your Request. Please contact Baadal Team"
    else :
        session.flash = "You already have VPN files  you can  download it from  given link "
    redirect(URL(r = request, c = 'user', f = 'vpn'))


@auth.requires_login()
@handle_exception
def download_vpn_keys():
    user_info=get_vpn_user_details()
    logger.debug(type(user_info))
    user_name=user_info['username']
    logger.debug(user_name+"\n")
    file_name = user_name+'_baadalVPN.tar'
    file_path = os.path.join(get_context_path(), 'private/VPN/' + file_name)
    logger.debug(file_path+"\n")

    #import contenttype as c
    response.headers['Content-Type'] = "application/zip"
    #response.headers['ContentType'] ="application/octet-stream";
    response.headers['Content-Disposition']="attachment; filename=" +file_name
    logger.debug("******************************************************")
    try:
        return response.stream(get_file_stream(file_path),chunk_size=4096)

    except Exception:
        session.flash = "Unable to download your VPN files. Please Register first if you have not registered yet."
    redirect(URL(r = request, c = 'user', f = 'vpn'))


@check_vm_owner
@handle_exception
def settings():
    vm_id=request.args[0]
    vm_users = None
    vm_info = get_vm_config(vm_id)
    if not vm_info:
        redirect(URL(f='list_my_vm'))
    if not is_general_user():
        vm_users = get_vm_user_list(vm_id)
    
    vm_operations = get_vm_operations(vm_id)
    vm_snapshots = get_vm_snapshots(vm_id)
    
    return dict(vminfo = vm_info , vmoperations = vm_operations, vmsnapshots = vm_snapshots, vmusers = vm_users)     

@check_cont_owner
@handle_exception
def cont_settings():
    cont_id=request.args[0]
    cont_info = get_cont_config(cont_id)
    if not cont_info:
        redirect(URL(f='list_my_container'))
    
    cont_operations = get_cont_operations(cont_id)
    
    return dict(cont_info = cont_info , cont_operations = cont_operations)     


def get_vnc_url():
    vm_id=request.vars['vm_id']
    vnc_url=create_vnc_url(vm_id)
    return vnc_url
    

def handle_vm_operation(vm_id, task_type):

    if is_request_in_queue(vm_id, VM_TASK_DELETE):
        session.flash = "Delete request is in queue. No operation can be performed"
    elif is_request_in_queue(vm_id, task_type):
        session.flash = "%s request already in queue." %task_type
    else:
        add_vm_task_to_queue(vm_id,task_type)
        session.flash = '%s request added to queue.' %task_type
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

def handle_cont_operation(cont_id, task_type):

    add_cont_task_to_queue(cont_id,task_type)
    session.flash = '%s request added to queue.' %task_type
    redirect(URL(r = request, c = 'user', f = 'cont_settings', args = cont_id))

@check_cont_owner
@handle_exception
def container_logs():
    cont_id = request.args[0]
    cont_logs = get_container_logs(cont_id)
    return dict(cont_id = cont_id, cont_logs = cont_logs)

@check_cont_owner
@handle_exception
def container_stats():
    cont_id = request.args[0]
    cont_uuid = get_container_uuid(cont_id)
    cont_stats = get_container_stats(cont_uuid)
    return dict(cont_uuid = cont_uuid, cont_id = cont_id, cont_stats = cont_stats)

@check_cont_owner
@handle_exception
def container_top():
    cont_id = request.args[0]
    cont_top = get_container_top(cont_id)
    return dict(cont_id = cont_id, cont_top = cont_top)

@check_cont_owner
@handle_exception
def container_execute():
    cont_id = request.args[0]
    cont_uuid = get_container_uuid(cont_id)
    return dict(cont_uuid = cont_uuid, cont_id = cont_id)

@check_cont_owner
@handle_exception
def start_cont():
    handle_cont_operation(request.args[0], CONTAINER_START)

@check_cont_owner
@handle_exception
def pause_cont():
    handle_cont_operation(request.args[0], CONTAINER_SUSPEND)

@check_cont_owner
@handle_exception
def resume_cont():
    handle_cont_operation(request.args[0], CONTAINER_RESUME)

@check_cont_owner
@handle_exception
def stop_cont():
    handle_cont_operation(request.args[0], CONTAINER_STOP)

@check_cont_owner
@handle_exception
def restart_cont():
    handle_cont_operation(request.args[0], CONTAINER_RESTART)

@check_cont_owner
@handle_exception
def delete_cont():
    handle_cont_operation(request.args[0], CONTAINER_DELETE)

@check_cont_owner
@handle_exception
def recreate_cont():
    handle_cont_operation(request.args[0], CONTAINER_RECREATE)

@check_vm_owner
@handle_exception
def start_vm():
    handle_vm_operation(request.args[0], VM_TASK_START)

@check_vm_owner
@handle_exception
def stop_vm():
    handle_vm_operation(request.args[0], VM_TASK_STOP)

@check_vm_owner
@handle_exception
def resume_vm():
    handle_vm_operation(request.args[0], VM_TASK_RESUME)

@check_vm_owner
@handle_exception
def suspend_vm():
    handle_vm_operation(request.args[0], VM_TASK_SUSPEND)

@check_vm_owner
@handle_exception
def destroy_vm():
    handle_vm_operation(request.args[0], VM_TASK_DESTROY)

@check_vm_owner
@handle_exception
def delete_vm():
    handle_vm_operation(request.args[0], VM_TASK_DELETE)

@check_vm_owner
@handle_exception       
def snapshot():
    vm_id = int(request.args[0])
    if is_request_in_queue(vm_id, VM_TASK_SNAPSHOT):
        session.flash = "Snapshot request already in queue."
    elif check_snapshot_limit(vm_id):
        add_vm_task_to_queue(vm_id, VM_TASK_SNAPSHOT, {'snapshot_type': SNAPSHOT_USER})
        session.flash = "Your request to snapshot VM has been queued"
    else:
        session.flash = "Snapshot Limit Reached. Delete Previous Snapshots to take new snapshot."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception
def delete_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    if is_request_in_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Delete Snapshot request already in queue."
    else:
        add_vm_task_to_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, {'snapshot_id':snapshot_id})
        session.flash = "Your delete snapshot request has been queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@check_vm_owner
@handle_exception
def revert_to_snapshot():
    vm_id = int(request.args[0])
    snapshot_id = int(request.args[1])
    if is_request_in_queue(vm_id, VM_TASK_DELETE_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Delete Snapshot request in queue. Revert operation aborted."
    elif is_request_in_queue(vm_id, VM_TASK_REVERT_TO_SNAPSHOT, snapshot_id=snapshot_id):
        session.flash = "Revert to Snapshot request already in queue."
    else:
        add_vm_task_to_queue(vm_id, VM_TASK_REVERT_TO_SNAPSHOT, {'snapshot_id':snapshot_id})
        session.flash = "Your revert to snapshot request has been queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@auth.requires_login()
@handle_exception       
def list_my_task():
    form = get_task_num_form()
    task_num = ITEMS_PER_PAGE
    form.vars.task_num = task_num

    if form.accepts(request.vars, session, keepvalues=True):
        task_num = int(form.vars.task_num)
    
    pending = get_my_task_list([TASK_QUEUE_STATUS_PENDING], task_num)
    success = get_my_task_list([TASK_QUEUE_STATUS_SUCCESS], task_num)
    failed = get_my_task_list([TASK_QUEUE_STATUS_FAILED, TASK_QUEUE_STATUS_PARTIAL_SUCCESS], task_num)

    return dict(pending=pending, success=success, failed=failed, form=form)  


@check_vm_owner
@handle_exception       
def show_vm_performance():
    vm_id = int(request.args[0])
    vm_info = get_vm_info(vm_id)  
    m_type="vm"
    return dict(vm_id = vm_id, vm_identity = vm_info.vm_data.vm_identity, vm_ram = vm_info.vm_data.RAM,m_type=m_type,vm_cpu=vm_info.vm_data.vCPU)


@check_vm_owner
@handle_exception       
def show_vm_graph():
    vm_id = int(request.args[0])
    vm_info = get_vm_info(vm_id)  
    
    return dict(vm_id = vm_id, vm_identity = vm_info.vm_data.vm_identity, vm_ram = vm_info.vm_data.RAM)



def create_graph_for_vm():
    
    ret=create_graph()
    return ret

def create_graph():
    ret={}
    logger.debug(request.vars['graphType'])
    logger.debug(request.vars['vmIdentity'])
    logger.debug(request.vars['graphPeriod'])
    logger.debug(request.vars['vm_RAM'])
    logger.debug(request.vars['mtype'])
    graph_period=request.vars['graphPeriod']
    vm_ram=request.vars['vm_RAM']
    vm_identity=request.vars['vmIdentity']
    g_type=request.vars['graphType']
    m_type=request.vars['mtype']
    title=check_graph_type(g_type,vm_ram,m_type)
    host_cpu=request.vars['host_CPU']
    ret['valueformat']=check_graph_period(graph_period)
    ret['y_title']=title['y_title']
    ret['g_title']=title['g_title']
    
    
    ret['data']=fetch_info_graph(vm_identity,graph_period,g_type,vm_ram,m_type,host_cpu)
    
    mem=float(vm_ram)/(1024) if int(vm_ram)>1024 else vm_ram
    
    ret['mem']=mem
    

    if g_type=='disk':
        ret['legend_read']='disk read'
        ret['legend_write']='disk write'
    
    elif g_type=='nw':
        ret['legend_read']='network read'
        ret['legend_write']='network write'
    elif g_type=='cpu':
        ret['name']='cpu'
    else:
        ret['name']='mem'
    import json
    
    json_str = json.dumps(ret,ensure_ascii=False)
    
    return json_str




def create_container_graph():
    
    logger.debug('INSIDE create_container_graph' + request.args[0])
    logger.debug(request.args[0])
    cont_uuid = request.args[0]
    cont_stats = get_container_stats(cont_uuid)
    
    import json
    
    json_str = json.dumps(cont_stats,ensure_ascii=False)
    
    return json_str

@check_vm_owner
@handle_exception

def novnc_access():

    token=request.vars['token']
    port = config.get("NOVNC_CONF","port")
    url_ip = config.get("NOVNC_CONF","url_ip")
    url = "http://"+ str(url_ip)+ ":" + str(port)+"/vnc_auto.html?path=?token=" + str(token)
    return redirect(url)


@check_vm_owner
@handle_exception       
def grant_vnc():
    vm_id = request.args[0]   
    token = grant_novnc_access(vm_id)
    if token :
        redirect(URL(r = request, f = 'novnc_access', args = vm_id, vars =dict(token=token)))


@check_vm_owner
@handle_exception       
def clone_vm():

    vm_id = request.args[0]
    form = get_clone_vm_form(vm_id)
    if form.accepts(request.vars,session):
        session.flash = "Your request has been sent for approval."
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.flash = "Error in form."

    return dict(form=form)

@check_vm_owner
@handle_exception       
def attach_extra_disk():

    vm_id = request.args[0]
    form = get_attach_extra_disk_form(vm_id)
    if form.accepts(request.vars, session):
        session.flash = "Your request has been sent for approval."
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))
    elif form.errors:
        session.flash = "Error in form."

    return dict(form=form)

@check_vm_owner
@handle_exception       
def edit_vm_config():

    vm_id = request.args[0]
    form = get_edit_vm_config_form(vm_id)

    if form.accepts(request.vars, session, onvalidation=edit_vm_config_validation, hideerror=True):
        session.flash = "Your request has been queued!!!"
        redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

    elif form.errors:
        session.flash = "Error in form!!!"

    return dict(form=form)

@check_vm_owner
@handle_exception       
def save_vm_as_template():
    vm_id = int(request.args[0])
    if is_request_in_queue(vm_id, VM_TASK_SAVE_AS_TEMPLATE):    
        session.flash = "Request to save VM as template already in queue."
    elif check_vm_template_limit(vm_id):
        add_vm_task_to_queue(vm_id, VM_TASK_SAVE_AS_TEMPLATE)
        session.flash = "Your request to save VM as template is queued"
    else:
        session.flash = "Template for this VM already present. Delete a previous template to save new template."
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))

@handle_exception       
def delete_template():
    
    vm_id = int(request.args[0])
    params = {'template_id' : request.args[1]}
    add_vm_task_to_queue(vm_id, VM_TASK_DELETE_TEMPLATE, params)
    session.flash = "Your request to delete template is queued"
    redirect(URL(r = request, c = 'user', f = 'settings', args = vm_id))


@auth.requires_login()
@handle_exception
def mail_admin():
    form = get_mail_admin_form()
    if form.accepts(request.vars, session):
        email_type = form.vars.email_type
        email_subject = form.vars.email_subject
        email_message = form.vars.email_message
        send_email_to_admin(email_subject, email_message, email_type)
        redirect(URL(c='default', f='index'))
    return dict(form = form)

@auth.requires_login()
@handle_exception
def list_my_requests():
    my_requests = get_my_requests()
    requests = get_segregated_requests(my_requests)

    return dict(install_requests = requests[0], 
                clone_requests = requests[1], 
                disk_requests = requests[2], 
                edit_requests= requests[3],
		        install_object_store_requests= requests[4],
		        install_container_requests= requests[5])
        
@check_vm_owner
@handle_exception
def vm_history():

    vm_id = request.args[0]
    vm_history = get_vm_history(vm_id)        
    return dict(vm_id = vm_id, vm_history = vm_history)



@check_vm_owner
@handle_exception       
def configure_snapshot():

    vm_id = int(request.args[0])
    flag = request.vars['snapshot_flag']
    update_snapshot_flag(vm_id, flag)


