function run
{
  route_del_net $ROUTE_GW 0.0.0.0 $OVS_BRIDGE 
  ovsvsctl_del_port $OVS_ETHERNET
  ifconfig_noip $OVS_ETHERNET
  dhclient $OVS_ETHERNET
}
