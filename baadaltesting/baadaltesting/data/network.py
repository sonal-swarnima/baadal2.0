import paramiko
import os
import time
import datetime


c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=60)

while(e_time>=datetime.datetime.now()):
	for i in range (0,2):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    	ssh.connect('10.208.21.111', username='root', password='duolc123')     
		stdin, stdout, stderr =ssh.exec_command("cd /mnt/testdatastore/vm_rrds/;rrdtool fetch baadal_testing_vm.rrd AVERAGE -s -600s -e now")
   		initial_data=stdout.readlines()
    	print initial_data
    	ssh.close()
    
       
