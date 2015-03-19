function run
{
  check_root
#  package_update_db
  package_install qemu-kvm
  disk_create $MYSQL_DISK ${MYSQL_SPACE}G
  remaster_ubuntu $MYSQL_KICKSTART $MYSQL_TRANSFER $MYSQL_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$MYSQL_ARCH \
    --name $MYSQL_NAME \
    --ram=$MYSQL_RAM \
    --vcpus=$MYSQL_VCPUS \
    --os-type=Linux \
    --disk path=$MYSQL_DISK,format=qcow2,size=$MYSQL_SPACE \
    --cdrom $MYSQL_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_MYSQL \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER MYSQL vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK MYSQL vm created
  fi
}
