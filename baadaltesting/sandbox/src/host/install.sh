function run
{
  check_root
  #package_update_db
  package_install qemu-kvm virt-what

  echo "\n"
  echo $HOST_SPACE
  echo "\n"

  disk_create $HOST_DISK ${HOST_SPACE}G

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$HOST_ARCH \
    --name $HOST_NAME \
    --ram=$HOST_RAM \
    --vcpus=$HOST_VCPUS \
    --os-type=Linux \
    --disk path=$HOST_DISK,format=qcow2,size=$HOST_SPACE \
    --pxe \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_HOST \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Host vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK Host vm created
  fi
}
