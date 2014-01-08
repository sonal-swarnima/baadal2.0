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
REQ_STATUS_FAILED    =-1
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
SNAPSHOT_DAILY=1
SNAPSHOT_WEEKLY=1
SNAPSHOT_MONTHLY=2
SNAPSHOT_YEARLY=3
SNAPSHOT_USER=4
current.SNAPSHOT_USER=SNAPSHOT_USER

ADMIN = 'admin'
ORGADMIN = 'orgadmin'
FACULTY = 'faculty'
USER = 'user'

current.ADMIN = ADMIN
current.ORGADMIN = ORGADMIN
current.FACULTY = FACULTY
current.USER = USER

PUBLIC_IP_NOT_ASSIGNED = "Not Assigned"
current.PUBLIC_IP_NOT_ASSIGNED = PUBLIC_IP_NOT_ASSIGNED

ITEMS_PER_PAGE=20

#Email templates and subject constants
VM_CREATION_TEMPLATE="Dear {0[userName]},\n\nThe VM {0[vmName]} requested on {0[vmRequestTime]} is successfully created and is now available for use. The following operations are allowed on the VM:\n1. Start\n2. Stop\n3. Pause\n4. Resume\n5. Destroy\n6. Delete\n\nRegards,\nBaadal Admin"

VM_CREATION_SUBJECT = "VM created successfully"

VM_REQUEST_TEMPLATE_FOR_USER="Dear {0[userName]},\n\nYour request for VM({0[vmName]}) creation has been successfully registered. Please note that you will be getting a separate email on successful VM creation.\n\nRegards,\nBaadal Admin"
                    
VM_REQUEST_SUBJECT_FOR_USER = "VM request successful"
                    
REQ_APPROVAL_REMINDER_TEMPLATE ="Dear {0[approverName]},\n\n{0[userName]} has made a {0[requestType]} request on {0[requestTime]}. It is waiting for your approval.\n\nRegards,\nBaadal Admin"
                    
REQ_APPROVAL_REMINDER_SUBJECT = "Request waiting for your approval"

VM_RAM_SET = (1024,2048,4096,8192)
VM_vCPU_SET = (1,2,4,8)

IP_ERROR_MESSAGE = 'Enter valid IP address'

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS

VM_UTIL_24_HOURS = 1
VM_UTIL_ONE_WEEK = 2
VM_UTIL_ONE_MNTH = 3
VM_UTIL_ONE_YEAR = 4
#Added so that changes in modules are instantlly loaded and reflected.
from gluon.custom_import import track_changes; track_changes(True)