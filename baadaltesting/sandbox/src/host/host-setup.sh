function run
{  
  check_root
  
  hostname="$(uname -n)"
  if [ "$hostname" != "$HOST_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $HOST_HOSTNAME. This script should be run on HOST.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi
  
  #Install the ovs packages on NAT.
  ovsvsctl_del_br $OVS_HOST_BRIDGE
    
  ovsvsctl_add_br $OVS_HOST_BRIDGE
  
  ovsvsctl_add_port $OVS_HOST_BRIDGE $HOST_INTERFACE
  ovsvsctl_set_port $HOST_INTERFACE "vlan_mode=native-untagged"
   
  #Get the IP Address of Host from ifconfig.
  host_ip="$(/sbin/ifconfig $NAT_INTERNAL_INTERFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  ifconfig_noip $HOST_INTERFACE
  ifconfig_ip $OVS_HOST_BRIDGE $host_ip $VLAN_NETMASK

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
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
  auto $OVS_HOST_BRIDGE\n
  iface $OVS_HOST_BRIDGE inet static\n
  address $host_ip\n
  netmask $VLAN_NETMASK\n
  "
  
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $OVS_HOST_BRIDGE $i
      ifconfig_ip vlan$i $baseaddr.$i.1 $VLAN_NETMASK
      interfaces_str+="\n
      auto vlan$i\n
      iface vlan$i inet static\n
      address $baseaddr.$i.1\n
      netmask $VLAN_NETMASK\n
      "
      trunk_str+="$i,"
  done

  # NOTE TO DEVELOPER
  # Apparently trunking is not needed here. This will work if no trunking
  # is set on eth0. But theoretically since OVS is a bridge, and there is
  # another physical bridge that eth0 is connected to, the trunking rules
  # should be defined on both eth0-in-OVS and the port-on-physical-bridge
  # where eth0 is connected. I am not quite sure why it works if trunking
  # is not defined on eth0-in-OVS. I am not deleting it until I've got an
  # answer.  
  trunk_str="$(echo ${trunk_str:0:-1})"
  trunk_str="trunk=[$trunk_str]"
  ovsvsctl_set_port $HOST_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
}
