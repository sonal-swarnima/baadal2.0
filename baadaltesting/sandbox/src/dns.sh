function dns_get
{
  if [[ $DNS != '' ]]; then
    dns=$DNS
  else
    dns=$(cat /var/run/dnsmasq/resolv.conf | grep "nameserver" | sed "s:nameserver ::g" | head -n 1)
  fi

  package_install ipcalc
  ipcalc -b $dns | tee -a $LOGS/log.err | grep INVALID\ ADDRESS 1>>$LOGS/log.out
  status=$?

  if [[ $status -eq 0 ]]; then
    dns=$(cat /etc/resolv.conf | grep "nameserver" | sed "s:nameserver ::g" | head -n 1)

    ipcalc -b $dns | tee -a $LOGS/log.err | grep INVALID\ ADDRESS 1>>$LOGS/log.out
    status=$?

    if [[ $status -eq 0 ]]; then
      $ECHO_ER Failed to retrieve DNS info from sandbox system \(check logs\) OR \
        manually specify DNS as \'make switch DNS=a.b.c.d\' or \'make controller-setup DNS=a.b.c.d\'
      tail -15 $LOGS/log.err
      exit 1
    else
      $ECHO_OK DNS = $dns
    fi
  else
    $ECHO_OK DNS = $dns
  fi
}
