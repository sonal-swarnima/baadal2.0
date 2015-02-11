function kernelmod_remove
{
  module=$1
  $ECHO_PROGRESS "Removing module $module"
  rmmod $module 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Removed module $module
}

function kernelmod_modprobe 
{
  module=$1
  $ECHO_PROGRESS "modprobe $module"
  modprobe $module 1>>$LOGS/log.out 2>>$LOGS/log.err

  if [[ $status -ne 0 ]]; then
    $ECHO_ER modprobe $module failed. Check logs.
    exit 1
  else
    $ECHO_OK modprobe $module
    tail -$LOG_SIZE $LOGS/log.err 
  fi
}
