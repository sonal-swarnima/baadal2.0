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

OVS_BRIDGE=baadalbr1
OVS_NET=ovs-net
OVS_NET_XML=$BIN/ovs-net.xml

ROUTE_GW=10.209.0.1
ROUTE_DEV_IP=10.209.0.1
ROUTE_NETMASK=255.255.0.0
ROUTE_DEV=$OVS_BRIDGE

INTERFACES_DST=/etc/network/interfaces

CONTROLLER_DISK=$DISKS/controller.img
CONTROLLER_SPACE=5
CONTROLLER_ARCH=x86_64
CONTROLLER_NAME=baadal_controller
CONTROLLER_RAM=1024
CONTROLLER_VCPUS=1
CONTROLLER_ISO=$UTILS/ubuntu.controller.iso
CONTROLLER_KICKSTART=$BIN/ks.controller.cfg

FILER_DISK=$DISKS/filer.img
FILER_SPACE=50
FILER_ARCH=x86_64
FILER_NAME=baadal_filer
FILER_RAM=1024
FILER_VCPUS=1
FILER_ISO=$UTILS/ubuntu.filer.iso
FILER_KICKSTART=$BIN/ks.filer.cfg
