function disk_create
{
  file=$1
  size=$2

  $ECHO_PROGRESS "Creating virtual disk using qemu-img"

  echo $size
  echo $file

  qemu-img create -f qcow2 $file $size 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?
  if [[ $status -ne 0 ]]; then
    $ECHO_ER Disk creation failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err
  else
    $ECHO_OK Virtual disk created.
  fi
}

