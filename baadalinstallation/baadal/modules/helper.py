# -*- coding: utf-8 -*-
###################################################################################

import os, re, random
import paramiko
from gluon.validators import Validator
from gluon import current
from log_handler import logger


def get_context_path():

    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/baadalapp.cfg'));
    return config

config = get_config_file()

def get_datetime():
    import datetime
    return datetime.datetime.now()

# Get value from table 'costants'
def get_constant(constant_name):
    constant = current.db.constants(name = constant_name)['value']
    return constant

# Update value into table 'costants'
def update_constant(constant_name, constant_value):
    current.db(current.db.constants.name == constant_name).update(value = constant_value)
    return 

#Executes command on remote machine using paramiko SSHClient
def execute_remote_cmd(machine_ip, user_name, command, password = None, ret_list = False):

    logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))

    output = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username = user_name, password = password)
        logger.debug("Connected to host %s " % machine_ip)
        stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable
        
        output = stdout.readlines() if ret_list else "".join(stdout.readlines())
        #logger.debug("Output : %s " % output)

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

#Executes command on remote machine using paramiko SSHClient
def execute_remote_bulk_cmd(machine_ip, user_name, command, password=None):

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

#Checks if string represents 4 octets seperated by decimal.
def is_valid_ipv4(value):
    regex = re.compile(
        '^(([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}([1-9]?\d|1\d\d|2[0-4]\d|25[0-5])$')
    return regex.match(value)

#Validates each IP string, checks if first three octets are same; and the last octet has a valid range.
def validate_ip_range(ipFrom, ipTo):
    
    if is_valid_ipv4(ipFrom) and is_valid_ipv4(ipTo):
        ip1 = ipFrom.split('.')
        ip2 = ipTo.split('.')
        if ip1[0] == ip2[0] and ip1[1] == ip2[1] and ip1[2] == ip2[2] and int(ip1[3]) < int(ip2[3]):
            return True
    return False

#Get List of IPs in a validated IP range
def get_ips_in_range(ipFrom, ipTo):
    
    ip_addr_lst = []
    ip1 = ipFrom.split('.')
    ip2 = ipTo.split('.')
    idx =  - (len(ip1[3]))
    subnet = str(ipFrom[:idx])
    for x in range(int(ip1[3]), int(ip2[3])+1):
        ip_addr_lst.append(subnet + str(x))
    return ip_addr_lst


# Generates MAC address
def generate_random_mac():
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
    
    log_handler = logger if log_handler == None else log_handler
    import sys, traceback
    etype, value, tb = sys.exc_info()
    trace = ''.join(traceback.format_exception(etype, value, tb, 10))
    if message:
        trace = message + trace
    log_handler.error(trace)
    return trace

def is_pingable(ip):

    command = "ping -c 1 %s" % ip
    response = os.system(command)
    
    return not(response)

"""Custom validator to check if string is a valid mac address"""
class IS_MAC_ADDRESS(Validator):
    
    regex = re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    
    def __init__(self, error_message='enter valid MAC address'):
        self.error_message = error_message

    def __call__(self, value):
        if self.regex.match(value):
            return (value, None)
        else:
            return (value, self.error_message)

