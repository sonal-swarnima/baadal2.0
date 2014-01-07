Normal_pkg_lst=(debconf-utils make python kvm qemu qemu-kvm libvirt-bin libvirt0 python-libvirt gettext python-urlgrabber python-gtk-vnc virtinst nfs-common virt-top kvm-ipxe vlan munin-node munin-libvirt-plugins vim libnl-dev gcc make pkg-config libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev python-dev libyajl-dev aptitude linux-headers-3.2.0-29-generic  openssh-server dhcp3-relay)

Chk_Root_Login()
{
	username=`whoami`
	if test $username != "root"; then

  		echo "LOGIN AS SUPER USER(root) TO INSTALL BAADAL!!!"
  		exit 1
	fi

	echo "User Logged in as Root............................................"
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
					echo "dhcp3-relay dhcp3-relay/servers CONTROLLER_IP" | debconf-set-selections
        				echo "dhcp3-relay dhcp3-relay/interfaces \"\"" | debconf-set-selections
				        echo "dhcp3-relay dhcp3-relay/options \"\"" | debconf-set-selections
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
	rmmod bridge

	echo "Restarting libvirt"

	invoke-rc.d libvirt-bin restart

	echo "Installing OpenvSwitch"

	aptitude -y purge ebtables
	apt-get -y install openvswitch-controller openvswitch-brcompat openvswitch-switch openvswitch-datapath-source
	echo "BRCOMPAT=yes" >> /etc/default/openvswitch-switch
	service openvswitch-switch start
	module-assistant --text-mode --force auto-install openvswitch-datapath

	brcompat_exist=`lsmod | grep brcompat`
	if test -z "$brcompat_exist" ; then
		echo "brcompat module is not configured properly. Please retry with \" rmmod bridge \" followed by \"service openvswitch-switch restart\" "
		exit 1
	fi

	echo "Configuring OpenvSwitch"

	ovs-vsctl add-br br0
	ovs-vsctl add-port br0 eth0
#	ovs-vsctl add-br vlan10 br0 10
#	ovs-vsctl add-br vlan20 br0 20
#	ovs-vsctl set port eth0 tag=1
#	ovs-vsctl set port eth0 trunk=10,20

	cd /etc/network
	mv interfaces interfaces.bak
	cp /root/interfaces_file interfaces

	echo "eth0 on 0.0.0.0"
	ifconfig eth0 0.0.0.0 up
	echo "restarting networking"
	/etc/init.d/networking restart
	
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

	virsh net-destroy default
	virsh net-autostart --disable default

	touch ovs-net.xml
	
        ovs_net_config="<network>\n<name>ovs-net</name>\n<forward mode='bridge'/>\n<bridge name='br0'/>\n<virtualport type='openvswitch'/>\nPORTGROUPS</network>"
	echo -e $ovs_net_config > ovs-net.xml

	virsh net-define ovs-net.xml
	virsh net-start ovs-net
	virsh net-autostart ovs-net


	echo "If you have done all the steps correctly, Congo!!!"
}

#MAIN SCRIPT 

FLAG="/var/log/firstboot.log"
if [ ! -f $FLAG ]; then
	echo "this is our first boot script"
	apt-get update && apt-get -y upgrade
	Instl_Pkgs
	Enbl_Modules
	touch $FLAG
	hostname baadalhost
	echo "baadalhost" > /etc/hostname
	reboot
fi
