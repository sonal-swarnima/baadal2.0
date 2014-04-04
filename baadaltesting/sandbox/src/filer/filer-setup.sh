function run
{
  check_root
 
  # nfs-kernel-server should already be installed

  file_run "mkdir -p /baadal/data/vm_deleted"
  file_run "mkdir -p /baadal/data/vm_extra_disks"
  file_run "mkdir -p /baadal/data/vm_images"
  file_run "mkdir -p /baadal/data/vm_migration_data"
  file_run "mkdir -p /baadal/data/vm_rrds"
  file_run "mkdir -p /baadal/data/vm_templates"
  
  chmod 757 -R /baadal/data

  config_get NETWORK_INTERNAL
  exports_str="/baadal/data $NETWORK_INTERNAL/16(rw,sync,no_root_squash,no_all_squash,subtree_check)\n"

  echo -e $exports_str > /etc/exports

  service nfs-kernel-server restart 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER service nfs-kernel-server restart
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK service nfs-kernel-server restart
  fi

  $ECHO_OK Filer has been setup.
}
