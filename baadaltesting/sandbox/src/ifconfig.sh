function ifconfig_ip
{
  iface=$1
  ip=$2
  netmask=$3

  $ECHO_PROGRESS "ifconfig $iface $ip netmask $netmask"
  ifconfig $iface $ip netmask $netmask 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER ifconfig $iface $ip netmask $netmask failed. Check logs.
    exit 1
  else
    $ECHO_OK ifconfig $iface $ip netmask $netmask
  fi
}

function ifconfig_up
{
  iface=$1

  $ECHO_PROGRESS "ifconfig $iface up"
  ifconfig $iface up 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER ifconfig $iface up failed. Check logs.
    exit 1
  else
    $ECHO_OK ifconfig $iface up
  fi
}

function ifconfig_down
{
  iface=$1

  $ECHO_PROGRESS "ifconfig $iface down"
  ifconfig $iface down 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER ifconfig $iface down failed. Check logs.
    exit 1
  else
    $ECHO_OK ifconfig $iface down
  fi
}
