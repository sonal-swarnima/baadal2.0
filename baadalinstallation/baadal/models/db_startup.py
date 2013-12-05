# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
###################################################################################


from gluon import current

#Startup Data
GROUP_DATA = {ADMIN : 'Super User', 
              ORGADMIN : 'Organisation Level Admin', 
              FACULTY : 'Faculty User', 
              USER:'Normal User'}

ORG_DATA = {'IIT Delhi':'Indian Institude of Technology, Delhi',
            'IIT Bombay':'Indian Institude of Technology, Mumbai'}

DB_CONSTANTS = {'vmfiles_path' : '/mnt/testdatastore',
              'datastore_int'  : 'ds_',
              'vncport_range'  : 20000,
              'templates_dir'  : 'vm_templates',
              'archives_dir'   : 'vm_archives',
              'vmcount'        :  1,
              'vm_rrds_dir'    : 'vm_rrds',
              'graph_file_dir' : '/home/www-data/web2py/applications/baadal/static/images/vm_graphs/',
              'admin_email'    : 'baadalsupport@cse.iitd.ernet.in',
              'vms'            : '/vms' }

MAC_PRIVATE_IP_POOL = { 
                '54:52:00:01:17:98' : '10.208.21.74',
                '54:52:00:01:17:89' : '10.208.21.75',
                '54:52:00:01:17:88' : '10.208.21.76',
                '54:52:00:01:17:87' : '10.208.21.77',
                '54:52:00:01:17:86' : '10.208.21.78',
                '54:52:00:01:17:85' : '10.208.21.79',
                '54:52:00:01:17:84' : '10.208.21.80',
                '54:52:00:01:17:83' : '10.208.21.81',
                '54:52:00:01:17:82' : '10.208.21.82',
                '54:52:00:01:17:81' : '10.208.21.83',
                '54:52:00:01:17:80' : '10.208.21.84',
                '54:52:00:01:17:79' : '10.208.21.86',
                '54:52:00:01:17:78' : '10.208.21.87',
                '54:52:00:01:17:77' : '10.208.21.88',
                '54:52:00:01:17:76' : '10.208.21.89',
                '54:52:00:01:17:01' : '10.208.23.61',
                '54:52:00:01:17:02' : '10.208.23.62',
                '54:52:00:01:17:03' : '10.208.23.63',
                '54:52:00:01:17:04' : '10.208.23.64',
                '54:52:00:01:17:05' : '10.208.23.65',
                '54:52:00:01:17:06' : '10.208.23.66',
                '54:52:00:01:17:07' : '10.208.23.67',
                '54:52:00:01:17:92' : '10.208.23.68',
                '54:52:00:01:17:93' : '10.208.23.69',
                '54:52:00:01:17:94' : '10.208.23.70' }

current.MAC_PRIVATE_IP_POOL = MAC_PRIVATE_IP_POOL

VLAN_DATA = [{'name' : 'VLAN10', 'tag':'vlan10','addr':'10.20.10.0'},
             {'name' : 'VLAN20', 'tag':'vlan20','addr':'10.20.20.0'},
             {'name' : 'VLAN30', 'tag':'vlan30','addr':'10.20.30.0'},
             {'name' : 'VLAN40', 'tag':'vlan40','addr':'10.20.40.0'}]

DEFAULT_SECURITY_DOMAIN = {'name' : 'Research', 'vlan':1, 'visible_to_all':True}


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

if not db(db.vlan).count():
    _list = list(VLAN_DATA)
    for _dict in _list:
        db.vlan.insert(name = _dict['name'],
                       vlan_tag = _dict['tag'],
                       vlan_addr = _dict['addr'])

if not db(db.security_domain).count():
    _dict = dict(DEFAULT_SECURITY_DOMAIN)
    db.security_domain.insert(name = _dict['name'],
                              vlan= _dict['vlan'],
                              visible_to_all = _dict['visible_to_all'])
