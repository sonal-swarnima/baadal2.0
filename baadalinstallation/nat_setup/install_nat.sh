#!/bin/bashi
source config-nat.cfg 2>> /dev/null

rmmod bridge
apt-get -y install openvswitch-controller openvswitch-brcompat openvswitch-switch openvswitch-datapath-source
echo "BRCOMPAT=yes" >> /etc/default/openvswitch-switch
service openvswitch-switch start
module-assistant --text-mode --force auto-install openvswitch-datapath

ovs-vsctl add-br br0
ovs-vsctl add-br br0 $INTERNAL_INTERFACE

touch $BASE_PATH/ovs_postup.sh

iptables --flush
iptables -t nat --flush
iptables --delete-chain
iptables -t nat --delete-chain
iptables --append FORWARD --in-interface $EXTERNAL_INTERFACE -j ACCEPT

trunk_str=""
ovs_str=""
if test $VLANS_IN_RANGE -eq 1; then
	for ((i=$VLAN_START_RANGE;i<=$VLAN_END_RANGE;i++))
	do
		if test $i -ne $NAT_VLAN; then
			ovs_str+="ovs-vsctl add-br vlan$i br0 $i\n"
			iptables --table nat --append POSTROUTING --out-interface vlan$i -j MASQUERADE
		fi
		trunk_str+="$i,"	
	done
else
	IFS=, vlans=( $SPECIFIC_VLANS )
	for i in "${vlans[@]}"
	do
		if test $i -ne $NAT_VLAN; then
                        ovs_str+="ovs-vsctl add-br vlan$i br0 $i\n"
			iptables --table nat --append POSTROUTING --out-interface vlan$i -j MASQUERADE
                fi
		trunk_str+="$i,"
	done
fi
ovs_str+="ovs-vsct set port br0 tag=$NAT_VLAN\n"
trunk_str=$(echo ${trunk_str:1:${#trunk_str}-2})

echo -e "$ovs_str\novs-vsctl set port $INTERNAL_INTERFACE trunk=$trunk_str" > $BASE_PATH/ovs_postup.sh
sed -i -e "s/iface\ lo\ inet\ loopback/iface\ lo\ inet\ loopback\nup\ service\ openvswitch-switch\ restart/" /etc/network/interfaces
echo -e "\nauto $INTERNAL_INTERFACE\niface $INTERNAL_INTERFACE inet static\n\taddress 0.0.0.0\n\nauto br0\niface br0 inet dhcp" >> /etc/network/interfaces

while read line
do
	vlan_interface=$(echo "$line" | cut -d "|" -f 1)
	vlan_ip=$(echo "$line" | cut -d "|" -f 2)
	echo -e "\n\nauto $vlan_interface\niface $vlan_interface inet static\n\taddress $vlan_ip\n\tnetmask $NETMASK" >> /etc/network/interfaces
done < $VLAN_IP_CONFIG_FILE

chmod u+x $BASE_PATH/ovs_postup.sh
$BASE_PATH/ovs_postup.sh
/etc/init.d/networking restart

apt-get install -y debconf-utils
echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections
DEBIAN_FRONTEND=noninteractive  apt-get install -y iptables-persistent

iptables --table nat --append POSTROUTING --out-interface br0 -j MASQUERADE
echo 1 > /proc/sys/net/ipv4/ip_forward 
/etc/init.d/iptables-persistent save
/etc/init.d/iptables-persistent reload
