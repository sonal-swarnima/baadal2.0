#Task Queue status
TASK_QUEUE_STATUS_PENDING = 1
TASK_QUEUE_STATUS_PROCESSING = 2
TASK_QUEUE_STATUS_SUCCESS = 3
TASK_QUEUE_STATUS_FAILED = 4
TASK_QUEUE_STATUS_RETRY = 5
TASK_QUEUE_STATUS_IGNORE = 6

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
VM_STATUS_APPROVED = 1
VM_STATUS_RUNNING = 2
VM_STATUS_SUSPENDED = 3
VM_STATUS_PAUSED = 4
VM_STATUS_REJECTED = 5

#Startup Data
GROUP_DATA = {'admin':'Super User',
            'faculty':'Faculty User',
            'user':'Normal User'}

ORG_DATA = {'IIT Delhi':'Indian Institude of Technology, Delhi'}

DB_CONSTANTS = {'ifbaadaldown':'0',
              'vmfiles_path':'/mnt/testdatastore',
              'datastore_int':'ds_',
              'ip_range':'10.20.',
              'vncport_range':'5920',
              'templates_dir':'vm_templates',
              'defined_vms':'1700',
              'mac_range':'54:52:00:01:'}

ADMIN = 'admin'
FACULTY = 'faculty'
USER = 'user'

#Added so that changes in modules are instantlly loaded and reflected.
from gluon.custom_import import track_changes; track_changes(True)