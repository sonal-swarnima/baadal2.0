function run
{
  check_root
#  package_update_db
  package_install qemu-kvm
  disk_create /root/disk/pxe_dhcp.img ${PXE_SPACE}G
  remaster_ubuntu $PXE_KICKSTART $PXE_TRANSFER $PXE_ISO

  $ECHO_PROGRESS Installing OS
  virt-install \
    --connect qemu:///system \
    --accelerate \
    --arch=$PXE_ARCH \
    --name $PXE_NAME \
    --ram=$PXE_RAM \
    --vcpus=$PXE_VCPUS \
    --os-type=Linux \
    --disk path=/root/disk/pxe_dhcp.img,format=qcow2,size=$PXE_SPACE \
    --cdrom $PXE_ISO \
    --network network=$OVS_NET_INTERNAL,mac=$MAC_PXE \
    --noautoconsole \
    --graphics vnc,listen=0.0.0.0 \
    1>>$LOGS/log.out 2>>/$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER PXE vm creation error. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
  else
    $ECHO_OK PXE vm created
  fi
}
