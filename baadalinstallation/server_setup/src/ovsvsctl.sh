# function for ovs-vsctl add-br
function ovsvsctl_add_br
{
  bridge=$1

  $ECHO_PROGRESS "Adding bridge $bridge"

  ovs-vsctl add-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Adding bridge $bridge failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err 
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

# function for ovs-vsctl add-br. always pass.
function ovsvsctl_add_fake_br_force
{
  fake=$1
  bridge=$2
  tag=$3

  $ECHO_PROGRESS "Adding fake bridge $fake $bridge $tag"

  ovs-vsctl add-br $fake $bridge $tag 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Fake Bridge added $fake $bridge $tag
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
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Port $port added to bridge $bridge
  fi
}

# function for ovs-vsctl set port
function ovsvsctl_set_port
{
  port=$1
  arg=$2

  $ECHO_PROGRESS "Setting port $port parameter"

  ovs-vsctl set port $port $arg 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Setting port $port parameter failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Port $port parameter set.
  fi
}

# function for ovs-vsctl set bridge
function ovsvsctl_set_bridge
{
  bridge=$1
  arg=$2

  $ECHO_PROGRESS "Setting bridge $port parameter"

  ovs-vsctl set bridge $bridge $arg 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Setting bridge $port parameter failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err
    exit 1
  else
    $ECHO_OK Bridge $port parameter set.
  fi
}

# function for ovs-vsctl add-port
function ovsvsctl_add_port_force
{
  bridge=$1
  port=$2

  $ECHO_PROGRESS "Adding port $port to bridge $bridge"

  ovs-vsctl add-port $bridge $port 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Port $port added to bridge $bridge
}

# function for ovs-vsctl del-br
function ovsvsctl_del_br
{
  bridge=$1

  $ECHO_PROGRESS "Deleting bridge $bridge"

  ovs-vsctl del-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Bridge deleted $bridge
}

# function for ovs-vsctl del-port
function ovsvsctl_del_port
{
  bridge=$1
  port=$2

  $ECHO_PROGRESS "Deleting port $port"

  ovs-vsctl del-port $bridge $port 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Port deleted $port
}
