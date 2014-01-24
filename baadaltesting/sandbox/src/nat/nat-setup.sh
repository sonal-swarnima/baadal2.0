OVS_NAT_BRIDGE=nat-br-int
NAT_EXTERNAL_INTERFACE=eth0
NAT_INTERNAL_INTERFACE=eth1
VLAN_START=1
VLAN_END=255
VLAN_NETMASK=255.255.255.0

function run
{
  
  check_root
  
  hostname="$(uname -n)"
  if [ "$hostname" != "$NAT_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $NAT_NAME. This script should be run on NAT.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi

  $ECHO_PROGRESS "Checking iptables-persistent"
  /etc/init.d/iptables-persistent save 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Install iptables-persistent or check logs.
    exit 1
  else
    $ECHO_OK iptables-persistent found
  fi
 
  service_restart openvswitch-switch
  
  #Install the ovs packages on NAT.
  ovsvsctl_del_br $OVS_NAT_BRIDGE
    
  ovsvsctl_add_br $OVS_NAT_BRIDGE
  
  ovsvsctl_add_port $OVS_NAT_BRIDGE $NAT_INTERNAL_INTERFACE
  ovsvsctl_set_port $NAT_INTERNAL_INTERFACE "vlan_mode=native-untagged"
   
  #Get the IP Address of NAT from ifconfig.
  nat_ip="$(/sbin/ifconfig $NAT_INTERNAL_INTERFACE | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"
  ifconfig_noip $NAT_INTERNAL_INTERFACE
  ifconfig_ip $OVS_NAT_BRIDGE $nat_ip $VLAN_NETMASK

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  baseaddr="$(echo $nat_ip | cut -d. -f1-2)"
  
  #Clear up the IP tables.
  iptables_run "--flush"
  iptables_run "-t nat --flush"
  iptables_run "--delete-chain"
  iptables_run "-t nat --delete-chain"
  iptables_run "--append FORWARD --in-interface $NAT_EXTERNAL_INTERFACE -j ACCEPT"

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
  auto $OVS_NAT_BRIDGE\n
  iface $OVS_NAT_BRIDGE inet static\n
  address $nat_ip\n
  netmask $VLAN_NETMASK\n
  "
  
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $OVS_NAT_BRIDGE $i
      ifconfig_ip vlan$i $baseaddr.$i.0 $VLAN_NETMASK
      iptables_run "--table nat --append POSTROUTING --out-interface vlan$i -j MASQUERADE"
      interfaces_str+="\n
      auto vlan$i\n
      iface vlan$i inet static\n
      address $baseaddr.$i.0\n
      netmask $VLAN_NETMASK\n
      "
      trunk_str+="$i,"
  done

  trunk_str="$(echo ${trunk_str:0:-1})"
  trunk_str="trunk=[$trunk_str]"
  ovsvsctl_set_port $NAT_INTERNAL_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces

  $ECHO_PROGRESS "Saving iptables"
  /etc/init.d/iptables-persistent save 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER iptables-persistent save failed. Check logs.
    exit 1
  else
    $ECHO_OK iptables-persistent save
  fi
}
