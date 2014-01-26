#!/bin/bash

Normal_pkg_lst=(debconf-utils make python kvm qemu qemu-kvm  python-libvirt gettext python-urlgrabber python-gtk-vnc virtinst nfs-common virt-top kvm-ipxe vlan vim libnl-dev gcc make pkg-config libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev python-dev libyajl-dev aptitude linux-headers-3.2.0-29-generic  openssh-server dhcp3-relay cgroup-bin libpciaccess-dev)

############################################################################################################################
 
Chk_Root_Login()
{
	username=`whoami`
	if test $username != "root"; then

  		echo "LOGIN AS SUPER USER(root) TO INSTALL BAADAL!!!"
  		exit 1
	fi

	echo "User Logged in as Root............................................"
}

#Function to check whther the network gateway is pingable or not
Chk_Gateway()
{
        ping -q -c5 NETWORK_GATEWAY_IP > /dev/null

        if test $? -ne 0;then
                echo "NETWORK GATEWAY IS NOT REACHABLE!!!"
                exit 1
        fi

}


#Function that install all the packages packages
Instl_Pkgs()
{	
	echo "Installing some useful packages"
	echo "==============================="

	Pkg_lst=()
	Pkg_lst=${Normal_pkg_lst[@]}

	for pkg_multi_vrsn in ${Pkg_lst[@]}; do

                pkg_status=0
                pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)

                for pkg in ${pkg_multi_vrsn[@]}; do

                                echo "Installing Package: $pkg.................."
                                DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
				if test $pkg == "debconf-utils"; then
					echo "isc-dhcp-relay isc-dhcp-relay/servers string CONTROLLER_IP" | debconf-set-selections
        				echo "isc-dhcp-relay isc-dhcp-relay/interfaces string VLAN_INTERFACES" | debconf-set-selections
				        echo "isc-dhcp-relay isc-dhcp-relay/options string \"\"" | debconf-set-selections
				fi

                done


	done
	
	echo "Packages Installed Successfully..................................."
}


Enbl_Modules()
{

	echo "Enabling KVM support"

	modprobe kvm
	modprobe kvm_intel

	cd /root
	libvirt_output=`ls | grep "libvirt"`

	if test -z $libvirt_output; then
        	echo "libvirt tar is not found. Please retry SCP"
        	exit 1
	fi

	echo "Installing libvirt-1.0"

	tar -xvzf libvirt-1.0.0.tar.gz
	cd libvirt-1.0.0
	./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes
	make
	make install
	/etc/init.d/libvirt-bin restart
	
	mkdir -p NFS_MOUNT_POINT
	mount $STORAGE_SERVER_IP:$STORAGE_DIRECTORY $LOCAL_MOUNT_POINT
	echo "If you have done all the steps correctly, Congo!!!"
}

############################################################################################################################

#MAIN SCRIPT 

FLAG="/var/log/firstboot.log"
if [ ! -f $FLAG ]; then
	echo "this is our first boot script"
	apt-get update && apt-get -y upgrade
	Chk_Root_Login	
	Chk_Gateway
	Instl_Pkgs
	Enbl_Modules
	touch $FLAG
	hostname baadalhost
	echo "baadalhost" > /etc/hostname
	reboot
fi
