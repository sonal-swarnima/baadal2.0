#Funtion to check root login
function check_root
{
  $ECHO_PROGRESS "Checking root"
  username=`whoami`
  if test $username != "root"; then
    $ECHO_ER Root Check
    exit 1
  fi

  $ECHO_OK Root Check
}

