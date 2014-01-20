#!/bin/bash

external_interface="eth1"
if test "$1" != "add" && test "$1" != "remove" || test $# -ne 3; then
	basename=$(basename $0)
	echo "USAGE error!!"
	echo "USAGE:: $basename <add|remove> <public_ip> <private_ip>"
	exit 1
fi
if [ "$1" == "add" ]; then
	iptables -t nat -A PREROUTING -i $external_interface -d $2 -j DNAT --to-destination $3
	iptables -t nat -A POSTROUTING -s $3 -o $external_interface -j SNAT --to-source $2
else
	iptables -t nat -D PREROUTING -i $external_interface -d $2 -j DNAT --to-destination $3
	iptables -t nat -D POSTROUTING -s $3 -o $external_interface -j SNAT --to-source $2
fi
/etc/init.d/iptables-persistent save
/etc/init.d/iptables-persistent reload
