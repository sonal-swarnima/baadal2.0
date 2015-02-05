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
VM_TASK_CREATE = 'Create VM'
VM_TASK_START = 'Start VM'
VM_TASK_STOP = 'Stop VM'
VM_TASK_SUSPEND = 'Suspend VM'
VM_TASK_RESUME = 'Resume VM'
VM_TASK_DELETE = 'Delete VM'
VM_TASK_DESTROY = 'Destroy VM'
VM_TASK_DELETE_SNAPSHOT = 'Delete Snapshot'
VM_TASK_REVERT_TO_SNAPSHOT = 'Revert to Snapshot'
VM_TASK_EDIT_CONFIG = 'Edit VM Config'
VM_TASK_SNAPSHOT = 'Snapshot VM'
VM_TASK_CLONE = 'Clone VM'
VM_TASK_ATTACH_DISK = 'Attach Disk'
VM_TASK_MIGRATE_HOST = 'Migrate VM Between Hosts'
VM_TASK_MIGRATE_DS = 'Migrate VM Between Datastores'
VM_TASK_SAVE_AS_TEMPLATE = 'Save As Template'
VM_TASK_DELETE_TEMPLATE = 'Delete Template'
current.VM_TASK_MIGRATE_HOST = VM_TASK_MIGRATE_HOST

#Task Queue Priority
TASK_QUEUE_PRIORITY_LOW = 0
TASK_QUEUE_PRIORITY_NORMAL = 1
TASK_QUEUE_PRIORITY_HIGH = 2
TASK_QUEUE_PRIORITY_URGENT = 3

#Scheduler task
TASK_SNAPSHOT = 'snapshot_vm'
TASK_VM_SANITY = 'vm_sanity'
TASK_HOST_SANITY = 'host_sanity'
TASK_RRD = 'vm_util_rrd'
TASK_VNC = 'vnc_access'
TASK_CLONE_VM = 'clone_task'
TASK_VM = 'vm_task'
TASK_DAILY_CHECKS = 'vm_daily_checks'
TASK_PURGE_UNUSEDVM = 'vm_purge_unused'

#Request Status
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
current.VM_STATUS_UNKNOWN = VM_STATUS_UNKNOWN
current.VM_STATUS_IN_QUEUE = VM_STATUS_IN_QUEUE

#NETWORK
LIBVIRT_NETWORK ='ovs-net'
current.LIBVIRT_NETWORK = LIBVIRT_NETWORK

#STORAGE
STORAGE_NETAPP_NFS = 'netapp_nfs'
STORAGE_LINUX_NFS = 'linux_nfs'

current.STORAGE_NETAPP_NFS = STORAGE_NETAPP_NFS
current.STORAGE_LINUX_NFS = STORAGE_LINUX_NFS

#SNAPSHOTTING LIMIT
SNAPSHOTTING_LIMIT = 3
SNAPSHOT_DAILY=1
SNAPSHOT_WEEKLY=2
SNAPSHOT_MONTHLY=4
SNAPSHOT_YEARLY=8
SNAPSHOT_USER=101
SNAPSHOT_SYSTEM=102
current.SNAPSHOT_USER=SNAPSHOT_USER
current.SNAPSHOT_SYSTEM=SNAPSHOT_SYSTEM

#User status
USER_PENDING_APPROVAL='pending'

ADMIN = 'admin'
ORGADMIN = 'orgadmin'
FACULTY = 'faculty'
USER = 'user'

current.ADMIN = ADMIN
current.ORGADMIN = ORGADMIN
current.FACULTY = FACULTY
current.USER = USER

UUID_SNAPSHOT_DAILY = 'scheduler-uuid-snapshot-daily'
UUID_SNAPSHOT_WEEKLY = 'scheduler-uuid-snapshot-weekly'
UUID_SNAPSHOT_MONTHLY = 'scheduler-uuid-snapshot-monthly'
UUID_VM_SANITY_CHECK = 'scheduler-uuid-vm-sanity-check'
UUID_HOST_SANITY_CHECK = 'scheduler-uuid-host-sanity-check'
UUID_VM_UTIL_RRD = 'scheduler-uuid-vm-util-rrd'
UUID_VNC_ACCESS = 'scheduler-uuid-vnc-access'
UUID_MEMORY_OVERLOAD = 'scheduler-uuid-memory'
UUID_DAILY_CHECKS = 'scheduler-uuid-daily-check'
UUID_PURGE_UNUSEDVM = 'scheduler-uuid-purge-unusedvm'
UUID_HOST_NETWORKING='scheduler-uuid-host-networking'
PUBLIC_IP_NOT_ASSIGNED = "Not Assigned"

ITEMS_PER_PAGE=20

VM_RAM_SET = (256, 512,1024,2048,4096,8192,16384,32768,65536)
VM_vCPU_SET = (1,2,4,8,16)

IP_ERROR_MESSAGE = 'Enter valid IP address'
NAME_ERROR_MESSAGE = 'Name should start with alphanumeric and can only contain letters, numbers, dash and underscore'
SECURITY_DOMAIN_DELETE_MESSAGE = 'There are VMs assigned to this security domain. It can''t be deleted.'
PRIVATE_IP_DELETE_MESSAGE = 'Private IP is assigned to a VM. It can''t be deleted.'
PUBLIC_IP_DELETE_MESSAGE = 'Public IP is assigned to a VM. It can''t be deleted.'

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES
DAYS = 24 * HOURS

BYTE = 1
KILOBYTE = 1024 * BYTE
MEGABYTE = 1024 * KILOBYTE
GIGABYTE = 1024 * MEGABYTE

HOST_VLAN_ID=1

# List of valid CPU and RAM combination
VM_CONFIGURATION = [(1,0.25),(1,0.5),(1,1),(1,2),(2,2),(2,4),(4,4),(4,8),(8,8),(8,16),(16,16)]

MAX_VNC_ALLOWED_IN_A_DAY = 10

SYSTEM_USER = -1
#Added so that changes in modules are instantlly loaded and reflected.
from gluon.custom_import import track_changes; track_changes(True)



