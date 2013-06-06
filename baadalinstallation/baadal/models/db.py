# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    from authuser import login_callback
###################################################################################

import ConfigParser
import os

ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))

config = ConfigParser.ConfigParser()
config.read(os.path.join(ctx_path, 'static/config-db.cfg'));
conn_str = config.get("MYSQL_CONF","mysql_conn")
db = DAL(conn_str)

db.define_table('constants',
    Field('name','string', notnull=True, unique=True),
    Field('value','string',notnull=True))

db.define_table('organisation',
    Field('name','string', notnull=True),
    Field('details','string'),
    Field('public_ip','string',length=15), 
    format='%(name)s (%(id)s)')

from gluon.tools import Auth
auth = Auth(db)

## configure custom auth tables
auth.settings.table_user_name = 'user'
auth.settings.table_group_name = 'user_group'
auth.settings.table_membership_name = 'user_membership'

## configure auth policy
auth.settings.allow_basic_login = config.getboolean("AUTH_CONF","allow_basic_login")
auth.settings.login_after_registration = config.getboolean("AUTH_CONF","login_after_registration")
auth.settings.actions_disabled=config.get("AUTH_CONF",config.get("AUTH_CONF","actions_disabled"))
auth.settings.remember_me_form = config.getboolean("AUTH_CONF","remember_me_form")

db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length=128, default=''),
    Field('last_name', length=128, default=''),
    Field('email', length=128, default='', unique=True), # required
    Field('username', length=128, default='', unique=True),
    Field('password', 'password', length=512, readable=False, label='Password'), # required
    Field('organisation_id', db.organisation, label='Organisation'),
    Field('block_user','boolean',default=False, notnull=True, writable=False, readable=False),
    Field('registration_key', length=512, writable=False, readable=False, default=''), # required
    Field('reset_password_key', length=512, writable=False, readable=False, default=''), # required
    Field('registration_id', length=512, writable=False, readable=False, default='')) # required

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.first_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.last_name.requires =   IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table

auth.settings.table_group = db.define_table(
    auth.settings.table_group_name,
    Field('role','string',length=100,notnull=True, unique=True),
    Field('description', length=255, default=''))

auth.settings.table_membership = db.define_table(
    auth.settings.table_membership_name,
    Field('user_id', db.user),
    Field('group_id', db.user_group))

###############################################################################
auth.define_tables(username=True)
###############################################################################
if config.get("AUTH_CONF","auth_type") == 'ldap':
    from gluon.contrib.login_methods.pam_auth import pam_auth
    auth.settings.login_methods=[pam_auth()]
    auth.settings.login_onaccept= [login_callback]  
    
###############################################################################

db.define_table('host',
    Field('host_ip','string',length=15,notnull=True),
    Field('mac_addr','string',length=100,notnull=True),
    Field('HDD','integer'),
    Field('CPUs','integer'),
    Field('RAM','integer'),
    Field("category","string"),
    Field('status','integer'),
    Field('vm_count','integer'))

db.define_table('datastore',
    Field('ds_name','string'),
    Field('ds_ip','string',length=15),
    Field('path','string'),
    Field('username','string'),
    Field('password','string'),
    Field('capacity','integer'))

db.define_table('template',
    Field('name','string',notnull=True),
    Field('os_type','string',length=30,notnull=True),
    Field('arch','string',notnull=True),
    Field('hdd','integer',notnull=True),
    Field('hdfile','string',notnull=True),
    Field('type','string',notnull=True),
    Field('datastore_id',db.datastore))

db.define_table('vm_data',
    Field('vm_name','string',length=512,notnull=True, unique=True),
    Field('user_id',db.user),
    Field('host_id',db.host),
    Field('RAM','integer'),
    Field('HDD','integer'),
    Field('vCPU','integer'),
    Field('template_id',db.template),
    Field('vm_ip','string',length=15),
    Field('vnc_port','integer'),
    Field('mac_addr','string',length=100),
    Field('datastore_id',db.datastore),
    Field('purpose','text'),
    Field('expiry_date','date'),
    Field('total_cost','integer'),
    Field('current_run_level','integer'),
    Field('last_run_level','integer'),
    Field('next_run_level','integer'),
    Field('start_time','time'),
    Field('end_time','time'),
    Field('status','integer'))

db.define_table('user_vm_map',
    Field('user_id', db.user),
    Field('vm_id', db.vm_data),
    primarykey=['user_id','vm_id'])

db.define_table('vm_data_event',
    Field('vm_id',db.vm_data),
    Field('vm_name','string',length=512,notnull=True),
    Field('user_id',db.user),
    Field('host_id',db.host),
    Field('RAM','integer'),
    Field('HDD','integer'),
    Field('vCPU','integer'),
    Field('template_id',db.template),
    Field('vm_ip','string',length=15),
    Field('vnc_port','integer'),
    Field('mac_addr','string',length=100),
    Field('datastore_id',db.datastore),
    Field('purpose','text'),
    Field('expiry_date','date'),
    Field('total_cost','integer'),
    Field('current_run_level','integer'),
    Field('last_run_level','integer'),
    Field('next_run_level','integer'),
    Field('start_time','time'),
    Field('end_time','time'),
    Field('status','integer'))

db.define_table('attached_disks',
    Field('vm_id',db.vm_data,notnull=True),
    Field('datastore_id',db.datastore,notnull=True),
    Field('capacity','string',length=45))

db.define_table('snapshot',
    Field('vm_id',db.vm_data,notnull=True),
    Field('datastore_id',db.datastore,notnull=True),
    Field('path','string',notnull=True))

db.define_table('task_queue',
    Field('task_type','string',length=30,notnull=True),
    Field('vm_id',db.vm_data),
    Field('priority','integer',default=1, notnull=True),
    Field('status','integer',notnull=True))

db.define_table('task_queue_event',
    Field('task_id',db.task_queue,notnull=True),
    Field('task_type','string',length=30,notnull=True),
    Field('vm_id',db.vm_data,notnull=True),
    Field('status','integer',notnull=True),
    Field('error','string', length=512),
    Field('start_time','time',notnull=True),
    Field('end_time','time',notnull=True),
    Field('attention_time','time',notnull=True))

db.define_table('vlan_map',
    Field('vm_id',db.vm_data))

db.define_table('vnc_server',
    Field('ip_addr','string',length=15,notnull=True))

db.define_table('vnc_access',
    Field('vm_id',db.vm_data),
    Field('vnc_server_id',db.vnc_server,length=15, notnull=True),
    Field('vnc_proxy_port','integer',notnull=True),
    Field('duration','integer'),
    Field('time_requested','integer'))

