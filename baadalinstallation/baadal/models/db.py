# -*- coding: utf-8 -*-

db = DAL('mysql://root:dbadmin@localhost/')

from gluon.tools import Auth, Crud, Service, PluginManager
auth = Auth(globals(),db)

db.define_table('constants',
    Field('name','string',notnull=True),
    Field('value1','string',notnull=True))

db.define_table('organisation',
    Field('name','string',notnull=True),
    Field('details','string',))

db.define_table('role',
    Field('role_id','id'),
    Field('name','string',length=100,notnull=True),
    Field('description','string',length=255),
    primarykey=['role_id'])

db.define_table('user',
    Field('user_id','id'),
    Field('first_name','string',length=128,notnull=True),
    Field('last_name','string',length=128),
    Field('email','string',length=128,notnull=True,requires=IS_EMAIL),
    Field('username','string',length=30,notnull=True),
    Field('password','string',length=512,notnull=True),
    Field('organisation_id','integer',notnull=True),
    Field('block_user','boolean',default=False,notnull=True),
    primarykey=['user_id'])

db.define_table('user_role_map',
    Field('user_id', db.user),
    Field('role_id', db.role))

db.define_table('host',
    Field('host_id','id'),
    Field('host_ip','string',length=15,notnull=True),
    Field('mac_addr','string',length=100,notnull=True),
    Field('HDD','integer'),
    Field('CPUs','integer'),
    Field('RAM','integer'),
    Field("category","string"),
    Field('status','integer'),
    Field('vm_count','integer'),
    primarykey=['host_id'])

db.define_table('datastore',
    Field('datastore_id','id'),
    Field('ds_name','string'),
    Field('ds_ip','string',length=15),
    Field('path','string'),
    Field('username','string'),
    Field('password','string'),
    Field('capacity','integer'))

db.define_table('template',
    Field('template_id','id'),
    Field('name','string',notnull=True),
    Field('os_type','string',length=30,notnull=True),
    Field('arch','string',notnull=True),
    Field('hdd','integer',notnull=True),
    Field('hdfile','string',notnull=True),
    Field('type','string',notnull=True),
    Field('datastore_id',db.datastore,notnull=True),
    primarykey=['template_id'])

db.define_table('vm_data',
    Field('vm_id','id'),
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
    Field('status','integer'),
    primarykey=['vm_id'])

db.define_table('vm_data_event',
    Field('vm_event_id','id'),
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
    Field('status','integer'),
    primarykey=['vm_event_id'])

db.define_table('attached_disks',
    Field('disk_id','id'),
    Field('vm_id',db.vm_data,notnull=True),
    Field('datastore_id',db.datastore,notnull=True),
    Field('capacity','string',length=45),
    primarykey=['disk_id'])

db.define_table('snapshot',
    Field('snapshot_id','id'),
    Field('vm_id',db.vm_data,notnull=True),
    Field('datastore_id',db.datastore,notnull=True),
    Field('path','string',notnull=True),
    primarykey=['snapshot_id'])

db.define_table('task_queue',
    Field('task_id','id'),
    Field('task_type','string',length=30,notnull=True),
    Field('vm_id',db.vm_data),
    Field('priority','integer',default=1, notnull=True),
    Field('status','integer',notnull=True),
    primarykey=['task_id'])

db.define_table('task_queue_event',
    Field('task_event_id','id'),
    Field('task_id',db.task_queue,notnull=True),
    Field('task_type','string',length=30,notnull=True),
    Field('vm_id',db.vm_data,notnull=True),
    Field('status','integer',notnull=True),
    Field('error','string', length=512),
    Field('start_time','time',notnull=True),
    Field('end_time','time',notnull=True),
    Field('attention_time','time',notnull=True),
    primarykey=['task_event_id'])

db.define_table('vlan_map',
    Field('vlan_id','id'),
    Field('vm_id',db.vm_data))

db.define_table('vnc_server',
    Field('vnc_server_id','id'),
    Field('ip_addr','string',length=15,notnull=True),
    primarykey=['vnc_server_id'])

db.define_table('vnc_access',
    Field('vm_id',db.vm_data),
    Field('vnc_server_id',db.vnc_server,length=15, notnull=True),
    Field('vnc_proxy_port','integer',notnull=True),
    Field('duration','integer'),
    Field('time_requested','integer'))



