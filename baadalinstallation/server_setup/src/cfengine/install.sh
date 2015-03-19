function run
{
  check_root
#  package_update_db
  package_install qemu-kvm
  disk_create $CFENGINE_DISK ${CFENGINE_SPACE}G
  remaster_ubuntu $CFENGINE_KICKSTART $CFENGINE_TRANSFER $CFENGINE_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$CFENGINE_ARCH \
    --name $CFENGINE_NAME \
    --ram=$CFENGINE_RAM \
    --vcpus=$CFENGINE_VCPUS \
    --os-type=Linux \
    --disk path=$CFENGINE_DISK,format=qcow2,size=$CFENGINE_SPACE \
    --cdrom $CFENGINE_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_CFENGINE \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER CFENGINE vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK CFENGINE vm created
  fi
}
