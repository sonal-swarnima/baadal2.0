# apt-get update to get correct version info from sources
function package_update_db
{
  #export http_proxy=http://10.10.78.62:3128/
  $ECHO_PROGRESS "Running apt-get update"
  apt-get update 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Update failed. Check logs.
    exit 1
  else
    $ECHO_OK apt-get update
    tail -$LOG_SIZE $LOGS/log.err 
  fi
}

# function to install a specified package
function package_install
{
  #export http_proxy=http://10.10.78.62:3128/
  package=$1
  dpkg -s $package 2>>$LOGS/log.err | grep Status | grep installed 1>>$LOGS/log.out
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_PROGRESS "Installing package : $package"
    apt-get -y install $package --force-yes 1>>$LOGS/log.out 2>>$LOGS/log.err
    install_status=$?
    if [[ $install_status -ne 0 ]]; then
      $ECHO_ER Installation failed. Check logs.
      tail -$LOG_SIZE $LOGS/log.err 
      exit 1
    else
      $ECHO_OK Installed $package
    fi
  else
    $ECHO_OK Already installed $package
  fi
}

# function to remove a specified package
function package_remove
{
  package=$1
  $ECHO_PROGRESS "Removing $package"
  aptitude purge -y $package 1>>$LOGS/log.out 2>>$LOGS/log.err
  $ECHO_OK Removed $package
}

function libvirt_install
{
  VERSION=$(virsh --version 2>/dev/null)
  if [[ $VERSION != "1.2.6" || ${LIBVIRT_INSTALL} == "yes" ]]; then
    package_install libxml2-dev
    package_install libgnutls-dev
    package_install libyajl-dev
    package_install libdevmapper-dev
    package_install libcurl4-gnutls-dev
    package_install python-dev
    package_install libnl-dev
    package_install libpciaccess-dev
    package_install python
    package_install uuid-dev

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

    $ECHO_PROGRESS "libvirt-python-1.2.6 - build"
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
    package_install libglib2.0-dev
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
