function sandbox_setup
{
	touch /etc/modprobe.d/dist.conf
	echo "options kvm-intel nested=y" >> /etc/modprobe.d/dist.conf

	apt-get -y install make python kvm qemu qemu-kvm gettext python-urlgrabber python-gtk-vnc virtinst virt-top kvm-ipxe vlan vim libnl-dev gcc pkg-config libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev python-dev libyajl-dev libpciaccess-dev aptitude linux-headers-3.2.0-29-generic  openssh-server cgroup-bin

	modprobe kvm
	modprobe kvm_intel
	rmmod bridge
	aptitude -y purge ebtables

	apt-get -y install openvswitch-controller openvswitch-brcompat openvswitch-switch openvswitch-datapath-source
	echo "BRCOMPAT=yes" >> /etc/default/openvswitch-switch
	service openvswitch-switch start
	module-assistant --non-inter --quiet auto-install openvswitch-datapath

	brcompat_exist=`lsmod | grep brcompat`
	if test -z "$brcompat_exist" ; then
		echo "brcompat module is not configured properly. Please retry with \" rmmod bridge \" followed by \"service openvswitch-switch restart\" "
		exit 1
	fi

	ovs-vsctl add-br $OVS_BRIDGE_EXTERNAL
	ovs-vsctl add-port $OVS_BRIDGE_EXTERNAL $OVS_ETHERNET
	ovs-vsctl add-br $OVS_BRIDGE_INTERNAL

	mv /etc/network/interfaces /etc/network/interfaces.bak

	cp $OVS_EXTERNEL_CUSTOM_IFS /etc/network/interfaces
	/etc/init.d/networking restart

	VERSION=$(virsh --version 2>/dev/null)
	if [[ $VERSION != "1.2.1" ]]; then
		echo "Installing $LIBVIRT"
		tar -xvzf $LIBVIRT_TAR	
		cd $LIBVIRT
		./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes
		make
		make install
		/etc/init.d/libvirt-bin restart
		cd -
	fi

	virsh net-define $OVS_NET_XML_INTERNAL
	virsh net-start $OVS_NET_INTERNAL
	virsh net-autostart $OVS_NET_INTERNAL

	virsh net-define $OVS_NET_XML_EXTERNAL
	virsh net-start $OVS_NET_EXTERNAL
	virsh net-autostart $OVS_NET_EXTERNAL

	/etc/init.d/networking restart

	echo "SANDBOX Installation Complete"
}
