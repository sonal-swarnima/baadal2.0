function check_root
{
  $ECHO_PROGRESS "Checking root"
  username=`whoami`
  if test $username != "root"; then
    $ECHO_ER Root Check
    exit 1
  fi

  $ECHO_OK Root Check
}


function run
{
  check_root

## setting up libvirt and virt-manager packages 
  libvirt_install
  virtmanager_install

  libvirtd -d 1>>$LOGS/log.out 2>>$LOGS/log.err

## setting up bridge
  config_get INTERFACE

  MAC_INTERFACE=$(ifconfig $INTERFACE | grep HWaddr | cut -d ' ' -f 1,11 | cut -d ' ' -f 2)

  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_add_port $OVS_BRIDGE_INTERNAL $INTERFACE

  ifconfig $INTERFACE 0
  ifconfig_dhcp $OVS_BRIDGE_INTERNAL

  file_backup /etc/network/interfaces
 
  interfaces_str=" auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet dhcp\n
  \n
  auto $INTERFACE\n
  iface $INTERFACE inet static\n
  address 0.0.0.0\n
  "
  echo -e $interfaces_str > /etc/network/interfaces

  virsh_force "net-destroy   $OVS_NET_INTERNAL"
  virsh_force "net-undefine  $OVS_NET_INTERNAL"
  virsh_run   "net-define    $OVS_NET_XML_INTERNAL"
  virsh_run   "net-start     $OVS_NET_INTERNAL"
  virsh_run   "net-autostart $OVS_NET_INTERNAL"

  # Not really a good idea
  killall dnsmasq 2>/dev/null

}
