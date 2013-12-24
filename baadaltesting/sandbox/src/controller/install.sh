function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  #package_install libvirt-bin
  package_install virtinst
  disk_create $CONTROLLER_DISK ${CONTROLLER_SPACE}G
  remaster_ubuntu $CONTROLLER_KICKSTART $CONTROLLER_ISO

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
    1>$LOGS/log.out 2>/$LOGS/log.err
  $ECHO_OK Filer Created

  $LOG_CLEAN
}
