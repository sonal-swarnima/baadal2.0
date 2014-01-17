function run
{
  check_root
  sandbox_setup 
}

function libvirt_install
{
  VERSION=$(virsh --version 2>/dev/null)
  if [[ $VERSION != "1.0.0" ]]; then
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
   fi
}
