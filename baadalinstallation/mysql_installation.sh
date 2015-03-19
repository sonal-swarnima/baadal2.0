#!/bin/bash

source ./controller_installation.cfg 2>> /dev/null

Normal_pkg_lst=(git zip unzip tar openssh-server build-essential nfs-common)
Mysql_pkg_lst=(mysql-server-5.5:mysql-server-5.1 libapache2-mod-auth-mysql php5-mysql)

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

#Function to populate the list of packages to be installted
Populate_Pkg_Lst()
{

	Pkg_lst=${Normal_pkg_lst[@]}

	Pkg_lst=("${Pkg_lst[@]}" "${Mysql_pkg_lst[@]}")
	
}

#Function that install all the packages packages
Instl_Pkgs()
{	
	apt-get update && apt-get -y upgrade

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
	echo "Packages Installed Successfully..................................."
}

loaddb()
{

    ## to enable remote login to mysql
    sed -i 's/bind-address/#bind-address/g' /etc/mysql/my.cnf
    service mysql restart

    mysql -uroot -p$MYSQL_ROOT_PASSWD -e "drop database baadal ; create database baadal;"  
    mysql -uroot -p$MYSQL_ROOT_PASSWD baadal < dumpfile.sql 
    mysql -uroot -p$MYSQL_ROOT_PASSWD baadal -e "grant all privileges on *.* to root@'%' identified by '$MYSQL_ROOT_PASSWD' with grant option; grant all privileges on *.* to baadaltesting@'%' identified by 'test_baadal' with grant option ;" 

}



##############################################################################################################################

#Including Config File to the current script

Chk_Root_Login
Chk_installation_config
Chk_Gateway
Instl_Pkgs
loaddb
