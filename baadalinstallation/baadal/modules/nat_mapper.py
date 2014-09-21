# -*- coding: utf-8 -*-
###################################################################################
from helper import logger, config, get_datetime, execute_remote_bulk_cmd, log_exception
from gluon import current

#nat types
NAT_TYPE_SOFTWARE = 'software_nat'
NAT_TYPE_HARDWARE = 'hardware_nat'
NAT_TYPE_MAPPING = 'mapping_nat'

#VNC access status
VNC_ACCESS_STATUS_ACTIVE = 'active'
VNC_ACCESS_STATUS_INACTIVE = 'inactive'

def get_nat_details():
    nat_type = config.get("GENERAL_CONF", "nat_type")
    nat_ip = config.get("GENERAL_CONF", "nat_ip")
    nat_user = config.get("GENERAL_CONF", "nat_user")
    
    return (nat_type, nat_ip, nat_user)

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
            # Create SSH session to execute all commands on NAT box

            destination_ip_octets = destination_ip.split('.')
            interfaces_entry_command = "echo -e 'auto eth0:%s.%s\niface eth0:%s.%s inet static\n\taddress %s' >> /etc/network/interfaces" %(destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], source_ip)
            interfaces_command = "ifconfig eth0:%s.%s %s up" %(destination_ip_octets[2], destination_ip_octets[3], source_ip)
            iptables_command = "iptables -t nat -I PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -I POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(source_ip, destination_ip, destination_ip, source_ip)
            
            command = '''
                %s
                %s
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(interfaces_entry_command, interfaces_command, iptables_command)
            execute_remote_bulk_cmd(nat_ip, nat_user, command)

        else:
            logger.debug("Creating VNC mapping on NAT box for public IP %s host IP %s public VNC port %s private VNC port %s duration %s" %(source_ip, destination_ip, source_port, destination_port, duration))
            source_ip_octets = source_ip.split('.')
            interfaces_alias = "%s%s%s" %(source_ip_octets[1], source_ip_octets[2], source_ip_octets[3])
            
            # Create SSH session to execute all commands on NAT box.
            logger.debug("Creating SSH session on NAT box %s" %(nat_ip))
            
            iptables_command = "iptables -I PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -I FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(source_ip, source_port,  destination_ip, destination_port, destination_ip, destination_port)
            command = '''
                ip_present=$(ifconfig | grep %s)
                if test -z "$ip_present"; then
                    echo -e "auto eth0:%s\niface eth0:%s inet static\n\taddress %s" >> /etc/network/interfaces
                    ifconfig eth0:%s %s up
                fi
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
                '''%(source_ip, interfaces_alias, interfaces_alias, source_ip, interfaces_alias, source_ip, iptables_command)
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
            destination_ip_octets = destination_ip.split('.')
            interfaces_entry_command = "sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g}' /etc/network/interfaces" %(destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], source_ip)
            interfaces_command = "ifconfig eth0:%s.%s down" %(destination_ip_octets[2], destination_ip_octets[3])
            iptables_command = "iptables -t nat -D PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -D POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(source_ip, destination_ip, destination_ip, source_ip)

            command = '''
                %s
                %s
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(interfaces_entry_command, interfaces_command, iptables_command)
            execute_remote_bulk_cmd(nat_ip, nat_user, command)
        else:
            logger.debug("Removing VNC mapping from NAT for public IP %s host IP %s public VNC port %s private VNC port %s" %(source_ip, destination_ip, source_port, destination_port))
            iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(source_ip, source_port,  destination_ip, destination_port, destination_ip, destination_port)

            command = '''
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(iptables_command)
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
        public_ip_mappings = db(db.vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED).select(db.vm_data.private_ip, db.vm_data.public_ip)
        for mapping in public_ip_mappings:
            logger.debug('Removing private to public IP mapping for private IP: %s and public IP:%s' %(mapping['private_ip'],mapping['public_ip']))
            private_ip_octets = mapping['private_ip'].split('.')

            command += '''
                        sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g} /etc/network/interfaces
                        ifconfig eth0:%s.%S down
                       ''' %(private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3])

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
        db.vm_data.update(public_ip = current.PUBLIC_IP_NOT_ASSIGNED)
        db.public_ip_pool.update(vm_id = None)
        db.vnc_access.update(status = VNC_ACCESS_STATUS_INACTIVE)
    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        raise Exception("No implementation for NAT type hardware")
    elif nat_type == NAT_TYPE_MAPPING:
        logger.debug("Clearing all mapping information from DB")

        db.vm_data.update(public_ip = current.PUBLIC_IP_NOT_ASSIGNED)
        db.public_ip_pool.update(vm_id = None)
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
                host_ip = mapping.host_id.host_ip
                # Delete rules from iptables on NAT box
                command += '''
                iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s
                iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT''' %(mapping.vnc_server_ip, mapping.vnc_source_port, host_ip, mapping.vnc_destination_port, host_ip, mapping.vnc_destination_port)

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
    host_ip = vm_data.host_id.host_ip
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
    host_ip = vm_data.host_id.host_ip
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
        current.db(current.db.public_ip_pool.public_ip == vm_data.public_ip).update(vm_id = None)
        vm_data.update_record(public_ip = current.PUBLIC_IP_NOT_ASSIGNED)
    except:
        log_exception()

