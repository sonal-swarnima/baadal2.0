function run
{ 
 
  $ECHO_PROGRESS "Checking root"
  username=`whoami`
  if test $username != "root"; then
    $ECHO_ER Root Check
    exit 1
  fi

  hostname="$(uname -n)"
  if [ "$hostname" != "$PXE_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $PXE_HOSTNAME. This script should be run on PXE.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi

  dns_get
  # config_get CONTROLLER_INTERFACE

  PXEDHCP_INTERFACE=`ip route get 8.8.8.8 | awk '{ print $5; exit }'`
  
  ovsvsctl_del_br $DHCP_BRIDGE_INTERNAL

  ovsvsctl_add_br $DHCP_BRIDGE_INTERNAL
  
  ovsvsctl_add_port $DHCP_BRIDGE_INTERNAL $PXEDHCP_INTERFACE
  ovsvsctl_set_port $PXEDHCP_INTERFACE "vlan_mode=native-untagged"
  INTERFACE_MAC=$(cat /sys/class/net/$PXEDHCP_INTERFACE/address)
  ovsvsctl_set_bridge $DHCP_BRIDGE_INTERNAL "other-config:hwaddr=$INTERFACE_MAC"
   
  #Get the IP Address of Controller from ifconfig.
  pxedhcp_ip="$(/sbin/ifconfig $PXEDHCP_INTERFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  INTERNAL_GATEWAY_IP=$(ip route | awk '/default/{print $3}')
  ifconfig_noip $PXEDHCP_INTERFACE
  ifconfig_ip $DHCP_BRIDGE_INTERNAL $controller_ip $VLAN_NETMASK
  route_add_net $INTERNAL_GATEWAY_IP 0.0.0.0 $DHCP_BRIDGE_INTERNAL

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  baseaddr="$(echo $pxedhcp_ip | cut -d. -f1-2)"
  
  echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
  echo 1 > /proc/sys/net/ipv4/ip_forward

  trunk_str=""
  ovs_str=""
  interfaces_str="auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $PXEDHCP_INTERFACE\n
  iface $PXEDHCP_INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $DHCP_BRIDGE_INTERNAL\n
  iface $DHCP_BRIDGE_INTERNAL inet static\n
  address $pxedhcp_ip\n
  netmask $VLAN_NETMASK\n
  dns-nameservers $dns\n
  gateway $NETWORK_INTERNAL_IP_NAT\n
  "
 
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $DHCP_BRIDGE_INTERNAL $i
      ifconfig_ip vlan$i $baseaddr.$i.2 $VLAN_NETMASK
      interfaces_str+="\n
      auto vlan$i\n
      iface vlan$i inet static\n
      address $baseaddr.$i.2\n
      netmask $VLAN_NETMASK\n
      "
      trunk_str+="$i,"
  done

  # NOTE TO DEVELOPER
  # Apparently trunking is not needed here. This is because an openvswitch
  # interface will act as trunk port for all vlans by default if there are
  # no trunk values as well as no tag values defined for the interface. It
  # should be better is these things are explicitly defined as this is not
  # well documented in openvswitch's docs. If any trunk value or tag value
  # is defined for an interface on openvswitch then it automatically won't
  # work as trunk for all other remaining vlans. In baadal's current state
  # eth0 will act as trunk for vlans 1-255 and will filter out traffic for
  # all other vlans.
  trunk_str="$(echo ${trunk_str:0:-1})"
  trunk_str="trunk=[$trunk_str]"
  ovsvsctl_set_port $PXEDHCP_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
}   

