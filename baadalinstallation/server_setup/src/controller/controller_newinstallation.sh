#!/bin/bash

source ./controller_installation.cfg 2>> /dev/null

Normal_pkg_lst=(git zip unzip tar openssh-server build-essential python2.7:python2.5 python-dev python-paramiko libapache2-mod-wsgi debconf-utils wget libapache2-mod-gnutls python-matplotlib python-reportlab inetutils-inetd apache2 apt-mirror python-rrdtool python-lxml libnl-dev libxml2-dev libgnutls-dev libdevmapper-dev libcurl4-gnutls-dev libyajl-dev libpciaccess-dev nfs-common qemu-utils python-simplejson uuid-dev)

Ldap_pkg_lst=(python-ldap perl-modules libpam-krb5 libpam-cracklib php5-auth-pam libnss-ldap krb5-user ldap-utils libldap-2.4-2 nscd ca-certificates ldap-auth-client krb5-config:libkrb5-dev ntpdate)

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


        if test ! -d $ABSOLUTE_PATH_OF_BAADALREPO; then
                echo "Baadal Repo not Found!!!"
                exit 1
        fi


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


        if test "$INSTALL_LOCAL_UBUNTU_REPO" == "y"; then

                if test "$EXTERNAL_REPO_IP" == "" || test "$LOCAL_REPO_SETUP_FILES_PATH" == ""; then
                        echo "local ubuntu repo setup config missing!!!"
                        exit 1
                fi

                if test ! -d $LOCAL_REPO_SETUP_FILES_PATH; then
                        echo "Setup Files Required to configure local ubuntu repo not found!!!"
                        exit 1
                fi

        fi

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

Configure_Ldap_Kerberos()
{

	echo "Starting LDAP/kerberos Configuration"	

	if test -f "ldap_krb/krb5.conf";then
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/krb5.conf /etc/.
	else
		echo "ERROR: ldap_krb/krb5.conf"	
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	
	
	if test -f "ldap_krb/ldap.conf";then
		cp /etc/{ldap.conf,ldap.conf.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/ldap.conf /etc/.
	else
		echo "ERROR: ldap_krb/ldap.conf"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	
	
	if test -f "ldap_krb/nsswitch.conf";then
		cp /etc/{nsswitch.conf,nsswitch.conf.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/nsswitch.conf /etc/.
	else
		echo "ERROR: ldap_krb/nsswitch.conf"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi	

	
	if test -f "ldap_krb/common-account";then
		cp /etc/pam.d/{common-account,common-account.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/common-account /etc/pam.d/.
	else
		echo "ERROR: ldap_krb/common-account"
		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	
	
	if test -f "ldap_krb/common-auth";then
		cp /etc/pam.d/{common-auth,common-auth.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/common-auth /etc/pam.d/.
	else
		echo "ERROR: ldap_krb/common-auth"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	
	if test -f "ldap_krb/common-password";then
		cp /etc/pam.d/{common-password,common-password.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/common-password /etc/pam.d/.
	else
		echo "ERROR: ldap_krb/common-password"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi
	

	if test -f "ldap_krb/common-session";then
		cp /etc/pam.d/{common-session,common-session.bkp}
		cp -f $LDAP_KERBEROS_SETUP_FILES_PATH/common-session /etc/pam.d/.		
	else
		echo "ERROR: ldap_krb/common-session"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi

}


Setup_Ldap_Kerberos()
{
	Configure_Ldap_Kerberos

	for pkg in ${Ldap_pkg_lst[@]}; do
		DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
	done
	
}

#Function that install all the packages packages
Instl_Pkgs()
{
        apt-get update && apt-get -y upgrade

        echo "Updating System............."

        for pkg_multi_vrsn in ${Normal_pkg_lst[@]}; do
                pkg_status=0

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
	done	

        cd /baadal/baadal/baadaltesting/sandbox/utils
        	tar -xvzf libvirt-1.2.6.tar.gz
	        mv libvirt-1.2.6 /tmp/libvirt-1.2.6

        	cd /tmp/libvirt-1.2.6
                	./configure --prefix=/usr --localstatedir=/var --sysconfdir=/etc --with-esx=yes
	                make
        	        make install
                	/usr/sbin/libvirtd -d
	                if test $? -ne 0; then
        	                echo "Unable to start libvirtd. Check installation and try again"
                	        exit $?
	                fi
                        sed -i -e "s@exit 0\$@/usr/sbin/libvirtd -d\nexit 0@" /etc/rc.local
                 cd -

                 cd libvirt-python-1.2.6
                        /tmp/libvirt-1.2.6/run python setup.py build
                        /tmp/libvirt-1.2.6/run python setup.py install
                 cd -
        cd -

	if test "$AUTH_TYPE" == "ldap"; then
		Setup_Ldap_Kerberos
	fi

	echo "Packages Installed Successfully..................................."
}

Setup_Baadalapp()
{
        baadalapp_config_path=/home/www-data/web2py/applications/baadal/static/baadalapp.cfg

        sed -i -e 's/nat_ip=/'"nat_ip=$NETWORK_GATEWAY_IP"'/g' $baadalapp_config_path

        sed -i -e 's/storage_type=/'"storage_type=$STORAGE_TYPE"'/g' $baadalapp_config_path

        sed -i -e 's/nat_type=/nat_type='"$NAT_TYPE"'/g' $baadalapp_config_path

	sed -i -e 's/vnc_ip=/vnc_ip='"$VNC_IP"'/g' $baadalapp_config_path

        sed -i -e 's/'"$DB_TYPE"'_db=/'"$DB_TYPE"'_db='"$DB_NAME"'/g' $baadalapp_config_path

        sed -i -e 's/mysql_password=/'"mysql_password=$MYSQL_ROOT_PASSWD"'/g' $baadalapp_config_path

        sed -i -e 's/auth_type=/'"auth_type=$AUTH_TYPE"'/g' $baadalapp_config_path

        sed -i -e 's/mysql_ip=/'"mysql_ip=localhost"'/g' $baadalapp_config_path

        sed -i -e 's/dhcp_ip=/'"dhcp_ip=localhost"'/g' $baadalapp_config_path

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


#creating local ubuntu repo for trusty(14.04)
Configure_Local_Ubuntu_Repo()
{

if test $INSTALL_LOCAL_UBUNTU_REPO == 'y'; then
	mkdir -p /var/local_rep/var
	cp /var/local_rep/var/postmirror.sh /var/local_rep/var/postmirror.sh.bak
	cp $LOCAL_REPO_SETUP_FILES_PATH/postmirror.sh /var/local_rep/var/.
	cp /etc/apt/mirror.list /etc/apt/mirror.list.bak
	cp $LOCAL_REPO_SETUP_FILES_PATH/mirror.list /etc/apt/mirror.list
	sed -i -e 's/EXTERNAL_REPO_IP/'"$EXTERNAL_REPO_IP"'/g' $LOCAL_REPO_SETUP_FILES_PATH/mirror.list
	apt-mirror

	#create link for local repositories in www for making them accessible
	ln -s ../local_rep/mirror/$EXTERNAL_REPO_IP/ubuntu/ /var/www/ubuntu
	ln -s ../local_rep/mirror/$EXTERNAL_REPO_IP/ubuntupartner/ /var/www/ubuntupartner

fi


}


Enbl_Modules()
{
	if test $AUTH_TYPE == "ldap"; then
		/etc/init.d/nscd restart
		ntpdate $LDAP_URL
	fi
	echo "Enabling Apache Modules.........................................."
	a2enmod ssl
	a2enmod proxy
	a2enmod proxy_http
	a2enmod rewrite
	a2enmod headers
	a2enmod expires
	a2enmod wsgi

	shopt -s nocasematch

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

	su www-data -c "python web2py.py -K baadal:vm_task,baadal:vm_sanity,baadal:host_task,baadal:vm_rrd,baadal:snapshot_task &"
	cd -

	echo "Controller Installation Complete!!!"
}

##############################################################################################################################

#Including Config File to the current script

Chk_Root_Login
Chk_installation_config
Chk_Gateway
Instl_Pkgs
Setup_Web2py
Configure_Local_Ubuntu_Repo
Enbl_Modules
Create_SSL_Certi
Rewrite_Apache_Conf
Configure_Tftp
Configure_Dhcp_Pxe
Setup_Baadalapp
Start_Web2py
