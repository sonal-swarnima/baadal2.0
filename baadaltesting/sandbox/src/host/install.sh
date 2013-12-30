function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  package_install virtinst
  package_install virt-manager
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
    --network network=$OVS_NET \
    1>$LOGS/log.out 2>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Host vm creation error. Check logs.
  else
    $ECHO_OK Host vm created
  fi
}
