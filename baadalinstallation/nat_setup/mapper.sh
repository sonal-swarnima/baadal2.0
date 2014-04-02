#!/bin/bash
# sqlite3 baadal_nat.db "CREATE TABLE mappings (id INTEGER PRIMARY KEY,public_ip TEXT UNIQUE, private_ip TEXT);"
# sqlite3 baadal_nat.db "CREATE TABLE vnc_ips (id INTEGER PRIMARY KEY, public_ip TEXT UNIQUE);"

db_name="/baadal/baadal/baadalinstallation/nat_setup/baadal_nat.db"
public_ip_mapping_table=mappings
vnc_ips_table=vnc_ips

create_mapping()
{
	public_ip=($(echo "$1" | tr "." " "))
        private_ip=($(echo "$2" | tr "." " "))
	if test "$1" != "$2" && test ${public_ip[0]} -ne 0 && test ${public_ip[0]} -le 255 && test ${public_ip[1]} -le 255 && test ${public_ip[2]} -le 255 && test ${public_ip[3]} -le 255 && test ${public_ip[3]} -ne 0 && test ${private_ip[0]} -ne 0 && test ${private_ip[0]} -le 255 && test ${private_ip[1]} -le 255 && test ${private_ip[2]} -le 255 && test ${private_ip[3]} -le 255 && test ${private_ip[3]} -ne 0; then
		if test "$3" -eq -1 && test "$4" -eq -1; then
			db_schema=$(sqlite3 $db_name ".schema $public_ip_mapping_table")
			if test -f $db_name && test "$db_schema" != ""; then	
				sqlite3 $db_name "insert into $public_ip_mapping_table values(NULL,'$1','$2');" 2> db.err

				if test "$(cat db.err)" == ""; then

                                	iptables -t nat -I PREROUTING 1 -i eth0 -d $1 -j DNAT --to-destination $2 2> iptables.err
                                        iptables -t nat -I POSTROUTING 1 -s $2 -o eth0 -j SNAT --to-source $1 2>> iptables.err

                                        if test "$(cat iptables.err)" == ""; then

                                        	ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $1 up 2> ipaliasing.err

                                                if test "$(cat ipaliasing.err)" != ""; then

                                                	echo "IP ALIASING ERROR!!!"
                                                        cat ipaliasing.err
                                                        ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $1 down
                                                        iptables -t nat -D PREROUTING -i eth0 -d $1 -j DNAT --to-destination $2
                                                        iptables -t nat -D POSTROUTING -s $2 -o eth0 -j SNAT --to-source $1
                                                        sqlite3 $db_name "delete from $public_ip_mapping_table where public_ip='$1' and private_ip='$2';"
							exit 1
                                                fi

                                        else
						echo "IPTABLES ERROR!!!"
						cat iptables.err
                                                iptables -t nat -D PREROUTING -i eth0 -d $1 -j DNAT --to-destination $2
                                                iptables -t nat -D POSTROUTING -s $2 -o eth0 -j SNAT --to-source $1
                                                sqlite3 $db_name "delete from $public_ip_mapping_table where public_ip='$1' and private_ip='$2';"
                                                exit 1

                                        fi

                                else
					echo "DB Error!!!"
                                        cat db.err
                                        sqlite3 $db_name  "select public_ip,private_ip from $public_ip_mapping_table;"
                                        exit 1

                                fi
			else
				echo "ERROR: Database or Table does not exist!!!"
			fi
		else
			vnc_ip=$(sqlite3 $db_name "select public_ip from $vnc_ips_table where public_ip = '$1';")
			if test -z "$vnc_ip"; then
				echo "ERROR:: PUBLIC IP IS NOT CONFIGURED FOR VNC ACCESS!!"
				exit 1
			else
				if test "$4" -eq -1; then
					private_port=$3
				else 
					private_port=$4
				fi
				iptables -I PREROUTING -t nat -i eth0 -p tcp -d $1 --dport $3 -j DNAT --to $2:$private_port  2> iptables.err
				iptables -I FORWARD -p tcp -d $2 --dport $private_port -j ACCEPT 2> iptables.err
				if test "$(cat iptables.err)" != ""; then
					echo "IPTABLES ERROR!!!"
					cat iptables.err
					iptables -D PREROUTING -t nat -i eth0 -p tcp -d $1 --dport $3 -j DNAT --to $2:$private_port
					iptables -D FORWARD -p tcp -d $2 --dport $private_port -j ACCEPT	
					exit 1
				fi
			fi
		fi
		/etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload	
	else
		echo "ERROR: Invalid IPs!!!"
                exit 1
	fi
}


remove_mapping()
{
	public_ip=($(echo "$1" | tr "." " "))
	private_ip=($(echo "$2" | tr "." " "))
	if test "$1" != "$2" && test ${public_ip[0]} -ne 0 && test ${public_ip[0]} -le 255 && test ${public_ip[1]} -le 255 && test ${public_ip[2]} -le 255 && test ${public_ip[3]} -le 255 && test ${public_ip[3]} -ne 0 && test ${private_ip[0]} -ne 0 && test ${private_ip[0]} -le 255 && test ${private_ip[1]} -le 255 && test ${private_ip[2]} -le 255 && test ${private_ip[3]} -le 255 && test ${private_ip[3]} -ne 0; then
                if test "$3" -eq -1 && test "$4" -eq -1; then
			db_schema=$(sqlite3 $db_name ".schema $public_ip_mapping_table")
	                if test -f $db_name && test "$db_schema" != ""; then
				ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $1 down
				iptables -t nat -D PREROUTING -i eth0 -d $1 -j DNAT --to-destination $2
				iptables -t nat -D POSTROUTING -s $2 -o eth0 -j SNAT --to-source $1
                                sqlite3 $db_name "delete from $public_ip_mapping_table where public_ip='$1' and private_ip='$2';"		
			else
				echo "ERROR: Database or Table does not exist!!!"
			fi
		else
			if test "$4" -eq -1; then
				private_port=$3
			else
				private_port=$4
			fi
			iptables -D PREROUTING -t nat -i eth0 -p tcp -d $1 --dport $3 -j DNAT --to $2:$private_port
			iptables -D FORWARD -p tcp -d $2 --dport $private_port -j ACCEPT
		fi
		/etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
	else
		echo "ERROR: Invalid IPs!!!"
                exit 1
	fi
}

change_mapping()
{
	remove_mapping $1 $2 $4 $5
	create_mapping $1 $3 $4 $5
}


create_alias()
{
	db_schema=$(sqlite3 $db_name ".schema $vnc_ips_table")
	if test -f $db_name && test "$db_schema" != ""; then
		sqlite3 $db_name "insert into $vnc_ips_table values(NULL,'$1');" 2> db.err
		public_ip=($(echo "$1"| tr "." " "))
		if test ${public_ip[0]} -ne 0 && test ${public_ip[0]} -le 255 && test ${public_ip[1]} -le 255 && test ${public_ip[2]} -le 255 && test ${public_ip[3]} -le 255 && test ${public_ip[3]} -ne 0; then
			if test "$(cat db.err)" == ""; then
				ifconfig eth0:"${public_ip[1]}${public_ip[2]}${public_ip[3]}" $1 up 2> ipaliasing.err
				if test "$(cat ipaliasing.err)" != ""; then
					echo "IP ALIASING ERROR!!!"
                                	cat ipaliasing.err
	                                ifconfig eth0:"$1" $1 down
        	                        sqlite3 $db_name "delete from $vnc_ips_table where public_ip='$1';"				
					exit 1
				fi
			else
				echo "DB Error!!!"
                	        cat db.err
                        	sqlite3 $db_name "select public_ip from $vnc_ips_table;"
	                        exit 1
			fi
		else
			echo "ERROR: Invalid public IP"
			exit 1
		fi
	else
		echo "ERROR: Database or Table does not exist!!!"
	fi
}

remove_alias()
{
	db_schema=$(sqlite3 $db_name ".schema $vnc_ips_table")
	public_ip=($(echo "$1"| tr "." " "))
        if test -f $db_name && test "$db_schema" != ""; then
		ifconfig eth0:"${public_ip[1]}${public_ip[2]}${public_ip[3]}" $1 down
		sqlite3 $db_name "delete from $vnc_ips_table where public_ip='$1';"
	else
		echo "ERROR: Database or Table does not exist!!!"
	fi
}

remove_all_vnc_mappings()
{
	vnc_mappings=($(echo "$1" | tr "|" " "))
	for mapping in ${vnc_mappings[@]}; do
		vnc_entry=($(echo $mapping | tr "," " "))
		public_ip=${vnc_entry[0]}
		private_ip=${vnc_entry[1]}
		public_port=${vnc_entry[2]:--1}
		private_port=${vnc_entry[3]:--1}
		echo "Removing entry $public_ip $private_ip $public_port $private_port"
		remove_mapping $public_ip $private_ip $public_port $private_port
	done
}

if test $# -eq 0; then

        ip_mapping_string=$(sqlite3 $db_name "select public_ip,private_ip from $public_ip_mapping_table;")
        ip_mapping_list=(`echo "$ip_mapping_string" | tr " " " "`)
        echo "" > restart.err

        for ip_mapping in ${ip_mapping_list[@]}; do

                ip_pair=(`echo "$ip_mapping" | tr "|" " "`)
                public_ip=${ip_pair[0]}
                private_ip=${ip_pair[1]}
                mapping_name=(`echo "$private_ip" | tr "." " "`)
                ifconfig eth0:"${mapping_name[2]}.${mapping_name[3]}" $public_ip up 2>> restart.err

        done

	vnc_ips_string=$(sqlite3 $db_name "select public_ip from $vnc_ips_table;")
	vnc_ips_list=(`echo "$vnc_ips_string" | tr " " " "`)
	for vnc_ip in ${vnc_ips_list[@]}; do
		ifconfig eth0:"$vnc_ip" $vnc_ip up 2>> restart.err
	done

        cat restart.err
elif test $# -eq 2; then
	echo "$1"
	if test $1 == 'create_alias'; then
		create_alias $2
	elif test $1 == 'remove_alias'; then
		remove_alias $2
	elif test $1 == 'remove_vnc_mappings'; then
		remove_all_vnc_mappings $2
	else
		echo "ERROR: INVALID OPERATION"
		exit 1
	fi
elif test $# -eq 3 || test $# -eq 4 || (test $# -eq 5 && test $1 != 'change_mapping'); then
	public_port=${4:--1} 
	private_port=${5:--1}
	if test $1 == 'create_mapping'; then
		create_mapping $2 $3 $public_port $private_port
	elif test $1 == 'remove_mapping'; then
		remove_mapping $2 $3 $public_port $private_port
	else
		echo "ERROR: INVALID OPERATION"
		exit 1	
	fi	
elif test $# -eq 5 || test $# -eq 6; then
	private_port=${6:--1}
	if test $1 == 'change_mapping'; then
		change_mapping $2 $3 $4 $5 $private_port
	else
		echo "ERROR: INVALID OPERATION"
                exit 1
	fi
fi
