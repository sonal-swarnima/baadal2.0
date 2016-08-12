import os
import paramiko
from log_handler import logger

def rexists(sftp, path):
    """os.path.exists for paramiko's SCP object
    """
    try:
        sftp.stat(path)
    except IOError, e:
        if e[0] == 2:
            return False
        raise
    else:
        return True
        
def execute_remote_cmd(machine_ip, user_name, command, password = None, ret_list = False):
    """
    Executes command on remote machine using paramiko SSHClient
    """
    logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip == 'localhost':
        output=os.popen(command).readline()
        #logger.debug(output)
    else:
        #logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip, username = user_name, password = password)
            #logger.debug("Connected to host %s " % machine_ip)
            stdin,stdout,stderr = ssh.exec_command(command)  # @UnusedVariable

            output = stdout.readlines() if ret_list else "".join(stdout.readlines())

            error = "".join(stderr.readlines())
            if (stdout.channel.recv_exit_status()) != 0:
                raise Exception("Exception while executing remote command %s on %s: %s" %(command, machine_ip, error))
        except paramiko.SSHException:
            #log_exception()
            raise
        finally:
            if ssh:
                ssh.close()

    return output
    
def copy_remote_file(machine_ip, user_name, remotepath,localpath, password = None, ret_list = False):
    """
    Executes command on remote machine using paramiko SSHClient
    """
    #logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip == 'localhost':
        #output=os.popen(command).readline()
        logger.debug("TODO")
    else:
        #logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
        try :
            sftp = None
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip, username=user_name, password=password)
            #logger.debug("Connected to host %s " % machine_ip)
            sftp = ssh.open_sftp()
            if not rexists(sftp,remotepath):
                raise paramiko.SSHException('filepath on remote machine : ' + remotepath +'not found');    
            sftp.get(remotepath, localpath)
            
        except paramiko.SSHException as e:
            #log_exception()
            print (e)
            raise
        finally:
            
            if ssh:
                ssh.close() 
            if sftp:
                sftp.close()    

def paste_remote_file(machine_ip, user_name, remotepath,localpath, password = None, ret_list = False):
    """
    Executes command on remote machine using paramiko SSHClient
    """
    #logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
    output = None
    if machine_ip == 'localhost':
#         output=os.popen(command).readline()
        #logger.debug(output)
        logger.debug("TODO")
    else:
        #logger.debug("executing remote command %s on %s with %s:"  %(command, machine_ip, user_name))
        try :
            sftp = None
            ssh = paramiko.SSHClient() 
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(machine_ip, username=user_name, password=password)
            #logger.debug("Connected to host %s " % machine_ip)
            sftp = ssh.open_sftp()
            if not os.path.exists(localpath):
                raise paramiko.SSHException('filepath: ' + localpath +'not found');
            sftp.put(localpath, remotepath)
            
        except paramiko.SSHException as e:
            #log_exception()
            print (e)
        finally:
                   
            if sftp:
                sftp.close()
            if ssh:
                ssh.close() 
                                    
#copy_remote_file('10.237.20.236' , 'root' , '/root/paramicotest1/test.txt','/root/mynewfile/test.txt','dockervm');
#paste_remote_file('10.237.20.236' , 'root' , '/root/test.txt','/root/test.txt','dockervm');
