function kernelmod_remove
{
  module=$1
  $ECHO_PROGRESS "Removing module $module"
  rmmod $module 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Removed module $module
}
