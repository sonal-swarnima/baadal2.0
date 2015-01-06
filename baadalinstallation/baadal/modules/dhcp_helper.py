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
            ip_present=$(grep 'host %s ' /etc/dhcp/dhcpd.conf)
            if test -z "$ip_present"; then
                echo "host %s {\n\thardware ethernet %s;\n\tfixed-address %s;\n}\n" >> /etc/dhcp/dhcpd.conf
            else
                echo %s
            fi
            ''' %(host_name, host_name, dhcp_info[1], dhcp_info[2], dhcp_info[2])

        entry_cmd += dhcp_cmd
        
    restart_cmd = "/etc/init.d/isc-dhcp-server restart"

    execute_remote_cmd(dhcp_ip, 'root', entry_cmd)
    execute_remote_cmd(dhcp_ip, 'root', restart_cmd)

#Creates single entry into DHCP
def create_dhcp_entry(host_name, mac_addr, ip_addr):
    
    dhcp_info_list = [(host_name, mac_addr, ip_addr)]
    create_dhcp_bulk_entry(dhcp_info_list)

#Removes entry from DHCP
def remove_dhcp_entry(host_name, mac_addr, ip_addr):

    host_name = host_name if host_name != None else ('IP_' + ip_addr.replace(".", '_'))

    if mac_addr != None:
        entry_cmd = "sed -i '/host.*%s.*{/ {N;N;N; s/host.*%s.*{.*hardware.*ethernet.*%s;.*fixed-address.*%s;.*}//g}' /etc/dhcp/dhcpd.conf" %(host_name, host_name, mac_addr, ip_addr)
    else:
        entry_cmd = "sed -i '/host.*%s.*{/ {N;N;N; s/host.*%s.*{.*}//g}' /etc/dhcp/dhcpd.conf" %(host_name, host_name)

    restart_cmd = "/etc/init.d/isc-dhcp-server restart"
    
    execute_remote_cmd(dhcp_ip, 'root', entry_cmd)
    execute_remote_cmd(dhcp_ip, 'root', restart_cmd)


