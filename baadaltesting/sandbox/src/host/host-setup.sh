function run
{  
  check_root
  config_get HOST_INTERFACE

  HOST_INTERFACE=`ip route get 8.8.8.8 | awk '{ print $5; exit }'`
  #Install the ovs packages on NAT.
  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL
    
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_add_port $OVS_BRIDGE_INTERNAL $HOST_INTERFACE
  ovsvsctl_set_port $HOST_INTERFACE "vlan_mode=native-untagged"
  INTERFACE_MAC=$(cat /sys/class/net/$HOST_INTERFACE/address)
  ovsvsctl_set_bridge $OVS_BRIDGE_INTERNAL "other-config:hwaddr=$INTERFACE_MAC"

  ifconfig_noip $HOST_INTERFACE
  ifconfig_dhcp $OVS_BRIDGE_INTERNAL

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  host_ip="$(/sbin/ifconfig $OVS_BRIDGE_INTERNAL | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  baseaddr="$(echo $host_ip | cut -d. -f1-2)"

  echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
  echo 1 > /proc/sys/net/ipv4/ip_forward

  trunk_str=""
  ovs_str=""
  interfaces_str="auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $HOST_INTERFACE\n
  iface $HOST_INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet dhcp\n
  "

  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
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
  ovsvsctl_set_port $HOST_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
}

