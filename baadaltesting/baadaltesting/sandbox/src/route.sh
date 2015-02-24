function route_add_net
{
  gateway=$1
  netmask=$2
  device=$3

  $ECHO_PROGRESS "Adding route through $gateway"

  route add -net 0.0.0.0 gw $gateway netmask $netmask $device 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Route add failed \(route add -net 0.0.0.0 gw $gateway netmask $netmask $device\). Check logs
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK route add -net 0.0.0.0 gw $gateway netmask $netmask $device 
  fi
}

function route_del_net
{
  gateway=$1
  netmask=$2
  device=$3

  $ECHO_PROGRESS "Deleting route through $gateway"

  route del -net 0.0.0.0 gw $gateway netmask $netmask $device 1>>$LOGS/log.out 2>>$LOGS/log.err
  
  $ECHO_OK route del -net 0.0.0.0 gw $gateway netmask $netmask $device 
}
