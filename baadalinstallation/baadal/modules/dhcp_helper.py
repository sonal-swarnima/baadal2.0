# -*- coding: utf-8 -*-
###################################################################################
from helper import config, execute_remote_cmd

dhcp_ip = config.get("GENERAL_CONF","dhcp_ip")

#Creates bulk entry into DHCP
# Gets list of tuple containing (host_name, mac_addr, ip_addr)
def create_dhcp_bulk_entry(dhcp_info_list):
    
    if len(dhcp_info_list) == 0: return
    entry_cmd = ""
    
    for dhcp_info in dhcp_info_list:
        host_name = dhcp_info[0] if dhcp_info[0] != None else ('IP_' + dhcp_info[2].replace(".", '_'))
        dhcp_cmd = '''
            file_name="/etc/dhcp/dhcp.d/1_%s.conf"
            if [ -e "$file_name" ]
            then
                echo $file_name
            else
               echo "host %s {\n\thardware ethernet %s;\n\tfixed-address %s;\n}\n" > $file_name
            fi
            ''' %(host_name, host_name, dhcp_info[1], dhcp_info[2])

        entry_cmd += dhcp_cmd
        
    restart_cmd = '''
                    cat /etc/dhcp/dhcp.d/*.conf > /etc/dhcp/dhcpd.conf
                    /etc/init.d/isc-dhcp-server restart                        
                    ''' 

    execute_remote_cmd(dhcp_ip, 'root', entry_cmd)
    execute_remote_cmd(dhcp_ip, 'root', restart_cmd)

#Creates single entry into DHCP
def create_dhcp_entry(host_name, mac_addr, ip_addr):
    
    dhcp_info_list = [(host_name, mac_addr, ip_addr)]
    create_dhcp_bulk_entry(dhcp_info_list)

#Removes entry from DHCP
<<<<<<< HEAD
def remove_dhcp_entry(host_name, ip_addr):
=======
def remove_dhcp_entry(host_name,ip_addr):
>>>>>>> 9bb3b24126028473b105a1463445d5e7edc3759c

    host_name = host_name if host_name != None else ('IP_' + ip_addr.replace(".", '_'))

    entry_cmd = "rm /etc/dhcp/dhcp.d/1_%s.conf" %(host_name)
    restart_cmd = '''
                    cat /etc/dhcp/dhcp.d/*.conf > /etc/dhcp/dhcpd.conf
                    /etc/init.d/isc-dhcp-server restart                        
                    ''' 

    execute_remote_cmd(dhcp_ip, 'root', entry_cmd)
    execute_remote_cmd(dhcp_ip, 'root', restart_cmd)


