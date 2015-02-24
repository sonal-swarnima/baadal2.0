# -*- coding: utf-8 -*-

import os, re, random
from ast import literal_eval
from datetime import timedelta
from gluon.tools import Auth, Service, PluginManager
from auth_user import login_ldap_callback,login_callback, AUTH_TYPE_LDAP

def get_context_path():
    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_datetime():
    import datetime
    return datetime.datetime.now()

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/baadalapp.cfg'));
    return config

config = get_config_file()

db_type = config.get("GENERAL_CONF","database_type")
conn_str = config.get(db_type.upper() + "_CONF", db_type + "_conn")
print conn_str
db=DAL(conn_str,fake_migrate_all=True)
#db = DAL(conn_str)

from gluon.tools import Auth
auth = Auth(db)

from gluon import current  # @Reimport
current.auth = auth
current.db = db
current.auth_type = config.get("AUTH_CONF","auth_type")

#########################################################################

## configure custom auth tables
auth.settings.table_user_name = 'user'
auth.settings.table_group_name = 'user_group'
auth.settings.table_membership_name = 'user_membership'

db.define_table(
    auth.settings.table_user_name,
    Field('first_name', length = 128, default = ''),
    Field('last_name', length = 128, default = ''),
    Field('email', length = 128, unique = True), # required
    Field('username', length = 128, default = '', unique = True),
    Field('password', 'password', length = 512, readable = False, label = 'Password'), # required
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

auth.settings.allow_basic_login = config.getboolean("AUTH_CONF","allow_basic_login")
auth.settings.login_after_registration = config.getboolean("AUTH_CONF","login_after_registration")
auth.settings.actions_disabled = config.get("AUTH_CONF",config.get("AUTH_CONF","actions_disabled"))
auth.settings.remember_me_form = config.getboolean("AUTH_CONF","remember_me_form")


###############################################################################
auth.define_tables(username = True)
###############################################################################
#from gluon.contrib.login_methods.pam_auth import pam_auth
#auth.settings.login_methods = [pam_auth()]
#auth.settings.login_onaccept = [login_ldap_callback]
if current.auth_type == AUTH_TYPE_LDAP :
    from gluon.contrib.login_methods.pam_auth import pam_auth
    auth.settings.login_methods = [pam_auth()]
    auth.settings.login_onaccept = [login_ldap_callback]
else:
    auth.settings.login_onaccept = [login_callback]
    
###############################################################################

db.define_table('task_queue',
    Field('ip_addr', 'string', length = 30, notnull = True),
    Field('task_type', 'string',length = 30,notnull = True),
    Field('user_name','string',length=30,notnull=True),
    Field('requester_type', 'string',length = 30,notnull = True),
    Field('priority', 'integer', default = 1, notnull = True),
    Field('email_id','string',length = 50)
    )



db.define_table('task_queue_event',
    Field('task_id', 'integer', notnull = True),
    Field('server_name', 'string', length = 30, notnull = True),
    Field('task_type', 'string', length = 30, notnull = True),
    Field('test_case_list', 'string', length = 150, notnull = True),
    Field('status', 'integer', notnull = True),
    Field('requester_id','string',length=30,notnull=True),
    Field('start_time', 'datetime', default = get_datetime()),
    Field('file_name', 'string',length = 30,notnull = True),
    Field('end_time', 'datetime'),
    Field('attention_time', 'datetime'),
    Field('email_id','string',length = 50)
    )

###############################################################################

from gluon.tools import Mail
mail = Mail()
if config.getboolean("MAIL_CONF","mail_active"):
    mail.settings.server = config.get("MAIL_CONF","mail_server")
    mail.settings.sender = config.get("MAIL_CONF","mail_sender")
    mail.settings.login = config.get("MAIL_CONF","mail_login")
    mail.settings.tls = literal_eval(config.get("MAIL_CONF","mail_server_tls"))




