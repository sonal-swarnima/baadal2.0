# function to start a service. will fail and exit if service doesn't start
function service_start
{
  service=$1

  $ECHO_PROGRESS "Starting service $service"

  service $service start 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Failed to start service $service. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Service started $service
  fi
}

# function to restart a service. will faile and exit if service doesn't restart
function service_restart
{
  service=$1

  $ECHO_PROGRESS "Restarting service $service"

  service $service restart 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Failed to restart service $service. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Service restarted $service
  fi
}

# function to stop a service. will never fail
function service_stop
{
  service=$1

  $ECHO_PROGRESS "Stopping service $service"

  service $service stop 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Service stopped $service
}

function kill_all
{
  program=$1

  $ECHO_PROGRESS "Killing the process $program"

  killall $program 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK $program successfully killed
}

function network_restart
{
  service=$1
  $ECHO_PROGRESS "Restarting Networking service"

  $service restart 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Failed to restart service $service. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Service restarted $service
  fi  
}
