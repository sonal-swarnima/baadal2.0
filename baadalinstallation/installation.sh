################################ FILE CONSTANTS USED ###########################

Normal_pkg_lst=(ssh zip unzip tar openssh-server build-essential python2.7:python2.5 python-dev python-paramiko apache2 libapache2-mod-wsgi postfix debconf-utils wget libapache2-mod-gnutls  libvirt-bin apache2.2-common python-matplotlib python-reportlab mercurial python-libvirt sshpass inetutils-inted tftpd-hpa dhcp3-server apache2 apt-mirror)

Ldap_pkg_lst=(python-ldap perl-modules libpam-krb5 libpam-cracklib php5-auth-pam libnss-ldap krb5-user ldap-utils libldap-2.4-2 nscd ca-certificates ldap-auth-client krb5-config:libkrb5-dev)

Mysql_pkg_lst=(mysql-server-5.5:mysql-server-5.1 libapache2-mod-auth-mysql php5-mysql)

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


Configure_Ldap_Kerberos()
{

if test -f "/etc/krb5.conf";then
		if test -f "ldap_krb/krb5.conf";then
			mv /etc/{krb5.conf,krb5.conf.bkp}
			cp -f ldap_krb/krb5.conf /etc/
		else
			echo "ERROR: ldap_krb/krb5.conf"	
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
fi 
	
	
if test -f "/etc/ldap.conf";then
		if test -f "ldap_krb/ldap.conf";then
			mv /etc/{ldap.conf,ldap.conf.bkp}
			cp -f ldap_krb/ldap.conf /etc/
		else
			echo "ERROR: ldap_krb/ldap.conf"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
fi
	
	
if test -f "/etc/nsswitch.conf";then
		if test -f "ldap_krb/nsswitch.conf";then
			mv /etc/{nsswitch.conf,nsswitch.conf.bkp}
			cp -f ldap_krb/nsswitch.conf /etc/
		else
			echo "ERROR: ldap_krb/nsswitch.conf"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi	
fi

	
if test -f "/etc/pam.d/common-account";then
		if test -f "ldap_krb/common-account";then
			mv /etc/pam.d/{common-account,common-account.bkp}
			cp -f ldap_krb/common-account /etc/pam.d/
		else
			echo "ERROR: ldap_krb/common-account"
  			echo "EXITING INSTALLATION......................................"
			exit 1
		fi
fi
	
	
if test -f "/etc/pam.d/common-auth";then
		if test -f "ldap_krb/common-auth";then
			mv /etc/pam.d/{common-auth,common-auth.bkp}
			cp -f ldap_krb/common-auth /etc/pam.d/	
		else
			echo "ERROR: ldap_krb/common-auth"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
fi
	
	
if test -f "/etc/pam.d/common-password";then
		if test -f "ldap_krb/common-password";then
			mv /etc/pam.d/{common-password,common-password.bkp}
			cp -f ldap_krb/common-password /etc/pam.d/	
		else
			echo "ERROR: ldap_krb/common-password"
	  		echo "EXITING INSTALLATION......................................"
			exit 1
		fi
fi
	
	
if test -f "/etc/pam.d/common-session";then
		if test -f "ldap_krb/common-session";then
			mv /etc/pam.d/{common-session,common-session.bkp}
			cp -f ldap_krb/common-session /etc/pam.d/		
		else
			echo "ERROR: ldap_krb/common-session"
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
		Configure_Ldap_Kerberos

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

	Pkg_lst=()
	Populate_Pkg_Lst

	for pkg_multi_vrsn in ${Pkg_lst[@]}; do

		pkg_status=0
		pkg_multi_vrsn=(`echo $pkg_multi_vrsn | tr ":" " "`)
 		
		for pkg in ${pkg_multi_vrsn[@]}; do

			echo "Installing Package: $pkg.................."
					
			skip_pkg_installation=0
					
		  if [[ "$pkg" =~ "mysql-server" ]]; then

				dpkg-query -S $pkg>/dev/null;
	  		status=$?;

				if test $status -eq 1;  then 

					echo "mysql-server-5.5 mysql-server/root_password password $mysql_password" | debconf-set-selections
					echo "mysql-server-5.5 mysql-server/root_password_again password $mysql_password" | debconf-set-selections

				else 
				
					if test $reinstall_mysql == 'y' -o 'Y' ; then

						sudo apt-get remove --purge $pkg
						sudo apt-get autoremove
						sudo apt-get autoclean
						
						status=$?
						
						if test $status -eq 0 ; then 
		      
							echo "$pkg Package Removed Successfully" 
							break
						
					 	else

							echo "PACKAGE REMOVAL UNSUCCESSFULL: $pkg !!!"
							echo "EXITING INSTALLATION......................................"
							exit 1
	
						fi						
			
					else
					
						skip_pkg_installation=1
					
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

	echo "Packages Installed Successfully..................................."
}


Setup_Web2py()
{

install_web2py=1

if test -d "/home/www-data/web2py/"; then

	echo "Web2py Already Exists!!!"

	if test $reinstall_web2py == 'n' -o 'N';then
		install_web2py=0
	fi
	
fi



if test $install_web2py -eq 1; then
		
	echo "Initializing Web2py Setup"	
	
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
cp logging.conf /home/www-data/web2py/
cp -r baadal/ /home/www-data/web2py/applications/baadal/

if test $? -ne '0'; then
	echo "UNABLE TO SETUP BAADAL!!!"
	echo "EXITING INSTALLATION......................................"
	exit 1
fi

chown -R www-data:www-data /home/www-data/

echo "Web2py Setup Successful.........................................."


}

#Helper functions for calculating subnet IP network addresses
function full_subnet_octet(){
        octet_limit=$(( $(( $1 >> $2)) & 255 ))
        return $octet_limit
}

function adjusted_subnet_octet(){
        if test $1 -eq 8; then
                return $(full_subnet_octet $2 0)
        fi
        adjusted_num=$(($2 << $(( 8 - $1 )) ))
        octet_limit=$(($adjusted_num & 255))
        return $octet_limit
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
	cd $TFTP_DIR
	mkdir pxelinux.cfg
	cd pxelinux.cfg
	touch default
	echo -e "include mybootmenu.cfg\ndefault ../ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/vesamenu.c32\nprompt 0\ntimeout 100" >> default
	cd ..
	touch mybootmenu.cfg
	echo -e "menu hshift 13\nmenu width 49\nmenu margin 8\nmenu title My Customised Network Boot Menu\ninclude ubuntu/install/netboot/ubuntu-installer/amd64/boot-screens/stdmenu.cfg\ndefault ubuntu-12.04-server-amd64\nlabel Boot from the first HDD\n\tlocalboot 0\nlabel ubuntu-12.04-server-amd64\n\tkernel ubuntu/install/netboot/ubuntu-installer/amd64/linux\n\tappend vga=normal initrd=ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz ks=http://$CONTROLLER_IP/ks.cfg --" >> mybootmenu.cfg

	cp $BASE_PATH/libvirt-1.0.0.tar.gz $TFTP_DIR/libvirt-1.0.0.tar.gz
	ln -s $TFTP_DIR/libvirt-1.0.0.tar.gz libvirt-1.0.0.tar.gz
	chmod 777 -R $TFTP_DIR
fi

/etc/init.d/tftpd-hpa restart
/etc/init.d/inetutils-inetd restart



}

Configure_Dhcp_Pxe()
{

# Get the number of bits for the host IPs
vlan_loop_iterator=$NUMBER_OF_VLANS
#subnet bits are initialized to 0, considering number of bits from second octet
subnet_bits=0
while [ $vlan_loop_iterator -gt 0 ]
do
	subnet_bits=$(( $subnet_bits + 1 ))
	vlan_loop_iterator=$(( $vlan_loop_iterator / 2 ))
done
echo "number of subnet bits are $subnet_bits"

#maximum number of subnet bits can be 12 as maximum number of vlans possible are 4096
if test $subnet_bits -gt 12; then
	echo "Number of VLANs can not exceed 4096. Fix the number in config file and retry."
	exit 1
fi

#Hosts are to be accomodated in the remaining bits after the subnet so maximum hosts can be 2^(24-<number_of_subnet_bits>)
host_bits=$((24 - $subnet_bits))
max_hosts=$((2**$host_bits))
if test $NUMBER_OF_HOSTS -gt $max_hosts; then
	echo "Number of hosts specified exceeds the maximum possible. Maximum number of hosts per VLAN can be $max_hosts."
	echo "You can either reduce the number of VLANs or number of hosts. Fix and retry."
	exit 1
fi

#calculating subnet mask corresponding to the subnet bits and the subnet declarations for the VLANs
subnet_block="subnet 10."
helper_numbers[1]=1
helper_numbers[2]=3
helper_numbers[3]=7
helper_numbers[4]=15
helper_numbers[5]=31
helper_numbers[6]=63
helper_numbers[7]=127
declare -a subnet_helpers=('128' '192' '224' '240' '248' '252' '254');



#calculate subnet mask
subnet="255"
test_subnet_bits=$subnet_bits
octet_count=0
while [ $test_subnet_bits -gt 0 ] 
do
	if test $test_subnet_bits -gt 8; then
		subnet+=".255"
	else
		rest=$(echo ${subnet_helpers[$test_subnet_bits-1]})
		subnet="$subnet.$rest"
	fi
	test_subnet_bits=$(( $test_subnet_bits - 8 ))
	octet_count=$(($octet_count + 1))
done

if test $octet_count -eq 1; then
	subnet+=".0.0"
elif test $octet_count -eq 2; then
	subnet+=".0"
fi

echo "subnet mask is $subnet"
#Subnet mask calculated

#Assign IP to controller NIC
echo -e "auto eth0\niface eth0 inet static\n\taddress $CONTROLLER_IP\n\tnetmask $subnet" >> /etc/network/interfaces
/etc/init.d/networking restart

num_hosts=$NUMBER_OF_HOSTS
#Calculation of subnet declaration for default VLAN in dhcp
forth_range_octet=$(( ($num_hosts & 255) + 1  ))
third_range_octet=$(( ($num_hosts >> 8) & 255 ))
second_range_octet=$(( ($num_hosts >> 16) & 255 ))
second_broadcast_octet=0
if test $subnet_bits -lt 8; then
	second_broadcast_octet=$(( 255 >> $subnet_bits ))
	third_broadcast_octet=255
else 
	third_broadcast_octet=$(( 255 >> ($subnet_bits - 8) ))
fi 
final_subnet_string="subnet 10.0.0.0 netmask $subnet {\n\trange 10.0.0.2 10.$second_range_octet.$third_range_octet.$forth_range_octet;\n\toption routers 10.0.0.1;\n\toption broadcast-address 10.$second_broadcast_octet.$third_broadcast_octet.255;\n\toption subnet-mask $subnet;\n\tfilename \"pxelinux.0\";\n}\n\n"

#Calculatings subnet IP network address, forming ovs declaration string and network interfaces settings for internal VLAN gateways.
final_interfaces_string=""
final_ovs_string=""
final_trunk_string=""
PORTGROUP_STRING=""
#Default VLAN configuration is already figured out, remaining (NUMBER_OF_VLANS -1) VLANs are configured here
for (( i=1;i<$NUMBER_OF_VLANS;i++ )) 
do
	second_octet=0
	third_octet=0
	forth_octet=0
	#VLAN tags start from 2 as 1 is default VLAN
	vlan_tag=$(($i + 1))
	if test $subnet_bits -gt 8; then
		#calculating the octets for subnet IP addresses
		remaining_bits=$(( $subnet_bits - 8 )) 
		full_subnet_octet $i $remaining_bits
		second_octet=$?
		adjusted_subnet_octet $remaining_bits $i
		third_octet=$?
		#calculating broadcast address
		host_bits=$(( 8 - $remaining_bits ))
	        helper_number=helper_numbers[$host_bits]
        	range_octet=$(( $third_octet | $helper_number))
		broadcast_str="10.$second_octet.$range_octet.255"
		# calculating range for defining subnets
		third_range_octet=$(($third_octet | $(( ($num_hosts >> 8) & helper_number )) ))
		end_range_str="$second_octet.$third_range_octet"
	else
		#calculating the octets for subnet IP addresses
		remaining_bits=$subnet_bits
		adjusted_subnet_octet $subnet_bits $i
		second_octet=$?
		#calculating the broadcast address
		host_bits=$(( 8 - $subnet_bits ))
	        helper_number=helper_numbers[$host_bits]
        	range_octet=$(( $second_octet | helper_number))
		broadcast_str="10.$range_octet.255.255"
		#calculating range for defining subnets
		third_range_octet=$(( ($num_hosts >> 8) & 255 ))
		second_range_octet=$(( $second_octet | ( ($num_hosts >> 16) & helper_number) ))
		end_range_str="$second_range_octet.$third_range_octet"
	fi
	forth_range_octet=$(( ($num_hosts & 255) + 1))
	range_str="10.$second_octet.$third_octet.2 10.$end_range_str.$forth_range_octet"
	final_subnet_string+=$(echo "$subnet_block$second_octet.$third_octet.$forth_octet netmask $subnet {\n\trange $range_str;\n\toption routers 10.$second_octet.$third_octet.1;\n\toption broadcast-address $broadcast_str;\n\toption subnet-mask $subnet;\n}\n\n")
	final_interfaces_string+="auto vlan$vlan_tag\niface vlan$vlan_tag inet static\n\taddress 10.$second_octet.$third_octet.1\n\tnetmask $subnet\n\tvlan_raw_device br0\n\n"
	final_ovs_string+="ovs-vsctl add-br vlan$vlan_tag br0 $vlan_tag\n"
	final_trunk_string+=$(echo "$vlan_tag")
	if test $i -ne $(($NUMBER_OF_VLANS-1)); then
		final_trunk_string+=","
	fi
	PORTGROUP_STRING+="<portgroup name=\'vlan$vlan_tag\'>\\\n\\\t<vlan><tag id=\'$vlan_tag\'\/><\/vlan>\\\n<\/portgroup>\\\n"
done

echo -e $final_subnet_string >> /etc/dhcp/dhcpd.conf
sed -i -e 's/#authoritative/authoritative/g' /etc/dhcp/dhcpd.conf
sed -i -e 's/INTERFACES=\"\"/INTERFACES=\"eth0\"/g' /etc/default/isc-dhcp-server

/etc/init.d/isc-dhcp-server restart


# Host ubuntu ISO, local repository and other files in www directory for host PXE boot and installation
cd /var/www
#create link for ubuntu iso in www for PXE boot
ln -s $TFTP_DIR/ubuntu ubuntu-12.04-server-amd64
#create link for local repositories in www for making them accessible
ln -s ../local_rep/mirror/repo.iitd.ernet.in/ubuntu/ ubuntu
ln -s ../local_rep/mirror/repo.iitd.ernet.in/ubuntupartner/ ubuntupartner

echo "portgroups $PORTGROUP_STRING"
cp $BASE_PATH/ks.cfg  ks.cfg
sed -i -e 's/CONTROLLER_IP/'"$CONTROLLER_IP"'/g' ks.cfg
cp $BASE_PATH/interfaces_file interfaces_file
echo -e $final_interfaces_string >> interfaces_file
cp $BASE_PATH/sources.list sources.list
sed -i -e 's/CONTROLLER_IP/'"$CONTROLLER_IP"'/g' sources.list

cp $BASE_PATH/host_installation.sh host_installation
sed -i -e 's/PORTGROUPS/'"$PORTGROUP_STRING"'/g' host_installation.sh
sed -i -e 's/CONTROLLER_IP/'"$CONTROLLER_IP"'/g/' host_installation.sh

touch ovs-postup.sh
echo -e "$final_ovs_string\novs-vsctl set port eth0 trunk=$final_trunk_string" > ovs-postup.sh

}

#creating local ubuntu repo for precise(12.04)
Configure_Local_Ubuntu_Repo()
{

if test $LOCAL_REPO_FLAG -eq 1; then
	mkdir /var/local_rep
	sed -i -e 's/^/^#/g' /etc/apt/mirror.list
	echo -e "set base_path\t/var/local_rep\nset nthreads\t5\nset _tilde 0\ndeb-i386 http://repo.iitd.ernet.in/ubuntu precise main restricted universe multiverse\ndeb-amd64 http://repo.iitd.ernet.in/ubuntu precise main restricted universe multiverse\ndeb-i386 http://repo.iitd.ernet.in/ubuntu precise-proposed main restricted universe multiverse\ndeb-amd64 http://repo.iitd.ernet.in/ubuntu precise-proposed main restricted universe multiverse\ndeb-i386 http://repo.iitd.ernet.in/ubuntu precise-updates main restricted universe multiverse\ndeb-amd64 http://repo.iitd.ernet.in/ubuntu precise-updates main restricted universe multiverse\ndeb-i386 http://repo.iitd.ernet.in/ubuntu precise-security main restricted universe multiverse\ndeb-amd64 http://repo.iitd.ernet.in/ubuntu precise-security main restricted universe multiverse\ndeb-i386 http://repo.iitd.ernet.in/ubuntu precise-backports main restricted universe multiverse\ndeb-amd64 http://repo.iitd.ernet.in/ubuntu precise-backports main restricted universe multiverse\ndeb-i386 http://repo.iitd.ernet.in/ubuntupartner precise partner\ndeb-amd64 http://repo.iitd.ernet.in/ubuntupartner precise partner" >> /etc/apt/mirror.list
	apt-mirror
fi


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
	
	Configure_Tftp
	Configure_Dhcp_Pxe
	Configure_Local_Ubuntu_Repo

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
		  DocumentRoot /var/www
                  Redirect permanent /(baadal|admin).* https://10.208.21.111%{REQUEST_URI}   
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

	cd /home/www-data/web2py/logs/

	python /home/www-data/web2py/web2py.py -K  baadal &

}




################################ SCRIPT ########################################

#Including Config File to the current script
source installation.cfg

Chk_Root_Login

apt-get update
apt-get upgrade

Instl_Pkgs
Setup_Web2py
Enbl_Modules
Create_SSL_Certi
Rewrite_Apache_Conf
Start_Web2py

#####################################################################################
#####################################################################################
