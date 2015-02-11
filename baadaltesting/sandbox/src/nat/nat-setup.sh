function run
{
  check_root
  
  hostname="$(uname -n)"
  if [ "$hostname" != "$NAT_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $NAT_HOSTNAME. This script should be run on NAT.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi

  echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
  echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections

  package_install iptables-persistent

  $ECHO_PROGRESS "Checking iptables-persistent"
  /etc/init.d/iptables-persistent save 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Install iptables-persistent or check logs.
    exit 1
  else
    $ECHO_OK iptables-persistent found
  fi
   
  #Install the ovs packages on NAT.
  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL
    
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL
  
  ovsvsctl_add_port $OVS_BRIDGE_INTERNAL $NAT_INTERNAL_INTERFACE
  ovsvsctl_set_port $NAT_INTERNAL_INTERFACE "vlan_mode=native-untagged"
  INTERFACE_MAC=$(cat /sys/class/net/$NAT_INTERNAL_INTERFACE/address)
  ovsvsctl_set_bridge $OVS_BRIDGE_INTERNAL "other-config:hwaddr=$INTERFACE_MAC"
   
  #Get the IP Address of NAT from ifconfig.
  nat_ip="$(/sbin/ifconfig $NAT_INTERNAL_INTERFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  ifconfig_noip $NAT_INTERNAL_INTERFACE
  ifconfig_ip $OVS_BRIDGE_INTERNAL $nat_ip $VLAN_NETMASK

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  baseaddr="$(echo $nat_ip | cut -d. -f1-2)"
  
  #Clear up the IP tables.
  iptables_run "--flush"
  iptables_run "-t nat --flush"
  iptables_run "--delete-chain"
  iptables_run "-t nat --delete-chain"
  iptables_run "-t nat -A POSTROUTING -o $NAT_EXTERNAL_INTERFACE -j MASQUERADE"

  echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
  echo 1 > /proc/sys/net/ipv4/ip_forward

  $ECHO_PROGRESS "Saving iptables"
  /etc/init.d/iptables-persistent save 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER iptables-persistent save failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK iptables-persistent save
  fi

  trunk_str=""
  ovs_str=""
  interfaces_str="auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $NAT_EXTERNAL_INTERFACE\n
  iface $NAT_EXTERNAL_INTERFACE inet dhcp\n
  \n
  auto $NAT_INTERNAL_INTERFACE\n
  iface $NAT_INTERNAL_INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet static\n
  address $nat_ip\n
  netmask $VLAN_NETMASK\n
  "
  
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $OVS_BRIDGE_INTERNAL $i
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
  ovsvsctl_set_port $NAT_INTERNAL_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
  mkdir /etc/network/interfaces.d
  echo -e $interfaces_str > /etc/network/interfaces.d/0_main.cfg

  package_install sqlite3
}
