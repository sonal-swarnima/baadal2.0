function run
{
  check_root

  libvirt_install

  # TODO
  # Compile and install libvirt-python bindings
  # and virt-manager

	ovsvsctl_add_br_force $OVS_BRIDGE_EXTERNAL

	ovsvsctl_add_port_force $OVS_BRIDGE_EXTERNAL $OVS_ETHERNET
  ovsvsctl_add_br_force $OVS_BRIDGE_INTERNAL

  ovsvsctl_set_port $OVS_BRIDGE_INTERNAL "tag=1"

  ifconfig $OVS_ETHERNET 0
  dhclient $OVS_BRIDGE_EXTERNAL 2>/dev/null

  ifconfig_ip $OVS_BRIDGE_INTERNAL $NETWORK_INTERNAL_IP_SANDBOX 255.255.0.0 

	mv /etc/network/interfaces /etc/network/interfaces.bak

	cp $OVS_EXTERNAL_CUSTOM_IFS /etc/network/interfaces

  virsh_force "net-destroy $OVS_NET_INTERNAL"
  virsh_force "net-undefine $OVS_NET_INTERNAL"
	virsh_force "net-define $OVS_NET_XML_INTERNAL"
	virsh_force "net-start $OVS_NET_INTERNAL"
	virsh_run "net-autostart $OVS_NET_INTERNAL"

  virsh_force "net-destroy $OVS_NET_EXTERNAL"
  virsh_force "net-undefine $OVS_NET_EXTERNAL"
	virsh_force "net-define $OVS_NET_XML_EXTERNAL"
	virsh_force "net-start $OVS_NET_EXTERNAL"
	virsh_run "net-autostart $OVS_NET_EXTERNAL"

  $ECHO_OK Switch Installation Complete

}

function libvirt_install
{
  VERSION=$(virsh --version 2>/dev/null)
  if [[ $VERSION != "1.2.1" ]]; then
    package_install libpciaccess-dev
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
    tar -xvzf $LIBVIRT_TAR 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt - extract \(check logs\)
      exit 1
    else
      $ECHO_OK libvirt - extract
    fi

    cd $LIBVIRT
    
    $ECHO_PROGRESS "libvirt - configure"
    ./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc 1>>$LOGS/log.out 2>>$LOGS/log.err
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

    libvirtd -d

    cd $pwd
    rm -rf $TEMP
   fi
}
