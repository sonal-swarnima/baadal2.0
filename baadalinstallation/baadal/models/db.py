# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from simplejson import loads, dumps
from helper import get_config_file,get_datetime
from auth_user import login_callback,login_ldap_callback

#### Connection Pooling of Db is also possible

config = get_config_file()
db_type = config.get("GENERAL_CONF","database_type")
conn_str = config.get(db_type.upper() + "_CONF", db_type + "_conn")
db = DAL(conn_str)

db.define_table('constants',
    Field('name', 'string', notnull = True, unique = True),
    Field('value', 'string', notnull = True))

db.define_table('organisation',
    Field('name', 'string', notnull = True, unique = True),
    Field('details', 'string'),
    Field('public_ip', 'string',length = 15), 
    Field('admin_mailid', 'string', length = 50),
    format = '%(details)s')

from gluon.tools import Auth
auth = Auth(db)

from gluon.tools import Mail
mail = Mail()
mail.settings.server = config.get("MAIL_CONF","mail_server")
mail.settings.sender = config.get("MAIL_CONF","mail_sender")
mail.settings.login = config.get("MAIL_CONF","mail_login")
mail.settings.tls = True


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
    Field('registration_key', length = 512, writable = False, readable = False, default = ''), # required
    Field('reset_password_key', length = 512, writable = False, readable = False, default = ''), # required
    Field('registration_id', length = 512, writable = False, readable = False, default = ''),
    format = '%(username)s') # required

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message = auth.messages.is_empty)
custom_auth_table.email.requires = [
  IS_EMAIL(error_message = auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

auth.settings.table_group = db.define_table(
    auth.settings.table_group_name,
    Field('role', 'string',length = 100,notnull = True, unique = True),
    Field('description', length = 255, default = ''))

auth.settings.table_membership = db.define_table(
    auth.settings.table_membership_name,
    Field('user_id', db.user),
    Field('group_id', db.user_group),
    primarykey = ['user_id', 'group_id'])

###############################################################################
auth.define_tables(username = True)
###############################################################################
if current.auth_type == 'ldap':
    from gluon.contrib.login_methods.pam_auth import pam_auth
    auth.settings.login_methods = [pam_auth()]
    auth.settings.login_onaccept = [login_ldap_callback]  
else:
    auth.settings.login_onaccept = [login_callback]  
###############################################################################

db.define_table('host',
    Field('host_ip', 'string',length = 15,notnull = True, unique = True, label='Host IP'),
    Field('host_name', 'string',length = 100,notnull = True, unique = True),
    Field('mac_addr', 'string',length = 100,notnull = True, unique = True),
    Field('HDD', 'integer'),
    Field('CPUs', 'integer'),
    Field('RAM', 'integer'),
    Field("category","string"),
    Field('status', 'integer'),
    Field('vm_count', 'integer', default = 0))

db.define_table('datastore',
    Field('ds_name', 'string', unique = True, label='Name of Datastore'),
    Field('ds_ip', 'string',length = 15, unique = True, label='Mount IP'),
    Field('path', 'string', label='Path'),
    Field('username', 'string', label='Username'),
    Field('password', 'password', label='Password'),
    Field('used', 'integer', default = 0, readable=False, writable=False),
    Field('capacity', 'integer', label='Capacity'),
    format = '%(ds_name)s')

db.define_table('template',
    Field('name', 'string', notnull = True, unique = True, label='Name of Template'),
    Field('os_type', default = "Linux", requires = IS_IN_SET(('Linux', 'Windows', 'Others')), label='Operating System'),
    Field('arch', default = "amd64", requires = IS_IN_SET(('amd64', 'i386', 'win7')), label='Architecture'),
    Field('hdd', 'integer', notnull = True, label='Harddisk(GB)'),
    Field('hdfile', 'string', notnull = True, label='HD File'),
    Field('type', 'string', notnull = True, requires = IS_IN_SET(('QCOW2', 'RAW', 'ISO')), label='Template type'),
    Field('datastore_id', db.datastore, label='Datastore'),
    format = '%(name)s')

db.define_table('vm_data',
    Field('vm_name', 'string',length = 512,notnull = True, unique = True, label='Name'),
    Field('host_id', db.host),
    Field('RAM', 'integer', label='RAM'),
    Field('HDD', 'integer'),
    Field('extra_HDD', 'integer'),
    Field('vCPU', 'integer', label='vCPUs'),
    Field('template_id', db.template),
    Field('requester_id',db.user, represent=lambda x, row: get_full_name(x), label='Requester'),
    Field('owner_id', db.user, represent=lambda x, row: get_full_name(x), label='Owner'),
    Field('mac_addr_1', 'string',length = 100),
    Field('private_ip', 'string',length = 15, label='Private IP'),
    Field('mac_addr_2', 'string',length = 100),
    Field('public_ip', 'string',length = 15, label='Public IP'),
    Field('vnc_port', 'integer'),
    Field('datastore_id', db.datastore),
    Field('purpose', 'text'),
    Field('expiry_date', 'date'),
    Field('total_cost', 'float', default = 0),
    Field('current_run_level', 'integer', default = 0),
    Field('last_run_level', 'integer'),
    Field('next_run_level', 'integer'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('parent_id', 'reference vm_data'),
    Field('locked', 'boolean', default = False),
    Field('parameters', 'text', default={}),
    Field('status', 'integer', represent=lambda x, row: get_vm_status(x)))

db.vm_data.parameters.filter_in = lambda obj, dumps=dumps: dumps(obj)
db.vm_data.parameters.filter_out = lambda txt, loads=loads: loads(txt)

db.define_table('user_vm_map',
    Field('user_id', db.user),
    Field('vm_id', db.vm_data),
    primarykey = ['user_id', 'vm_id'])

db.define_table('vm_data_event',
    Field('vm_id', 'integer'),
    Field('vm_name', 'string',length = 512,notnull = True),
    Field('host_id', db.host),
    Field('RAM', 'integer'),
    Field('HDD', 'integer'),
    Field('extra_HDD', 'integer'),
    Field('vCPU', 'integer'),
    Field('template_id', db.template),
    Field('requester_id',db.user),
    Field('owner_id', db.user),
    Field('mac_addr_1', 'string',length = 100),
    Field('private_ip', 'string',length = 15),
    Field('mac_addr_2', 'string',length = 100),
    Field('public_ip', 'string',length = 15),
    Field('vnc_port', 'integer'),
    Field('datastore_id', db.datastore),
    Field('purpose', 'text'),
    Field('expiry_date', 'date'),
    Field('total_cost', 'integer', default = 0),
    Field('current_run_level', 'integer', default = 0),
    Field('last_run_level', 'integer'),
    Field('next_run_level', 'integer'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('end_time', 'datetime'),
    Field('parent_id', 'integer'),
    Field('parameters', 'text'),
    Field('status', 'integer'))

db.define_table('attached_disks',
    Field('vm_id', db.vm_data,notnull = True),
    Field('datastore_id', db.datastore,notnull = True),
    Field('capacity', 'string',length = 45),
    primarykey = ['datastore_id', 'vm_id'])

db.define_table('snapshot',
    Field('vm_id', db.vm_data,notnull = True),
    Field('datastore_id', db.datastore,notnull = True),
    Field('snapshot_name', 'string', length = 50),
    Field('path', 'string'))

db.define_table('task_queue',
    Field('task_type', 'string',length = 30,notnull = True),
    Field('vm_id', db.vm_data),
    Field('parameters', 'text', default={}),
    Field('priority', 'integer', default = 1, notnull = True),
    Field('status', 'integer', notnull = True))

db.task_queue.parameters.filter_in = lambda obj, dumps=dumps: dumps(obj)
db.task_queue.parameters.filter_out = lambda txt, loads=loads: loads(txt)

db.define_table('task_queue_event',
    Field('task_id', 'integer', notnull = True),
    Field('task_type', 'string',length = 30,notnull = True),
    Field('vm_id', db.vm_data,notnull = True),
    Field('parameters', 'text', default={}),
    Field('status', 'integer', notnull = True),
    Field('error', 'text'),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('attention_time', 'datetime'),
    Field('end_time', 'datetime'))

db.task_queue_event.parameters.filter_in = lambda obj, dumps=dumps: dumps(obj)
db.task_queue_event.parameters.filter_out = lambda txt, loads=loads: loads(txt)

#TODO: to be modified after networking details have been finalized 
db.define_table('vlan_map',
    Field('vm_id', db.vm_data))

#TODO: to be modified after networking details have been finalized 
db.define_table('vnc_server',
    Field('ip_addr', 'string',length = 15,notnull = True))

#TODO: to be modified after networking details have been finalized 
db.define_table('vnc_access',
    Field('vm_id', db.vm_data),
    Field('vnc_server_id', db.vnc_server,length = 15, notnull = True),
    Field('vnc_proxy_port', 'integer', notnull = True),
    Field('duration', 'integer'),
    Field('time_requested', 'datetime', default = get_datetime()))

if not db(db.constants).count():
    _dict = dict(DB_CONSTANTS)
    for _key in _dict.keys():
        db.constants.insert(name = _key,value = _dict[_key])

if not db(db.user_group).count():
    _dict = dict(GROUP_DATA)
    for _key in _dict.keys():
        db.user_group.insert(role = _key,description = _dict[_key])

if not db(db.organisation).count():
    _dict = dict(ORG_DATA)
    for _key in _dict.keys():
        db.organisation.insert(name = _key,details = _dict[_key])

