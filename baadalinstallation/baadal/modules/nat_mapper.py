# -*- coding: utf-8 -*-
###################################################################################
""" nat_mapper.py: Manages NAT(Network Address Translation) machine so that;  
a Linux machine can act as router

Following scenarios are handled
1. Create mapping between public IP and private IP by creating interface for public
   IP and adding corresponding rules in IP tables
2. Remove mapping between public IP and private IP by deleting interface for public
   IP and removing corresponding rules from IP tables
3. Create mapping between VNC_Server:VNC_port & Host_Server:VNC_Port_of_VM by creating
   interface for VNC server if not present already and adding corresponding rules in 
   IP tables
4. Removing mapping between VNC_Server:VNC_port & Host_Server:VNC_Port_of_VM by deleting 
   corresponding rules from IP tables
5. Delete all VNC server mapping that has exceeded given duration
"""

from helper import logger, config, get_datetime, execute_remote_bulk_cmd, log_exception
from gluon import current

#nat types
NAT_TYPE_SOFTWARE = 'software_nat'
NAT_TYPE_HARDWARE = 'hardware_nat'
NAT_TYPE_MAPPING = 'mapping_nat'
NAT_PUBLIC_INTERFACE = 'eth0'

#VNC access status
VNC_ACCESS_STATUS_ACTIVE = 'active'
VNC_ACCESS_STATUS_INACTIVE = 'inactive'


def get_nat_details():
    nat_type = config.get("GENERAL_CONF", "nat_type")
    nat_ip = config.get("GENERAL_CONF", "nat_ip")
    nat_user = config.get("GENERAL_CONF", "nat_user")
    
    return (nat_type, nat_ip, nat_user)

#Construct command for updating IP tables
def get_ip_tables_command(command_type, source_ip , destination_ip, source_port = -1, destination_port = -1):
    
    pre_command = "iptables -t nat -I PREROUTING " if command_type == "Add" else "iptables -t nat -D PREROUTING  "
    
    if source_port == -1 & destination_port == -1:
        
        pre_command += "-i %s -d %s -j DNAT --to-destination %s" %(NAT_PUBLIC_INTERFACE, source_ip, destination_ip)

        post_command = "iptables -t nat -I POSTROUTING " if command_type == "Add" else "iptables -t nat -D POSTROUTING  "
        post_command += "-s %s -o %s -j SNAT --to-source %s" %(destination_ip, NAT_PUBLIC_INTERFACE, source_ip)
    else:
        pre_command += "-i %s -p tcp -d %s --dport %s -j DNAT --to %s:%s" %(NAT_PUBLIC_INTERFACE, source_ip, source_port, destination_ip, destination_port)

        post_command = "iptables -I FORWARD -p tcp " if command_type == "Add" else "iptables -D FORWARD -p tcp "
        post_command += "-d %s --dport %s -j ACCEPT" %(destination_ip, destination_port)
    
    command = '''
                %s
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(pre_command, post_command)

    
    return command

#Construct command for updating interfaces file
def get_interfaces_command(command_type, source_ip):

    source_ip_octets = source_ip.split('.')
    interface_alias = "%s:%s.%s.%s" %(NAT_PUBLIC_INTERFACE, source_ip_octets[1], source_ip_octets[2], source_ip_octets[3])
    interfaces_merge_command = "cat /etc/network/interfaces.d/*.cfg > /etc/network/interfaces"

    if command_type == 'Add':
        interfaces_command = '''
            ip_present=$(ifconfig | grep %s)
            if test -z "$ip_present"; then
                echo -e "auto %s\n iface %s inet static\n address %s\n netmask 255.255.255.255\n" > /etc/network/interfaces.d/2_%s.cfg
                %s
                ifconfig %s %s netmask 255.255.255.255 up
            fi
            ''' %(source_ip, interface_alias, interface_alias, source_ip, interface_alias, interfaces_merge_command, interface_alias, source_ip)
    else:
        interfaces_command = '''
            rm /etc/network/interfaces.d/2_%s.cfg
            ifconfig %s down
            %s
            ''' %(interface_alias, interface_alias, interfaces_merge_command)

    return interfaces_command

"""Function to create mappings in NAT
 If NAT type is software_nat then for creating public - private IP mapping:
 1) Create the alias on NAT that will listen on the public IP.
 2) Create rules in iptables to forward the traffic coming on public IP to private IP and vice versa.
 And for providing VNC access:
 1) Check if the NAT is listening on the public IP to be used for VNC access.
 2) If NAT is not listening on the desired public IP, create an alias to listen on that IP.
 3) Create rules in iptables to forward the VNC traffic to the host."""
def create_mapping(source_ip , destination_ip, source_port = -1, destination_port = -1, duration = -1 ):

    nat_type, nat_ip, nat_user = get_nat_details()

    if nat_type == NAT_TYPE_SOFTWARE:
        
        if source_port == -1 & destination_port == -1:
            logger.debug("Adding public ip %s private ip %s mapping on NAT" %(source_ip, destination_ip))

            interfaces_command = get_interfaces_command('Add', source_ip)
            iptables_command = get_ip_tables_command('Add', source_ip , destination_ip)
            
            command = interfaces_command + iptables_command

        else:
            logger.debug("Creating VNC mapping on NAT box for public IP %s host IP %s public VNC port %s private VNC port %s duration %s" %(source_ip, destination_ip, source_port, destination_port, duration))
            
            logger.debug("Creating SSH session on NAT box %s" %(nat_ip))
            
            interfaces_command = get_interfaces_command('Add', source_ip)
            iptables_command = get_ip_tables_command('Add', source_ip , destination_ip, source_port, destination_port)

            command = interfaces_command + iptables_command

        # Create SSH session to execute all commands on NAT box.
        execute_remote_bulk_cmd(nat_ip, nat_user, command)

    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        raise Exception("No implementation for NAT type hardware")
    elif nat_type == NAT_TYPE_MAPPING:
        # This function is to be implemented
        return
    else:
        raise Exception("NAT type is not supported")


"""Function to remove mapping from NAT
If NAT type is software_nat then for removing public IP - private IP mapping:
1) Remove the alias on NAT listening on the public IP.
2) Delete rules from iptables to forward the traffic coming on public IP to private IP and vice versa.
3) Flush the entries from DB and make public IP free.
And for revoking VNC access:
1) Delete rules from iptables to forward the VNC traffic to the host.
2) Update DB to make the VNC access inactive."""
def remove_mapping(source_ip, destination_ip, source_port=-1, destination_port=-1):

    nat_type, nat_ip, nat_user = get_nat_details()

    if nat_type == NAT_TYPE_SOFTWARE:
        # source_port and destination_port are -1 when function is called for removing public IP - private IP mapping
        if source_port == -1 and destination_port == -1:
            logger.debug("Removing mapping for public IP: %s and private IP: %s" %(source_ip, destination_ip))
            
            interfaces_command = get_interfaces_command('Delete', source_ip)
            iptables_command = get_ip_tables_command('Delete', source_ip , destination_ip)
            
            command = interfaces_command + iptables_command
            
        else:
            logger.debug("Removing VNC mapping from NAT for public IP %s host IP %s public VNC port %s private VNC port %s" %(source_ip, destination_ip, source_port, destination_port))

            command = get_ip_tables_command('Delete', source_ip , destination_ip, source_port, destination_port)

        # Create SSH session to execute all commands on NAT box.
        execute_remote_bulk_cmd(nat_ip, nat_user, command)

    elif nat_type == NAT_TYPE_HARDWARE:
        #This function is to be implemented
        raise Exception("No implementation for NAT type hardware")
    elif nat_type == NAT_TYPE_MAPPING:
        # This function is to be implemented
        return
    else:
        raise Exception("NAT type is not supported")

# Function to flush all mappings from NAT
def clear_all_nat_mappings(db):
    
    nat_type, nat_ip, nat_user = get_nat_details()

    if nat_type == NAT_TYPE_SOFTWARE:

        logger.debug("Clearing all NAT mappings")
    
        command = ''
        # For all public IP - private IP mappings, Delete aliases
        for vm_data_info in db(db.vm_data.public_ip != None).select():
            private_ip = vm_data_info.private_ip.private_ip
            public_ip = vm_data_info.public_ip.public_ip
            logger.debug('Removing private to public IP mapping for private IP: %s and public IP:%s' %(private_ip, public_ip))
#             private_ip_octets = mapping['private_ip'].split('.')
            public_ip_octets = public_ip.split('.')
            interface_alias = "%s:%s.%s.%s" %(NAT_PUBLIC_INTERFACE, public_ip_octets[1], public_ip_octets[2], public_ip_octets[3])

            command += '''
                        rm /etc/network/interfaces.d/2_%s.cfg
                        ifconfig %s down
                        cat /etc/network/interfaces.d/*.cfg > /etc/network/interfaces
                       ''' %(interface_alias, interface_alias)

        # Flushing all rules from iptables
        command += '''
            iptables --flush
            iptables -t nat --flush
            iptables --delete-chain
            iptables -t nat --delete-chain
            /etc/init.d/iptables-persistent save
            /etc/init.d/iptables-persistent reload
            exit
        '''
        execute_remote_bulk_cmd(nat_ip, nat_user, command)

        # Updating DB
        logger.debug("Flushing all public Ip - private IP mappings and VNC mappings from DB")
        db.vm_data.update(public_ip = None)
        db.vnc_access.update(status = VNC_ACCESS_STATUS_INACTIVE)
    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        raise Exception("No implementation for NAT type hardware")
    elif nat_type == NAT_TYPE_MAPPING:
        logger.debug("Clearing all mapping information from DB")

        db.vm_data.update(public_ip = None)
        db.vnc_access.update(status = VNC_ACCESS_STATUS_INACTIVE)

    else:
        raise Exception("NAT type is not supported")
        

# Function to delete all timed-out VNC mappings from NAT
def clear_all_timedout_vnc_mappings():
    
    nat_type, nat_ip, nat_user = get_nat_details()

    if nat_type == NAT_TYPE_SOFTWARE:
       
        logger.debug("Clearing all timed out VNC mappings from NAT box %s" %(nat_ip)) 

        # Get all active VNC mappings from DB
        vnc_mappings = current.db((current.db.vnc_access.status == VNC_ACCESS_STATUS_ACTIVE) & 
                                  (current.db.vnc_access.expiry_time < get_datetime())).select()
        if (vnc_mappings != None) & (len(vnc_mappings) != 0):
            # Delete the VNC mapping from NAT if the duration of access has past its requested time duration
            command = ''
            for mapping in vnc_mappings:
                logger.debug('Removing VNC mapping for vm id: %s, host: %s, source IP: %s, source port: %s, destination port: %s' %(mapping.vm_id, mapping.host_id, mapping.vnc_server_ip, mapping.vnc_source_port, mapping.vnc_destination_port))
                host_ip = mapping.host_id.host_ip.private_ip
                # Delete rules from iptables on NAT box
                command += '''
                iptables -D PREROUTING -t nat -i %s -p tcp -d %s --dport %s -j DNAT --to %s:%s
                iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT''' %(NAT_PUBLIC_INTERFACE, mapping.vnc_server_ip, mapping.vnc_source_port, host_ip, mapping.vnc_destination_port, host_ip, mapping.vnc_destination_port)

                # Update DB for each VNC access
                current.db(current.db.vnc_access.id == mapping.id).update(status=VNC_ACCESS_STATUS_INACTIVE)

            command += '''
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' 

            current.db.commit()
            execute_remote_bulk_cmd(nat_ip, nat_user, command)
        logger.debug("Done clearing vnc mappings")    
    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        raise Exception("No implementation for NAT type hardware")
    elif nat_type == NAT_TYPE_MAPPING:
        # This function is to be implemented
        logger.debug('Clearing all timed out VNC mappings') 

        # Get all active VNC mappings from DB
        vnc_mappings = current.db((current.db.vnc_access.status == VNC_ACCESS_STATUS_ACTIVE) & 
                                  (current.db.vnc_access.expiry_time < get_datetime())).select()
        if (vnc_mappings != None) & (len(vnc_mappings) != 0):

            for mapping in vnc_mappings:
                # Update DB for each VNC access
                current.db(current.db.vnc_access.id == mapping.id).update(status=VNC_ACCESS_STATUS_INACTIVE)
            current.db.commit()
        logger.debug("Done clearing vnc mappings")    
    else:
        raise Exception("NAT type is not supported")


# Function to create mapping in NAT for VNC access
def create_vnc_mapping_in_nat(vm_id):

    vm_data = current.db.vm_data[vm_id]
    vnc_host_ip = config.get("GENERAL_CONF", "vnc_ip")
    duration = 30 * 60 #30 minutes
    host_ip = vm_data.host_id.host_ip.private_ip
    vnc_port = vm_data.vnc_port
    
    vnc_id = current.db.vnc_access.insert(vm_id = vm_id,
                                    host_id = vm_data.host_id, 
                                    vnc_server_ip = vnc_host_ip, 
                                    vnc_source_port = vnc_port, 
                                    vnc_destination_port = vnc_port, 
                                    duration = duration, 
                                    status = VNC_ACCESS_STATUS_INACTIVE)
    
    try:
        create_mapping(vnc_host_ip, host_ip, vnc_port, vnc_port, duration)
        current.db.vnc_access[vnc_id] = dict(status = VNC_ACCESS_STATUS_ACTIVE)
    except:
        log_exception()


# Function to create mapping in NAT for public IP - private IP
def create_public_ip_mapping_in_nat(vm_id):
    
    vm_data = current.db.vm_data[vm_id]
    try:
        create_mapping(vm_data.public_ip, vm_data.private_ip)
        
        logger.debug("Updating DB")
        current.db(current.db.public_ip_pool.public_ip == vm_data.public_ip).update(vm_id = vm_id)
    except:
        log_exception()
    
# Function to remove mapping for VNC access from NAT
def remove_vnc_mapping_from_nat(vm_id):
    vm_data = current.db.vm_data[vm_id]
    vnc_host_ip = config.get("GENERAL_CONF", "vnc_ip")
    host_ip = vm_data.host_id.host_ip.private_ip
    vnc_port = vm_data.vnc_port

    try:
        remove_mapping(vnc_host_ip, host_ip, vnc_port, vnc_port)
        logger.debug("Updating DB")
        current.db(current.db.vnc_access.vm_id == vm_id).update(status = VNC_ACCESS_STATUS_INACTIVE)
    except:
        log_exception()
    
# Function to remove public IP - private IP mapping from NAT
def remove_public_ip_mapping_from_nat(vm_id):
    
    vm_data = current.db.vm_data[vm_id]
    try:
        remove_mapping(vm_data.public_ip, vm_data.private_ip)
        
        # Update DB 
        logger.debug("Updating DB")
        vm_data.update_record(public_ip = None)
    except:
        log_exception()

