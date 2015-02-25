#!/usr/bin/env python
# coding: utf8
import os
import paramiko
import logging
import ConfigParser
import logging.config
import MySQLdb as mdb
import xml.etree.ElementTree as ET

#creating a logger for logging the records
logger = logging.getLogger("web2py.app.baadal")

def xml_connect():
	tree = ET.parse(os.path.join(get_context_path(),'static/testdata.xml'))# parsing the xml file
	root = tree.getroot()
	return root

def xml_connect_sys():
    tree = ET.parse(os.path.join(get_context_path(),'static/systemdata.xml'))# parsing the xml file
    root = tree.getroot()
    return root
def xml_connect_perf():
    tree = ET.parse(os.path.join(get_context_path(),'static/perf.xml'))# parsing the xml file
    perf_root = tree.getroot()
    return perf_root

def get_config_file():
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(),'static/db.conf'));
    return config
    
def get_context_path():
    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    print ctx_path
    return ctx_path 
    

def get_app_name():
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(get_context_path(),'static/db.conf'))
    path=Config.get("web2py_app_name","path")
    return path


#Executes command on remote machine using paramiko SSHClient
def execute_remote_cmd(machine_ip,user_name,command, password,my_logger, ret_list = False):
    my_logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    logger.debug("machine_ip is : " +str(machine_ip))
    logger.debug("user_name is : " +str(user_name))
    logger.debug("password is : " +str(password))
    try:
        logger.debug("inside try block")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(machine_ip, username = user_name, password = password)
        my_logger.debug("Connected to host %s " % machine_ip)
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
    logger.debug("output is : " +str(output))   
    return output
