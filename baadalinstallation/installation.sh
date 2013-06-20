################################ FILE CONSTANTS USED ###########################

Normal_pkg_lst=(ssh zip unzip tar openssh-server build-essential python2.7:python2.5 python-dev python-paramiko apache2 libapache2-mod-wsgi postfix wget libapache2-mod-gnutls  libvirt-bin apache2.2-common python-matplotlib python-reportlab mercurial python-libvirt sshpass)

Ldap_pkg_lst=(python-ldap perl-modules libpam-krb5 libpam-cracklib php5-auth-pam libnss-ldap krb5-user ldap-utils libldap-2.4-2 nscd ca-certificates ldap-auth-client krb5-config:libkrb5-dev)

Mysql_pkg_lst=(mysql-server-5.5:mysql-server-5.1 libapache2-mod-auth-mysql php5-mysql debconf-utils)

############################### FUNCTIONS USED #################################


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

#Function to place ldap and kerberos config files to there correct places
Cnfgr_Ldap_Srvc()
{
	temp=0;

	if test -f "/etc/krb5.conf";then
		if test -f "ldap-krb/krb5.conf";then
			mv /etc/{krb5.conf,krb5.conf.bkp}
			cp -f ldap-krb/krb5.conf /etc/
		else
			echo "ERROR: ldap-krb/krb5.conf"	
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi 
	
	
	if test -f "/etc/ldap.conf";then
		if test -f "ldap-krb/ldap.conf";then
			mv /etc/{ldap.conf,ldap.conf.bkp}
			cp -f ldap-krb/ldap.conf /etc/
		else
			echo "ERROR: ldap-krb/ldap.conf"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi
	
	
	if test -f "/etc/nsswitch.conf";then
		if test -f "ldap-krb/nsswitch.conf";then
			mv /etc/{nsswitch.conf,nsswitch.conf.bkp}
			cp -f ldap-krb/nsswitch.conf /etc/
		else
			echo "ERROR: ldap-krb/nsswitch.conf"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi	
	fi

	
	if test -f "/etc/pam.d/common-account";then
		if test -f "ldap-krb/common-account";then
			mv /etc/pam.d/{common-account,common-account.bkp}
			cp -f ldap-krb/common-account /etc/pam.d/
		else
			echo "ERROR: ldap-krb/common-account"
  			echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi
	
	
	if test -f "/etc/pam.d/common-auth";then
		if test -f "ldap-krb/common-auth";then
			mv /etc/pam.d/{common-auth,common-auth.bkp}
			cp -f ldap-krb/common-auth /etc/pam.d/	
		else
			echo "ERROR: ldap-krb/common-auth"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi
	
	
	if test -f "/etc/pam.d/common-password";then
		if test -f "ldap-krb/common-password";then
			mv /etc/pam.d/{common-password,common-password.bkp}
			cp -f ldap-krb/common-password /etc/pam.d/	
		else
			echo "ERROR: ldap-krb/common-password"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi
	
	
	if test -f "/etc/pam.d/common-session";then
		if test -f "ldap-krb/common-session";then
			mv /etc/pam.d/{common-session,common-session.bkp}
			cp -f ldap-krb/common-session /etc/pam.d/		
		else
			echo "ERROR: ldap-krb/common-session"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
	fi	
}

#Function to populate the list of packages to be installted
Populate_Pkg_Lst()
{

	Pkg_lst=${Normal_pkg_lst[@]}

	if [[ $database_type == "mysql" ]]; then

		Pkg_lst=("${Pkg_lst[@]}" "${Mysql_pkg_lst[@]}")
	
	elif [[ $database_type == "sqlite" ]]; then

		echo "Do nothing as of now"
	else
		echo "Invalid Database Type!!!"
		echo "Please Check Configuration File.........."
  		echo "EXITING INSTALLATION......................................"
		exit 1

	fi			
			
	if [[ $authentication_type == "ldap" ]]; then
	
		Pkg_lst=("${Pkg_lst[@]}" "${Ldap_pkg_lst[@]}")
		Cnfgr_Ldap_Srvc

	elif [[ $authentication_type == "localdb" ]]; then

		echo "Do nothing as of now"
	else
		
		echo "Invalid Authentication Type!!!"
		echo "Please Check Configuration File.........."
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi

}

#Function that install all the packages packages
Instl_Pkgs()
{	

	echo "Updating System............."
	apt-get update	

	Pkg_lst=()
	Populate_Pkg_Lst

	for pkg_multi_vrsn in ${Pkg_lst[@]}; do

		pkg_status=0
		pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)
 		
		for pkg in ${pkg_multi_vrsn[@]}; do

			dpkg-query -S $pkg>/dev/null;
	  		status=$?;
 	
			if test $status -eq 1;  then 

					echo "Installing Package: $pkg.................."
				
					if [[ "$pkg" =~ "mysql-server" ]]; then

						echo "mysql-server-5.5 mysql-server/root_password password $mysql_password" | debconf-set-selections
						echo "mysql-server-5.5 mysql-server/root_password_again password $mysql_password" | debconf-set-selections
						DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
					else
						DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
					fi
		        	
					status=$?
		
					if test $status -eq 0 ; then 
		      
						echo "$pkg Package Installed Successfully" 
						pkg_status=1
						break
					fi

		     elif test $status -eq 0 ; then
			
#					if [[ "$pkg" =~ "mysql-server" ]]; then

#						echo "Mysql Already Installed!!!"	
#						echo "Uninstall Mysql and Restart Installation Process................."
#						echo "Exiting Baadal Installation Process.............................."
#						exit
#					fi

		        	echo "$pkg Package Already Installed" 
					pkg_status=1;break     
			 fi
		done
		
		# end of FOR loop / package installation from pkg_multi_vrsn
		
		if test $pkg_status -eq 0; then
			
			echo "PACKAGE INSTALLATION UNSUCCESSFULL: ${pkg_multi_vrsn[@]} !!!"
			echo "NETWORK CONNECTION ERROR/ REPOSITORY ERROR!!!"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi	
	done
	# end of FOR loop / package installation from pkg_lst

	echo "Packages Installed Successfully..................................."
}


#Function to setup web2py
Setup_Web2py()
{
	Instl_Web2py=1
	
    if [ -d "/home/www-data/web2py/" ]; then
		echo "Web2py Already Exists!!!"
		
		while true; do
			case $reinstall_web2py in
				n|N) 	Instl_Web2py=0; break; ;;
				y|Y|"") break; ;;
				*) 		echo "Invalid value of reinstall_web2py in config-file!!!!";break; ;;
			esac
		done
	fi

	if test $Instl_Web2py -ne 0; then

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
		
		if test $? -ne '0'; then
			echo "UNABLE TO SETUP WEB2PY!!!"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		else
			rm -rf web2py/
		fi
	fi

	rm -rf /home/www-data/web2py/applications/baadal/
	cp logging.conf /home/www-data/web2py/
	cp -r baadal/ /home/www-data/web2py/applications/baadal/

	if test $? -ne '0'; then
		echo "UNABLE TO SETUP BAADAL!!!"
  		echo "EXITING INSTALLATION......................................"
		exit 1
	fi

#	shopt -s nocasematch
#	case $authentication_type in
#
#		ldap) mv /home/www-data/web2py/applications/baadal/models/functions.py.ldap /home/www-data/web2py/applications/baadal/models/functions.py
#		      rm /home/www-data/web2py/applications/baadal/models/functions.py.localdb
#		      ;;
#	     localdb) mv /home/www-data/web2py/applications/baadal/models/functions.py.localdb /home/www-data/web2py/applications/baadal/models/functions.py
#		      rm /home/www-data/web2py/applications/baadal/models/functions.py.ldap
#	esac

	chown -R www-data:www-data /home/www-data/

	echo "Web2py Setup Successful.........................................."

}

Enbl_Modules()
{
	/etc/init.d/nscd restart
	echo "Enabling Apache Modules.........................................."
	a2enmod ssl
	a2enmod proxy
	a2enmod proxy_http
	a2enmod rewrite
	a2enmod headers
	a2enmod expires

	shopt -s nocasematch
	case $database_type in
		
		mysql) /etc/init.d/mysql restart

			    if test $? -ne 0; then
					echo "UNABLE TO RESTART MYSQL!!!"
			  		echo "EXITING INSTALLATION......................................"
					exit 1
			    fi

			    if [ -d /var/lib/mysql/$mysql_database_name ] ; then
			    	echo "$mysql_database_name already exists!!!"
			    	echo "Please remove the $mysql_database_name database and restart the installation process..."
			  		echo "EXITING INSTALLATION......................................"
					exit 1
			    fi

			    echo "Creating Database $mysql_database_name......................"


				mysql -uroot -p$mysql_password -e "create database $mysql_database_name" 2> temp

				if test $? -ne 0;then
					cat temp					
					is_valid_paswd=`grep "ERROR 1045 (28000): Access denied for user 'root'@'localhost' " temp | wc -l`
					rm -rf temp	

					if test $is_valid_paswd -ne 0; then
						echo "INVALID MYSQL PASSWORD!!!!"				    
					else
						break
					fi

					echo "UNABLE TO CREATE DATABASE!!!"
			  		echo "EXITING INSTALLATION......................................"
					exit 1						
				fi					
	esac

}

#Function to create SSL certificate
Create_SSL_Certi()
{
	mkdir /etc/apache2/ssl
	echo "creating Self Signed Certificate................................."
	openssl genrsa 1024 > /etc/apache2/ssl/self_signed.key
	chmod 400 /etc/apache2/ssl/self_signed.key
	openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/apache2/ssl/self_signed.key -config config-file > /etc/apache2/ssl/self_signed.cert
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
		  RewriteEngine On
          RewriteCond %{SERVER_PORT} ^80$
          RewriteRule .* https://%{SERVER_NAME}%{REQUEST_URI} [R,L] 
		</VirtualHost>

		<VirtualHost *:443>
		  SSLEngine on
		  SSLCertificateFile /etc/apache2/ssl/self_signed.cert
		  SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
		
		  WSGIProcessGroup web2py
		  WSGIScriptAlias / /home/www-data/web2py/wsgihandler.py
		  WSGIPassAuthorization On
		
		  <Directory /home/www-data/web2py>
		    AllowOverride None
		    Order Allow,Deny
		    Deny from all
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
		  </Directory>
		
		  CustomLog /var/log/apache2/access.log common
		  ErrorLog /var/log/apache2/error.log
		</VirtualHost>
		' > /etc/apache2/sites-available/default

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

	elif test ! -f "/var/www/.ssh/id_rsa"; then
		if test ! -d "/var/www/.ssh"; then
			mkdir /var/www/.ssh
			chown -R www-data:www-data /var/www/.
		fi

		su www-data -c "ssh-keygen -t rsa -f /var/www/.ssh/id_rsa -N \"\""
		echo "BAADAL PUBLIC KEY CREATED!!!"

	elif test -f "/var/www/.ssh/id_rsa"; then
		echo "PUBLIC KEY ALREADY EXISTS!!!"
	fi

	echo "setting up web2py.................."
	cd /home/www-data/web2py
	sudo -u www-data python -c "from gluon.widget import console; console();"
	sudo -u www-data python -c "from gluon.main import save_password; save_password(\"$web2py_password\",443)"

	cd applications/baadal/

#	nohup python -u /home/www-data/web2py/web2py.py -S baadal -M -R /home/www-data/web2py/applications/baadal/private/hostpower.py &
#	nohup python -u /home/www-data/web2py/web2py.py -S baadal -M -R /home/www-data/web2py/applications/baadal/private/process.py >> process.out &
	
#	val=`cat /etc/crontab | grep "\*\/45 \* \* \* \* www-data python /home/www-data/web2py/applications/baadal/cron/check_baadal_status.py" | wc -l`

#	if [[ $val -eq 0 ]]; then
#		echo "*/45 * * * * www-data python /home/www-data/web2py/applications/baadal/cron/check_baadal_status.py" >> /etc/crontab
#	fi

}

################################ SCRIPT ########################################

#Including Config File to the current script
. ./config-file 2>>/dev/null

Chk_Root_Login
Instl_Pkgs
Setup_Web2py
Enbl_Modules
Create_SSL_Certi
Rewrite_Apache_Conf
Start_Web2py
echo "done!"


#####################################################################################
#####################################################################################
