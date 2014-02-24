# sqlite3 baadal_nat.db "CREATE TABLE mappings (id INTEGER PRIMARY KEY,public_ip TEXT UNIQUE, private_ip TEXT);"
#!/bin/bash

db_name="/baadal/baadal/baadalinstallation/nat_setup/baadal_nat.db"
table=mappings

if test $# -eq 0; then

	ip_mapping_string=$(sqlite3 $db_name "select public_ip,private_ip from $table;")
	ip_mapping_list=(`echo "$ip_mapping_string" | tr " " " "`)
	echo "" > restart.err
	
	for ip_mapping in ${ip_mapping_list[@]}; do
	
		ip_pair=(`echo "$ip_mapping" | tr "|" " "`)
		public_ip=${ip_pair[0]}
		private_ip=${ip_pair[1]}
		mapping_name=(`echo "$private_ip" | tr "." " "`)
		ifconfig eth0:"${mapping_name[2]}.${mapping_name[3]}" $public_ip up 2>> restart.err	
	
	done
	
	cat restart.err

elif test $# -eq 3; then

	public_ip=(`echo "$2" | tr "." " "`)
	private_ip=(`echo "$3" | tr "." " "`)

	if test $1 == 'add' || test $1 == 'remove'; then

		if test "$2" != "$3" && test ${public_ip[0]} -ne 0 && test ${public_ip[0]} -le 255 && test ${public_ip[1]} -le 255 && test ${public_ip[2]} -le 255 && test ${public_ip[3]} -le 255 && test ${public_ip[3]} -ne 0 && test ${private_ip[0]} -ne 0 && test ${private_ip[0]} -le 255 && test ${private_ip[1]} -le 255 && test ${private_ip[2]} -le 255 && test ${private_ip[3]} -le 255 && test ${private_ip[3]} -ne 0; then

			db_schema=$(sqlite3 $db_name ".schema $table")

			if test -f $db_name && test "$db_schema" != ""; then
			
				if test $1 == 'add'; then

					sqlite3 $db_name "insert into $table values(NULL,'$2','$3');" 2> db.err

					if test "$(cat db.err)" == ""; then

						iptables -t nat -I PREROUTING 1 -i eth0 -d $2 -j DNAT --to-destination $3 2> iptables.err
						iptables -t nat -I POSTROUTING 1 -s $3 -o eth0 -j SNAT --to-source $2 2>> iptables.err

						if test "$(cat iptables.err)" == ""; then

							ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $2 up 2> ipaliasing.err
			        
							if test "$(cat ipaliasing.err)" != ""; then

								echo "IP ALIASING ERROR!!!"
								cat ipaliasing.err
								ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $2 down
								iptables -t nat -D PREROUTING -i eth0 -d $2 -j DNAT --to-destination $3
								iptables -t nat -D POSTROUTING -s $3 -o eth0 -j SNAT --to-source $2			
								sqlite3 $db_name "delete from $table where public_ip='$2' and private_ip='$3';"

							fi

						else

							echo "IPTABLES ERROR!!!"
							cat iptables.err
							iptables -t nat -D PREROUTING -i eth0 -d $2 -j DNAT --to-destination $3
							iptables -t nat -D POSTROUTING -s $3 -o eth0 -j SNAT --to-source $2			
							sqlite3 $db_name "delete from $table where public_ip='$2' and private_ip='$3';"
							exit 1

						fi
						
					else 
								
						echo "DB Error!!!"
						cat db.err
						sqlite3 baadal_nat.db "select public_ip,private_ip from mappings;"
						exit 1
						
					fi
					
				elif test $1 == 'remove'; then

					ifconfig eth0:"${private_ip[2]}.${private_ip[3]}" $2 down
					iptables -t nat -D PREROUTING -i eth0 -d $2 -j DNAT --to-destination $3
					iptables -t nat -D POSTROUTING -s $3 -o eth0 -j SNAT --to-source $2			
					sqlite3 $db_name "delete from $table where public_ip='$2' and private_ip='$3';"

				fi
			
				/etc/init.d/iptables-persistent save
				/etc/init.d/iptables-persistent reload
				
			else

				echo "ERROR: Database or Table does not exists!!!"

			fi

		else

			echo "ERROR: Invalid IPs!!!"
			exit 1

		fi

	else

		echo "ERROR: Invalid Operation!!!"
		exit 1

	fi

else

	echo "ERROR: Invalid Number of Arguments!!!"
	exit 1

fi
