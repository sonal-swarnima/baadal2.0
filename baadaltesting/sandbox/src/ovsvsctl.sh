# function for ovs-vsctl add-br
function ovsvsctl_add_br
{
  bridge=$1

  $ECHO_PROGRESS "Adding bridge $bridge"

  ovs-vsctl add-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Adding bridge $bridge failed. Please check logs.
    exit 1
  else
    $ECHO_OK Bridge added $bridge
  fi
}

# function for ovs-vsctl add-br. always pass.
function ovsvsctl_add_br_force
{
  bridge=$1

  $ECHO_PROGRESS "Adding bridge $bridge"

  ovs-vsctl add-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Bridge added $bridge
}

# function for ovs-vsctl add-port
function ovsvsctl_add_port
{
  bridge=$1
  port=$2

  $ECHO_PROGRESS "Adding port $port to bridge $bridge"

  ovs-vsctl add-port $bridge $port 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Adding port $port to bridge $bridge failed. Please check logs.
    exit 1
  else
    $ECHO_OK Port $port added to bridge $bridge
  fi
}

# function for ovs-vsctl del-br
function ovsvsctl_del_br
{
  bridge=$1

  $ECHO_PROGRESS "Deleting bridge $bridge"

  ovs-vsctl del-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Bridge deleted $bridge
}
