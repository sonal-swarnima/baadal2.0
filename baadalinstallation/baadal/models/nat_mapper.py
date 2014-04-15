from helper import get_config_file, logger

config = get_config_file()

def create_mapping(public_ip, private_ip,vm_data_id, duration=-1, public_port=-1, private_port=-1 ):
    import paramiko
    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        if public_port == -1 and private_port == -1:
	    check_existence = db(db.vm_data.public.ip == public_ip & db.vm_data.private_ip == private_ip).select()
	    if check_existence != None:
		db.vm_data.update_or_insert(db.vm_data.id == vm_data_id, public_ip = public_ip)
		db.public_ip_pool.update_or_insert(db.public_ip_pool.public_ip == public_ip, vm_id=vm_data_id)
	        ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	        ssh.connect(nat_ip, username=nat_user)
		channel = ssh.invoke_shell()
		stdin = channel.makefile('wb')
		stdout = channel.makefile('rb')
		
		private_ip_octets = private_ip.split('.')
		interfaces_entry_command = "echo -e 'auto eth0:%s.%s\niface eth0:%s.%s inet static\n\taddress %s' >> /etc/network/interfaces" %(private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3], public_ip)
		interfaces_command = "ifconfig eth0:%s.%s %s up" %(private_ip_octets[2], private_ip_octets[3], public_ip)
		iptables_command = "iptables -t nat -I PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -I POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(public_ip, private_ip, private_ip, public_ip)
		stdin.write('''
			%s
			%s
			%s
			/etc/init.d/iptables-persistent restart
			exit
		''' %(interfaces_entry_command, interfaces_command, iptables_command))
		logger.debug(stdout.read())
		stdout.close()
		stdin.close()
		ssh.close()
	    else:
		logger.debug("public IP already assigned to some other VM in the DB. Please check and try again!")
	else:
	    if private_port == -1:
		private_port = public_port
	    host_id = db(db.host.host_ip == private_ip).select(id)
	    check_existence = db(db.vnc_access.vnc_server_ip == public_ip & db.vnc_access.host_id == host_id & db.vnc_access.vnc_public_port == public_port & db.vnc_access.vnc_private_port == private_port).select()
	    if check_existence != None:
		if duration == -1:
		    duration = 30
		db.vnc_access.insert(vm_id = vm_data_id, host_id = host_id, vnc_server_id = vnc_server_id, vnc_public_port = public_port, vnc_private_port = private_port, duration = duration, status = VNC_ACCESS_STATUS_ACTIVE)
		ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	        ssh.connect(nat_ip, username=nat_user)
		channel = ssh.invoke_shell()
		stdin = channel.makefile('wb')
		stdout = channel.makefile('rb')

		iptables_command = "iptables -I PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -I FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(public_ip, public_port,  private_ip, private_port, private_ip, private_port)
		stdin.write('''
			%s
			/etc/init.d/iptables-persistent restart
			exit
		''' %(iptables_command))
		logger.debug(stdout.read())
		stdout.close()
		stdin.close()
		ssh.close()
	
    elif nat_type == NAT_TYPE_HARDWARE:
	# This function is to be implemented
	logger.debug("No implementation for NAT type hardware")
    else:
	logger.debug("NAT type is not supported")


def remove_mapping(public_ip, private_ip,  vm_data_id, public_port=-1, private_port=-1):
    import paramiko
    nat_type = config.get("GENERAL_CONF", "nat_type")
    if nat_type == NAT_TYPE_SOFTWARE:
        nat_ip = config.get("GENERAL_CONF", "nat_ip")
        nat_user = config.get("GENERAL_CONF", "nat_user")
        if public_port == -1 and private_port == -1:
	    private_ip_octets = private_ip.split('.')
	    interfaces_entry_command = "sed -i '/auto.*eth0:%s.%s/ {N;N; s/auto.*eth0:%s.%s.*iface.*eth0:%s.%s.*inet.*static.*address.*%s//g} /etc/network/interfaces" %(private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3], private_ip_octets[2], private_ip_octets[3])
	    interfaces_command = "ifconfig eth0:%s.%S down" %(private_ip_octets[2], private_ip_octets[3])
	    iptables_command = "iptables -t nat -D PREROUTING -i eth0 -d %s -j DNAT --to-destination %s & iptables -t nat -D POSTROUTING -s %s -o eth0 -j SNAT --to-source %s" %(public_ip, private_ip, private_ip, public_ip)

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
		    /etc/init.d/iptables-persistent restart
		    exit
	    ''' %(interfaces_entry_command, interfaces_command, iptables_command))
	    logger.debug(stdout.read())
	    stdout.close()
	    stdin.close()
	    ssh.close()
	
	    db.vm_data.update_or_insert(db.vm_data.id==vm_data_id, public_ip = PUBLIC_IP_NOT_ASSIGNED)
	    
	else:
	    if private_port == -1:
		private_port = public_port
	    iptables_command = "iptables -D PREROUTING -t nat -i eth0 -p tcp -d %s --dport %s -j DNAT --to %s:%s  & iptables -D FORWARD -p tcp -d %s --dport %s -j ACCEPT" %(public_ip, public_port,  private_ip, private_port, private_ip, private_port)
	    ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    ssh.connect(nat_ip, username=nat_user)
	    channel = ssh.invoke_shell()
	    stdin = channel.makefile('wb')
	    stdout = channel.makefile('rb')

	    stdin.write('''
		    %s
		    /etc/init.d/iptables-persistent restart
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
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(nat_ip, username=nat_user)
    channel = ssh.invoke_shell()
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')

    public_ips_mapping = db(db.vm_data.public_ip != PUBLIC_IP_NOT_ASSIGNED).select(private_ip, public_ip)
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
	    /etc/init.d/iptables-persistent restart
	    exit
    ''')
    logger.debug(stdout.read())
    stdout.close()
    stdin.close()
    ssh.close()
