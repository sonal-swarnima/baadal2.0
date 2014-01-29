function iptables_run
{
  command=$1

  $ECHO_PROGRESS "iptables $command"
  iptables $command 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER iptables $command failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK iptables $command
  fi
}
