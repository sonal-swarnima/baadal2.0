#!/bin/bash

source ./devbox.cfg 2>> /dev/null
Normal_pkg_lst=(apache2 aptitude apt-mirror build-essential cgroup-bin debconf-utils dhcp3-server gcc gconf2 inetutils-inetd intltool kvm-ipxe libapache2-mod-gnutls libapache2-mod-wsgi libcurl4-gnutls-dev libdevmapper-dev libglib2.0-dev libgnutls-dev libnl-dev libpciaccess-dev librsvg2-common libvirt-glib-1.0-dev libxml2-dev libyajl-dev netperf nfs-common openssh-server pkg-config python python2.7:python2.5 python-appindicator python-dbus python-dev python-glade2 python-gnome2 python-gtk2 python-gtk-vnc python-libxml2 python-lxml python-matplotlib python-paramiko python-reportlab python-rrdtool python-simplejson python-urlgrabber python-vte qemu-kvm qemu-utils smem sysbench sysstat tar tftpd-hpa unzip uuid-dev vim virt-what virt-viewer wget zip nfs-kernel-server pip libpq-dev)

#Changes made by Anmol Panda on 22 Aug 2016 to include new pakages in the installation procedure
Pip_pkg_list=(docker-py psycopg2 dockerpty)

#ECHO_PROGRESS="echo -e -n"
#ECHO_OK="echo -e \"\r\033[K[\e[0;32mOK\e[0m]\t"
#ECHO_ER="echo -e \"\r\033[K[\e[0;31mER\e[0m]\t"
#OVS_BRIDGE_EXTERNAL=baadal-br-ext

check_root()
{
  echo $ECHO_PROGRESS
  $ECHO_PROGRESS "Checking root"
  username=`whoami`
  if test $username != "root"; then
    $ECHO_ER Root Check
    exit 1
  fi

  $ECHO_OK Root Check
}

virsh_run()
{
  run_command=$1

  $ECHO_PROGRESS "virsh $run_command"

  virsh $run_command 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER virsh $run_command failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err
    exit 1
  else
    $ECHO_OK virsh $run_command
  fi
}

# will always pass
virsh_force()
{
  run_command=$1

  $ECHO_PROGRESS "virsh $run_command"

  virsh $run_command 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK virsh $run_command
}


file_backup()
{
  file=$1

  $ECHO_PROGRESS "$file -\> $file.bak"

  cp $file $file.bak 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK $file -\> $file.bak
}


ifconfig_ip()
{
  iface=$1
  ip=$2
  netmask=$3

  $ECHO_PROGRESS "ifconfig $iface $ip netmask $netmask"
  ifconfig $iface $ip netmask $netmask 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER ifconfig $iface $ip netmask $netmask failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK ifconfig $iface $ip netmask $netmask
  fi
}


ifconfig_dhcp()
{
  iface=$1

  $ECHO_PROGRESS "dhclient $iface"
  dhclient -v $iface 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER dhclient $iface failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK dhclient $iface
  fi

}

package_remove()
{
  package=$1
  $ECHO_PROGRESS "Removing $package"
  aptitude purge -y $package 1>>$LOGS/log.out 2>>$LOGS/log.err
  $ECHO_OK Removed $package
}


ovsvsctl_set_port()
{
  port=$1
  arg=$2

  $ECHO_PROGRESS "Setting port $port parameter"

  ovs-vsctl set port $port $arg 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Setting port $port parameter failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Port $port parameter set.
  fi
}

ovsvsctl_add_br()
{
  bridge=$1

  $ECHO_PROGRESS "Adding bridge $bridge"

  ovs-vsctl add-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Adding bridge $bridge failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Bridge added $bridge
  fi
}


# function for ovs-vsctl del-br
ovsvsctl_del_br()
{
  bridge=$1

  $ECHO_PROGRESS "Deleting bridge $bridge"

  ovs-vsctl del-br $bridge 1>>$LOGS/log.out 2>>$LOGS/log.err

  $ECHO_OK Bridge deleted $bridge
}


# function for ovs-vsctl add-port
ovsvsctl_add_port()
{
  bridge=$1
  port=$2

  $ECHO_PROGRESS "Adding port $port to bridge $bridge"

  ovs-vsctl add-port $bridge $port 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER Adding port $port to bridge $bridge failed. Please check logs.
    tail -$LOG_SIZE $LOGS/log.err 
    exit 1
  else
    $ECHO_OK Port $port added to bridge $bridge
  fi
}

Instl_Pkgs()
{
  #apt-get update && apt-get -y upgrade
  echo "Updating System............."     
  #Pkg_lst=${Normal_pkg_lst[@]}
  
  for pkg_multi_vrsn in ${Normal_pkg_lst[@]}; do
     pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)
     for pkg in ${pkg_multi_vrsn[@]}; do
         DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
         status=$?
         if test $status -eq 0 ; then
            echo "$pkg Package Installed Successfully" 
            break
         else
            echo "PACKAGE INSTALLATION UNSUCCESSFULL: ${pkg_multi_vrsn[@]} !!!"
            echo "NETWORK CONNECTION ERROR/ REPOSITORY ERROR!!!"
            echo "EXITING INSTALLATION......................................"
            exit 1
         fi
      done
  done

}

Instl_pip_pkgs()
{
        #pip install pkg
        echo "Installing Python Packages using Pip"
        #Pkg_list = Pip_pkg_list

        for pip_pkg in ${Pip_pkg_list[@]}; do
        pip_pkg=(`echo $pip_pkg | tr ":" " " `)
                for pkg in ${pip_pkg[@]}; do
                        DEBIAN_FRONTEND=noninteractive pip install $pkg
                 status=$?
                 if test $status -eq 0 ; then
                    echo "$pkg Pip - Package Installed Successfully" 
                    break
                 else
                    echo "Pip - PACKAGE INSTALLATION UNSUCCESSFULL: ${pip_pkg[@]} !!!"
                    echo "NETWORK CONNECTION ERROR/ REPOSITORY ERROR!!!"
                    echo "EXITING INSTALLATION......................................"
                    exit 1
                 fi
                 done
         done

}

# function for ovs-vsctl add-br. always pass.
ovsvsctl_add_fake_br_force()
{
  fake=$1
  bridge=$2
  tag=$3

  $ECHO_PROGRESS "Adding fake bridge $fake $bridge $tag"

  ovs-vsctl add-br $fake $bridge $tag 

  $ECHO_OK Fake Bridge added $fake $bridge $tag
}

iptables_run()
{
  command=$1

  $ECHO_PROGRESS "iptables $command"
  iptables $command 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER iptables $command failed. Check logs.
    tail -$LOG_SIZE $LOGS/log.err
    exit 1
  else
    $ECHO_OK iptables $command
  fi
}


run()
{
  check_root
  echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
  echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections
 
  apt-get -y install iptables-persistent --force-yes
  install_status=$?
    if [[ $install_status -ne 0 ]]; then
      $ECHO_ER Installation failed.
    fi

  $ECHO_PROGRESS "Checking iptables-persistent"
  /etc/init.d/iptables-persistent save
  status=$?
  if [[ $status -ne 0 ]]; then
     $ECHO_ER Install iptables-persistent
     exit 1
  else
    $ECHO_OK iptables-persistent found
  fi

  ovsvsctl_del_br $OVS_BRIDGE_EXTERNAL ;  ovsvsctl_del_br $OVS_BRIDGE_INTERNAL ; dhclient -v eth0

  ovsvsctl_add_br $OVS_BRIDGE_EXTERNAL

  #config_get INTERFACE

  INTERFACE=`ip route get 8.8.8.8 | awk '{ print $5; exit }'`
  echo $INTERFACE  

  MAC_INTERFACE=$(ifconfig $INTERFACE | grep HWaddr | cut -d ' ' -f 1,11 | cut -d ' ' -f 2)
  echo $MAC_INTERFACE

  ovs-vsctl set bridge $OVS_BRIDGE_EXTERNAL other-config:hwaddr=${MAC_INTERFACE}

  ovsvsctl_add_port $OVS_BRIDGE_EXTERNAL $INTERFACE
  ovsvsctl_add_br $OVS_BRIDGE_INTERNAL

  ovsvsctl_set_port $OVS_BRIDGE_INTERNAL "tag=1"

  package_remove network-manager

  ifconfig $INTERFACE 0
  ifconfig_dhcp $OVS_BRIDGE_EXTERNAL

  ###config_get NETWORK_INTERNAL_IP_SANDBOX
  ifconfig_ip $OVS_BRIDGE_INTERNAL $NETWORK_INTERNAL_IP_SANDBOX $VLAN_NETMASK

  #Get the IP Address of devbox from ifconfig.
  devbox_ip="$(/sbin/ifconfig $OVS_BRIDGE_INTERNAL | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')"

  #Get the base address from the ip address, we assume subnet mask to be 255.255.0.0.
  baseaddr="$(echo $devbox_ip | cut -d. -f1-2)"

  #Clear up the IP tables.
  iptables_run "--flush"
  iptables_run "-t nat --flush"
  iptables_run "--delete-chain"
  iptables_run "-t nat --delete-chain"
  iptables_run "-t nat -A POSTROUTING -o $OVS_BRIDGE_EXTERNAL -j MASQUERADE"

  echo "net.ipv4.ip_forward = 1" > /etc/sysctl.conf
  echo 1 > /proc/sys/net/ipv4/ip_forward

  $ECHO_PROGRESS "Saving iptables"
  /etc/init.d/iptables-persistent save 
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER iptables-persistent save failed. Check logs.
    exit 1
  else
    $ECHO_OK iptables-persistent save
  fi


  trunk_str=""
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
 
  for ((i=$VLAN_START;i<=$VLAN_END;i++))
    do
      ovsvsctl_add_fake_br_force vlan$i $OVS_BRIDGE_INTERNAL $i
      ifconfig_ip vlan$i $baseaddr.$i.1 $VLAN_NETMASK
      interfaces_str+="\n
      auto vlan$i\n
      iface vlan$i inet static\n
      address $baseaddr.$i.1\n
      netmask $VLAN_NETMASK\n
      "
      trunk_str+="$i,"
  done

# NOTE TO DEVELOPER
  # Apparently trunking is not needed here. This is because an openvswitch
  # interface will act as trunk port for all vlans by default if there are
  # no trunk values as well as no tag values defined for the interface. It
  # should be better is these things are explicitly defined as this is not
  # well documented in openvswitch's docs. If any trunk value or tag value
  # is defined for an interface on openvswitch then it automatically won't
  # work as trunk for all other remaining vlans. In baadal's current state
  # eth0 will act as trunk for vlans 1-255 and will filter out traffic for
  # all other vlans.
  #trunk_str="$(echo ${trunk_str:0:-1})"
  echo $trunk_str
  trunk_str="trunk=[$trunk_str]"
  ovsvsctl_set_port $NAT_INTERNAL_INTERFACE $trunk_str

  file_backup /etc/network/interfaces
  echo -e $interfaces_str > /etc/network/interfaces
  mkdir /etc/network/interfaces.d
  echo -e $interfaces_str > /etc/network/interfaces.d/0_main.cfg


   ### install all the required packages
   echo "Instl_Pkgs"
   Instl_Pkgs
   echo "Pkgs Installed"
   
   echo "Instl_pip_pkgs"
   Instl_pip_pkgs
   echo "Pip pkgs installed"
   
   ##installing libvirt packages
   cd ../utils
      tar -xvzf libvirt-1.2.6.tar.gz
      
      mv libvirt-1.2.6 /tmp/libvirt-1.2.6

      cd /tmp/libvirt-1.2.6
         ./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes
          make
          make install
	  killall libvirtd
          /usr/sbin/libvirtd -d
          if test $? -ne 0; then
              echo "Unable to start libvirtd. Check installation and try again"
              exit $?
          fi
          echo "Libvirt Installed"
          sed -i -e "s@exit 0\$@/usr/sbin/libvirtd -d\nexit 0@" /etc/rc.local
      cd -

      tar -xvzf libvirt-python-1.2.6.tar.gz 
      cd libvirt-python-1.2.6
          /tmp/libvirt-1.2.6/run python setup.py build
          /tmp/libvirt-1.2.6/run python setup.py install
      cd -

      tar -xvzf virt-manager-0.10.0.tar.gz -C /root
      cd /root/virt-manager-0.10.0
          python setup.py install --prefix=/usr
      cd -

   cd ../src

   virsh net-destroy default
   virsh net-autostart --disable default
   echo "default network destroyed"
 

  $ECHO_OK Devbox Setup Complete

  pwd
  ./devbox-installation.sh	
}

run
