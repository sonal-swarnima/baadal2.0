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
TASK_TYPE_EDITCONFIG_VM = 'Edit VM Config'
TASK_TYPE_SNAPSHOT_VM = 'Snapshot VM'
TASK_TYPE_CLONE_VM = 'Clone VM'
TASK_TYPE_ATTACH_DISK = 'Attach Disk'

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

REQ_STATUS_REQUESTED = 1
REQ_STATUS_REJECTED  = 2
REQ_STATUS_VERIFIED  = 3
REQ_STATUS_APPROVED  = 4
REQ_STATUS_IN_QUEUE  = 5
#VM Status
VM_STATUS_UNKNOWN   =-1
VM_STATUS_IN_QUEUE  = 1
VM_STATUS_RUNNING   = 2
VM_STATUS_SUSPENDED = 3
VM_STATUS_SHUTDOWN  = 4

current.VM_STATUS_RUNNING = VM_STATUS_RUNNING
current.VM_STATUS_SUSPENDED = VM_STATUS_SUSPENDED
current.VM_STATUS_SHUTDOWN = VM_STATUS_SHUTDOWN

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

ORG_DATA = {'IIT Delhi':'Indian Institude of Technology, Delhi',
            'IIT Bombay':'Indian Institude of Technology, Mumbai'}

DEFAULT_SECURITY_DOMAIN = {'name' : 'Research', 'vlan_tag':'research', 'ip_range_lb':'10.20.1.1', 'ip_range_ub':'10.20.1.255', 'visible_to_all':True}

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

PUBLIC_IP_NOT_ASSIGNED = "Not Assigned"
current.PUBLIC_IP_NOT_ASSIGNED = PUBLIC_IP_NOT_ASSIGNED

ITEMS_PER_PAGE=20
#Added so that changes in modules are instantlly loaded and reflected.
from gluon.custom_import import track_changes; track_changes(True)

#Email templates and subject constants
VM_CREATION_TEMPLATE="Dear {0[userName]},\n\nThe VM {0[vmName]} requested on {0[vmRequestTime]} is successfully created and is now available for use. The following operations are allowed on the VM:\n1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nRegards,\nBaadal Admin"

VM_CREATION_SUBJECT = "VM created successfully"

VM_REQUEST_TEMPLATE_FOR_USER="Dear {0[userName]},\n\nYour request for VM({0[vmName]}) creation has been successfully registered. Please note that you will be getting a separate email on successful VM creation.\n\nRegards,\nBaadal Admin"
                    
VM_REQUEST_SUBJECT_FOR_USER = "VM request successful"
                    
VM_APPROVAL_TEMPLATE_FOR_FACULTY ="Dear {0[facultyName]},\n\n{0[userName]} requested a VM {0[vmName]} on {0[vmRequestTime]} and is pending approval from you.\n\nRegards,\nBaadal Admin"
                    
VM_APPROVAL_SUBJECT_FOR_FACULTY = "VM pending approval"

VM_RAM_SET = (1024,2048,4096,8192)
VM_vCPU_SET = (1,2,4,8)

