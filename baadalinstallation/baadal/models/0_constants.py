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
VM_STATUS_REJECTED  = 1
VM_STATUS_VERIFIED  = 2
VM_STATUS_APPROVED  = 3
VM_STATUS_IN_QUEUE  = 4
VM_STATUS_RUNNING   = 5
VM_STATUS_SUSPENDED = 6
VM_STATUS_SHUTDOWN  = 7

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
              'vm_rrds_dir'    : 'vm_rrds',
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

#Email templates and subject constants
VM_CREATION_TEMPLATE="Dear {0[userName]},\n\nThe VM {0[vmName]} requested on {0[vmRequestTime]} is successfully created and is now available for use. The following operations are allowed on the VM:\n1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nRegards,\nBaadal Admin"

VM_CREATION_SUBJECT = "VM created successfully"
current.VM_CREATION_TEMPLATE = VM_CREATION_TEMPLATE
current.VM_CREATION_SUBJECT = VM_CREATION_SUBJECT

VM_REQUEST_TEMPLATE_FOR_USER="Dear {0[userName]},\n\nYour request for VM({0[vmName]}) creation has been successfully registered. Please note that you will be getting a separate email on successful VM creation.\n\nRegards,\nBaadal Admin"
                    
VM_REQUEST_SUBJECT_FOR_USER = "VM request successful"
                    
VM_APPROVAL_TEMPLATE_FOR_FACULTY ="Dear {0[facultyName]},\n\n{0[userName]} requested a VM {0[vmName]} on {0[vmRequestTime]} and is pending approval from you.\n\nRegards,\nBaadal Admin"
                    
VM_APPROVAL_SUBJECT_FOR_FACULTY = "VM pending approval"
current.VM_APPROVAL_TEMPLATE_FOR_FACULTY = VM_APPROVAL_TEMPLATE_FOR_FACULTY
current.VM_APPROVAL_SUBJECT_FOR_FACULTY = VM_APPROVAL_SUBJECT_FOR_FACULTY
