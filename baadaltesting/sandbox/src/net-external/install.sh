function run
{
  check_root
  ovsvsctl_add_port_force $OVS_BRIDGE_EXTERNAL $OVS_ETHERNET
  ifconfig_noip $OVS_BRIDGE_EXTERNAL
  ifconfig_noip $OVS_ETHERNET
  route_add_net $ROUTE_GW 0.0.0.0 $OVS_BRIDGE
}
