#Funtion to check root login
function check_root
{
  echo -e -n "Checking root"
  username=`whoami`
  if test $username != "root"; then
    echo -e "\r\033[K[ERR]\tRoot Check"
    exit 1
  fi

  echo -e "\r\033[K[OK]\tRoot Check"
}

