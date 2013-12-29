ROOT=$PWD

BIN=$ROOT/bin
UTILS=$ROOT/utils
DISKS=$ROOT/disks
LOGS=$ROOT/logs
TEMP=$ROOT/temp

UBUNTU=$UTILS/ubuntu.iso
LIBVIRT=$UTILS/libvirt-1.0.0.tar.gz

ECHO_PROGRESS="echo -e -n"
ECHO_OK="echo -e \"\r\033[K[\e[0;32mOK\e[0m]\t"
ECHO_ER="echo -e \"\r\033[K[\e[0;31mER\e[0m]\t"
LOG_CLEAN="rm -f $LOGS/*"

BRCOMPAT_SRC=$BIN/openvswitch-switch
BRCOMPAT_DST=/etc/default/openvswitch-switch

OVS_ETHERNET=eth0
OVS_ETHERNET_GW=10.252.220.1

#Update this in OVS_NET_XML too
OVS_BRIDGE=baadalbr1
OVS_NET=ovs-net
OVS_NET_XML=$BIN/ovs-net.xml

#Update this in OVS_NET_XML_EXTERNAL too
OVS_BRIDGE_EXTERNAL=baadalbr0
OVS_NET_EXTERNAL=ovs-net-external
OVS_NET_XML_EXTERNAL=$BIN/ovs-net-external.xml
OVS_EXTERNEL_CUSTOM_IFS=$BIN/switch-external-interfaces

ROUTE_GW=10.209.0.1
ROUTE_DEV_IP=10.209.0.4
ROUTE_NETMASK=255.255.0.0
ROUTE_DEV=$OVS_BRIDGE

NETWORKING=/etc/init.d/networking
INTERFACES_DST=/etc/network/interfaces

NAT_DISK=$DISKS/nat.img
NAT_SPACE=5
NAT_ARCH=x86_64
NAT_NAME=baadal_nat
NAT_RAM=1024
NAT_VCPUS=1
NAT_ISO=$UTILS/ubuntu.nat.iso
NAT_KICKSTART=$BIN/ks.nat.cfg
NAT_TRANSFER=$BIN/transfer.nat/

CONTROLLER_DISK=$DISKS/controller.img
CONTROLLER_SPACE=5
CONTROLLER_ARCH=x86_64
CONTROLLER_NAME=baadal_controller
CONTROLLER_RAM=1024
CONTROLLER_VCPUS=1
CONTROLLER_ISO=$UTILS/ubuntu.controller.iso
CONTROLLER_KICKSTART=$BIN/ks.controller.cfg
CONTROLLER_TRANSFER=$BIN/transfer.controller/

FILER_DISK=$DISKS/filer.img
FILER_SPACE=50
FILER_ARCH=x86_64
FILER_NAME=baadal_filer
FILER_RAM=1024
FILER_VCPUS=1
FILER_ISO=$UTILS/ubuntu.filer.iso
FILER_KICKSTART=$BIN/ks.filer.cfg
FILER_TRANSFER=$BIN/transfer.filer/
