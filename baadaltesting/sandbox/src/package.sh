# apt-get update to get correct version info from sources
function package_update_db
{
  export http_proxy=http://10.10.78.62:3128/
  echo -e -n "Running apt-get update"
  apt-get update 1>log.out 2>log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    echo -e "\r\033[K[ERR]\tUpdate failed. Check logs."
    exit 1
  else
    echo -e "\r\033[K[OK]\tapt-get update"
    rm log.out
    rm log.err
  fi
}

# function to install a specified package
function package_install
{
  export http_proxy=http://10.10.78.62:3128/
  package=$1
  dpkg -s $package 2>log.err | grep Status | grep installed 1>log.out
  status=$?
  # If debugging needed comment these
  rm log.out
  rm log.err

  if [[ $status -ne 0 ]]; then
    echo -e -n "Installing package : $package"
    apt-get -y install $package --force-yes 1>log.out 2>log.err
    install_status=$?
    if [[ $install_status -ne 0 ]]; then
      echo -e "\r\033[K[ERR]\tInstallation failed. Check logs."
      exit 1
    else
      echo -e "\r\033[K[OK]\tInstalled $package"
      rm log.out
      rm log.err
    fi
  else
    echo -e "[OK]\tAlready installed $package"
  fi
}

