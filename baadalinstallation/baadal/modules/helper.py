# -*- coding: utf-8 -*-
###################################################################################

from gluon import current
from gluon.validators import Validator
from log_handler import logger
import os
import paramiko
import random
import re


def get_context_path():
    """
    Returns the application context path
    """
    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_config_file():
    """
    Returns the handler for application config file
    """
    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'private/baadalapp.cfg'));
    return config

config = get_config_file()

def get_datetime():
    """
    Generic method defined to return datetime, for uniformity
    """
    import datetime
    return datetime.datetime.now()


def get_constant(constant_name):
    """
    Get value from table 'costants'
    """
    constant = current.db.constants(name = constant_name)['value']
    return constant


def update_constant(constant_name, constant_value):
    """
    Update value into table 'costants'
    """
    current.db(current.db.constants.name == constant_name).update(value = constant_value)
    return 


def execute_remote_cmd(machine_ip, user_name, command, password = None, ret_list = False):
    """
    Executes command on remote machine using paramiko SSHClient
    """
    logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip == 'localhost':
        output=os.popen(command).readline()
        logger.debug(output)
    else:
        logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip, username = user_name, password = password)
            logger.debug("Connected to host %s " % machine_ip)
            stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable
        
            output = stdout.readlines() if ret_list else "".join(stdout.readlines())

            error = "".join(stderr.readlines())
            if (stdout.channel.recv_exit_status()) != 0:
                raise Exception("Exception while executing remote command %s on %s: %s" %(command, machine_ip, error))
        except paramiko.SSHException:
            log_exception()
            raise
        finally:
            if ssh:
                ssh.close()
    
    return output


def execute_remote_bulk_cmd(machine_ip, user_name, command, password=None):
    """
    Executes multiple commands on remote machine using paramiko SSHClient
    """
    logger.debug("executing remote command %s on %s:"  %(command, machine_ip))
    output = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username=user_name)
        channel = ssh.invoke_shell()
        stdin = channel.makefile('wb')
        stdout = channel.makefile('rb')
        
        stdin.write(command)

        if (stdout.channel.recv_exit_status()) != 0:
            raise Exception("Exception while executing remote command %s on %s" %(command, machine_ip))
        output = stdout.read()
        stdout.close()
        stdin.close()
    except paramiko.SSHException:
        log_exception()
    finally:
        if ssh:
            ssh.close()
    
    return output


def sftp_files(machine_ip, user_name, remote_file_path, local_file_path):
    """
    FTP file using paramiko SSHClient
    """
    logger.debug("executing remote ftp on %s with %s:"  %(machine_ip, user_name))

    try:
        transport = paramiko.Transport((machine_ip, 22))
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        transport.connect(username = user_name, pkey = mykey)
        logger.debug("Connected to host %s " % machine_ip)
       
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_file_path, local_file_path)
    except paramiko.SSHException:
        log_exception()
        raise
    finally:
        if sftp:
            sftp.close()
        if transport:
            transport.close()

def is_valid_ipv4(value):
    """
    Checks if string represents 4 octets seperated by decimal.
    """
    regex = re.compile(
        '^(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])$')
    return regex.match(value)


def validate_ip_range(ipFrom, ipTo):
    """
    Validates each IP string, checks if first three octets are same; and the last octet has a valid range.
    """
    if is_valid_ipv4(ipFrom) and is_valid_ipv4(ipTo):
        ip1 = ipFrom.split('.')
        ip2 = ipTo.split('.')
        if ip1[0] == ip2[0] and ip1[1] == ip2[1] and ip1[2] == ip2[2] and int(ip1[3]) < int(ip2[3]):
            return True
    return False


def get_ips_in_range(ipFrom, ipTo):
    """
    Get List of IPs in a validated IP range
    """
    ip_addr_lst = []
    ip1 = ipFrom.split('.')
    ip2 = ipTo.split('.')
    idx =  - (len(ip1[3]))
    subnet = str(ipFrom[:idx])
    for x in range(int(ip1[3]), int(ip2[3])+1):
        ip_addr_lst.append(subnet + str(x))
    return ip_addr_lst


def get_file_stream(file_path):
    return open(file_path,'rb')
    

def get_file_append_mode(file_path):
    return open(file_path,'a')
def generate_random_mac():
    """
    Generates MAC address
    """
    MAC_GEN_FIRST_BIT=0xa2
    MAC_GEN_FIXED_BITS=3
    
    mac = [MAC_GEN_FIRST_BIT]
    i = 1
    while i <  MAC_GEN_FIXED_BITS:
        mac.append(0x00)
        i += 1
    while i <  6:    
        mac.append(random.randint(0x00, 0xff))
        i += 1
    return (':'.join(map(lambda x: "%02x" % x, mac))).upper()
    

def log_exception(message=None, log_handler=None):
    """
    Formats the exception using traceback
    """
    log_handler = logger if log_handler == None else log_handler
    import sys, traceback
    etype, value, tb = sys.exc_info()
    trace = ''.join(traceback.format_exception(etype, value, tb, 10))
    if message:
        trace = message + trace
    log_handler.error(trace)
    return trace

def is_pingable(ip):
    """
    Checks if IP is pingable
    """
    command = "ping -c 1 %s" % ip
    response = os.system(command)
    
    return not(response)

def get_docker_daemon_address():
    docker_machine_ip = config.get("DOCKER_CONF","docker_machine_ip");
    docker_machine_port = config.get("DOCKER_CONF","docker_machine_port");
    return (docker_machine_ip,docker_machine_port);

def get_nginx_server_address():
    nginx_machine_ip = config.get("DOCKER_CONF","nginx_machine_ip");
    nginx_machine_user = config.get("DOCKER_CONF","nginx_machine_user");
    nginx_machine_passwd = config.get("DOCKER_CONF","nginx_machine_passwd");
    return (nginx_machine_ip, nginx_machine_user,nginx_machine_passwd);

class IS_MAC_ADDRESS(Validator):
    """
    Custom validator to check if string is a valid mac address
    """
    regex = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    
    def __init__(self, error_message='enter valid MAC address'):
        self.error_message = error_message

    def __call__(self, value):
        if self.regex.match(value):
            return (value, None)
        else:
            return (value, self.error_message)

