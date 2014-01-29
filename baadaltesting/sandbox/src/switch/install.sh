function run
{
  check_root

  libvirt_install
  virtmanager_install

	ovsvsctl_add_br_force $OVS_BRIDGE_EXTERNAL

	ovsvsctl_add_port_force $OVS_BRIDGE_EXTERNAL $OVS_ETHERNET
  ovsvsctl_add_br_force $OVS_BRIDGE_INTERNAL

  ovsvsctl_set_port $OVS_BRIDGE_INTERNAL "tag=1"

  ifconfig $OVS_ETHERNET 0
  dhclient $OVS_BRIDGE_EXTERNAL 2>/dev/null

  ifconfig_ip $OVS_BRIDGE_INTERNAL $NETWORK_INTERNAL_IP_SANDBOX 255.255.0.0 

	cp /etc/network/interfaces /etc/network/interfaces.bak

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

    libvirtd -d 1>>$LOGS/log.out 2>>$LOGS/log.err

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
