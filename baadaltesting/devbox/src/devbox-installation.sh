#!/bin/bash

source devbox.cfg 2>> /dev/null

IS_DEVBOX=true
NUMBER_OF_HOSTS=5

NUMBER_OF_VLANS=5

CONTROLLER_IP=$(ifconfig $OVS_BRIDGE_NAME | grep "inet addr"| cut -d: -f2 | cut -d' ' -f1)

Normal_pkg_lst=(apache2 aptitude apt-mirror build-essential cgroup-bin debconf-utils dhcp3-server gcc gconf2 inetutils-inetd intltool kvm-ipxe libapache2-mod-gnutls libapache2-mod-wsgi libcurl4-gnutls-dev libdevmapper-dev libglib2.0-dev libgnutls-dev libnl-dev libpciaccess-dev librsvg2-common libvirt-glib-1.0-dev libxml2-dev libyajl-dev netperf nfs-common openssh-server pkg-config python python2.7:python2.5 python-appindicator python-dbus python-dev python-glade2 python-gnome2 python-gtk2 python-gtk-vnc python-libxml2 python-lxml python-matplotlib python-paramiko python-reportlab python-rrdtool python-simplejson python-urlgrabber python-vte qemu-kvm qemu-utils smem sysbench sysstat tar tftpd-hpa unzip uuid-dev vim virt-what virt-viewer wget zip nfs-kernel-server)

###Ldap_pkg_lst=(python-ldap perl-modules libpam-krb5 libpam-cracklib php5-auth-pam libnss-ldap krb5-user ldap-utils libldap-2.4-2 nscd ca-certificates ldap-auth-client krb5-config:libkrb5-dev ntpdate)

Mysql_pkg_lst=(mysql-server-5.5:mysql-server-5.1 libapache2-mod-auth-mysql php5-mysql)

VM_MAC_LIST=(A2:00:00:6B:B0:EB A2:00:00:FA:35:7E A2:00:00:3E:1A:54 A2:00:00:77:2F:49 A2:00:00:9B:D7:BD)
###################################################################################################################################

#Funtion to check root login
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

#Function to check whther the network gateway is pingable or not
Chk_Gateway()
{
	ping -q -c4 $NETWORK_GATEWAY_IP > /dev/null 
	
	if test $? -ne 0;then
		echo "NETWORK GATEWAY IS NOT REACHABLE!!!"
		exit 1
	fi

	echo "Network Gateway is Pingable!!!"
}

Chk_installation_config()
{

	if test "$NETWORK_GATEWAY_IP" == ""; then
		echo "Network Gateway not specified!!!"
		exit 1
	fi

	network_gateway_ip=(`echo "$NETWORK_GATEWAY_IP" | tr "." " "`)

	if test ${network_gateway_ip[0]} -ne 0 && test ${network_gateway_ip[0]} -le 255 && test ${network_gateway_ip[1]} -le 255 && test ${network_gateway_ip[2]} -le 255 && test ${network_gateway_ip[3]} -le 255; then
		echo "Valid Network Gateway IP!!!"
	else
		echo "Invalid Network Gateway IP!!!"
		exit 1
	fi

	if test "$AUTH_TYPE" == "ldap"; then

		if test "$LDAP_KERBEROS_SETUP_FILES_PATH" == "" || test "$LDAP_URL" == "" || test "$LDAP_DN" == ""; then

			echo "Ldap setup config missing/incomplete!!!"
			exit 1
		fi

		if test ! -d $LDAP_KERBEROS_SETUP_FILES_PATH; then
                	echo "Ldap/Kerberos Setup Files not Found!!!"
			exit 1
		fi

	fi

	if test "$DB_NAME" == ""; then
		echo "Please specify a name for the orchestrator database!!!"
		exit 1
	fi

	if test "$DB_TYPE" == "mysql" && test "$MYSQL_ROOT_PASSWD" == ""; then
		echo "Please speficy mysql root password!!!"
		exit 1
	fi
	

	###KANIKA
        ###   if test "$TFTP_DIR" == "" || test "$PXE_SETUP_FILES_PATH" == "" || test "$ISO_LOCATION" == "" || test "$ABSOLUTE_PATH_OF_PARENT_BAADALREPO" == "" || test "$BAADAL_REPO_DIR" == ""; then
	###	echo "TFTP Setup config missing/incomplete!!!"
	###	exit 1
	###fi	

        ###if test ! -f $ISO_LOCATION; then
        ###        echo "ISO to be mounted for PXE server missing!!!"
        ###        exit 1
        ###fi


	###if test ! -d $PXE_SETUP_FILES_PATH; then
	###	echo "PXE Setup Files not Found!!!"
        ###       exit 1
        ###fi 

        #if test ! -d $ABSOLUTE_PATH_OF_BAADALREPO; then
        #       echo "Baadal Repo not Found!!!"
        #        exit 1
        #fi 


        if test ! -d $BAADAL_APP_DIR_PATH; then
                echo "Baadal App not Found!!!"
                exit 1
        fi 

	if test "$STORAGE_TYPE" == "" || test "$STORAGE_SERVER_IP" == "" || test "$STORAGE_DIRECTORY" == "" || test "$LOCAL_MOUNT_POINT" == ""; then
		echo "Storage server details missing!!!"
		exit 1
	fi

	if test "$OVS_BRIDGE_NAME" == ""; then
		echo "OVS Bridge missing!!!"
		exit 1
	fi

	if test "$STARTING_IP_RANGE" == ""; then
		echo "Starting IP range missing!!!"
		exit 1
	fi

	if [[ "$CONTROLLER_IP" =~ "$STARTING_IP_RANGE" ]];then
        	echo "IP RANGE specified is correct"
	else
        	echo "Invalid IP Range!!!"
        	exit 1
	fi

	###if test "$INSTALL_LOCAL_UBUNTU_REPO" == "y"; then

	###	if test "$EXTERNAL_REPO_IP" == "" || test "$LOCAL_REPO_SETUP_FILES_PATH" == ""; then
	###		echo "local ubuntu repo setup config missing!!!"
	###		exit 1
	###	fi

	###	if test ! -d $LOCAL_REPO_SETUP_FILES_PATH; then
	###		echo "Setup Files Required to configure local ubuntu repo not found!!!"
	###		exit 1
	###	fi

	###fi

	if test "$WEB2PY_PASSWD" == ""; then
		echo "Web2py root pasword missing!!!"
		exit 1
	fi

	if test "$DISABLE_MAIL_SENDING" != "y"; then
		if test "$MAIL_SERVER_URL" == "" || test "$MAIL_SERVER_PORT" == "" || test "$SUPPORT_MAIL_ID" == "" || test "$LOGIN_USERNAME" == "" || test "$LOGIN_PASSWORD" == ""; then
			echo "mailing client setup details missing!!!"
			exit 1
		fi
	fi

        if test "$AUTH_TYPE" != "ldap" && test "$AUTH_TYPE" !=  "db"; then
                echo "Invalid Auth Type!!!"
                exit 1
        fi

	echo "config verification complete!!!"
}


#Function to populate the list of packages to be installted
Populate_Pkg_Lst()
{

	Pkg_lst=${Normal_pkg_lst[@]}

	if [[ $DB_TYPE == "mysql" ]]; then

		Pkg_lst=("${Pkg_lst[@]}" "${Mysql_pkg_lst[@]}")
	
	elif [[ $DB_TYPE == "sqlite" ]]; then

		echo "Do nothing as of now"
	else
		echo "Invalid Database Type!!!"
		echo "Please Check Configuration File.........."
  		echo "EXITING INSTALLATION......................................"
		exit 1

	fi			
			
}

#Function that install all the packages packages
Instl_Pkgs()
{	
#	apt-get update && apt-get -y upgrade

	echo "Updating System............."	

	Pkg_lst=()
	#Populate_Pkg_Lst

	for pkg_multi_vrsn in ${Mysql_pkg_lst[@]}; do

		pkg_status=0
		pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)
 		
		for pkg in ${pkg_multi_vrsn[@]}; do

			echo "Installing Package: $pkg.................."
					
			skip_pkg_installation=0
					
		  if [[ "$pkg" =~ "mysql-server" ]]; then

				dpkg-query -S $pkg>/dev/null;
	  		status=$?;

				if test $status -eq 1;  then 

					echo "mysql-server-5.5 mysql-server/root_password password $MYSQL_ROOT_PASSWD" | debconf-set-selections
					echo "mysql-server-5.5 mysql-server/root_password_again password $MYSQL_ROOT_PASSWD" | debconf-set-selections

				else 
				
					if test $REINSTALL_MYSQL == 'y' -o 'Y' ; then

						sudo apt-get -y remove --purge $pkg
						sudo apt-get -y autoremove
						sudo apt-get -y autoclean
						
						status=$?
						
						if test $status -eq 0 ; then 
		      
							echo "$pkg Package Removed Successfully" 
						
					 	else

							echo "PACKAGE REMOVAL UNSUCCESSFULL: $pkg !!!"
							echo "EXITING INSTALLATION......................................"
							exit 1
	
						fi						
			
					else
					
						skip_pkg_installation=1
					
					fi
				fi

			fi
				
			if test $skip_pkg_installation -eq 0; then
			
				DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes

			fi
			
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

        PID=`ps -eaf | grep mysql | grep -v grep | awk '{print $2}'`
        if [[ "" !=  "$PID" ]]; then
            echo "killing $PID"
            kill -9 $PID
        fi
        /usr/sbin/mysqld


        ovs_net_config="<network>\n<name>ovs-net</name>\n<forward mode='bridge'/>\n<bridge name='baadal-br-int'/>\n<virtualport type='openvswitch'/>\n"
        for ((i=1;i<=$NUMBER_OF_VLANS;i++))
        do
            ovs_net_config+="<portgroup name='vlan$i'>\n\t<vlan><tag id='$i'/></vlan>\n</portgroup>\n"
        done

        ovs_net_config+="</network>"
        echo -e $ovs_net_config > ovs-net.xml

        virsh net-define ovs-net.xml
        virsh net-start ovs-net
        virsh net-autostart ovs-net 


        mkdir -p /mnt/datastore
        mount 192.168.0.1:/baadal/data /mnt/datastore
        echo -e "192.168.0.1:/baadal/data /mnt/datastore nfs rw,auto" >> /etc/fstab
        echo "If you have done all the steps correctly, Congo!!!"


        cd ../../../baadalinstallation

	echo "Packages Installed Successfully..................................."
}


Setup_Baadalapp()
{
        baadalapp_config_path=/home/www-data/web2py/applications/baadal/private/baadalapp.cfg

        sed -i -e 's/nat_ip=/'"nat_ip=$NETWORK_GATEWAY_IP"'/g' $baadalapp_config_path

        sed -i -e 's/storage_type=/'"storage_type=$STORAGE_TYPE"'/g' $baadalapp_config_path

        sed -i -e 's/nat_type=/nat_type='"$NAT_TYPE"'/g' $baadalapp_config_path

	sed -i -e 's/vnc_ip=/vnc_ip='"$VNC_IP"'/g' $baadalapp_config_path

        sed -i -e 's/'"$DB_TYPE"'_db=/'"$DB_TYPE"'_db='"$DB_NAME"'/g' $baadalapp_config_path

        sed -i -e 's/mysql_password=/'"mysql_password=$MYSQL_ROOT_PASSWD"'/g' $baadalapp_config_path

        sed -i -e 's/auth_type=/'"auth_type=$AUTH_TYPE"'/g' $baadalapp_config_path

        sed -i -e 's/mysql_ip=/'"mysql_ip=localhost"'/g' $baadalapp_config_path

        sed -i -e 's/dhcp_ip=/'"dhcp_ip=127.0.0.1"'/g' $baadalapp_config_path

        sed -i -e 's/mysql_user=/'"mysql_user=root"'/g' $baadalapp_config_path

        sed -i -e 's/ldap_url=/'"ldap_url=$LDAP_URL"'/g' $baadalapp_config_path

        sed -i -e 's/ldap_dn=/'"ldap_dn=$LDAP_DN"'/g' $baadalapp_config_path

        if test $DISABLE_MAIL_SENDING != 'y'; then

                sed -i -e 's/mail_active=/'"mail_active=True"'/g' $baadalapp_config_path

                sed -i -e 's/mail_server=/'"mail_server=$MAIL_SERVER_URL:$MAIL_SERVER_PORT"'/g' $baadalapp_config_path

                sed -i -e 's/mail_sender=/'"mail_sender=noreply@baadal"'/g' $baadalapp_config_path

                sed -i -e 's/mail_admin_bug_report=/'"mail_admin_bug_report=$SUPPORT_MAIL_ID"'/g' $baadalapp_config_path

                sed -i -e 's/mail_admin_request=/'"mail_admin_request=$SUPPORT_MAIL_ID"'/g' $baadalapp_config_path

                sed -i -e 's/mail_admin_complaint=/'"mail_admin_complaint=$SUPPORT_MAIL_ID"'/g' $baadalapp_config_path
                
                sed -i -e 's/mail_login=/'"mail_login=$LOGIN_USERNAME:$LOGIN_PASSWORD"'/g' $baadalapp_config_path

		sed -i -e 's/mail_server_tls=/'"mail_server_tls=$MAIL_SERVER_TLS"'/g' $baadalapp_config_path

        else

                sed -i -e 's/mail_active=/'"mail_active=False"'/g' $baadalapp_config_path

        fi

        baadalapp_startup_file_path=/home/www-data/web2py/applications/baadal/private/startup_data.xml
        BAADAL_BR_INT_MAC=$(ifconfig $OVS_BRIDGE_INTERNAL | grep HWaddr |cut -d ' ' -f 1,6| cut -d ' ' -f 2)
        echo $BAADAL_BR_INT_MAC
 
        DEVBOX_HOST_CPU=$(nproc)
 
        DEVBOX_HOST_RAM=$(cat /proc/meminfo | grep MemTotal | awk '{ print $2 }')
        BYTES_TO_GB=1048576
        DEVBOX_HOST_RAM=$(expr $DEVBOX_HOST_RAM / $BYTES_TO_GB)
        echo $DEVBOX_HOST_RAM
  
        echo '
<dataset>
	<table name="user_group">
		<row role="admin" description="Super User"/>
		<row role="orgadmin" description="Organisation Level Admin"/>
		<row role="faculty" description="Faculty User"/>
		<row role="user" description="Normal User"/>
	</table>
	
	<table name="organisation">
		<row id="1" name="ADMIN" details="Baadal Admin"/>
		<row id="2" name="IITD" details="Indian Institute of Technology"/>
	</table>
	
	<table name="constants">
		<row name="baadal_status" value="up"/>
		<row name="vmfiles_path" value="/mnt/datastore"/>
		<row name="extra_disks_dir" value="vm_extra_disks"/>
		<row name="templates_dir" value="vm_templates"/>
		<row name="archives_dir" value="vm_deleted"/>
                <row name="vm_migration_data" value="vm_migration_data"/>
		<row name="vncport_start_range" value="20000"/>
		<row name="vncport_end_range" value="50000"/>
		<row name="vm_rrds_dir" value="vm_rrds"/>
		<row name="graph_file_dir" value="/images/vm_graphs/"/>
		<row name="admin_email" value="baadalsupport@cse.iitd.ernet.in"/>
		<row name="vms" value="/vm_images"/>
		<row name="memory_overload_file_path" value="/baadal/baadal/baadalinstallation/baadal/private"/>
	</table>

	<table name="vlan">
		<row id="1" name="vlan0" vlan_tag="1" vlan_addr="'$STARTING_IP_RANGE.0.0'"/>
		<row id="2" name="vlan1" vlan_tag="1" vlan_addr="'$STARTING_IP_RANGE.1.0'" />
		<row id="3" name="vlan2" vlan_tag="2" vlan_addr="'$STARTING_IP_RANGE.2.0'" />
		<row name="vlan" vlan_tag="3" vlan_addr="'$STARTING_IP_RANGE.3.0'"/>
		<row name="vlan4" vlan_tag="4" vlan_addr="'$STARTING_IP_RANGE.4.0'" />
	</table>

	<table name="security_domain">
		<row id="1" name="Private" vlan="1" visible_to_all="False" />
		<row id="2" name="Infrastructure" vlan="2" visible_to_all="False" />
		<row id="3" name="Research" vlan="3" visible_to_all="True" />
	</table>

	<table name="user">
		<row id="-1" first_name="System" last_name="User" email="System@baadal.tmp" username="system" registration_id="system" organisation_id="1"/>
		<row id="1" first_name="Admin" last_name="User" email="Admin@baadal.tmp" username="admin" password="baadal" organisation_id="1"/>
	</table>

	<table name="user_membership">
		<row user_id="1" group_id="1"/>
		<row user_id="1" group_id="4"/>
	</table>

	<table name="public_ip_pool">
		<row id="-1" public_ip="0.0.0.0" is_active="False" />
	</table>

	<table name="private_ip_pool">
		<row id="1" private_ip="'$DEVBOX_HOST_IP'" mac_addr="'$BAADAL_BR_INT_MAC'" vlan="1" is_active="True"/>
                <row id="2" private_ip="'$STARTING_IP_RANGE.2.5'" mac_addr="'${VM_MAC_LIST[0]}'" vlan="3" is_active="True"/>
                <row id="3" private_ip="'$STARTING_IP_RANGE.2.6'" mac_addr="'${VM_MAC_LIST[1]}'" vlan="3" is_active="True"/>
                <row id="4" private_ip="'$STARTING_IP_RANGE.2.7'" mac_addr="'${VM_MAC_LIST[2]}'" vlan="3" is_active="True"/>
                <row id="5" private_ip="'$STARTING_IP_RANGE.2.8'" mac_addr="'${VM_MAC_LIST[3]}'" vlan="3" is_active="True"/>
                <row id="6" private_ip="'$STARTING_IP_RANGE.2.9'" mac_addr="'${VM_MAC_LIST[4]}'" vlan="3" is_active="True"/>
	</table>

	<table name="datastore">
		<row id="1" ds_name="filer01" ds_ip="'$STORAGE_SERVER_IP'" capacity="10" username="root" path="/baadal/data/" used="0" system_mount_point="/mnt/datastore/"/>
	</table>

        <table name="host">
                <row id="1" host_name="host01" host_ip="1" public_ip="" HDD="50" CPUs="'$DEVBOX_HOST_CPU'" RAM="'$DEVBOX_HOST_RAM'" category="" status="1" slot_number="" rack_number="" extra="" host_type="Physical"/>
        </table>

        <table name="template">
                <row id="1" name="template" os="Linux" os_name="Ubuntu" os_version="14.04" os_type="Desktop" arch="amd64" hdd="10" hdfile="template.qcow2" type="QCOW2" tag="" datastore_id="1" owner="" is_active="T"/>
        </table>

</dataset>' > $baadalapp_startup_file_path
}


Setup_Web2py()
{

install_web2py=1

if test -d "/home/www-data/web2py/"; then

	echo "Web2py Already Exists!!!"

	if test $REINSTALL_WEB2PY == 'n' -o 'N';then
		install_web2py=0
	fi
	
fi

cd ../../../baadalinstallation
if test $install_web2py -eq 1; then
		
	echo "Initializing Web2py Setup"	
	pwd	
	rm -rf web2py/
	unzip web2py_src.zip
		
	if test ! -d web2py/; then
		echo "UNABLE TO EXTRACT WEB2PY!!!"
 		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
		
	rm -rf /home/www-data/
	mkdir /home/www-data/
	mv web2py/ /home/www-data/web2py/
	
	if test $? -ne 0; then
		echo "UNABLE TO SETUP WEB2PY!!!"
		echo "EXITING INSTALLATION......................................"
		exit 1
	else
		rm -rf web2py/
	fi
		
fi	

echo "Initializing Baadal WebApp Deployment"

rm -rf /home/www-data/web2py/applications/baadal/
cp -r $BAADAL_APP_DIR_PATH/baadal/ /home/www-data/web2py/applications/baadal/

if test $? -ne '0'; then
	echo "UNABLE TO SETUP BAADAL!!!"
	echo "EXITING INSTALLATION......................................"
	exit 1
fi

chown -R www-data:www-data /home/www-data/

echo "Web2py Setup Successful.........................................."


}

Enbl_Modules()
{


###	if test $AUTH_TYPE == "ldap"; then
###		/etc/init.d/nscd restart
###		ntpdate $LDAP_URL
###	fi
        apt-get -y purge apache2
        apt-get -y install apache2 --force-yes
	echo "Enabling Apache Modules.........................................."
	a2enmod ssl
	a2enmod proxy
	a2enmod proxy_http
	a2enmod rewrite
	a2enmod headers
	a2enmod expires
	a2enmod wsgi
  
        modprobe kvm
        modprobe kvm_intel
 

	shopt -s nocasematch
	case $DB_TYPE in
		
		mysql) 
			    if test $? -ne 0; then
					echo "UNABLE TO RESTART MYSQL!!!"
			  		echo "EXITING INSTALLATION......................................"
					exit 1
			    fi

			    if test $REINSTALL_MYSQL == 'y'; then

				echo "trying to remove baadal database(if exists)"
				mysql -uroot -pbaadal -e "drop database baadal"

			    elif test -d /var/lib/mysql/$DB_NAME; then

			    	echo "$DB_NAME already exists!!!"
			    	echo "Please remove the $DB_NAME database and restart the installation process..."
			  		echo "EXITING INSTALLATION......................................"
					exit 1
			    fi

			    echo "Creating Database $DB_NAME......................"

				mysql -uroot -p$MYSQL_ROOT_PASSWD -e "create database $DB_NAME" 2> temp

				if test $? -ne 0;then
					cat temp					
					is_valid_paswd=`grep "ERROR 1045 (28000): Access denied for user 'root'@'localhost' " temp | wc -l`
					rm -rf temp	

					if test $is_valid_paswd -ne 0; then
						echo "INVALID MYSQL ROOT PASSWORD!!!!"				    
					fi

					echo "UNABLE TO CREATE DATABASE!!!"
			  		echo "EXITING INSTALLATION......................................"
					exit 1						
				fi				
                          /etc/init.d/mysql restart	
	esac

	mkdir -p $LOCAL_MOUNT_POINT
	
	mount -t nfs $STORAGE_SERVER_IP:$STORAGE_DIRECTORY $LOCAL_MOUNT_POINT
	echo -e "$STORAGE_SERVER_IP:$STORAGE_DIRECTORY $LOCAL_MOUNT_POINT nfs rw,auto" >> /etc/fstab
}

#Function to create SSL certificate
Create_SSL_Certi()
{
	echo "current path"
	pwd

	mkdir /etc/apache2/ssl
	echo "creating Self Signed Certificate................................."
	openssl genrsa 1024 > /etc/apache2/ssl/self_signed.key
	chmod 400 /etc/apache2/ssl/self_signed.key
	openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/apache2/ssl/self_signed.key -config controller_installation.cfg > /etc/apache2/ssl/self_signed.cert
	openssl x509 -noout -fingerprint -text < /etc/apache2/ssl/self_signed.cert > /etc/apache2/ssl/self_signed.info
}

#Function to modify Apache configurations according to our application
Rewrite_Apache_Conf()
{
	echo "rewriting your apache config file to use mod_wsgi"

	echo '
		NameVirtualHost *:80
		NameVirtualHost *:443
		# If the WSGIDaemonProcess directive is specified outside of all virtual
		# host containers, any WSGI application can be delegated to be run within
		# that daemon process group.
		# If the WSGIDaemonProcess directive is specified
		# within a virtual host container, only WSGI applications associated with
		# virtual hosts with the same server name as that virtual host can be
		# delegated to that set of daemon processes.
		WSGIDaemonProcess web2py user=www-data group=www-data

		<VirtualHost *:80>
		  DocumentRoot /var/www
		  RewriteEngine On
		  RewriteRule /(baadal|admin).* https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
		  RewriteRule /$ https://%{HTTP_HOST}/baadal [R=301,L]
		</VirtualHost>

		<VirtualHost *:443>
		  SSLEngine on
		  SSLCertificateFile /etc/apache2/ssl/self_signed.cert
		  SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
		
		  WSGIProcessGroup web2py
		  WSGIScriptAlias / /home/www-data/web2py/wsgihandler.py
		  WSGIPassAuthorization On
		
		  <LocationMatch ^/admin>
		    Order Deny,Allow
                    Allow from all
                    Allow from 127.0.0.1
                  </LocationMatch>		
		  <Directory /home/www-data/web2py>
		    AllowOverride None
		    Order Allow,Deny
		    Allow from all
                    Require all granted
		    <Files wsgihandler.py>
		      Allow from all
		    </Files>
		  </Directory>

		  AliasMatch ^/([^/]+)/static/(.*) \
		        /home/www-data/web2py/applications/$1/static/$2
		
		  <Directory /home/www-data/web2py/applications/*/static/>
		    Options -Indexes
		    ExpiresActive On
		    ExpiresDefault "access plus 1 hour"
		    Order Allow,Deny
		    Allow from all
                    Require all granted
		  </Directory>
		
		  CustomLog /var/log/apache2/access.log common
		  ErrorLog /var/log/apache2/error.log
		</VirtualHost>
		' > /etc/apache2/sites-available/default.conf

        rm -rf /etc/apache2/sites-enabled/* 
        a2ensite default
	echo "Restarting Apache................................................"

	/etc/init.d/apache2 restart
	if test $? -ne 0; then
		echo "UNABLE TO RESTART APACHE!!!"
		echo "CHECK APACHE LOGS FOR DETAILS!!!"
		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	
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
			final_subnet_string+="subnet $STARTING_IP_RANGE.$i.0 netmask $subnet {\n\toption routers $NETWORK_GATEWAY_IP;\n\toption broadcast-address $STARTING_IP_RANGE.$i.255;\n\toption subnet-mask $subnet;\n\tfilename \"pxelinux.0\";\n}\n\n"

                else

                	final_subnet_string+="subnet $STARTING_IP_RANGE.$i.0 netmask $subnet {\n\toption routers $STARTING_IP_RANGE.$i.1;\n\toption broadcast-address $STARTING_IP_RANGE.$i.255;\n\toption subnet-mask $subnet;\n}\n\n"
		fi
		VLANS+="vlan$j "
        done


	final_subnet_string+="subnet $STARTING_IP_RANGE.$NUMBER_OF_VLANS.0 netmask $subnet {\n\trange $STARTING_IP_RANGE.$NUMBER_OF_VLANS.2 $STARTING_IP_RANGE.$NUMBER_OF_VLANS.$end_range;\n\toption routers $STARTING_IP_RANGE.$NUMBER_OF_VLANS.1;\n\toption broadcast-address $STARTING_IP_RANGE.$NUMBER_OF_VLANS.255;\n\toption subnet-mask $subnet;\n}\n\n"

        echo -e $final_subnet_string >> /etc/dhcp/dhcpd.conf
	sed -i -e "s/option domain-name/#option domain-name/g" /etc/dhcp/dhcpd.conf

	echo "option domain-name-servers $DNS_SERVERS;" >> /etc/dhcp/dhcpd.conf

	sed -i -e "s/INTERFACES=\"\"/INTERFACES=\"$OVS_BRIDGE_NAME $VLANS\"/" /etc/default/isc-dhcp-server
	mkdir /etc/dhcp/dhcp.d
	cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcp.d/0_dhcpd.conf
	
}


Start_Web2py()
{

	if test ! -d "/var/www/"; then

               echo "PROBLEM IN APACHE!!!"
               echo "EXITING INSTALLATION......................................"
               exit 1

	elif test -d "/var/www/.ssh"; then

		mv /var/www/.ssh /var/www/.ssh.bak
	
	elif test -d "/root/.ssh"; then
	
		mv /root/.ssh /root/.ssh.bak

	fi

	ssh-keygen -t rsa -f /root/.ssh/id_rsa -N ""
	chsh -s /bin/bash www-data 

        mkdir /var/www/.ssh
        chown -R www-data:www-data /var/www/.ssh	
	su www-data -c "ssh-keygen -t rsa -f /var/www/.ssh/id_rsa -N \"\""

         
	touch /root/.ssh/authorized_keys
	cat /var/www/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

	echo "setting up web2py.................."
	cd /home/www-data/web2py
	sudo -u www-data python -c "from gluon.widget import console; console();"
	sudo -u www-data python -c "from gluon.main import save_password; save_password(\"$WEB2PY_PASSWD\",443)"

        ssh-keyscan $DEVBOX_HOST_IP >> /var/www/.ssh/known_hosts
        ssh-keyscan localhost >> /var/www/.ssh/known_hosts

	su www-data -c "python web2py.py -K baadal &"
	cd -

        sed -i -e "s@exit 0\$@/baadal/baadal/baadalinstallation/web2py_start.sh\nexit 0@" /etc/rc.local
	echo "Controller Installation Complete!!!"
}

Disable_Apparmor()
{
        cd /etc/apparmor.d/disable
        ln -s /etc/apparmor.d/usr.sbin.libvirtd . 
        /usr/sbin/libvirtd -d
}

file_run()
{
  command=$1

  $ECHO_PROGRESS "$command"

  $command 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER $command
    tail -$LOG_SIZE $LOGS/log.err
    exit 1
  else
    $ECHO_OK $command
  fi
}

filer_setup()
{

  # nfs-kernel-server should already be installed

  file_run "mkdir -p /baadal/data/vm_deleted"
  file_run "mkdir -p /baadal/data/vm_extra_disks"
  file_run "mkdir -p /baadal/data/vm_images"
  file_run "mkdir -p /baadal/data/vm_migration_data"
  file_run "mkdir -p /baadal/data/vm_rrds"
  file_run "mkdir -p /baadal/data/vm_templates"

  chmod 757 -R /baadal/data

  exports_str="/baadal/data $NETWORK_INTERNAL/16(rw,sync,no_root_squash,no_all_squash,subtree_check)\n"

  echo -e $exports_str > /etc/exports

  service nfs-kernel-server restart 1>>$LOGS/log.out 2>>$LOGS/log.err
  status=$?

  if [[ $status -ne 0 ]]; then
    $ECHO_ER service nfs-kernel-server restart
    tail -$LOG_SIZE $LOGS/log.err
    exit 1
  else
    $ECHO_OK service nfs-kernel-server restart
  fi

  # copy template to datastore
  cp $PWD/../template.qcow2 /baadal/data/vm_templates 

  $ECHO_OK Filer has been setup.
}
    
Setup_VM_Dhcp_Entries()
{
  ip_mac_string=""
  final_ip_mac_string=""
  for (( i=5;i<10;i++ ))
  do
     ip_string+="$STARTING_IP_RANGE.2.$i "
  done

  #ip_string=${ip_string//./_}
  ip_list=($ip_string)

  for (( i=0;i<5;i++ )) do
     ip_mac_string="host IP_${ip_list[$i]//./_} {\n\thardware ethernet ${VM_MAC_LIST[$i]};\n\tfixed-address ${ip_list[$i]};\n}\n\n"
     echo -e $ip_mac_string > /etc/dhcp/dhcp.d/1_IP_${ip_list[$i]//./_}.conf
     final_ip_mac_string+=$ip_mac_string
  done
  echo -e $final_ip_mac_string >> /etc/dhcp/dhcpd.conf
  service isc-dhcp-server restart

}

exec > >(tee /var/log/installation.log)
exec 2>&1



##############################################################################################################################

#Including Config File to the current script

Chk_Root_Login
Chk_installation_config
Chk_Gateway
filer_setup
Instl_Pkgs
Setup_Web2py
Enbl_Modules
Create_SSL_Certi
Rewrite_Apache_Conf
Configure_Dhcp_Pxe
Setup_Baadalapp
Setup_VM_Dhcp_Entries
Start_Web2py
Disable_Apparmor
