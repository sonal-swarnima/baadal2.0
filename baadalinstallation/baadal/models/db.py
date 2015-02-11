# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from simplejson import loads, dumps
from ast import literal_eval
from helper import config,get_datetime, IS_MAC_ADDRESS
from auth_user import login_callback,login_ldap_callback, AUTH_TYPE_LDAP
from datetime import timedelta
from host_helper import HOST_TYPE_PHYSICAL

#### Connection Pooling of Db is also possible

db_type = config.get("GENERAL_CONF","database_type")
conn_str = config.get(db_type.upper() + "_CONF", db_type + "_conn")
#db = DAL(conn_str,fake_migrate_all=True)
db = DAL(conn_str)

db.define_table('constants',
    Field('name', 'string', length = 255, notnull = True, unique = True),
    Field('value', 'string', length = 255, notnull = True))

db.define_table('organisation',
    Field('name', 'string', length = 255, notnull = True, unique = True),
    Field('details', 'string', length = 255),
    Field('public_ip', 'string',length = 15),
    Field('admin_mailid', 'string', length = 50),
    format = '%(details)s')

from gluon.tools import Auth
auth = Auth(db)

from gluon.tools import Mail
mail = Mail()
if config.getboolean("MAIL_CONF","mail_active"):
    mail.settings.server = config.get("MAIL_CONF","mail_server")
    mail.settings.sender = config.get("MAIL_CONF","mail_sender")
    mail.settings.login = config.get("MAIL_CONF","mail_login")
    mail.settings.tls = literal_eval(config.get("MAIL_CONF","mail_server_tls"))

#added to make auth and db objects available in modules
from gluon import current  # @Reimport
current.auth = auth
current.db = db
current.auth_type = config.get("AUTH_CONF","auth_type")

## configure custom auth tables
auth.settings.table_user_name = 'user'
auth.settings.table_group_name = 'user_group'
auth.settings.table_membership_name = 'user_membership'

## configure auth policy
auth.settings.allow_basic_login = config.getboolean("AUTH_CONF","allow_basic_login")
auth.settings.login_after_registration = config.getboolean("AUTH_CONF","login_after_registration")
auth.settings.create_user_groups = config.getboolean("AUTH_CONF","create_user_groups")
auth.settings.actions_disabled = config.get("AUTH_CONF",config.get("AUTH_CONF","actions_disabled"))
auth.settings.remember_me_form = config.getboolean("AUTH_CONF","remember_me_form")

db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length = 128, default = ''),
    Field('last_name', length = 128, default = ''),
    Field('email', length = 128, unique = True), # required
    Field('username', length = 128, default = '', unique = True),
    Field('password', 'password', length = 512, readable = False, label = 'Password'), # required
    Field('organisation_id', db.organisation, label = 'Organisation'),
    Field('block_user', 'boolean', default = False, notnull = True, writable = False, readable = False),
    Field('mail_subscribed', 'boolean', default = True, notnull = True),
    Field('registration_key', length = 512, writable = False, readable = False, default = ''), # required
    Field('reset_password_key', length = 512, writable = False, readable = False, default = ''), # required
    Field('registration_id', length = 512, writable = False, readable = False, default = ''),
    format = '%(first_name)s %(last_name)s') # required

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.password.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.email.requires = [
  IS_EMAIL(error_message = auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

auth.settings.table_group = db.define_table(
    auth.settings.table_group_name,
    Field('role', 'string', length = 100, notnull = True, unique = True),
    Field('description', length = 255, default = ''),
    format = '%(role)s')

auth.settings.table_membership = db.define_table(
    auth.settings.table_membership_name,
    Field('user_id', db.user),
    Field('group_id', db.user_group),
    primarykey = ['user_id', 'group_id'])

###############################################################################
auth.define_tables(username = True)
###############################################################################
if current.auth_type == AUTH_TYPE_LDAP :
    from gluon.contrib.login_methods.pam_auth import pam_auth
    auth.settings.login_methods = [pam_auth()]
    auth.settings.login_onaccept = [login_ldap_callback]
else:
    auth.settings.login_onaccept = [login_callback]
    auth.settings.registration_requires_approval = True
###############################################################################

db.define_table('vlan',
    Field('name', 'string', length = 30, notnull = True, unique = True),
    Field('vlan_tag', 'string', length = 30, notnull = True),
    Field('vlan_addr', 'string', length = 15, notnull = True, requires=IS_IPV4()),
    format = '%(name)s')

db.define_table('security_domain',
    Field('name', 'string', length = 30, notnull = True, unique = True, label='Name'),
    Field('vlan', 'reference vlan', unique = True),
    Field('visible_to_all', 'boolean', notnull = True, default = True),
    Field('org_visibility', 'list:reference organisation', requires = IS_IN_DB(db, 'organisation.id', '%(details)s', multiple=True)),
    format = '%(name)s')

db.security_domain.name.requires = [IS_MATCH('^[a-zA-Z0-9][\w\-]*$', error_message=NAME_ERROR_MESSAGE), IS_LENGTH(30,1), IS_NOT_IN_DB(db,'security_domain.name')]

db.define_table('public_ip_pool',
    Field('public_ip', 'string', length = 15, notnull = True, unique = True),
    Field('is_active', 'boolean', notnull = True, default = True),
    format = '%(public_ip)s')

db.public_ip_pool.public_ip.requires = [IS_IPV4(error_message=IP_ERROR_MESSAGE), IS_NOT_IN_DB(db,'public_ip_pool.public_ip')]

db.define_table('private_ip_pool',
    Field('private_ip', 'string', length = 15, notnull = True, unique = True),
    Field('mac_addr', 'string', length = 20, unique = True),
    Field('vlan', db.vlan, notnull = True),
    Field('is_active', 'boolean', notnull = True, default = True),
    format = '%(private_ip)s')

db.private_ip_pool.private_ip.requires = [IS_IPV4(error_message=IP_ERROR_MESSAGE), IS_NOT_IN_DB(db,'private_ip_pool.private_ip')]
db.private_ip_pool.mac_addr.requires = [IS_EMPTY_OR([IS_UPPER(), IS_MAC_ADDRESS(), IS_NOT_IN_DB(db,'private_ip_pool.mac_addr')])]
db.private_ip_pool.vlan.requires = IS_IN_DB(db, 'vlan.id', '%(name)s', zero=None)


db.define_table('host',
    Field('host_name', 'string', length = 30, notnull = True, unique = True),
    Field('host_ip', db.private_ip_pool),
    Field('public_ip', db.public_ip_pool, label='Public IP', notnull = False),
    Field('HDD', 'integer', notnull = True, requires=IS_INT_IN_RANGE(1,None)),
    Field('CPUs', 'integer', notnull = True, requires=IS_INT_IN_RANGE(1,None)),
    Field('RAM', 'integer', requires=IS_INT_IN_RANGE(1,None), default=0),
    Field("category",'string', length = 50),
    Field('status', 'integer'),
    Field('slot_number', 'integer'),
    Field('rack_number', 'integer'),
    Field('extra', 'string', length = 50),
    Field('host_type', 'string', length = 20, default = HOST_TYPE_PHYSICAL))

db.define_table('datastore',
    Field('ds_name', 'string', notnull = True, length = 30, unique = True, label='Name of Datastore'),
    Field('ds_ip', 'string', length = 15, requires=IS_IPV4(error_message=IP_ERROR_MESSAGE), label='Mount IP'),
    Field('capacity', 'integer', notnull = True, label='Capacity(GB)'),
    Field('username', 'string', notnull = True, length = 255, label='Username'),
    Field('password', 'password', label='Password', readable=False),
    Field('path', 'string', notnull = True, label='Path'),
    Field('used', 'integer', default = 0, readable=False, writable=False),
    Field('system_mount_point', 'string', notnull = True, length = 255, label='System Mount Point'),
    format = '%(ds_name)s')
db.datastore.capacity.requires=IS_INT_IN_RANGE(1,10000)

db.define_table('template',
    Field('name', 'string', length = 30, notnull = True, unique = True, label='Name of Template'),
    Field('os', default = "Linux", requires = IS_IN_SET(('Linux', 'Windows','Others')), label='Operating System'),
    Field('os_name', default = "Ubuntu", requires = IS_IN_SET(('Ubuntu','Centos', 'Kali', 'Windows', 'Others')), label='OS Name'),
    Field('os_version','string',length = 50,notnull = True, label='OS Version'),
    Field('os_type', default = "Desktop", requires = IS_IN_SET(('Desktop','Server')), label='OS Type'),
    Field('arch', default = "amd64", requires = IS_IN_SET(('amd64', 'i386', 'x86', 'x64')), label='Architecture'),
    Field('hdd', 'integer', notnull = True, label='Harddisk(GB)'),
    Field('hdfile', 'string', length = 255, notnull = True, label='HD File'),
    Field('type', 'string', notnull = True, requires = IS_IN_SET(('QCOW2', 'RAW', 'ISO')), label='Template type'),
    Field('tag','string',length = 50,notnull = False, label='Tag'),
    Field('datastore_id', db.datastore, notnull = True, label='Datastore'),
    Field('owner', 'list:reference user', readable=False, writable=False),
    Field('is_active', 'boolean', notnull = True, default = True),
    format = lambda r: 
            '%s %s %s %s %sGB'%(r.os_name, r.os_version, r.os_type, r.arch, r.hdd) if r.tag == None else 
            '%s %s %s %s %sGB (%s)'%(r.os_name, r.os_version, r.os_type, r.arch, r.hdd, r.tag))
db.template.hdd.requires=IS_INT_IN_RANGE(1,1025)

db.define_table('vm_data',
    Field('vm_name', 'string', length = 100, notnull = True, label='Name'),
    Field('vm_identity', 'string', length = 100, notnull = True, unique = True),
    Field('host_id', db.host),
    Field('RAM', 'integer', label='RAM(MB)'),
    Field('HDD', 'integer', label='HDD(GB)'),
    Field('extra_HDD', 'integer', label='Extra HDD(GB)'),
    Field('vCPU', 'integer', label='CPUs'),
    Field('template_id', db.template),
    Field('requester_id',db.user, label='Requester'),
    Field('owner_id', db.user, label='Owner'),
    Field('private_ip', db.private_ip_pool, label='Private IP'),
    Field('public_ip', db.public_ip_pool, label='Public IP'),
    Field('vnc_port', 'integer'),
    Field('datastore_id', db.datastore),
    Field('purpose', 'string', length = 512),
    Field('expiry_date', 'date'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('parent_id', 'reference vm_data'),
    Field('locked', 'boolean', default = False),
    Field('security_domain', db.security_domain),
    Field('status', 'integer', represent=lambda x, row: get_vm_status(x)),
    Field('snapshot_flag', 'integer', default = 0),
    Field('saved_template', db.template),
    Field('delete_warning_date', 'datetime'))

db.vm_data.purpose.widget=SQLFORM.widgets.text.widget
db.vm_data.public_ip.requires = IS_EMPTY_OR(IS_IN_DB(db, 'public_ip_pool.id', '%(public_ip)s', zero=None))
db.vm_data.private_ip.requires = IS_EMPTY_OR(IS_IN_DB(db, 'private_ip_pool.id', '%(private_ip)s', zero=None))

db.define_table('request_queue',
    Field('vm_name', 'string', length = 100, notnull = True, label='VM Name'),
    Field('parent_id', 'reference vm_data'),
    Field('request_type', 'string', length = 20, notnull = True),
    Field('RAM', 'integer', label='RAM(MB)'),
    Field('HDD', 'integer', label='HDD(GB)'),
    Field('extra_HDD', 'integer', label='Extra HDD(GB)'),
    Field('attach_disk', 'integer', label='Disk Size(GB)'),
    Field('vCPU', 'integer', label='CPUs'),
    Field('template_id', db.template),
    Field('public_ip', 'boolean', default = False, label='Assign Public IP'),
    Field('security_domain', db.security_domain, label='Security Domain'),
    Field('requester_id',db.user, label='Requester'),
    Field('owner_id', db.user, label='Owner'),
    Field('collaborators', 'list:reference user'),
    Field('clone_count', 'integer', label='No. of Clones'),
    Field('purpose', 'string', length = 512),
    Field('status', 'integer'),
    Field('request_time', 'datetime', default = get_datetime()))

db.request_queue.vm_name.requires=[IS_MATCH('^[a-zA-Z0-9][\w\-]*$', error_message=NAME_ERROR_MESSAGE), IS_LENGTH(30,1)]
db.request_queue.extra_HDD.requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0,1025))
db.request_queue.extra_HDD.filter_in = lambda x: 0 if x == None else x
db.request_queue.attach_disk.requires=IS_INT_IN_RANGE(1,1025)
db.request_queue.purpose.widget=SQLFORM.widgets.text.widget
if not auth.user:
    tmp_query = db.template
elif is_moderator():
    tmp_query = db((db.template.is_active == True))
else:
    tmp_query = db((db.template.is_active == True) & ((db.template.owner == None) | (db.template.owner.contains(auth.user.id))))
    
db.request_queue.template_id.requires = IS_IN_DB(tmp_query, 'template.id', lambda r: 
                                                 '%s %s %s %s %sGB'%(r.os_name, r.os_version, r.os_type, r.arch, r.hdd) if r.tag == None else 
                                                 '%s %s %s %s %sGB (%s)'%(r.os_name, r.os_version, r.os_type, r.arch, r.hdd, r.tag), zero=None)
    
db.request_queue.clone_count.requires=IS_INT_IN_RANGE(1,101)

db.define_table('vm_event_log',
    Field('vm_id', db.vm_data),
    Field('attribute', 'string', length = 100),
    Field('old_value', 'string', length = 255),
    Field('new_value', 'string', length = 255),
    Field('requester_id', db.user),
    Field('timestamp', 'datetime', default = get_datetime()))

db.define_table('user_vm_map',
    Field('user_id', db.user),
    Field('vm_id', db.vm_data),
    primarykey = ['user_id', 'vm_id'])

db.define_table('vm_data_event',
    Field('vm_id', 'integer'),
    Field('vm_name', 'string', length = 100, notnull = True, label='Name'),
    Field('vm_identity', 'string', length = 100, notnull = True),
    Field('host_id', db.host),
    Field('RAM', 'integer'),
    Field('HDD', 'integer'),
    Field('extra_HDD', 'integer'),
    Field('vCPU', 'integer'),
    Field('template_id', db.template),
    Field('requester_id',db.user),
    Field('owner_id', db.user),
    Field('private_ip', 'string',length = 15),
    Field('public_ip', 'string',length = 15),
    Field('vnc_port', 'integer'),
    Field('datastore_id', db.datastore),
    Field('purpose', 'string', length = 512),
    Field('expiry_date', 'date'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('end_time', 'datetime'),
    Field('parent_id', 'integer'),
    Field('status', 'integer'))

db.define_table('attached_disks',
    Field('vm_id', db.vm_data, notnull = True),
    Field('datastore_id', db.datastore,notnull = True),
    Field('attached_disk_name', 'string', length=100, notnull = True),
    Field('capacity', 'string',length = 45),
    primarykey = ['datastore_id', 'vm_id', 'attached_disk_name'])

db.define_table('snapshot',
    Field('vm_id', db.vm_data,notnull = True),
    Field('datastore_id', db.datastore,notnull = True),
    Field('snapshot_name', 'string', length = 50),
    Field('type', 'integer'),
    Field('path', 'string', length = 255),
    Field('timestamp', 'datetime', default = get_datetime()))

db.define_table('task_queue',
    Field('task_type', 'string',length = 30,notnull = True),
    Field('requester_id', db.user),
    Field('parameters', 'text', default={}),
    Field('priority', 'integer', default = 1, notnull = True),
    Field('status', 'integer', notnull = True))

db.task_queue.parameters.filter_in = lambda obj, dumps=dumps: dumps(obj)
db.task_queue.parameters.filter_out = lambda txt, loads=loads: loads(txt)

db.define_table('task_queue_event',
    Field('task_id', 'integer', notnull = False),
    Field('task_type', 'string', length = 30, notnull = True),
    Field('vm_id', db.vm_data, notnull = False),
    Field('vm_name', 'string', length = 100, notnull = True),
    Field('requester_id', db.user),
    Field('parameters', 'text', default={}),
    Field('status', 'integer', notnull = True),
    Field('message', 'text'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('attention_time', 'datetime'),
    Field('end_time', 'datetime'))

db.task_queue_event.parameters.filter_in = lambda obj, dumps=dumps: dumps(obj)
db.task_queue_event.parameters.filter_out = lambda txt, loads=loads: loads(txt)

db.define_table('vnc_access',
    Field('vm_id', db.vm_data),
    Field('vnc_server_ip', 'string',length = 15, notnull = True),
    Field('host_id', db.host, length = 15, notnull = True),
    Field('vnc_source_port', 'integer', notnull = True),
    Field('vnc_destination_port','integer',default = -1),
    Field('duration', 'integer'),
    Field('status', 'string', length = 15, notnull = True, default = 'inactive'),
    Field('time_requested', 'datetime', default = get_datetime()),
    Field('expiry_time', compute=lambda r: r['time_requested']+ timedelta(seconds=r['duration'])))

