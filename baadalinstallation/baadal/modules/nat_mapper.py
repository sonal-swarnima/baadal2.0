# -*- coding: utf-8 -*-
###################################################################################
from helper import logger, config, get_datetime
import paramiko
from gluon import current

#nat types
NAT_TYPE_SOFTWARE = 'software_nat'
NAT_TYPE_HARDWARE = 'hardware_nat'

#VNC access status
VNC_ACCESS_STATUS_ACTIVE = 'active'
VNC_ACCESS_STATUS_INACTIVE = 'inactive'

#Function to create mappings in NAT
def create_mapping(db, vm_data_id, destination_ip, source_ip , source_port=-1, destination_port=-1, duration=-1 ):

    nat_type = config.get("GENERAL_CONF", "nat_type")
    # If NAT type is software_nat then for creating public - private IP mapping:
    # 1) Update DB to reflect the mapping.
    # 2) Create the alias on NAT that will listen on the public IP.
    # 3) Create rules in iptables to forward the traffic coming on public IP to private IP and vice versa.
    # And for providing VNC access:
    # 1) Update DB to reflect the VNC access info.
    # 2) Check if the NAT is listening on the public IP to be used for VNC access.
    # 3) If NAT is not listening on the desired public IP, create an alias to listen on that IP.
    # 4) Create rules in iptables to forward the VNC traffic to the host.
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        if source_port == -1 & destination_port == -1:
            logger.debug("Adding public ip %s private ip %s mapping on NAT" %(source_ip, destination_ip))
            # Check that the mapping does not exist already
            check_existence = db(db.vm_data.public_ip == source_ip).select()
            if check_existence != None:
                # Update entries in DB
                logger.debug("Updating DB")
                db(db.vm_data.id == vm_data_id).update(public_ip = source_ip)
                db(db.public_ip_pool.public_ip == source_ip).update(vm_id=vm_data_id)

                # Create SSH session to execute all commands on NAT box
                logger.debug("Creating SSH session on NAT box %s" %(nat_ip))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(nat_ip, username=nat_user)
                channel = ssh.invoke_shell()
                stdin = channel.makefile('wb')
                stdout = channel.makefile('rb')

                destination_ip_octets = destination_ip.split('.')
                interfaces_entry_command = "echo -e 'auto eth0:%s.%s\niface eth0:%s.%s inet static\n\taddress %s' >> /etc/network/interfaces" %(destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], source_ip)
                interfaces_command = "ifconfig eth0:%s.%s %s up" %(destination_ip_octets[2], destination_ip_octets[3], source_ip)
                iptables_command = "iptables -t nat -I PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -I POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(source_ip, destination_ip, destination_ip, source_ip)
                stdin.write('''
                    %s
                    %s
                    %s
                    /etc/init.d/iptables-persistent save
                    /etc/init.d/iptables-persistent reload
                    exit
                ''' %(interfaces_entry_command, interfaces_command, iptables_command))
                logger.debug(stdout.read())
                stdout.close()
                stdin.close()
                ssh.close()
            else:
                logger.debug("public IP already assigned to some other VM in the DB. Please check and try again!")
        else:
            vm_data = db.vm_data[vm_data_id]
            host_id = vm_data.host_id  
            logger.debug("Creating VNC mapping on NAT box for public IP %s host IP %s public VNC port %s private VNC port %s duration %s" %(source_ip, destination_ip, source_port, destination_port, duration))
            # Check for active VNC access
            check_existence = db(db.vnc_access.vnc_server_ip == source_ip and db.vnc_access.host_id == host_id and db.vnc_access.vnc_source_port == source_port and db.vnc_access.vnc_destination_port == destination_port and db.vnc_access.status == VNC_ACCESS_STATUS_ACTIVE).select()

            # Try granting new VNC access if missing
            if check_existence != None:
                # Updating DB
                logger.debug("Updating DB")
                db.vnc_access.insert(vm_id = vm_data_id, host_id = host_id, vnc_server_ip = source_ip, vnc_source_port = source_port, vnc_destination_port = destination_port, duration = duration, status = VNC_ACCESS_STATUS_ACTIVE)
                source_ip_octets = source_ip.split('.')
                interfaces_alias = "%s%s%s" %(source_ip_octets[1], source_ip_octets[2], source_ip_octets[3])

                # Create SSH session to execute all commands on NAT box.
                logger.debug("Creating SSH session on NAT box %s" %(nat_ip))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(nat_ip, username=nat_user)
                channel = ssh.invoke_shell()
                stdin = channel.makefile('wb')
                stdout = channel.makefile('rb')

                iptables_command = "iptables -I PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -I FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(source_ip, source_port,  destination_ip, destination_port, destination_ip, destination_port)
                stdin.write('''
                    ip_present=$(ifconfig | grep %s)
                    if test -z "$ip_present"; then
                        echo -e "auto eth0:%s\niface eth0:%s inet static\n\taddress %s" >> /etc/network/interfaces
                        ifconfig eth0:%s %s up
                    fi
                    %s
                    /etc/init.d/iptables-persistent save
                    /etc/init.d/iptables-persistent reload
                    exit
                '''%(source_ip, interfaces_alias, interfaces_alias, source_ip, interfaces_alias, source_ip, iptables_command))
                logger.debug(stdout.read())
                stdout.close()
                stdin.close()
                ssh.close()

    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        logger.debug("No implementation for NAT type hardware")
    else:
        logger.debug("NAT type is not supported")


# Function to remove mapping from NAT
def remove_mapping(db, vm_data_id, destination_ip, source_ip = None, source_port=-1, destination_port=-1):

    nat_type = config.get("GENERAL_CONF", "nat_type")
    # If NAT type is software_nat then for removing public IP - private IP mapping:
    # 1) Remove the alias on NAT listening on the public IP.
    # 2) Delete rules from iptables to forward the traffic coming on public IP to private IP and vice versa.
    # 3) Flush the entries from DB and make public IP free.
    # And for revoking VNC access:
    # 1) Delete rules from iptables to forward the VNC traffic to the host.
    # 2) Update DB to make the VNC access inactive.
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        # source_port and destination_port are -1 when function is called for removing public IP - private IP mapping
        if source_port == -1 and destination_port == -1:
            logger.debug("Removing mapping for public IP: %s and private IP: %s" %(source_ip, destination_ip))
            destination_ip_octets = destination_ip.split('.')
            interfaces_entry_command = "sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g}' /etc/network/interfaces" %(destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], source_ip)
            interfaces_command = "ifconfig eth0:%s.%s down" %(destination_ip_octets[2], destination_ip_octets[3])
            iptables_command = "iptables -t nat -D PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -D POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(source_ip, destination_ip, destination_ip, source_ip)

            # Create single SSh session to execute all commands on NAT box
            logger.debug("Creating ssh connection to NAT machine %s" %(nat_ip))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(nat_ip, username=nat_user)
            channel = ssh.invoke_shell()
            stdin = channel.makefile('wb')
            stdout = channel.makefile('rb')

            logger.debug("Executing commands on NAT machine %s\n%s\n%s" %(interfaces_entry_command, interfaces_command, iptables_command))
            stdin.write('''
                %s
                %s
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(interfaces_entry_command, interfaces_command, iptables_command))
            logger.debug(stdout.read())
            stdout.close()
            stdin.close()
            ssh.close()

            # Update DB 
            logger.debug("Updating DB")
            db(db.vm_data.id==vm_data_id).update(public_ip = current.PUBLIC_IP_NOT_ASSIGNED)
            db(db.public_ip_pool.public_ip == source_ip).update(vm_id = None)
            db.commit()

        else:
            logger.debug("Removing VNC mapping from NAT for public IP %s host IP %s public VNC port %s private VNC port %s" %(source_ip, destination_ip, source_port, destination_port))
            iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(source_ip, source_port,  destination_ip, destination_port, destination_ip, destination_port)

            # Create single SSh session to execute all commands on NAT box
            logger.debug("Creating ssh connection to NAT machine %s" %(nat_ip))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(nat_ip, username=nat_user)
            channel = ssh.invoke_shell()
            stdin = channel.makefile('wb')
            stdout = channel.makefile('rb')

            stdin.write('''
                %s
                /etc/init.d/iptables-persistent save
                /etc/init.d/iptables-persistent reload
                exit
            ''' %(iptables_command))
            logger.debug(stdout.read())
            stdout.close()
            stdin.close()
            ssh.close()

            # Update DB
            logger.debug("Updating DB")
            db(db.vnc_access.vm_id == vm_data_id).update(status = VNC_ACCESS_STATUS_INACTIVE)

    elif nat_type == NAT_TYPE_HARDWARE:
        #This function is to be implemented
        logger.debug("No implementation for NAT type hardware")
    else:
        logger.debug("NAT type is not supported")

# Function to flush all mappings from NAT
def clear_all_nat_mappings(db):
    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:

        logger.debug("Clearing all NAT mappings")
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
    
        # Create single SSh session to execute all commands on NAT box
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(nat_ip, username=nat_user)
        channel = ssh.invoke_shell()
        stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')

        # For all public IP - private IP mappings, Delete aliases
        public_ip_mappings = db(db.vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED).select(db.vm_data.private_ip, db.vm_data.public_ip)
        for mapping in public_ip_mappings:
            logger.debug('Removing private to public IP mapping for private IP: %s and public IP:%s' %(mapping['private_ip'],mapping['public_ip']))
            private_ip_octets = mapping['private_ip'].split('.')
            interfaces_entry_command = "sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g} /etc/network/interfaces" %(private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3])
            interfaces_command = "ifconfig eth0:%s.%S down" %(private_ip_octets[2], private_ip_octets[3])
            stdin.write('''
                %s
                %s
            ''' %(interfaces_entry_command, interfaces_command))

        # Flushing all rules from iptables
        stdin.write('''
            iptables --flush
            iptables -t nat --flush
            iptables --delete-chain
            iptables -t nat --delete-chain
            /etc/init.d/iptables-persistent save
            /etc/init.d/iptables-persistent reload
            exit
        ''')
        logger.debug(stdout.read())
        stdout.close()
        stdin.close()
        ssh.close()

        # Updating DB
        logger.debug("Flushing all public Ip - private IP mappings and VNC mappings from DB")
        db.vm_data.update(public_ip = current.PUBLIC_IP_NOT_ASSIGNED)
        db.public_ip_pool.update(vm_id = None)
        db.vnc_access.update(status = VNC_ACCESS_STATUS_INACTIVE)
    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        logger.debug("No implementation for NAT type hardware")
    else:
        logger.debug("NAT type is not supported")
        

# Function to delete all timed-out VNC mappings from NAT
def clear_all_timedout_vnc_mappings():

    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:

        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
       
        logger.debug("Clearing all timed out VNC mappings from NAT box %s" %(nat_ip)) 
        # Create single SSH session to execute all commands on the NAT box    
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(nat_ip, username=nat_user)
        channel = ssh.invoke_shell()
        stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')

        # Get all active VNC mappings from DB
        vnc_mappings = current.db(current.db.vnc_access.status == VNC_ACCESS_STATUS_ACTIVE).select(current.db.vnc_access.ALL)
        if vnc_mappings != None:
            # Delete the VNC mapping from NAT if the duration of access has past its requested time duration
            for mapping in vnc_mappings:
                if mapping.time_requested != None:
                    time_difference = (get_datetime() - mapping.time_requested).seconds/60
                    if time_difference >= mapping.duration:
                        logger.debug('Removing VNC mapping for vm id: %s, host: %s, source IP: %s, source port: %s, destination port: %s' %(mapping['vm_id'], mapping['host_id'], mapping['vnc_server_ip'], mapping['vnc_source_port'], mapping['vnc_destination_port']))
                        host_ip=current.db(current.db.host.id == mapping['host_id']).select(current.db.host.host_ip)
                        # Delete rules from iptables on NAT box
                        iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(mapping['vnc_server_ip'], mapping['vnc_source_port'],  host_ip, mapping['vnc_destination_port'], host_ip, mapping['vnc_destination_port'])
                        stdin.write('''
                            %s
                            /etc/init.d/iptables-persistent save
                            /etc/init.d/iptables-persistent reload
                            exit
                        ''' %(iptables_command))
                        # Update DB for each VNC access
                        current.db(current.db.vnc_access.id == mapping.id).update(status=VNC_ACCESS_STATUS_INACTIVE)
        logger.debug("Updating DB")
        current.db.commit()
        logger.debug("Done clearing vnc mappings")    
        logger.debug(stdout.read())
        stdout.close()
        stdin.close()
        ssh.close()
    elif nat_type == NAT_TYPE_HARDWARE:
        # This function is to be implemented
        logger.debug("No implementation for NAT type hardware")
    else:
        logger.debug("NAT type is not supported")


# Function to create mapping in NAT for VNC access
def create_vnc_mapping_in_nat(vm_data_id, destination_ip = None, source_ip = None, destination_port = -1, source_port = -1, duration = -1):
    vm_data = current.db.vm_data[vm_data_id]
    if destination_ip == None:
        destination_ip = vm_data.host_id.host_ip
    if source_ip == None:
        source_ip = config.get("GENERAL_CONF", "vnc_ip")
    if destination_port == -1:
        destination_port = vm_data.vnc_port
    if source_port == -1:
        source_port = vm_data.vnc_port
    if duration == -1:
        duration = 30
    create_mapping(current.db, vm_data_id, destination_ip, source_ip, source_port, destination_port, duration)


# Function to create mapping in NAT for public IP - private IP
def create_public_ip_mapping_in_nat(vm_data_id, source_ip, destination_ip = None):
    if destination_ip == None:
        vm_data = current.db.vm_data[vm_data_id]
        destination_ip = vm_data.private_ip
    create_mapping(current.db, vm_data_id, destination_ip, source_ip)
    
# Function to remove mapping for VNC access from NAT
def remove_vnc_mapping_from_nat(vm_data_id, destination_ip = None, source_ip = None, destination_port = -1, source_port = -1, duration  = -1):
    vm_data = current.db.vm_data[vm_data_id]
    if destination_ip ==None:
        destination_ip = vm_data.host_id.host_ip
    if source_ip == None:
        source_ip = config.get("GENERAL_CONF", "vnc_ip")
    if destination_port == -1:
        destination_port = vm_data.vnc_port
    if source_port == -1:
        source_port = vm_data.vnc_port
    remove_mapping(current.db, vm_data_id, destination_ip, source_ip, source_port, destination_port)
    
# Function to remove public IP - private IP mapping from NAT
def remove_public_ip_mapping_from_nat(vm_data_id, source_ip, destination_ip = None):
    if destination_ip == None:
        vm_data = current.db.vm_data[vm_data_id]
        destination_ip = vm_data.private_ip
    remove_mapping(current.db, vm_data_id, destination_ip, source_ip)

