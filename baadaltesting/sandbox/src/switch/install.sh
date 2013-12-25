function run
{
  check_root
  #package_update_db
  package_install qemu-kvm
  package_install virtinst

  libvirt_install

  virsh_force "net-destroy default"
  virsh_force "net-autostart --disable default"

  ovsvsctl_del_br $OVS_BRIDGE

  package_install aptitude
  package_remove ebtables

  service_restart libvirt-bin

  package_install openvswitch-datapath-lts-raring-dkms
  package_install openvswitch-datapath-lts-raring-source

  file_copy $BRCOMPAT_SRC $BRCOMPAT_DST
  kernelmod_remove bridge

  package_install openvswitch-controller
  package_install openvswitch-switch
  package_install openvswitch-brcompat
 
  service_start openvswitch-switch

  file_copy $OVS_IFUP_SRC $OVS_IFUP_DST
  file_copy $OVS_IFDOWN_SRC $OVS_IFDOWN_DST

  ovsvsctl_add_br $OVS_BRIDGE
  ovsvsctl_add_port $OVS_BRIDGE $OVS_ETHERNET

  virsh_run "net-define $OVS_NET_XML"
  virsh_run "net-start $OVS_NET"
  virsh_run "net-autostart $OVS_NET"
  #file_backup $INTERFACES_DST
}

function libvirt_install
{
  package_install libxml2-dev
  package_install libgnutls-dev
  package_install libyajl-dev
  package_install libdevmapper-dev
  package_install libcurl4-gnutls-dev
  package_install python-dev
  package_install libnl-dev

  dir=$pwd

  mkdir -p $TEMP
  cd $TEMP

  $ECHO_PROGRESS "libvirt - extract"
  tar -xvzf $LIBVIRT 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER libvirt - extract \(check logs\)
    exit 1
  else
    $ECHO_OK libvirt - extract
  fi

  cd libvirt-1.0.0
  
  $ECHO_PROGRESS "libvirt - configure"
  ./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER libvirt - configure \(check logs\)
    exit 1
  else
    $ECHO_OK libvirt - configure
  fi

  $ECHO_PROGRESS "libvirt - make"
  make 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER libvirt - make \(check logs\)
    exit 1
  else
    $ECHO_OK libvirt - make
  fi

  $ECHO_PROGRESS "libvirt - make install"
  make install 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER libvirt - make install \(check logs\)
    exit 1
  else
    $ECHO_OK libvirt - make install
  fi

  service_restart libvirt-bin

  cd $pwd
  rm -rf $TEMP
}
