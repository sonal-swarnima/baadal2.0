source /baadal/baadal/baadalinstallation/controller_installation.cfg 2>> /dev/null

Pxe_pkg_lst=(inetutils-inetd tftpd-hpa apache2)
PXE_IP=$(ifconfig $DHCP_BRIDGE_NAME | grep "inet addr"| cut -d: -f2 | cut -d' ' -f1)

Setup_Pxe_Server()
{

        for pkg in ${Pxe_pkg_lst[@]}; do
                DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
        done

}


Configure_Tftp()
{


mkdir -p $TFTP_DIR
sed -i -e 's/^/^#/g' /etc/default/tftpd-hpa
echo -e "RUN_DAEMON=\"yes\"\nOPTIONS=\"-l -s $TFTP_DIR\"" > /etc/default/tftpd-hpa
echo -e "TFTP_USERNAME=\"tftp\"\nTFTP_DIRECTORY=\"$TFTP_DIR\"\nTFTP_ADDRESS=\"0.0.0.0:69\"\nTFTP_OPTIONS=\"-s -c -l\"" >> /etc/default/tftpd-hpa
/etc/init.d/tftpd-hpa stop
/etc/init.d/tftpd-hpa start


# tftpd-hpa is called from inetd. The options passed to tftpd-hpa when it starts are thus found in /etc/inetd.conf
echo -e "tftp\tdgram\tudp\twait\troot\t/usr/sbin/in.tftpd\t/usr/sbin/in.tftpd\t-s\t$TFTP_DIR" >> /etc/inetd.conf
/etc/init.d/inetutils-inetd restart


#configure tftp server for pxe boot
if test $REMOUNT_FILES_TO_TFTP_DIRECTORY == 'y'; then
        mkdir $TFTP_DIR/ubuntu
        mount $ISO_LOCATION $TFTP_DIR/ubuntu
        echo -e "$ISO_LOCATION $TFTP_DIR/ubuntu\tudf,iso9660\tuser,loop\t0\t0" >> /etc/fstab
        cp -r $TFTP_DIR/ubuntu/install/netboot/* $TFTP_DIR/
        cp $TFTP_DIR/ubuntu/install/netboot/ubuntu-installer/amd64/pxelinux.0 $TFTP_DIR/
        rm -rf $TFTP_DIR/pxelinux.cfg
        mkdir $TFTP_DIR/pxelinux.cfg
        echo -e "include mybootmenu.cfg\ndefault ../ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/vesamenu.c32\nprompt 0\ntimeout 100" > $TFTP_DIR/pxelinux.cfg/default
        echo -e "menu hshift 13\nmenu width 60\nmenu margin 8\nmenu title My Customised Network Boot Menu\ninclude ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/stdmenu.cfg\ndefault ubuntu-14.04-server-amd64\nlabel ubuntu-14.04-server-amd64\n\tkernel ubuntu/install/netboot/ubuntu-installer/amd64/linux\n\tappend vga=normal initrd=ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz ksdevice=bootif live-installer/net-image=http://$PXE_IP/ubuntu-14.04-server-amd64/install/filesystem.squashfs ks=http://$PXE_IP/ks.cfg --\n\tIPAPPEND 2\nlabel Boot from the first HDD\n\tlocalboot 0" > $TFTP_DIR/mybootmenu.cfg
fi

/etc/init.d/tftpd-hpa restart
/etc/init.d/inetutils-inetd restart

echo "tftp is configured."

}

Configure_PXE()
{
        ln -s $TFTP_DIR/ubuntu /var/www/ubuntu-14.04-server-amd64

        sed -i -e 's/\/var\/www\/html/\/var\/www/g' /etc/apache2/sites-available/000-default.conf
        service apache2 restart

        if test $INSTALL_LOCAL_UBUNTU_REPO == 'y'; then
                cp $PXE_SETUP_FILES_PATH/sources_file $PXE_SETUP_FILES_PATH/sources.list
                sed -i -e 's/REPO_IP/'"$CONTROLLER_IP"'/g' $PXE_SETUP_FILES_PATH/sources.list
        elif test -n $EXTERNAL_REPO_IP; then
                cp $PXE_SETUP_FILES_PATH/sources_file $PXE_SETUP_FILES_PATH/sources.list
                sed -i -e 's/REPO_IP/'"$EXTERNAL_REPO_IP"'/g' $PXE_SETUP_FILES_PATH/sources.list
        else
                sed -i -e 's/cp \/etc\/apt\/sources.list \/etc\/apt\/sources.list.bak\ncp \/baadal\/baadal\/baadalinstallation\/pxe_host_setup\/sources.list \/etc\/apt\/sources.list//' $PXE_SETUP_FILES_PATH/ks_cfg

        fi

        cp $PXE_SETUP_FILES_PATH/ks_cfg $PXE_SETUP_FILES_PATH/ks.cfg

        sed -i -e 's/PXE_IP/'"$PXE_IP"'/g' $PXE_SETUP_FILES_PATH/ks.cfg
        sed -i -e 's/CFENGINE_IP/'"$CFENGINE_IP"'/g' $PXE_SETUP_FILES_PATH/ks.cfg

        mv $PXE_SETUP_FILES_PATH/ks.cfg /var/www/.

        cp $PXE_SETUP_FILES_PATH/host_installation_sh $PXE_SETUP_FILES_PATH/host_installation.sh

        sed -i -e 's/NETWORK_GATEWAY_IP/'"$NETWORK_GATEWAY_IP"'/g' $PXE_SETUP_FILES_PATH/host_installation.sh

        sed -i -e 's/OVS_BRIDGE_NAME/'"$OVS_BRIDGE_NAME"'/g' $PXE_SETUP_FILES_PATH/host_installation.sh

        sed -i -e "s@LOCAL_MOUNT_POINT@$LOCAL_MOUNT_POINT@g" $PXE_SETUP_FILES_PATH/host_installation.sh


        sed -i -e 's/STORAGE_SERVER_IP/'"$STORAGE_SERVER_IP"'/g' $PXE_SETUP_FILES_PATH/host_installation.sh

        sed -i -e 's@STORAGE_DIRECTORY@'"$STORAGE_DIRECTORY"'@g' $PXE_SETUP_FILES_PATH/host_installation.sh

        sed -i -e 's@BAADAL_REPO_INSTALL@'"$ABSOLUTE_PATH_OF_PARENT_BAADALREPO/$BAADAL_REPO_DIR"'@g' $PXE_SETUP_FILES_PATH/host_installation.sh

        cd $ABSOLUTE_PATH_OF_PARENT_BAADALREPO
        tar -cvf /var/www/newbaadal.tar $BAADAL_REPO_DIR/
        cd -

}

Setup_Pxe_Server
Configure_Tftp
Configure_PXE
