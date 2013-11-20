"""
1. This script is responsible for updating the rrd file for every VM defined in the system.
2. These rrd files are stored in vm_rrds/ directory stored on the file present at /vol/baadalcse.
3. These files can be accessed from /mnt/datastore/vm_rrds/ folders from local machine as /vol/baadalcse/ is mounted on /mnt/datastore on the local machine. 
4. This script is run every 5 minutes through a cron set in crontab on the local machine.
5. Its work in to ping active hosts, fetch the details(cpu usage, ram usage etc.) of all the running VM's on that host and update therrd file for that particular VM.
6. An rrd file is created when a VM is initiallly created. If by any chance the rrd file for a running VM does not exist then it is being created.

python -u /home/www-data/web2py/web2py.py -S baadal -M -R /home/www-data/web2py/applications/baadal/private/rrd_gen_cron.py

"""

import rrdtool
import os
import time
import libvirt
import re

import helper

from xml.etree import ElementTree

def create_rrd(rrd_file):

	ret = rrdtool.create( rrd_file, "--start", str(int(time.time())),
		"DS:cputime:GAUGE:300:0:U",
		"DS:memory:GAUGE:300:0:U",
		"DS:diskr:GAUGE:300:0:U",
		"DS:diskw:GAUGE:300:0:U",
		"DS:nwr:GAUGE:300:0:U",
		"DS:nww:GAUGE:300:0:U",
		"DS:cpus:GAUGE:300:0:U", 
		"RRA:MIN:0:1:525600",
		"RRA:AVERAGE:0:12:43800",
		"RRA:AVERAGE:0:2016:261",
		"RRA:AVERAGE:0:43200:61",
		"RRA:AVERAGE:0:105120:5")
	
	if ret:
		logger.warn(rrdtool.error())	


	logger.info("RRD Created")

def get_dom_mem_usage(dom_name, host):
	logger.debug("fecthing memory usage of domain %s defined on host %s" % (dom_name, host))
	
	import paramiko
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(host, username='root', password='')
	cmd = "ps aux | grep '\-name " + dom_name + " -uuid'"
	stdin, stdout, stderr = ssh.exec_command(cmd)
	output = stdout.readlines()
	ssh.close()

	if len(output) == 3:
		return int(re.split('\s+', output[0])[5])
	else:
		logger.warn("Unable to fetch memory usage details for dom %s" % (dom_name))

def get_dom_nw_usage(dom_obj):

	tree = ElementTree.fromstring(dom_obj.XMLDesc(0))
	nwr = 0
	nww = 0

	for target in tree.findall("devices/interface/target"):
		device = target.get("dev")
		stats  = dom_obj.interfaceStats(device)
		nwr   += stats[0]
		nww   += stats[4]

	logger.info("%s%s" % (nwr, nww))

	return [nwr, nww]

def get_dom_disk_usage(dom_obj):

	tree = ElementTree.fromstring(dom_obj.XMLDesc(0))
	bytesr = 0
	bytesw = 0
	rreq  = 0
	wreq  = 0

	for target in tree.findall("devices/disk/target"):

       		device = target.get("dev")
		stats  = dom_obj.blockStats(device)
		rreq   += stats[0]
		bytesr += stats[1]
		wreq   += stats[2]
		bytesw += stats[3]
	
	logger.info("rreq: %s bytesr: %s wreq: %s bytesw: %s" % (rreq, bytesr, wreq, bytesw))

	return [bytesr, bytesw]

def get_dom_info(dom_id, host_ip, conn):
	dom		= conn.lookupByID(dom_id)
	dom_name	= dom.name()
	dom_info	= dom.info()
	dom_status	= dom_info[0]
	dom_maxmem	= dom_info[1]
#	dom_memused	= dom_info[2]       Python libvirt unable to fetch correct memory usage details of a domain
	dom_cpus	= dom_info[3]
	dom_cputime	= dom_info[4]
	dom_memusage	= get_dom_mem_usage(dom_name, host_ip)
	dom_nw_usage	= get_dom_nw_usage(dom)
	dom_nwr		= dom_nw_usage[0]
	dom_nww		= dom_nw_usage[1]
	dom_disk_usage	= get_dom_disk_usage(dom)
	dom_diskr	= dom_disk_usage[0]
	dom_diskw	= dom_disk_usage[1]


	logger.info(dom_name)
	logger.warn("As we get VM mem usage info from rrs size of the process running on host therefore it is observed that the memused is sometimes greater than max mem specified in case when the VM uses memory near to its mam memory")

	return [dom_name, dom_maxmem, dom_memusage, dom_cputime, dom_cpus, dom_nwr, dom_nww, dom_diskr, dom_diskw]

def get_rrd_file_abs_path(dom_name):
        return helper.get_constant('vmfiles_path') + os.sep + helper.get_constant('vm_rrds_dir') + os.sep + dom_name + ".rrd"

@handle_exception
def update_rrd():

	active_host_list = db(db.host.status == HOST_STATUS_UP).select(db.host.host_ip)
	logger.debug(active_host_list)

	for host in active_host_list:

		conn = None
		try:
			host_ip = host['host_ip']
			conn = libvirt.open("qemu+ssh://root@" + host_ip + "/system")
			logger.debug(conn.getHostname())
			
			active_dom_ids = conn.listDomainsID()
			logger.debug(active_dom_ids)
			for dom_id in active_dom_ids:

			   try:
	
				dom_info = get_dom_info(dom_id, host_ip, conn)			
				logger.info(dom_info)
				rrd_file = get_rrd_file_abs_path(dom_info[0])
	
				if not (os.path.exists(rrd_file)):
					logger.warn("RRD file does not exists")
					logger.warn("Creating new RRD file")
					create_rrd(rrd_file)
					time.sleep(1)


				print str(dom_info[2])

				ret = rrdtool.update(rrd_file, str(int(time.time())) + ":" + str(dom_info[3]) + ":" + str(dom_info[2]) + ":" + str(dom_info[7]) + ":" + str(dom_info[8]) + ":" + str(dom_info[5]) + ":" + str(dom_info[6]) + ":" + str(dom_info[4]) )

				if ret:
					logger.warn("Error while Updating %s.rrd" % (dom_info[0]))
					logger.warn(rrdtool.error())
				else:
					logger.info("rrd updated successfully.")
			   except:
				import sys, traceback
				etype, value, tb = sys.exc_info()
				logger.warn("Error occured while creating/updating rrd.")
				msg = ''.join(traceback.format_exception(etype, value, tb, 10))
				logger.error(msg)
				pass

		except:
			import sys, traceback
			etype, value, tb = sys.exc_info()
			logger.warn("Error occured while creating/updating rrd or host.")
			msg = ''.join(traceback.format_exception(etype, value, tb, 10))           
			logger.error(msg)           
			pass
		finally: 
			if conn:
				conn.close()


if __name__=="__main__":
	update_rrd()


