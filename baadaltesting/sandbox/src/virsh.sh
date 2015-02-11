function virsh_run
{
  run_command=$1

  $ECHO_PROGRESS "virsh $run_command"

  virsh $run_command 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER virsh $run_command failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK virsh $run_command
  fi
}

# will always pass
function virsh_force
{
  run_command=$1

  $ECHO_PROGRESS "virsh $run_command"

  virsh $run_command 1>>$LOGS/log.out 2>>$LOGS/log.err
  
  $ECHO_OK virsh $run_command
}
