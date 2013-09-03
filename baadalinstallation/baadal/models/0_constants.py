#Task Queue status
TASK_QUEUE_STATUS_PENDING = 1
TASK_QUEUE_STATUS_PROCESSING = 2
TASK_QUEUE_STATUS_SUCCESS = 3
TASK_QUEUE_STATUS_FAILED = 4
TASK_QUEUE_STATUS_RETRY = 5
TASK_QUEUE_STATUS_IGNORE = 6
TASK_QUEUE_STATUS_PARTIAL_SUCCESS = 7

from gluon import current
current.TASK_QUEUE_STATUS_SUCCESS = TASK_QUEUE_STATUS_SUCCESS
current.TASK_QUEUE_STATUS_FAILED = TASK_QUEUE_STATUS_FAILED

#Task type
TASK_TYPE_CREATE_VM = 'Create VM'
TASK_TYPE_MIGRATE_VM = 'Migrate VM'
TASK_TYPE_START_VM = 'Start VM'
TASK_TYPE_STOP_VM = 'Stop VM'
TASK_TYPE_SUSPEND_VM = 'Suspend VM'
TASK_TYPE_RESUME_VM = 'Resume VM'
TASK_TYPE_DELETE_VM = 'Delete VM'
TASK_TYPE_DESTROY_VM = 'Destroy VM'
TASK_TYPE_CHANGELEVEL_VM = 'Changelevel VM'
TASK_TYPE_DELETE_SNAPSHOT = 'Delete Snapshot'
TASK_TYPE_REVERT_TO_SNAPSHOT = 'Revert to Snapshot'
TASK_TYPE_EDITCONFIG_VM = 'Edit Config VM'
TASK_TYPE_SNAPSHOT_VM = 'Snapshot VM'
TASK_TYPE_CLONE_VM = 'Clone VM'

#Task Queue Priority
TASK_QUEUE_PRIORITY_LOW = 0
TASK_QUEUE_PRIORITY_NORMAL = 1
TASK_QUEUE_PRIORITY_HIGH = 2
TASK_QUEUE_PRIORITY_URGENT = 3

#Host Status
HOST_STATUS_DOWN = 0
HOST_STATUS_UP = 1
HOST_STATUS_MAINTENANCE = 2

current.HOST_STATUS_UP = HOST_STATUS_UP
current.HOST_STATUS_DOWN = HOST_STATUS_DOWN

COST_CPU = 1.0
COST_RAM = 1.0
COST_SCALE = 1.2
COST_RUNLEVEL_0 = 0
COST_RUNLEVEL_1 = 5
COST_RUNLEVEL_2 = 15
COST_RUNLEVEL_3 = 30

#VM Status
VM_STATUS_REQUESTED = 0
VM_STATUS_REJECTED = 1
VM_STATUS_VERIFIED = 2
VM_STATUS_APPROVED = 3
VM_STATUS_RUNNING = 4
VM_STATUS_SUSPENDED = 5
VM_STATUS_SHUTDOWN = 6

current.VM_STATUS_RUNNING = VM_STATUS_RUNNING
current.VM_STATUS_SUSPENDED = VM_STATUS_SUSPENDED
current.VM_STATUS_SHUTDOWN = VM_STATUS_SHUTDOWN
current.VM_STATUS_VERIFIED = VM_STATUS_VERIFIED

#SNAPSHOTTING LIMIT
SNAPSHOTTING_LIMIT = 3

ADMIN = 'admin'
ORGADMIN = 'orgadmin'
FACULTY = 'faculty'
USER = 'user'

#Startup Data
GROUP_DATA = {ADMIN : 'Super User', 
              ORGADMIN : 'Organisation Level Admin', 
              FACULTY : 'Faculty User', 
              USER:'Normal User'}

ORG_DATA = {'IIT Delhi':'Indian Institude of Technology, Delhi'}

DB_CONSTANTS = {'vmfiles_path' : '/mnt/testdatastore',
              'datastore_int'  : 'ds_',
              'vncport_range'  : 20000,
              'templates_dir'  : 'vm_templates',
              'archives_dir'   : 'vm_archives',
              'vmcount'        :  1,
              'vm_rrds_dir'		 : 'vm_rrds',
              'graph_file_dir' : '/home/www-data/web2py/application/baadal/static/images/vm_graphs/',
              'admin_email'    : 'baadalsupport@cse.iitd.ernet.in' }

current.ADMIN = ADMIN
current.ORGADMIN = ORGADMIN
current.FACULTY = FACULTY
current.USER = USER

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
                '54:52:00:01:17:76' : '10.208.21.89' } 

MAC_PUBLIC_IP_POOL = { 
                '54:52:00:01:17:40' : '10.208.23.93',
                '54:52:00:01:17:41' : '10.208.23.94',
                '54:52:00:01:17:42' : '10.208.23.95',
                '54:52:00:01:17:43' : '10.208.23.96' } 

current.MAC_PRIVATE_IP_POOL = MAC_PRIVATE_IP_POOL
current.MAC_PUBLIC_IP_POOL = MAC_PUBLIC_IP_POOL

PUBLIC_IP_NOT_ASSIGNED = "Not Assigned"
current.PUBLIC_IP_NOT_ASSIGNED = PUBLIC_IP_NOT_ASSIGNED

ITEMS_PER_PAGE=20
#Added so that changes in modules are instantlly loaded and reflected.
from gluon.custom_import import track_changes; track_changes(True)
