function run
{
  ovsvsctl_del_port $OVS_ETHERNET
  ovsvsctl_del_br $OVS_BRIDGE_EXTERNAL
  dhclient $OVS_ETHERNET
  route_del_net $ROUTE_GW 0.0.0.0 $OVS_BRIDGE 
  route_add_net $OVS_ETHERNET_GW 0.0.0.0 $OVS_ETHERNET 
}
