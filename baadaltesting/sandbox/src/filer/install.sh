function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  package_install virtinst
  disk_create $FILER_DISK ${FILER_SPACE}G
  remaster_ubuntu $FILER_KICKSTART $FILER_ISO

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
    1>$LOGS/log.out 2>/$LOGS/log.err
  $ECHO_OK Filer Created
}
