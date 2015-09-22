# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from gluon import auth, request, session
    from applications.baadal.models import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
###################################################################################
from helper import get_constant
from maintenance import BAADAL_STATUS_UP

def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
    to decorate functions that need access control
	"""
    return dict(form=auth())


def index():
    if auth.is_logged_in():
        if get_constant('baadal_status') != BAADAL_STATUS_UP:
            if not is_moderator():
                redirect(URL(r=request,c='default', f='user/logout'))
            session.flash='Baadal is in Maintenance Mode'
    return dict(request=request)

def contact():
    return dict()

def team():
    query = ((db.private_ip_pool.is_active == True))
    ip_list = db(query).select()
    dhcp_info_list = []
    for ips in ip_list:
        if ips.vlan != HOST_VLAN_ID:
            dhcp_info_list.append((None, ips.mac_addr, ips.private_ip))
        else:
            dhcp_info_list.append(('host', ips.mac_addr, ips.private_ip))
        
    for dhcp_info in dhcp_info_list: 
        host_name = ('host_' + dhcp_info[2].replace(".", '_')) if dhcp_info[0] != None else ('IP_' + dhcp_info[2].replace(".", '_'))
        dhcp_cmd = 'echo "host %s {\n\thardware ethernet %s;\n\tfixed-address %s;\n}\n" > /home/www-data/1_%s.conf'%(host_name, dhcp_info[1], dhcp_info[2], host_name)
        logger.debug(dhcp_cmd);
        execute_remote_cmd('localhost', 'root', dhcp_cmd)    
    return dict()

def faq():
    return dict()

def error():
    return dict(error=request.vars['error'])

def page_under_construction():
    return dict()
