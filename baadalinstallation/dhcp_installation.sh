source /baadal/baadal/baadalinstallation/controller_installation.cfg 2>> /dev/null

NUMBER_OF_HOSTS=254

NUMBER_OF_VLANS=255
Dhcp_pkg_lst=(dhcp3-server)

Setup_Dhcp_Server()
{

        for pkg in ${Dhcp_pkg_lst[@]}; do
                DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
        done

}

Configure_Dhcp()
{

        subnet="255.255.255.0"
        num_hosts=$NUMBER_OF_HOSTS
        end_range=$(( $num_hosts + 1 ))
        final_subnet_string=""
        VLANS=""
	pxe_server_ip=`ip route get 8.8.8.8 | awk '{ print $7; exit }'`

        for ((i=0;i<$NUMBER_OF_VLANS;i++))
        do
                j=$(($i + 1))
                if test $i -eq 0;then
                        final_subnet_string+="subnet $STARTING_IP_RANGE.$i.0 netmask $subnet {\n\toption routers $NETWORK_GATEWAY_IP;\n\toption broadcast-address $STARTING_IP_RANGE.$i.255;\n\toption subnet-mask $subnet;\n\tfilename \"pxelinux.0\";\n\tnext-server $pxe_server_ip;\n}\n\n"

                else

                        final_subnet_string+="subnet $STARTING_IP_RANGE.$i.0 netmask $subnet {\n\toption routers $STARTING_IP_RANGE.$i.1;\n\toption broadcast-address $STARTING_IP_RANGE.$i.255;\n\toption subnet-mask $subnet;\n}\n\n"
                fi
                VLANS+="vlan$j "
        done


        final_subnet_string+="subnet $STARTING_IP_RANGE.$NUMBER_OF_VLANS.0 netmask $subnet {\n\trange $STARTING_IP_RANGE.$NUMBER_OF_VLANS.2 $STARTING_IP_RANGE.$NUMBER_OF_VLANS.$end_range;\n\toption routers $STARTING_IP_RANGE.$NUMBER_OF_VLANS.1;\n\toption broadcast-address $STARTING_IP_RANGE.$NUMBER_OF_VLANS.255;\n\toption subnet-mask $subnet;\n}\n\n"

        echo -e $final_subnet_string >> /etc/dhcp/dhcpd.conf
        sed -i -e "s/option domain-name/#option domain-name/g" /etc/dhcp/dhcpd.conf

        echo "option domain-name-servers $DNS_SERVERS;" >> /etc/dhcp/dhcpd.conf

        sed -i -e "s/INTERFACES=\"\"/INTERFACES=\"$OVS_BRIDGE_NAME $VLANS\"/" /etc/default/isc-dhcp-server

}

Setup_Dhcp_Server
Configure_Dhcp
