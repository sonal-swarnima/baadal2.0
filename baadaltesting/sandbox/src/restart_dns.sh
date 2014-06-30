function config_init
{
  mkdir -p $CONFIG
}

function config_get
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}
  CONFIG_VAL=

  # Get from $CONFIG
  CONFIG_VAL=$(cat $config_file 2>/dev/null)
  if [[ $CONFIG_VAL == "" ]]; then
    # Get default value or value from environment
    CONFIG_VAL=${!config_name}
  fi
  eval $config_name=\$CONFIG_VAL
}

function config_set
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}

  echo "${!config_name}" > $config_file
}

function config_clr
{
  config_init

  config_name=$1
  config_file=$CONFIG/${config_name,,}

  rm -f $config_file
}
ROOT=$PWD
BAADAL_LOCAL_DIR=~/.baadal

BIN=$BAADAL_LOCAL_DIR/bin
UTILS=$ROOT/utils
UTILS_LOCAL=$BAADAL_LOCAL_DIR/utils
DISKS=$BAADAL_LOCAL_DIR/disks
LOGS=$BAADAL_LOCAL_DIR/logs
TEMP=$BAADAL_LOCAL_DIR/temp
CONFIG=$BAADAL_LOCAL_DIR/config
SRC=$ROOT/src
NAT=$SRC/nat
CONTROLLER=$SRC/controller
FILER=$SRC/filer
CONFIGURE=$SRC/constants.sh

UBUNTU=$UTILS/ubuntu.iso
LIBVIRT=libvirt-1.2.1
LIBVIRT_TAR=$UTILS/$LIBVIRT.tar.gz
LIBVIRTPYTHON=libvirt-python
LIBVIRTPYTHON_DIR=$UTILS/$LIBVIRTPYTHON
VIRTMANAGER=virt-manager-0.10.0
VIRTMANAGER_TAR=$UTILS/$VIRTMANAGER.tar.gz

ECHO_PROGRESS="echo -e -n"
ECHO_OK="echo -e \"\r\033[K[\e[0;32mOK\e[0m]\t"
ECHO_ER="echo -e \"\r\033[K[\e[0;31mER\e[0m]\t"
LOG_CLEAN="rm -f $LOGS/*"
LOG_SIZE=10

INTERFACE=${INTERFACE:-eth0}

#Update this in OVS_NET_XML too
OVS_BRIDGE_INTERNAL=baadal-br-int
OVS_NET_INTERNAL=ovs-internal
OVS_NET_XML_INTERNAL=$BIN/ovs-net-internal.xml

#Update this in OVS_NET_XML_EXTERNAL too
OVS_BRIDGE_EXTERNAL=baadal-br-ext
OVS_NET_EXTERNAL=ovs-external
OVS_NET_XML_EXTERNAL=$BIN/ovs-net-external.xml
OVS_EXTERNAL_CUSTOM_IFS=$BIN/interfaces.sandbox

#Because we use a mask of 255.255.0.0
NETWORK_BITS=16
VLAN_START=1
VLAN_END=255
VLAN_NETMASK=255.255.255.0

#These values may be updated by configure.
NETWORK_INTERNAL=${NETWORK_INTERNAL:-10.0.0.0}
NETWORK_INTERNAL_IP_SANDBOX=${NETWORK_INTERNAL_IP_SANDBOX:-10.0.0.1}
NETWORK_INTERNAL_IP_CONTROLLER=${NETWORK_INTERNAL_IP_CONTROLLER:-10.0.0.2}
NETWORK_INTERNAL_IP_NAT=${NETWORK_INTERNAL_IP_NAT:-10.0.0.3}
NETWORK_INTERNAL_IP_FILER=${NETWORK_INTERNAL_IP_FILER:-10.0.0.4}

config_get NETWORK_INTERNAL_IP_NAT
NETWORK_INTERNAL_IP_GATEWAY=$NETWORK_INTERNAL_IP_NAT

NAT_DISK=$DISKS/nat.img
NAT_SPACE=5
NAT_ARCH=x86_64
NAT_NAME=baadal_nat
NAT_HOSTNAME=baadal-nat # Should match in ks.cfg
NAT_RAM=1024
NAT_VCPUS=1
NAT_ISO=$UTILS_LOCAL/ubuntu.nat.iso
NAT_KICKSTART=$BIN/ks.nat.cfg
NAT_TRANSFER=$BIN/transfer.nat/
NAT_KS=$NAT/ks.cfg
NAT_EXTERNAL_INTERFACE=eth0
NAT_INTERNAL_INTERFACE=eth1

CONTROLLER_DISK=$DISKS/controller.img
CONTROLLER_SPACE=5
CONTROLLER_ARCH=x86_64
CONTROLLER_NAME=baadal_controller
CONTROLLER_HOSTNAME=baadal-controller # Should match in ks.cfg
CONTROLLER_RAM=1024
CONTROLLER_VCPUS=1
CONTROLLER_ISO=$UTILS_LOCAL/ubuntu.controller.iso
CONTROLLER_KICKSTART=$BIN/ks.controller.cfg
CONTROLLER_TRANSFER=$BIN/transfer.controller/
CONTROLLER_KS=$CONTROLLER/ks.cfg
CONTROLLER_INTERFACE=${CONTROLLER_INTERFACE:-eth0}

FILER_DISK=$DISKS/filer.img
FILER_SPACE=150
FILER_ARCH=x86_64
FILER_NAME=baadal_filer
FILER_HOSTNAME=baadal-filer # Should match in ks.cfg
FILER_RAM=1024
FILER_VCPUS=1
FILER_ISO=$UTILS_LOCAL/ubuntu.filer.iso
FILER_KICKSTART=$BIN/ks.filer.cfg
FILER_TRANSFER=$BIN/transfer.filer/
FILER_KS=$FILER/ks.cfg

HOST_ID=${HOST_ID:-0}
HOST_DISK=$DISKS/host.$HOST_ID.img
HOST_SPACE=60
HOST_ARCH=x86_64
HOST_NAME=baadal_host_$HOST_ID
HOST_HOSTNAME=baadal-host # Should match in ks.cfg
HOST_RAM=8192
HOST_VCPUS=8
HOST_INTERFACE=${HOST_INTERFACE:-eth0}

MAC_SANDBOX=52:52:00:01:15:01
MAC_CONTROLLER=52:52:00:01:15:02
MAC_NAT=52:52:00:01:15:03
MAC_FILER=52:52:00:01:15:04
MAC_HOST_1=52:52:00:01:15:05
MAC_HOST_2=52:52:00:01:15:06
MAC_HOST_3=52:52:00:01:15:07
MAC_HOST_4=52:52:00:01:15:08
MAC_HOST_5=52:52:00:01:15:09
MAC_HOST_6=52:52:00:01:15:10
MAC_HOST_7=52:52:00:01:15:11
MAC_HOST_8=52:52:00:01:15:12
MAC_HOST_9=52:52:00:01:15:13
MAC_HOST_HELPER=MAC_HOST_${HOST_ID}
MAC_HOST=${!MAC_HOST_HELPER}

function dns_get
{
  if [[ $DNS != '' ]]; then
    dns=$DNS
  else
    dns=$(cat /var/run/dnsmasq/resolv.conf | grep "nameserver" | sed "s:nameserver ::g" | head -n 1)
  fi

  package_install ipcalc
  ipcalc -b $dns | tee -a $LOGS/log.err | grep INVALID\ ADDRESS 1>>$LOGS/log.out
  status=$?

  if [[ $status -eq 0 ]]; then
    dns=$(cat /etc/resolv.conf | grep "nameserver" | sed "s:nameserver ::g" | head -n 1)

    ipcalc -b $dns | tee -a $LOGS/log.err | grep INVALID\ ADDRESS 1>>$LOGS/log.out
    status=$?

    if [[ $status -eq 0 ]]; then
      $ECHO_ER Failed to retrieve DNS info from sandbox system \(check logs\) OR \
        manually specify DNS as \'make switch DNS=a.b.c.d\' or \'make controller-setup DNS=a.b.c.d\'
      tail -15 $LOGS/log.err
      exit 1
    else
      $ECHO_OK DNS = $dns
    fi
  else
    $ECHO_OK DNS = $dns
  fi
}

dns_get

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
    --dhcp-range=$NETWORK_INTERNAL,static
