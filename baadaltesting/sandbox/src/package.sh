# apt-get update to get correct version info from sources
function package_update_db
{
  #export http_proxy=http://10.10.78.62:3128/
  $ECHO_PROGRESS "Running apt-get update"
  apt-get update 1>$LOGS/log.out 2>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Update failed. Check logs.
    exit 1
  else
    $ECHO_OK apt-get update
    $LOG_CLEAN
  fi
}

# function to install a specified package
function package_install
{
  #export http_proxy=http://10.10.78.62:3128/
  package=$1
  dpkg -s $package 2>$LOGS/log.err | grep Status | grep installed 1>$LOGS/log.out
  status=$?
  $LOG_CLEAN

  if [[ $status -ne 0 ]]; then
    $ECHO_PROGRESS "Installing package : $package"
    apt-get -y install $package --force-yes 1>$LOGS/log.out 2>$LOGS/log.err
    install_status=$?
    if [[ $install_status -ne 0 ]]; then
      $ECHO_ER Installation failed. Check logs.
      exit 1
    else
      $ECHO_OK Installed $package
      $LOG_CLEAN
    fi
  else
    $ECHO_OK Already installed $package
  fi
}

