function run
{
  check_root

  package_install dnsmasq

  libvirt_install
  virtmanager_install
    
  libvirtd -d 1>>$LOGS/log.out 2>>$LOGS/log.err

  ovsvsctl_del_br $OVS_BRIDGE_EXTERNAL
  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL

	ovsvsctl_add_br $OVS_BRIDGE_EXTERNAL

  config_get INTERFACE
	ovsvsctl_add_port $OVS_BRIDGE_EXTERNAL $INTERFACE
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_set_port $OVS_BRIDGE_INTERNAL "tag=1"

  ifconfig $INTERFACE 0
  ifconfig_dhcp $OVS_BRIDGE_EXTERNAL

  config_get NETWORK_INTERNAL_IP_SANDBOX
  ifconfig_ip $OVS_BRIDGE_INTERNAL $NETWORK_INTERNAL_IP_SANDBOX $VLAN_NETMASK

  file_backup /etc/network/interfaces
  
  interfaces_str=" auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $OVS_BRIDGE_EXTERNAL\n
  iface $OVS_BRIDGE_EXTERNAL inet dhcp\n
  \n
  auto $INTERFACE\n
  iface $INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet static\n
  address $NETWORK_INTERNAL_IP_SANDBOX\n
  netmask $VLAN_NETMASK\n
  "
  echo -e $interfaces_str > /etc/network/interfaces

  virsh_force "net-destroy $OVS_NET_INTERNAL"
  virsh_force "net-undefine $OVS_NET_INTERNAL"
	virsh_run "net-define $OVS_NET_XML_INTERNAL"
	virsh_run "net-start $OVS_NET_INTERNAL"
	virsh_run "net-autostart $OVS_NET_INTERNAL"

  virsh_force "net-destroy $OVS_NET_EXTERNAL"
  virsh_force "net-undefine $OVS_NET_EXTERNAL"
	virsh_run "net-define $OVS_NET_XML_EXTERNAL"
	virsh_run "net-start $OVS_NET_EXTERNAL"
	virsh_run "net-autostart $OVS_NET_EXTERNAL"

  config_get NETWORK_INTERNAL
  config_get NETWORK_INTERNAL_IP_SANDBOX
  config_get NETWORK_INTERNAL_IP_CONTROLLER
  config_get NETWORK_INTERNAL_IP_NAT
  config_get NETWORK_INTERNAL_IP_FILER

  $ECHO_PROGRESS "dnsmasq"
  
  # Not really a good idea
  killall dnsmasq 2>/dev/null

  dnsmasq \
    --listen-address=$NETWORK_INTERNAL_IP_SANDBOX \
    --bind-interfaces \
    --dhcp-mac=nat,$MAC_NAT \
    --dhcp-host=$MAC_CONTROLLER,$NETWORK_INTERNAL_IP_CONTROLLER \
    --dhcp-host=$MAC_NAT,$NETWORK_INTERNAL_IP_NAT \
    --dhcp-host=$MAC_FILER,$NETWORK_INTERNAL_IP_FILER \
    --dhcp-option=nat,option:router,0.0.0.0 \
    --dhcp-option=3,$NETWORK_INTERNAL_IP_GATEWAY \
    --dhcp-range=$NETWORK_INTERNAL,static
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER dnsmasq \(check logs\)
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
      $ECHO_OK dnsmasq
  fi

  $ECHO_OK Switch Installation Complete
}

function libvirt_install
{
  VERSION=$(virsh --version 2>/dev/null)
  if [[ $VERSION != "1.2.1" || ${LIBVIRT_INSTALL} == "yes" ]]; then
    package_install libxml2-dev
    package_install libgnutls-dev
    package_install libyajl-dev
    package_install libdevmapper-dev
    package_install libcurl4-gnutls-dev
    package_install python-dev
    package_install libnl-dev
    package_install libpciaccess-dev
    package_install python

    dir=$pwd

    mkdir -p $TEMP
    cd $TEMP

    $ECHO_PROGRESS "libvirt - extract"
    tar -xvzf $LIBVIRT_TAR 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt - extract \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
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
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK libvirt - configure
    fi

    file_backup $(which libvirtd)
    kill_all libvirtd

    $ECHO_PROGRESS "libvirt - make"
    make 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt - make \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK libvirt - make
    fi

    $ECHO_PROGRESS "libvirt - make install"
    make install 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt - make install \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK libvirt - make install
    fi
    
    cd $pwd
    rm -rf $TEMP


    # Python-Bindings
    dir=$pwd

    cd $LIBVIRTPYTHON_DIR

    $ECHO_PROGRESS "libvirt-python - build"
    python setup.py build 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt-python - build \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK libvirt-python - build
    fi

    $ECHO_PROGRESS "libvirt-python - install"
    python setup.py install 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER libvirt-python - install \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK libvirt-python - install
    fi

    cd $pwd

   fi
}

function virtmanager_install
{
  VERSION=$(virt-install --version 2>&1)
  if [[ $VERSION != "0.10.0" || ${VIRTMANAGER_INSTALL} == "yes" ]]; then
    package_install gconf2
    package_install librsvg2-common
    package_install python
    package_install python-appindicator
    package_install python-dbus
    package_install python-glade2
    package_install python-gnome2
    package_install python-gtk-vnc
    package_install python-gtk2
    package_install python-urlgrabber
    package_install python-vte
    package_install intltool
    package_install libvirt-glib-1.0-dev

    dir=$pwd

    mkdir -p $TEMP
    cd $TEMP

    $ECHO_PROGRESS "virt-manager - extract"
    tar -xvzf $VIRTMANAGER_TAR 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER virt-manager - extract \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK virt-manager - extract
    fi

    cd $VIRTMANAGER
    
    $ECHO_PROGRESS "virt-manager - install"
    python setup.py install --prefix=/usr 1>>$LOGS/log.out 2>>$LOGS/log.err
    status=$?

    if [[ $status -ne 0 ]]; then
      $ECHO_ER virt-manager - install \(check logs\)
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK virt-manager - install
    fi

    cd $pwd
    rm -rf $TEMP
   fi
}
