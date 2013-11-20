Normal_pkg_lst=(make python kvm qemu qemu-kvm libvirt-bin libvirt0 python-libvirt gettext python-urlgrabber python-gtk-vnc virtinst nfs-common virt-top kvm-ipxe vlan munin-node munin-libvirt-plugins vim libnl-dev gcc make pkg-config libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev python-dev libyajl-dev aptitude)

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

			dpkg-query -S $pkg>/dev/null;
	  		status=$?;
 	
			if test $status -eq 1;  then 

		        	echo "$pkg Package not installed................"
				echo "Installing Package: $pkg.................."
				apt-get -y install $pkg --force-yes
				status=$?

				if test $status -eq 0 ; then 
		      
					echo "$pkg Package Installed Successfully" 
					pkg_status=1
					break
			 	fi

		        elif test $status -eq 0 ; then

		        	echo "$pkg Package Already Installed" 
				pkg_status=1;break     
			fi
		done
		
		if test $pkg_status -eq 0; then
			
			echo "PACKAGE INSTALLATION UNSUCCESSFULL: ${pkg_multi_vrsn[@]} !!!"
			echo "NETWORK CONNECTION ERROR/ REPOSITORY ERROR!!!"
			exit 1 
		fi	
	done

	echo "Packages Installed Successfully..................................."
}


Enbl_Modules()
{

echo "Enabling KVM support"
echo "===================="

modprobe kvm
modprobe kvm_intel

echo "Restarting libvirt"
echo "=================="

invoke-rc.d libvirt-bin restart

echo "Copying libvirt-1.0.0.tar.gz"
echo "============================"

user_name = `whoami`
cd /home/$user_name/

scp root@10.208.26.210:/home/shweta/Templates/libvirt-1.0.0.tar.gz .
libvirt_output=`ls | grep "libvirt"`
if test -z $libvirt_output; then
	echo "libvirt tar is not found. Please retry SCP"
	exit 1
fi

echo "Installing libvirt-1.0"
echo "====================="

tar -xvzf libvirt-1.0.0.tar.gz
cd libvirt-1.0.0
./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes && make && make install
initctl stop libvirt-bin
initctl start libvirt-bin
virsh --version
libvirtd --version

echo "Installing OpenvSwitch"
echo "=============="

virsh net-destroy default
virsh net-autostart --disable default
aptitude purge ebtables
apt-get install openvswitch-controller openvswitch-brcompat openvswitch-switch openvswitch-datapath-source
echo "BRCOMPAT=yes" >> /etc/default/openvswitch-switch
service openvswitch-switch start
module-assistant auto-install openvswitch-datapath

brcompat_exist=`lsmod | grep brcompat`
if test -z $brcompat_exist ; then
	echo "brcompat module is not configured properly. Please retry with \" rmmod bridge \" followed by \"service openvswitch-switch restart\" "
	exit
fi

echo "Configuring OpenvSwitch"
echo "======================"

ovs-vsctl add-br br0
ovs-vsctl add-port br0 eth0
ovs-vsctl add-br vlan10 br0 10
ovs-vsctl add-br vlan20 br0 20
ovs-vsctl set port br0 tag=1
ovs-vsctl set port eth0 trunk=10,20,1

interfaces_string="auto eth0\niface etho inet static\n\taddress 0.0.0.0\n\nauto br0\niface br0 inet static\n\taddress 192.168.0.4\n\tnetmask 255.255.255.0\n\tbridge_ports eth0 \n\tbridge_stp off"
echo -e $interfaces_string >> /etc/network/interfaces

vlan10_config="auto vlan10\niface vlan10 inet static\naddress 192.168.1.1\nnetmask 255.255.255.0\nvlan_raw_device br0\n"
vlan20_config="auto vlan20\niface vlan20 inet static\naddress 192.168.2.1\nnetmask 255.255.255.0\nvlan_raw_device br0"
echo -e $vlan10_config $vlan20_config >> /etc/network/interfaces

/etc/init.d/networking restart

touch ovs-net.xml
ovs_net_config="<network>\n<name>ovs-net</name>\n<forward mode='bridge'/>\n<bridge name='br0'/>\n<virtualport type='openvswitch'/>\n<portgroup name='vlan10'>\n\t<vlan><tag id='10'/></vlan>\n</portgroup>\n<portgroup name='vlan20'>\n\t<vlan><tag id='20'/></vlan>\n</portgroup>\n</network>"
echo -e $ovs_net_config > ovs-net.xml

virsh net-define ovs-net.xml
virsh net-start ovs-net
virsh net-autostart ovs-net

echo "If you have done all the steps correctly, Congos!!! you are done with adding the host"
}

#Script

Chk_Root_Login
apt-get update && apt-get upgrade
apt-get install make
Instl_Pkgs
Enbl_Modules
