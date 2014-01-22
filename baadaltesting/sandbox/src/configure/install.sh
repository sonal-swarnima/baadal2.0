function run
{
  # TODO
  # sed in sandbox's /etc/network/interfaces -> src/switch/interfaces

  maxValue=255
  count=4
  default=0.0.0.0
        
  echo -e "\n\nWelcome to Baadal Sandbox Setup\n"
  echo "Enter the starting IP Address(Internal) for the management systems "
  echo "(If you want to use previously defined/default values enter 0.0.0.0)"
  read start_ip

  baseaddr="$(echo $start_ip | cut -d. -f1-3)"
  lastaddr="$(echo $start_ip | cut -d. -f4)"

  if [ "$start_ip" == "$default" ]
  then
    echo "Using previously defined/default IP Addresses"
    return 0
  fi

  if [ $(($lastaddr+$count)) -ge $maxValue ] 
  then
    $ECHO_ER Your IP Address does not have the required $count addresses free.
    $ECHO_ER The last value of IP Address must be less than 252
    exit 1
  fi

  echo "Enter the subnet mask for the internal network"
  read subnet
  echo "Enter the default nameserver for the internal network"
  read nameserver

  NETWORK_INTERNAL_IP_SANDBOX=$baseaddr.$lastaddr
  sed -i "/NETWORK_INTERNAL_IP_SANDBOX=/c\NETWORK_INTERNAL_IP_SANDBOX=$baseaddr.$lastaddr" $CONFIGURE

  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_CONTROLLER=$baseaddr.$lastaddr
  sed -i "/NETWORK_INTERNAL_IP_CONTROLLER=/c\NETWORK_INTERNAL_IP_CONTROLLER=$baseaddr.$lastaddr" $CONFIGURE

  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_NAT=$baseaddr.$lastaddr
  sed -i "/NETWORK_INTERNAL_IP_NAT=/c\NETWORK_INTERNAL_IP_NAT=$baseaddr.$lastaddr" $CONFIGURE

  lastaddr=$(( $lastaddr + 1 ))
  NETWORK_INTERNAL_IP_FILER=$baseaddr.$lastaddr
  sed -i "/NETWORK_INTERNAL_IP_FILER=/c\NETWORK_INTERNAL_IP_FILER=$baseaddr.$lastaddr" $CONFIGURE

  gateway=$NETWORK_INTERNAL_IP_NAT

  sed -i "/network --bootproto=static/c\network --bootproto=static --ip=$NETWORK_INTERNAL_IP_NAT --netmask=$subnet --gateway=$gateway --nameserver=$nameserver --hostname=$NAT_HOSTNAME --device=eth1" $NAT_KS
  sed -i "/network --bootproto=static/c\network --bootproto=static --ip=$NETWORK_INTERNAL_IP_CONTROLLER --netmask=$subnet --gateway=$gateway --nameserver=$nameserver --hostname=$CONTROLLER_HOSTNAME --device=eth0" $CONTROLLER_KS
  sed -i "/network --bootproto=static/c\network --bootproto=static --ip=$NETWORK_INTERNAL_IP_FILER --netmask=$subnet --gateway=$gateway --nameserver=$nameserver --hostname=$FILER_HOSTNAME --device=eth0" $FILER_KS
}


