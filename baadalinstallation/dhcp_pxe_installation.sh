#!/bin/bash
source installation.cfg 2>> /dev/null

NUMBER_OF_HOSTS=254

NUMBER_OF_VLANS=255

PKG_LIST=(inetutils-inetd tftpd-hpa dhcp3-server apache2)

Chk_Root_Login()
{
        username=`whoami`
        if test $username != "root"; then

                echo "LOGIN AS SUPER USER(root) TO INSTALL BAADAL!!!"
                echo "EXITING INSTALLATION......................................"
                exit 1
        fi

        echo "User Logged in as Root............................................"
}

#Function that install all the packages packages
Instl_Pkgs()
{

        echo "Updating System............."     

        for pkg_multi_vrsn in ${PKG_LIST[@]}; do

                pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)

                for pkg in ${pkg_multi_vrsn[@]}; do

                        echo "Installing Package: $pkg.................."

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
                # end of FOR loop / package installation from pkg_multi_vrsn    

        done
        # end of FOR loop / package installation from pkg_lst

        echo "Packages Installed Successfully..................................."
}


Configure_Tftp()
{


mkdir -p $TFTP_DIR
sed -i -e 's/^/^#/g' /etc/default/tftpd-hpa
echo -e "RUN_DAEMON=\"yes\"\nOPTIONS=\"-l -s $TFTP_DIR\"" >> /etc/default/tftpd-hpa
/etc/init.d/tftpd-hpa restart

# tftpd-hpa is called from inetd. The options passed to tftpd-hpa when it starts are thus found in /etc/inetd.conf
echo -e "tftp\tdgram\tudp\twait\troot\t/usr/sbin/in.tftpd\t/usr/sbin/in.tftpd\t-s\t$TFTP_DIR" >> /etc/inetd.conf
/etc/init.d/inetutils-inetd restart


#configure tftp server for pxe boot
if test $TFTP_MOUNT_FLAG -eq 1; then
        mkdir $TFTP_DIR/ubuntu
        mount $ISO_LOCATION $TFTP_DIR/ubuntu
        cp -r $TFTP_DIR/ubuntu/install/netboot/* $TFTP_DIR/
        cp $TFTP_DIR/ubuntu/install/netboot/ubuntu-installer/amd64/pxelinux.0 $TFTP_DIR/
#       cd $TFTP_DIR
        mkdir $TFTP_DIR/pxelinux.cfg
#       cd pxelinux.cfg
        touch $TFTP_DIR/pxelinux.cfg/default
        echo -e "include mybootmenu.cfg\ndefault ../ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/vesamenu.c32\nprompt 0\ntimeout 100" >> $TFTP_DIR/pxelinux.cfg/default
#       cd ..
        touch $TFTP_DIR/mybootmenu.cfg
        echo -e "menu hshift 13\nmenu width 49\nmenu margin 8\nmenu title My Customised Network Boot Menu\ninclude ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/stdmenu.cfg\ndefault ubuntu-12.04-server-amd64\nlabel Boot from the first HDD\n\tlocalboot 0\nlabel ubuntu-12.04-server-amd64\n\tkernel ubuntu/install/netboot/ubuntu-installer/amd64/linux\n\tappend vga=normal initrd=ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz ks=http://$CONTROLLER_IP/ks.cfg --" >> $TFTP_DIR/mybootmenu.cfg

        cp $BASE_PATH/libvirt-1.0.0.tar.gz $TFTP_DIR/libvirt-1.0.0.tar.gz
        ln -s $TFTP_DIR/libvirt-1.0.0.tar.gz /var/www/libvirt-1.0.0.tar.gz
fi

/etc/init.d/tftpd-hpa restart
/etc/init.d/inetutils-inetd restart

echo "tftp is configured."

}

Configure_Dhcp_Pxe()
{

        subnet="255.255.255.0"
        num_hosts=$NUMBER_OF_HOSTS
        end_range=$(( $num_hosts + 1 ))
        final_subnet_string=""
	VLANS=""
        for ((i=0;i<$NUMBER_OF_VLANS;i++))
        do
		j=$(($i + 1))
                if test $i -eq 0;then
	final_subnet_string+="subnet $STARTING_RANGE.$i.0 netmask $subnet {\n\trange $STARTING_RANGE.$i.2 $STARTING_RANGE.$i.$end_range;\n\toption routers $STARTING_RANGE.$i.1;\n\toption broadcast-address $STARTING_RANGE.$i.255;\n\toption subnet-mask $subnet;\n\tfilename \"pxelinux.0\";\n}\n\n"
                fi
                final_subnet_string+="subnet $STARTING_RANGE.$i.0 netmask $subnet {\n\trange $STARTING_RANGE.$i.2 $STARTING_RANGE.$i.$end_range\n\toption routers $STARTING_RANGE.$i.1\n\toption broadcast-address $STARTING_RANGE.$i.255\n\toption subnet-mask $subnet\n}\n\n"
		if test $j -ge 2; then
			VLANS+="vlan$j,"
		fi
        done
        echo -e $final_subnet_string >> /etc/dhcp/dhcpd.conf


	ln -s $TFTP_DIR/ubuntu /var/www/ubuntu-12.04-server-amd64
	cp $BASE_PATH/sources.list /var/www/sources.list
	sed -i -e 's/EXTERNAL_REPO_IP/'"$EXTERNAL_REPO_IP"'/g' /var/www/sources.list

	cp $BASE_PATH/ks.cfg  /var/www/ks.cfg
	CONTROLLER_IP=$(ifconfig br0 | grep "inet addr"| cut -d: -f2 | cut -d' ' -f1)
	if test -z $CONTROLLER_IP; then
		CONTROLLER_IP=$(ifconfig eth0 | grep "inet addr"| cut -d: -f2 | cut -d' ' -f1)
	fi
	sed -i -e 's/CONTROLLER_IP/'"$CONTROLLER_IP"'/g' /var/www/ks.cfg
	

	VLANS=$(echo ${VLANS:0:-1})
	cp $BASE_PATH/host_installation.sh /var/www/.
	sed -i -e 's/CONTROLLER_IP/'"$CONTROLLER_IP"'/g' /var/www/host_installation.sh
	sed -i -e 's/VLAN_INTERFACES/'"$VLANS"'/g' /var/www/host_installation.sh
	sed -i -e 's/NFS_MOUNT_POINT/'"$NFS_MOUNT_POINT"'/g' /var/www/host_installation.sh
	sed -i -e 's/FILER_IP/'"$FILER_IP"'/g' /var/www/host_installation.sh
	sed -i -e 's/FILER_DIRECTORY/'"$FILER_DIRECTORY"'/g' /var/www/host_installation.sh
}



Chk_Root_Login
apt-get update
apt-get -y upgrade
Instl_Pkgs
Configure_Tftp
Configure_Dhcp_Pxe
