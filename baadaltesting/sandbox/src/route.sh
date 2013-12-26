function route_add
{
  ip=$1
  gateway=$2
  netmask=$3
  iface=$4

  $ECHO_PROGRESS "Adding route entry for $ip"

  route add -net $ip gw $gateway netmask $netmask $iface 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Route add $ip failed. Check logs.
    exit 1
  else
    $ECHO_OK Route added $ip
  fi
}

function route_del
{
  ip=$1
  gateway=$2
  netmask=$3
  iface=$4

  $ECHO_PROGRESS "Deleting route entry for $ip"

  route del -net $ip gw $gateway netmask $netmask $iface 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Route added $ip
}
