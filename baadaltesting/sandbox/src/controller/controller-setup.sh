function run
{  
  check_root
  
  hostname="$(uname -n)"
  if [ "$hostname" != "$CONTROLLER_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $CONTROLLER_HOSTNAME. This script should be run on CONTROLLER.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi

  dns_get
  config_get CONTROLLER_INTERFACE

  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL
  
  ovsvsctl_add_port $OVS_BRIDGE_INTERNAL $CONTROLLER_INTERFACE
  ovsvsctl_set_port $CONTROLLER_INTERFACE "vlan_mode=native-untagged"
  INTERFACE_MAC=$(cat /sys/class/net/$CONTROLLER_INTERFACE/address)
  ovsvsctl_set_bridge $OVS_BRIDGE_INTERNAL "other-config:hwaddr=$INTERFACE_MAC"
   
  #Get the IP Address of Controller from ifconfig.
  controller_ip="$(/sbin/ifconfig $CONTROLLER_INTERFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  INTERNAL_GATEWAY_IP=$(ip route | awk '/default/{print $3}')
  ifconfig_noip $CONTROLLER_INTERFACE
  ifconfig_ip $OVS_BRIDGE_INTERNAL $controller_ip $VLAN_NETMASK
  route_add_net $INTERNAL_GATEWAY_IP 0.0.0.0 $OVS_BRIDGE_INTERNAL

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  baseaddr="$(echo $controller_ip | cut -d. -f1-2)"
  
  echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
  echo 1 > /proc/sys/net/ipv4/ip_forward

  trunk_str=""
  ovs_str=""
  interfaces_str="auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $CONTROLLER_INTERFACE\n
  iface $CONTROLLER_INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet static\n
  address $controller_ip\n
  netmask $VLAN_NETMASK\n
  dns-nameservers $dns\n
  gateway $NETWORK_INTERNAL_IP_NAT\n
  "
 
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $OVS_BRIDGE_INTERNAL $i
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
  ovsvsctl_set_port $CONTROLLER_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
}   

