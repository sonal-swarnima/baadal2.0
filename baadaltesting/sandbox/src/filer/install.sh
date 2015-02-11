function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  disk_create $FILER_DISK ${FILER_SPACE}G
  remaster_ubuntu $FILER_KICKSTART $FILER_TRANSFER $FILER_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$FILER_ARCH \
    --name $FILER_NAME \
    --ram=$FILER_RAM \
    --vcpus=$FILER_VCPUS \
    --os-type=Linux \
    --disk path=$FILER_DISK,format=qcow2,size=$FILER_SPACE \
    --cdrom $FILER_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_FILER \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Filer vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK Filer vm created
  fi
}
