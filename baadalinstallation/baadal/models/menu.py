# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import T,request,response,URL,H2
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import get_constant
from auth_user import is_auth_type_db
from maintenance import BAADAL_STATUS_UP, BAADAL_STATUS_DOWN, BAADAL_STATUS_UP_IN_PROGRESS, BAADAL_STATUS_DOWN_IN_PROGRESS

vm_enabled = is_vm_enabled()
docker_enabled = is_docker_enabled()
object_store_enabled = is_object_store_enabled()
response.title = request.application
response.google_analytics_id = None

response.top_menu = [
    (T('Why Baadal?'), False, URL('default','about')),
    (T('FAQ'), False, URL('default','faq')),
    (T('Solutions'), False, URL('default','solutions')),
    (T('Pricing'), False, URL('default','pricing')),
    (T('Contact Us'), False, URL('default','contact'))
    ]
if auth.is_logged_in():
    response.user_menu = [
        (H2('USER MENU'),False, dict(_href='#', _id='menu_user')),
        (T('Home'), False, URL('default','index')),
        (T('Pending Requests'), False, URL('user','list_my_requests')),
        (T('My Tasks'), False, URL('user','list_my_task')),
        (T('VPN'),False, URL('user','vpn')), 
        (T('Mail Admin'), False, URL('user','mail_admin'))
        ]
    
    if docker_enabled:
        response.user_menu.insert(2, (T('Request Container'), False, URL('user','request_container')))
        response.user_menu.insert(3, (T('My Containers'), False, URL('user','list_my_container')))
    
    if object_store_enabled:
        response.user_menu.insert(2, (T('Request Object Store'), False, URL('user','request_object_store')))
        response.user_menu.insert(3, (T('My Object Stores'), False, URL('user','list_my_object_store')))

    if vm_enabled:
        response.user_menu.insert(2, (T('Request VM'), False, URL('user','request_vm')))
        response.user_menu.insert(3, (T('My VMs'), False, URL('user','list_my_vm')))

    if not is_general_user():
        response.faculty_menu = [
            (H2('FACULTY MENU'),False, dict(_href='#', _id='menu_faculty')),
            (T('Pending Approvals {'+str(get_pending_requests_count())+'} '), False, URL('faculty','pending_requests'))
            ]
            
    if (is_orgadmin()):
        response.orgadmin_menu = [
            (H2('ORG-ADMIN MENU'),False, dict(_href='#', _id='menu_orgadmin')),
            (T('List All Org-Level VMs'), False, URL('orgadmin','list_all_orglevel_vm')),
            (T('Pending Org-Level VM Approvals {'+str(get_pending_approval_count())+'}'), False, URL('orgadmin','pending_approvals'))
            ]
    elif (is_moderator()):
        response.orgadmin_menu = [
            (H2('ORG-ADMIN MENU'),False, dict(_href='#', _id='menu_orgadmin')),
            (T('Pending Org-Level VM Approvals {'+str(get_pending_approval_count())+'}'), False, URL('orgadmin','pending_approvals'))
            ]
    
    if is_moderator():
        response.admin_menu = [
            (H2('ADMIN MENU'),False, dict(_href='#', _id='menu_admin')),
            (T('All Pending Requests {'+str(get_all_pending_req_count())+'} '), False, URL('admin','list_all_pending_requests')),
            (T('Tasks'), False, URL('admin','task_list'))]

        if object_store_enabled:
            response.admin_menu.insert(1, (T('All Object Store'), False, URL('admin','list_all_object_store')))
        if docker_enabled:
            response.admin_menu.insert(1, (T('All Containers'), False, URL('admin','list_all_containers')))
        if vm_enabled:
            response.admin_menu.insert(1, (T('All VM''s'), False, URL('admin','list_all_vm')))

        if vm_enabled:
            response.admin_menu.extend([(T('VM Utilization'), False, URL('admin','vm_utilization')),
                                        (T('VM Sanity Check'), False, URL('admin','sanity_check')),
                                        (T('Host and VMs'), False, URL('admin','hosts_vms'))])
        if docker_enabled:
            response.admin_menu.extend([(T('Nodes and Containers'), False, URL('admin','nodes_containers')),
                                        (T('Container Sanity Check'), False, URL('admin','cont_sanity_check'))])
            
        if is_auth_type_db():
            response.admin_menu.extend([(T('Approve Users'), False, URL('admin','approve_users')),
                                        (T('Modify User Role'), False, URL('admin','modify_user_role'))])

        if vm_enabled:
            response.admin_menu.extend([(T('Configure System'), False,dict(_href='#', _id='configure'),[
                (T('Configure Host'), False, URL('admin','host_details')),
                (T('Configure Template'), False, URL('admin','manage_template')),
                (T('Configure Datastore'), False, URL('admin','manage_datastore')),
		        (T('Controller Performance'), False, URL('admin','show_cont_performance')),
		        (T('NAT Performance'), False, URL('admin','show_nat_performance')),
                (T('Host Throughput Graph'), False, URL('admin','network_graph')),
		        (T('Host Latency Graph'), False, URL('admin','host_network_graph')),
                (T('Utilization'), False, URL('admin','zoom_tree')),
                (T('Configure Security Domain'), False, URL('admin','manage_security_domain')),
                (T('Configure Private IP Pool'), False, URL('admin','manage_private_ip_pool')),
                (T('Configure Public IP Pool'), False, URL('admin','manage_public_ip_pool')),
                (T('Launch VM Image'), False, URL('admin','launch_vm_image'))
                ])])

        baadal_status = get_constant('baadal_status')
        status_txt = None
        if baadal_status == BAADAL_STATUS_DOWN:
            status_txt = 'Bootup Baadal'
        elif baadal_status == BAADAL_STATUS_DOWN_IN_PROGRESS:
            status_txt = 'Check Baadal Shutdown Status'
        elif baadal_status == BAADAL_STATUS_UP:
            status_txt = 'Shutdown Baadal'
        elif baadal_status == BAADAL_STATUS_UP_IN_PROGRESS:
            status_txt = 'Check Baadal Bootup Status'
        if status_txt:
            response.admin_menu.extend([((T(status_txt), False, URL('admin','baadal_status')))])


else:
    response.user_menu = [
        (H2('KNOW MORE'),False, dict(_href='#')),
        (T('Services'), False, URL('default','page_under_construction')),
        (T('Infrastructure'), False, URL('default','infrastructure')),
        (T('FAQs'), False, URL('default','faq')),
        (T('Register Organization'), False, URL('default','page_under_construction')),
        (T('Contact Us'), False, URL('default','contact'))
        ]
    