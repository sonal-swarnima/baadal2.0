function run
{
  # FIXME
  # sed in sandbox's /etc/network/interfaces -> src/switch/interfaces

  config_get NETWORK_INTERNAL 
        
  echo -e "\n\nWelcome to Baadal Sandbox Setup\n"
  echo "Enter the Network Address (Internal) for the management systems in form x.y.0.0 (default $NETWORK_INTERNAL) : "
  read start_ip

  if [ "$start_ip" == "" ]
  then
    start_ip=$NETWORK_INTERNAL
  fi

  baseaddr="$(echo $start_ip | cut -d. -f1-3)"
  lastaddr="$(echo $start_ip | cut -d. -f4)"
  qualifier="$(echo $start_ip | cut -d. -f3-4)"

  if [ "$qualifier" != "0.0" ] 
  then
    $ECHO_ER Your IP Address is not of form x.y.0.0
    exit 1
  fi

  NETWORK_INTERNAL=$baseaddr.$lastaddr
  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_SANDBOX=$baseaddr.$lastaddr
  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_CONTROLLER=$baseaddr.$lastaddr
  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_NAT=$baseaddr.$lastaddr
  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_FILER=$baseaddr.$lastaddr

  config_set NETWORK_INTERNAL
  config_set NETWORK_INTERNAL_IP_SANDBOX
  config_set NETWORK_INTERNAL_IP_CONTROLLER
  config_set NETWORK_INTERNAL_IP_NAT
  config_set NETWORK_INTERNAL_IP_FILER
}
