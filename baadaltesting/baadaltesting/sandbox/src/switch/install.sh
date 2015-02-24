function run
{
  check_root

  package_install dnsmasq
  package_remove resolvconf

  libvirt_install
  virtmanager_install

  libvirtd -d 1>>$LOGS/log.out 2>>$LOGS/log.err

  dns_get

  ovsvsctl_del_br $OVS_BRIDGE_EXTERNAL
  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_add_br $OVS_BRIDGE_EXTERNAL

  config_get INTERFACE

  MAC_INTERFACE=$(ifconfig $INTERFACE | grep HWaddr | cut -d ' ' -f 1,11 | cut -d ' ' -f 2)
  ovs-vsctl set bridge $OVS_BRIDGE_EXTERNAL other-config:hwaddr=${MAC_INTERFACE}

  ovsvsctl_add_port $OVS_BRIDGE_EXTERNAL $INTERFACE
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_set_port $OVS_BRIDGE_INTERNAL "tag=1"

  package_remove network-manager

  ifconfig $INTERFACE 0
  ifconfig_dhcp $OVS_BRIDGE_EXTERNAL

  config_get NETWORK_INTERNAL_IP_SANDBOX
  ifconfig_ip $OVS_BRIDGE_INTERNAL $NETWORK_INTERNAL_IP_SANDBOX $VLAN_NETMASK

  file_backup /etc/network/interfaces
  
  interfaces_str=" auto lo\n
  iface lo inet loopback\n
  up service openvswitch-switch restart\n
  \n
  auto $OVS_BRIDGE_EXTERNAL\n
  iface $OVS_BRIDGE_EXTERNAL inet dhcp\n
  \n
  auto $INTERFACE\n
  iface $INTERFACE inet static\n
  address 0.0.0.0\n
  \n
  auto $OVS_BRIDGE_INTERNAL\n
  iface $OVS_BRIDGE_INTERNAL inet static\n
  address $NETWORK_INTERNAL_IP_SANDBOX\n
  netmask $VLAN_NETMASK\n
  "
  echo -e $interfaces_str > /etc/network/interfaces

  virsh_force "net-destroy $OVS_NET_INTERNAL"
  virsh_force "net-undefine $OVS_NET_INTERNAL"
	virsh_run "net-define $OVS_NET_XML_INTERNAL"
	virsh_run "net-start $OVS_NET_INTERNAL"
	virsh_run "net-autostart $OVS_NET_INTERNAL"

  virsh_force "net-destroy $OVS_NET_EXTERNAL"
  virsh_force "net-undefine $OVS_NET_EXTERNAL"
	virsh_run "net-define $OVS_NET_XML_EXTERNAL"
	virsh_run "net-start $OVS_NET_EXTERNAL"
	virsh_run "net-autostart $OVS_NET_EXTERNAL"

  config_get NETWORK_INTERNAL
  config_get NETWORK_INTERNAL_IP_SANDBOX
  config_get NETWORK_INTERNAL_IP_CONTROLLER
  config_get NETWORK_INTERNAL_IP_NAT
  config_get NETWORK_INTERNAL_IP_FILER

  $ECHO_PROGRESS "dnsmasq"
  
  # Not really a good idea
  killall dnsmasq 2>/dev/null

  dnsmasq \
    --listen-address=$NETWORK_INTERNAL_IP_SANDBOX \
    --bind-interfaces \
    --dhcp-mac=nat,$MAC_NAT \
    --dhcp-host=$MAC_CONTROLLER,$NETWORK_INTERNAL_IP_CONTROLLER \
    --dhcp-host=$MAC_NAT,$NETWORK_INTERNAL_IP_NAT \
    --dhcp-host=$MAC_FILER,$NETWORK_INTERNAL_IP_FILER \
    --dhcp-option=6,$dns \
    --dhcp-option=nat,option:router,0.0.0.0 \
    --dhcp-option=3,$NETWORK_INTERNAL_IP_GATEWAY \
    --dhcp-range=$NETWORK_INTERNAL,static 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER dnsmasq \(check logs\)
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK dnsmasq
  fi

  # Running wake-on-lan listener
  bash -c "tcpdump -i $OVS_BRIDGE_INTERNAL -l \
    | grep --line-buffered ffff \
    | while read -r lineraw ; \
        do echo $lineraw \
          | awk '{print $5,$6,$7}' \
          | sed 's:\ ::g' \
          | sed 's/../&:/g;s/:$//' ;\
        done \
    | while read -r mac ; \
        do \
          if [[ -n ${MAC_VM[$mac]} ]]; \
            then virsh start ${MAC_VM[$mac]};\
          fi ;\
        done" 1>>$LOGS/log.out 2>>$LOGS/log.err &

  $ECHO_OK Switch Installation Complete
}
