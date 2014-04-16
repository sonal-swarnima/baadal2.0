# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
from helper import logger, config
from datetime import datetime
import paramiko

def create_mapping( vm_data_id, destination_ip, source_ip , source_port=-1, destination_port=-1, duration=-1 ):

    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        if source_port == -1 & destination_port == -1:
            check_existence = db(db.vm_data.public_ip == source_ip and db.vm_data.private_ip == destination_ip).select()
            if check_existence != None:
                db.vm_data.update_or_insert(db.vm_data.id == vm_data_id, public_ip = source_ip)
                db.public_ip_pool.update_or_insert(db.public_ip_pool.public_ip == source_ip, vm_id=vm_data_id)
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
            check_existence = db(db.vnc_access.vnc_server_ip == source_ip and db.vnc_access.host_id == host_id and db.vnc_access.vnc_source_port == source_port and db.vnc_access.vnc_destination_port == destination_port).select()

            if check_existence != None:
                db.vnc_access.insert(vm_id = vm_data_id, host_id = host_id, vnc_server_ip = source_ip, vnc_source_port = source_port, vnc_destination_port = destination_port, duration = duration, status = VNC_ACCESS_STATUS_ACTIVE)
                source_ip_octets = source_ip.split('.')
                interfaces_alias = "%s%s%s" %(source_ip_octets[1], source_ip_octets[2], source_ip_octets[3])
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


def remove_mapping(vm_data_id, destination_ip, source_ip = None, source_port=-1, destination_port=-1):

    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        if source_port == -1 and destination_port == -1:
            destination_ip_octets = destination_ip.split('.')
            interfaces_entry_command = "sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g} /etc/network/interfaces" %(destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3], destination_ip_octets[2], destination_ip_octets[3])
            interfaces_command = "ifconfig eth0:%s.%S down" %(destination_ip_octets[2], destination_ip_octets[3])
            iptables_command = "iptables -t nat -D PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -D POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(source_ip, destination_ip, destination_ip, source_ip)

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(nat_ip, username=nat_user)
            channel = ssh.invoke_shell()
            stdin = channel.makefile('wb')
            stdout = channel.makefile('rb')

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

            db.vm_data.update_or_insert(db.vm_data.id==vm_data_id, public_ip = PUBLIC_IP_NOT_ASSIGNED)

        else:
            iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(source_ip, source_port,  destination_ip, destination_port, destination_ip, destination_port)
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
            db.vnc_access.update_or_insert(db.vnc_access.vm_id == vm_data_id, status = VNC_ACCESS_STATUS_INACTIVE)

    elif nat_type == NAT_TYPE_HARDWARE:
        #This function is to be implemented
        logger.debug("No implementation for NAT type hardware")
    else:
        logger.debug("NAT type is not supported")

def clear_all_nat_mappings():

    nat_ip = config.get("GENERAL_CONF", "nat_ip")
    nat_user = config.get("GENERAL_CONF", "nat_user")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(nat_ip, username=nat_user)
    channel = ssh.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')

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

def clear_all_timedout_vnc_mappings():

    nat_ip = config.get("GENERAL_CONF", "nat_ip")
    nat_user = config.get("GENERAL_CONF", "nat_user")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(nat_ip, username=nat_user)
    channel = ssh.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')

    timedout_vnc_mappings = db(((datetime.now()-db.vnc_access.time_requested.isoformat()).seconds/60) >= db.vnc_access.duration).select(db.vnc_access.ALL)
    for mapping in timedout_vnc_mappings:
        logger.debug('Removing VNC mapping for vm id: %s, host: %s, source IP: %s, source port: %s, destination port: %s' %(mapping['vm_id'], mapping['host_id'], mapping['vnc_server_ip'], mapping['vnc_source_port'], mapping['vnc_destination_port']))
        host_ip=db(db.host.id == mapping['host_id']).select(db.host.host_ip)
        iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(mapping['vnc_server_ip'], mapping['vnc_source_port'],  host_ip, mapping['vnc_destination_port'], host_ip, mapping['vnc_destination_port'])
        stdin.write('''
            %s
            /etc/init.d/iptables-persistent save
            /etc/init.d/iptables-persistent reload
            exit
        ''' %(iptables_command))
        db.vnc_access.update_or_insert(db.vnc_access.id == mapping['id'], status = VNC_ACCESS_STATUS_INACTIVE)
        
    logger.debug(stdout.read())
    stdout.close()
    stdin.close()
    ssh.close()

def create_vnc_mapping_in_nat(vm_data_id, destination_ip = None, source_ip = None, destination_port = -1, source_port = -1, duration = -1):
    vm_data = db.vm_data[vm_data_id]
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
    create_mapping(vm_data_id, destination_ip, source_ip, source_port, destination_port, duration)


def create_public_ip_mapping_in_nat(vm_data_id, source_ip, destionation_ip = None):
    vm_data = db.vm_data[vm_data_id]
    if destination_ip == None:
        destination_ip = vm_data.private_ip
    create_mapping(vm_data_id, destination_ip, source_ip)
    
def remove_vnc_mapping_from_nat(vm_data_id, destination_ip = None, source_ip = None, destination_port = -1, source_port = -1, duration  = -1):
    vm_data = db.vm_data[vm_data_id]
    if destination_ip ==None:
        destination_ip = vm_data.host_id.host_ip
    if source_ip == None:
        source_ip = config.get("GENERAL_CONF", "vnc_ip")
    if destination_port == -1:
        destination_port = vm_data.vnc_port
    if source_port == -1:
        source_port = vm_data.vnc_port
    remove_mapping(vm_data_id, destination_ip, source_ip, source_port, destination_port)
    
def remove_public_ip_mapping_from_nat(vm_data_id, source_ip, destination_ip = None):
    vm_data = db.vm_data[vm_data_id]
    if destination_ip == None:
        destination_ip = vm_data.private_ip
    remove_mapping(vm_data_id, destination_ip, source_ip)

