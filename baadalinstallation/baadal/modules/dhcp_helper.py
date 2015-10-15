# -*- coding: utf-8 -*-
###################################################################################
""" dhcp_helper.py:  This module manages the DHCP configuration such as 
    - create an entry into DHCP
    - remove an entry from DHCP
    - create multiple entries in DHCP
    
    In order to manages all the configured IPs, a directory 'dhcp.d' is created within /etc/dhcp.
    
    For every new dhcp entry, a file with unique name is created in this directory with MAC address and fixed IP address configuration.

    The DHCP configuration file dhcpd.conf file is constructed using following command

    cat /etc/dhcp/dhcp.d/*.conf > /etc/dhcp/dhcpd.conf
    
    For removing the entry, corresponding file is deleted from the directory,
    and dhcp.d file is re-constructed
    
    DHCP is restarted after each modification.
"""
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
def remove_dhcp_entry(host_name, ip_addr):

    host_name = host_name if host_name != None else ('IP_' + ip_addr.replace(".", '_'))

    entry_cmd = "rm /etc/dhcp/dhcp.d/1_%s.conf" %(host_name)
    restart_cmd = '''
                    cat /etc/dhcp/dhcp.d/*.conf > /etc/dhcp/dhcpd.conf
                    /etc/init.d/isc-dhcp-server restart                        
                    ''' 

    execute_remote_cmd(dhcp_ip, 'root', entry_cmd)
    execute_remote_cmd(dhcp_ip, 'root', restart_cmd)


