function run
{
  check_root
#  package_update_db
  package_install qemu-kvm
  disk_create $HAPROXY_DISK ${HAPROXY_SPACE}G
  remaster_ubuntu $HAPROXY_KICKSTART $HAPROXY_TRANSFER $HAPROXY_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$HAPROXY_ARCH \
    --name $HAPROXY_NAME \
    --ram=$HAPROXY_RAM \
    --vcpus=$HAPROXY_VCPUS \
    --os-type=Linux \
    --disk path=$HAPROXY_DISK,format=qcow2,size=$HAPROXY_SPACE \
    --cdrom $HAPROXY_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_HAPROXY \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER HAPROXY vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK HAPROXY vm created
  fi
}
