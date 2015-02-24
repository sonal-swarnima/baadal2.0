function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  disk_create $CONTROLLER_DISK ${CONTROLLER_SPACE}G
  remaster_ubuntu $CONTROLLER_KICKSTART $CONTROLLER_TRANSFER $CONTROLLER_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$CONTROLLER_ARCH \
    --name $CONTROLLER_NAME \
    --ram=$CONTROLLER_RAM \
    --vcpus=$CONTROLLER_VCPUS \
    --os-type=Linux \
    --disk path=$CONTROLLER_DISK,format=qcow2,size=$CONTROLLER_SPACE \
    --cdrom $CONTROLLER_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_CONTROLLER \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Controller vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK Controller vm created
  fi
}
