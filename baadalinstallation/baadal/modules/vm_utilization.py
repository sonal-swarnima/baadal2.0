# -*- coding: utf-8 -*-
###################################################################################
""" vm_utilization.py:  Captures utilization data for virtual machines & hosts;  
and stores the information in a RRD database. 
RRD is a Round Robin Database which is created for pre-defined time interval. 
When new data reaches the starting point, it overwrites existing data. The RRDtool 
database is structured in such a way that it needs data at predefined time intervals. 
Then graphs can be directly generated from the information by specifying the 
Consolidation Function.
For more information on rrdtool visit http://oss.oetiker.ch/rrdtool/

Following utilization data is captured for each Host and VM:
Memory
CPU
Network(read & write)
Disk (read & write)

For virtual machines, CPU, network and disk utilization information is fetched from
the respective domain running on the hypervisor. Memory utilization is fetched from  
host, since VMs run as processes on the host.

"""
from gluon import IMG, URL, current
from helper import get_constant, get_context_path, execute_remote_cmd
from log_handler import rrd_logger
from xml.etree import ElementTree
import os
import re
import time
import rrdtool
import libvirt

VM_UTIL_10_MINS = 1
VM_UTIL_24_HOURS = 2
VM_UTIL_ONE_WEEK = 3
VM_UTIL_ONE_MNTH = 4
VM_UTIL_THREE_MNTH = 5
VM_UTIL_ONE_YEAR = 6
HOURS = 15
MINS = 16
VM_UTIL_20_DAYS = 20

STEP         = 300
TIME_DIFF_MS = 550

def get_rrd_file(identity):

    rrd_file = get_constant("vmfiles_path") + os.sep + get_constant("vm_rrds_dir") + os.sep + identity + ".rrd"
    return rrd_file




""""Fetch RRD data to display in tabular format"""
def fetch_rrd_data(rrd_file_name, period=VM_UTIL_24_HOURS, period_no=24):
    rrd_file = get_rrd_file(rrd_file_name)
   
    start_time = 'now-' + str(24*60*60) 
    end_time = 'now'

    if period == HOURS:
        start_time = 'now-' + str(period_no*60*60)
    elif period == MINS:
        start_time = 'now-' + str(period_no*60)
    elif period == VM_UTIL_10_MINS:
        start_time = 'now-' + str(10*60)
    elif period == VM_UTIL_ONE_WEEK:
        start_time = '-1w'
    elif period == VM_UTIL_ONE_MNTH:
        start_time = '-1m'
    elif period == VM_UTIL_THREE_MNTH:
        start_time = '-3m'
    elif period == VM_UTIL_ONE_YEAR:
        start_time = '-1y'
    cpu_data = []
    mem_data = []
    dskr_data = []
    dskw_data = []
    nwr_data = []
    nww_data = []
    if os.path.exists(rrd_file):
        rrd_ret =rrdtool.fetch(rrd_file, 'MIN', '--start', start_time, '--end', end_time)
	
        fld_info = rrd_ret[1]
        data_info = rrd_ret[2]
        cpu_idx = fld_info.index('cpu')
        mem_idx = fld_info.index('ram')
        dskr_idx = fld_info.index('dr')
        dskw_idx = fld_info.index('dw')
        nwr_idx = fld_info.index('tx')
        nww_idx = fld_info.index('rx')
        
        #Ignore the None values before computing average
        for row in data_info:
            if row[cpu_idx] != None: cpu_data.append(float(row[cpu_idx])) 
            if row[mem_idx] != None: mem_data.append(float(row[mem_idx]))
            if row[dskr_idx] != None: dskr_data.append(float(row[dskr_idx]))
            if row[dskw_idx] != None: dskw_data.append(float(row[dskw_idx]))
            if row[nwr_idx] != None: nwr_data.append(float(row[nwr_idx]))
            if row[nww_idx] != None: nww_data.append(float(row[nww_idx]))

    if str(rrd_file)=="/mnt/datastore/vm_rrds/IITD_cs5100299_Openvswitch_Host.rrd":
        rrd_logger.debug("cpu_utilization over 24hrs is :" + str(cpu_data)) 
        rrd_logger.debug("cpu_utilization over 24hrs is :" + str(sum(cpu_data)) + " " + str(len(cpu_data)))
    return (sum(mem_data)/float(len(mem_data)) if len(mem_data) > 0 else 0, 
            sum(cpu_data)/float(len(cpu_data)) if len(cpu_data) > 0 else 0, 
            sum(dskr_data)/float(len(dskr_data)) if len(dskr_data) > 0 else 0,
            sum(dskw_data)/float(len(dskw_data)) if len(dskw_data) > 0 else 0,
            sum(nwr_data)/float(len(nwr_data)) if len(nwr_data) > 0 else 0,
            sum(nww_data)/float(len(nww_data)) if len(nww_data) > 0 else 0)
  

''' check last 20 days data and compare against threshold.'''

def compare_rrd_data_with_threshold(rrd_file_name,thresholdcontext):
     
    start_time = 'now - ' + str(VM_UTIL_20_DAYS*24*60*60)
    ''' start_time = 'now - ' + str(60*60) '''
    end_time = 'now'
    rrd_file = get_rrd_file(rrd_file_name)

    cpu_data = []
    mem_data = []
    dskr_data = []
    dskw_data = []
    nwr_data = []
    nww_data = []

    rrd_logger.info("inside compare_rrd_data_with_threshold function rrd file is :"+str(rrd_file_name))
    if os.path.exists(rrd_file):
        rrd_ret =rrdtool.fetch(rrd_file, 'MIN', '--start', start_time, '--end', end_time)

        fld_info = rrd_ret[1]
        data_info = rrd_ret[2]
        cpu_idx = fld_info.index('cpu')
        mem_idx = fld_info.index('ram')
        dskr_idx = fld_info.index('dr')
        dskw_idx = fld_info.index('dw')
        nwr_idx = fld_info.index('tx')
        nww_idx = fld_info.index('rx')

        cpu_threshold='N'
        read_threshold='N'
        write_threshold='N'
        CPUNoneIdentifier='Y'
        NWRNoneIdentifier='Y'
        NWWNoneIdentifier='Y'

        for row in data_info:
            if (row[cpu_idx] != None) : 
                CPUNoneIdentifier='N'
                if int(row[cpu_idx]) > int(thresholdcontext['CPUThreshold']) : cpu_threshold='Y'
            
            if (row[nwr_idx] != None) : 
                NWRNoneIdentifier='N'
                if int(row[nwr_idx]) > int(thresholdcontext['ReadThreshold']) : read_threshold='Y' 

            if (row[nww_idx] != None) : 
                NWWNoneIdentifier='N'
                if int(row[nww_idx]) > int(thresholdcontext['WriteThreshold']) : write_threshold='Y'
		
            if (cpu_threshold=='Y' or read_threshold=='Y' or write_threshold=='Y') :
                rrd_logger.info("Info about the VM:%s,row[cpu_idx]:%s,row[nwr_idx]:%s,row[nww_idx]:%s" %(rrd_file_name,row[cpu_idx],row[nwr_idx],row[nww_idx])) 
                rrd_logger.info("Threshold is reached once.. VM:"+str(rrd_file_name)+" is in use") 
                return False
           
        ## If only none values are read from the rrd .. do not send a warning email                  
        if(CPUNoneIdentifier=='N' and  NWRNoneIdentifier=='N' and NWWNoneIdentifier =='N'):
            rrd_logger.info("Returning true to send warning email as threshold is never reached for VM:%s" %(rrd_file_name) )
            return True
        else:
            rrd_logger.info("RRD capturing is not correct... returning all null values only for VM:%s" %(rrd_file_name) )
            return False 


def create_rrd(rrd_file,m_type="None"):
    if m_type=="host":
        ret = rrdtool.create( rrd_file, "--step", str(STEP) ,"--start", str(int(time.time())),
        "DS:cpu:GAUGE:%s:0:U"   % str(TIME_DIFF_MS),
        "DS:ram:GAUGE:%s:0:U"     % str(TIME_DIFF_MS),
        "DS:dr:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:dw:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:tx:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:rx:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:tmp:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:pwr:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "RRA:MIN:0:1:200000",       # Data stored for every five minute
        "RRA:AVERAGE:0.5:12:100",   # Average data stored for every hour (300*12)
        "RRA:AVERAGE:0.5:288:50",   # Average data stored for every day (300*288)
        "RRA:AVERAGE:0.5:8928:24",  # Average data stored for every month (300*8928)
        "RRA:AVERAGE:0.5:107136:10")# Average data stored for every year (300*107136)
    else:
        ret = rrdtool.create( rrd_file, "--step", str(STEP) ,"--start", str(int(time.time())),
        "DS:cpu:GAUGE:%s:0:U"   % str(TIME_DIFF_MS),
        "DS:ram:GAUGE:%s:0:U"     % str(TIME_DIFF_MS),
        "DS:dr:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:dw:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:tx:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:rx:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "RRA:MIN:0:1:200000",       # Data stored for every five minute
        "RRA:AVERAGE:0.5:12:100",   # Average data stored for every hour (300*12)
        "RRA:AVERAGE:0.5:288:50",   # Average data stored for every day (300*288)
        "RRA:AVERAGE:0.5:8928:24",  # Average data stored for every month (300*8928)
        "RRA:AVERAGE:0.5:107136:10")# Average data stored for every year (300*107136)

    if ret:
        rrd_logger.warn(rrdtool.error())

"""Captures memory utilization of a VM from the host.
   VMs run on host as individual processes. Memory utilization of the process is derived."""

def get_dom_mem_usage(dom, host):
    rrd_logger.info("memory stats for VM:%s is %s" %(dom.name(),dom.memoryStats()))
    rrd_logger.warn(dom.memoryStats())
    try:
      domain_memUsed=(dom.memoryStats()['available']-dom.memoryStats()['unused'])
      rrd_logger.info("domain_memUsed is : "+str(domain_memUsed))
    except:
      domain_memUsed=(dom.memoryStats()['rss'])
      rrd_logger.info("in except and rss value is : "+str(domain_memUsed))
    return (domain_memUsed*1024)


"""Uses libvirt function to extract interface device statistics for a domain
   to find network usage of virtual machine."""
def get_dom_nw_usage(dom_obj):

    tree = ElementTree.fromstring(dom_obj.XMLDesc(0))
    rx = 0
    tx = 0

    for target in tree.findall("devices/interface/target"):
        device = target.get("dev")
        stats  = dom_obj.interfaceStats(device)
        rx   += stats[0]
        tx   += stats[4]

    rrd_logger.info("%s%s" % (rx, tx))

    return [rx, tx] #returned value in Bytes by default

"""Uses libvirt function to extract block device statistics for a domain
   to find disk usage of virtual machine."""
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

    rrd_logger.info("rreq: %s bytesr: %s wreq: %s bytesw: %s" % (rreq, bytesr, wreq, bytesw))

    return [bytesr, bytesw] #returned value in Bytes by default

def get_current_dom_resource_usage(dom, host_ip):

    dom_memusage   = get_dom_mem_usage(dom, host_ip)
    dom_nw_usage   = get_dom_nw_usage(dom)
    dom_disk_usage = get_dom_disk_usage(dom)
    timestamp_now = time.time()   #keerti

    dom_stats =      {'rx'     : dom_nw_usage[0]}
    dom_stats.update({'tx'     : dom_nw_usage[1]})
    dom_stats.update({'diskr'   : dom_disk_usage[0]})
    dom_stats.update({'diskw'   : dom_disk_usage[1]})
    dom_stats.update({'memory'  : dom_memusage})
    dom_stats.update({'cputime' : dom.info()[4]})
    dom_stats.update({'cpus'    : dom.info()[3]})
    dom_stats.update({'timestamp': timestamp_now})  

    rrd_logger.info(dom_stats)
    rrd_logger.warn("As we get VM mem usage info from rrs size of the process running on host therefore it is observed that the memused is sometimes greater than max mem specified in case when the VM uses memory near to its mam memory")

    return dom_stats

def get_actual_usage(dom_obj, host_ip):


    dom_name = dom_obj.name()
    cache_id = str(dom_name)

    dom_stats = get_current_dom_resource_usage(dom_obj, host_ip)

    """Fetch previous domain stat value from cache"""
    current.cache.disk(cache_id, lambda:dom_stats, 86400)  # @UndefinedVariable
    prev_dom_stats = current.cache.disk(cache_id, lambda:dom_stats, 86400)  # @UndefinedVariable
    rrd_logger.debug("prev_dom_stats for vm:"+str(dom_name)+" are: "+str(prev_dom_stats))
    
    #calulate usage
    timestamp = float(dom_stats['timestamp'] - prev_dom_stats['timestamp']) #keerti
   
    if timestamp == 0:
        cputime = dom_stats['cputime'] - prev_dom_stats['cputime'] 
    else:
        cputime = float((dom_stats['cputime'] - prev_dom_stats['cputime'])*300)/float(dom_stats['timestamp'] - prev_dom_stats['timestamp'])  #keerti

    usage = {'ram'      : dom_stats['memory']} #ram in Bytes usage
    usage.update({'cpu' : cputime})  
    usage.update({'tx'  : (dom_stats['tx'] - prev_dom_stats['tx'])}) #in KBytes
    usage.update({'rx'  : (dom_stats['rx'] - prev_dom_stats['rx'])}) #in KBytes
    usage.update({'dr'  : (dom_stats['diskr'] - prev_dom_stats['diskr'])}) #in KBytes
    usage.update({'dw'  : (dom_stats['diskw'] - prev_dom_stats['diskw'])}) #in KBytes

    current.cache.disk.clear(cache_id+"$")  # @UndefinedVariable
    

    """Cache the current CPU utilization, so that difference can be calculated in next instance"""
    current.cache.disk(cache_id, lambda:dom_stats, 86400)        # @UndefinedVariable
    latest_dom_stats = current.cache.disk(cache_id, lambda:dom_stats, 86400)        # @UndefinedVariable
    rrd_logger.debug("latest_dom_stats for vm:"+str(dom_name)+" are: "+str(latest_dom_stats))
   
    return usage 

"""Uses iostat tool to capture CPU statistics of host"""
def get_host_cpu_usage(host_ip,m_type=None):
    rrd_logger.info("getting cpu info")
    command = "cat /proc/stat | awk 'FNR == 1{print $2+$3+$4}'"
    
    if m_type=="controller":
        command_output =execute_remote_cmd("localhost", 'root', command, None,  True)
    else:
        command_output = execute_remote_cmd(host_ip, 'root', command, None,  True)
    rrd_logger.debug(command_output[0])
    timestamp_now = time.time()
   
    cpu_stats = {'cputicks'    :  float(command_output[0])}     # (cpu time in clock ticks
    cpu_stats.update({'timestamp'    :  timestamp_now})
 
    prev_cpu_stats = current.cache.disk(str(host_ip), lambda:cpu_stats, 86400)  # @UndefinedVariable
    rrd_logger.debug(prev_cpu_stats)
    timestamp = float(cpu_stats['timestamp'] - prev_cpu_stats['timestamp'])
    rrd_logger.debug("timestamp %s" % str(timestamp))
 
    #cpu_usage = cpu_stats - prev_cpu_stats # cpu usage in last 5 min (cputime-in ticks)
    if timestamp == 0:
        cpu_usage = float(cpu_stats['cputicks'] - prev_cpu_stats['cputicks'])
    else:
        cpu_usage = float((cpu_stats['cputicks'] - prev_cpu_stats['cputicks'])*300) / float(cpu_stats['timestamp'] - prev_cpu_stats['timestamp']) # keerti uncomment above line and comment it
    
    current.cache.disk.clear(str(host_ip))  # @UndefinedVariable

    """Cache the current CPU utilization, so that difference can be calculated in next instance"""
    latest_cpu_stats = current.cache.disk(str(host_ip), lambda:cpu_stats, 86400)        # @UndefinedVariable
    rrd_logger.debug(latest_cpu_stats)


    clock_ticks = os.sysconf(os.sysconf_names['SC_CLK_TCK'])     # (ticks per second) 
    cpu_usage = float(cpu_usage*1000000000) / float(clock_ticks)     # (cpu time in ns)
    rrd_logger.info("CPU stats of host %s is %s" % ( host_ip, cpu_usage))
    return (cpu_usage)

"""Uses iostat tool to capture input/output statistics for host"""
def get_host_disk_usage(host_ip,m_type=None):

    command = "iostat -d | sed '1,2d'"
    
    if m_type=="controller":
        command_output =execute_remote_cmd("localhost", 'root', command, None,  True)
    
    else:
        command_output = execute_remote_cmd(host_ip, 'root', command, None,  True)
    disk_stats = re.split('\s+', command_output[1])
    rrd_logger.info("Disk stats of host %s is dr: %s dw: %s" % (host_ip, disk_stats[2], disk_stats[3]))  
    return [float(disk_stats[2]), float(disk_stats[3])] #return memory in KB/sec

"""Uses top command to capture memory usage for host"""
def get_host_mem_usage(host_ip,m_type=None):

    command = "free -k | grep 'buffers/cache' | awk '{print $3}'"
    if m_type=="controller":
        command_output =execute_remote_cmd("localhost", 'root', command, None,  True)
   
    else:
        command_output = execute_remote_cmd(host_ip, 'root', command, None,  True)
    rrd_logger.info("command_output is %s"%(command_output[0]))
    used_mem_in_kb = int(command_output[0])
    rrd_logger.info("Mem stats of host %s is %s" % (host_ip, used_mem_in_kb))
    return used_mem_in_kb #return memory in KB


"""EXtracting impi output """
def get_impi_output(cmd,host_ip):
    rrd_logger.debug("entering ipmi")
    output=execute_remote_cmd(host_ip,'root', cmd, None,  True)
    rrd_logger.debug(output)
    rrd_logger.debug(output[0].split("|")[4].split(" ")[1])
    ret=output[0].split("|")[4].split(" ")[1]
    rrd_logger.debug("cheecking ret"+str(ret))
    return int(ret)

"""Uses IMPITOOL to get host temp """
def get_host_temp_usage(host_ip):
    rrd_logger.info("Checking temp on host"+str(type(host_ip)))
    command='ipmitool sdr elist full'
    ret=execute_remote_cmd(host_ip, 'root', command, None,  True)
    if str(ret).find("Inlet Temp")!=int(-1):
        rrd_logger.debug("Entering")
        temp=get_impi_output('ipmitool sdr elist full | grep "Inlet Temp"',host_ip)
    if str(ret).find("Ambient Temp")!=int(-1):
	rrd_logger.debug("Entering")
	temp=get_impi_output('ipmitool sdr elist full | grep "Ambient Temp"',host_ip)
    rrd_logger.info("temp stats" +str(type(temp)))
    rrd_logger.info("temp stats" +str(temp))
    return temp # returning temperature in degree Celsius

"""Uses IMPITOOL to get host power consumption"""
def get_host_power_usage(host_ip):
    rrd_logger.info("Checking power on host"+str(host_ip))
    command='ipmitool sdr elist full'
    ret=execute_remote_cmd(host_ip, 'root', command, None,  True)
    if str(ret).find("System Level")!=int(-1):
        pwr_usage=get_impi_output('ipmitool sdr elist full | grep "System Level"',host_ip)
    if str(ret).find("Pwr Consumption")!=int(-1):
        pwr_usage=get_impi_output('ipmitool sdr elist full | grep "Pwr Consumption"',host_ip)
    rrd_logger.info("power stats of host %s is %s" % (host_ip, str(pwr_usage)))
    return pwr_usage # returining power in Watt

"""Uses ifconfig command to capture network usage for host"""
def get_host_nw_usage(host_ip,m_type=None):

    command = "ifconfig baadal-br-int | grep 'RX bytes:'"
    if m_type=="controller":
        command_output =execute_remote_cmd("localhost", 'root', command, None,  True)
    
    else:
        command_output = execute_remote_cmd(host_ip, 'root', command, None,  True)
    nw_stats = re.split('\s+', command_output[0])
    rx = int(re.split(':', nw_stats[2])[1])
    tx = int(re.split(':', nw_stats[6])[1])
    rrd_logger.info("Network stats of host %s is rx: %s tx: %s" % (host_ip, rx, tx))
    return [rx, tx] # return network in Bytes

def get_host_resources_usage(host_ip,m_type=None):
    
    rrd_logger.info("getting data for RRD file")
    if m_type is None:
        host_cpu_usage = get_host_cpu_usage(host_ip)
        host_disk_usage = get_host_disk_usage(host_ip)
        host_mem_usage = get_host_mem_usage(host_ip)
        host_nw_usage = get_host_nw_usage(host_ip)
        host_temp_usage =get_host_temp_usage(host_ip)
        host_power_usage =get_host_power_usage(host_ip)
	rrd_logger.info("host_cpu_usage"+str(type(host_cpu_usage)))
        rrd_logger.info("host_temp_usage"+str(type(host_temp_usage)))
    else:

        host_cpu_usage = get_host_cpu_usage(host_ip,m_type)
        host_disk_usage = get_host_disk_usage(host_ip,m_type)
        host_mem_usage = get_host_mem_usage(host_ip,m_type)
        host_nw_usage = get_host_nw_usage(host_ip,m_type)
	
    host_usage = {'cpu' : host_cpu_usage} #percent cpu usage
    host_usage.update({'dr' : host_disk_usage[0]*1024}) #Bytes/s
    host_usage.update({'dw' : host_disk_usage[1]*1024})
    host_usage.update({'ram' : host_mem_usage*1024}) #Bytes
    host_usage.update({'rx' : host_nw_usage[0]}) #in Bytes
    host_usage.update({'tx' : host_nw_usage[1]}) #in Bytes
    if m_type is None:
	host_usage.update({'tmp' : host_temp_usage}) #in Degree Celsius
        host_usage.update({'pwr' : host_power_usage}) #in Watt
        
    rrd_logger.info("Host %s stats:  %s" % (host_ip, host_usage))
    
    return host_usage

#Update host rrd file on an interval of 5 min
def update_host_rrd(host_ip,m_type=None):
    
    try:
   
        rrd_file = get_rrd_file(host_ip.replace(".","_"))
        rrd_logger.info(rrd_file)
        timestamp_now = time.time()
        rrd_logger.info(timestamp_now)

        if not (os.path.exists(rrd_file)):

            rrd_logger.warn("RRD file (%s) does not exists" % (rrd_file))
            rrd_logger.warn("Creating new RRD file")
	    if m_type is None:
                create_rrd(rrd_file,"host")
	    else:
		create_rrd(rrd_file)
       
        else:
            rrd_logger.info("updating  RRD file")
            if m_type is None:
		rrd_logger.debug("host_ip is"+ str(host_ip))
                host_stats = get_host_resources_usage(host_ip)
                output=rrdtool.update(rrd_file, "%s:%s:%s:%s:%s:%s:%s:%s:%s" % (timestamp_now, host_stats['cpu'], host_stats['ram'], host_stats['dr'], host_stats['dw'], host_stats['tx'], host_stats['rx'],host_stats['tmp'], host_stats['pwr']))
		rrd_logger.debug("update status"+str(output))
            else:
                host_stats = get_host_resources_usage(host_ip,m_type)
                
                rrdtool.update(rrd_file, "%s:%s:%s:%s:%s:%s:%s" % (timestamp_now, host_stats['cpu'], host_stats['ram'], host_stats['dr'], host_stats['dw'], host_stats['tx'], host_stats['rx']))
	    
 
    except Exception, e:
 
        rrd_logger.debug("Error occured while creating/updating rrd for host: %s" % (host_ip))
        rrd_logger.debug(e)

#Update host rrd file on an interval of 5 min
def update_vm_rrd(dom, active_dom_ids, host_ip):

        dom_name = dom.name()
        rrd_file = get_rrd_file(dom.name())
 
        if not (os.path.exists(rrd_file)):
            rrd_logger.warn("RRD file (%s) does not exists" % (rrd_file))
            rrd_logger.warn("Creating new RRD file")
            create_rrd(rrd_file)
 
        else:
 
            timestamp_now = time.time()
 
            if dom.ID() in active_dom_ids:
                vm_usage = get_actual_usage(dom, host_ip)
                rrd_logger.debug("Usage Info for VM %s: %s" % (dom_name, vm_usage))
                rrdtool.update(rrd_file, "%s:%s:%s:%s:%s:%s:%s" % (timestamp_now, vm_usage['cpu'], vm_usage['ram'], vm_usage['dr'], vm_usage['dw'], vm_usage['tx'], vm_usage['rx']))
            else:
                rrdtool.update(rrd_file, "%s:0:0:0:0:0:0" % (timestamp_now))


def set_domain_memoryStatsperiod(host_ip):
    try:
        hypervisor_conn = libvirt.open("qemu+ssh://root@" + host_ip + "/system")
        active_dom_ids  = hypervisor_conn.listDomainsID()
        for dom_id in active_dom_ids:
            dom_info = hypervisor_conn.lookupByID(dom_id)
            dom_info.setMemoryStatsPeriod(2)
    except Exception, e:
        rrd_logger.debug(e)
    finally:
        rrd_logger.info("Ending setting memory stats periods for VM's %s" % host_ip)
        if hypervisor_conn:
           hypervisor_conn.close()


def update_rrd(host_ip,m_type=None):
    #UPDATE CONTROLLER AND NAT RRD
    if m_type is not None:
    
        rrd_logger.info("Startiing rrd updation for nat/controller %s" % (host_ip))
        update_host_rrd(host_ip,m_type)
        rrd_logger.info("Ending rrd updation for nat/controller %s" % (host_ip))
    
    #UPDATE HOST RRD
    else:
    
        rrd_logger.info("Startiing rrd updation for host %s" % (host_ip))
        update_host_rrd(host_ip)
        rrd_logger.info("Ending rrd updation for host %s" % (host_ip)) 


        rrd_logger.info("Startiing rrd updation for VMs on host %s" % (host_ip))
        #Adding the call for setting stat periods for all VM's on the host
        set_domain_memoryStatsperiod(host_ip)

        #UPDATE RRD for ALL VMs on GIVEN HOST
        hypervisor_conn = None
        
        try:
        
            hypervisor_conn = libvirt.openReadOnly("qemu+ssh://root@" + host_ip + "/system")
            rrd_logger.debug(hypervisor_conn.getHostname())
            
            active_dom_ids  = hypervisor_conn.listDomainsID()
            rrd_logger.info(active_dom_ids)
            all_dom_objs    = hypervisor_conn.listAllDomains()
            rrd_logger.info(all_dom_objs)
            
            for dom_obj in all_dom_objs:
            
                try:
                
                    rrd_logger.info("Starting rrd updation for vm %s on host %s" % (dom_obj.name(), host_ip))
                    update_vm_rrd(dom_obj, active_dom_ids, host_ip)
                
                except Exception, e:
                
                    rrd_logger.debug(e)
                    rrd_logger.debug("Error occured while creating/updating rrd for VM : %s" % dom_obj.name())
                
                finally:
                
                    rrd_logger.info("Ending rrd updation for vm %s on host %s" % (dom_obj.name(), host_ip))
        
        
        except Exception, e:
        
            rrd_logger.debug(e)
        
        finally:
            rrd_logger.info("Ending rrd updation for vms on host %s" % host_ip)
            if hypervisor_conn:
                hypervisor_conn.close()
#fetch graph data for vm/host from their respective rrd file
def fetch_info_graph(vm_identity,graph_period,g_type,vm_ram,m_type,host_cpu):
    rrd_logger.debug("fetch_info graph")
    start_time = None
#     consolidation = 'MIN' 
    end_time = 'now'
    rrd_file = get_rrd_file(vm_identity)
    if graph_period == 'hour':
        start_time = 'now - ' + str(12*300)
    elif graph_period == 'day':
        start_time = 'now - ' + str(12*300*24)
    elif graph_period == 'month':
        start_time = 'now - ' + str(12*300*24*30)
    elif graph_period == 'week':
        start_time = 'now - ' + str(12*300*24*7)
    elif graph_period == 'year':
        start_time = 'now - ' + str(12*300*24*365)
    result=[]
    
    result1=[]
    result2=[]
    result3=[]
    rrd_logger.debug(rrd_file)
    if os.path.exists(rrd_file):
        rrd_ret =rrdtool.fetch(rrd_file, 'MIN', '--start', start_time, '--end', end_time)    
        rrd_logger.debug("fetched rrd data")
        fld_info = rrd_ret[1]
        data_info = rrd_ret[2] 
        tim_info=rrd_ret[0][0]
        
        cpu_idx = fld_info.index('cpu')
        mem_idx = fld_info.index('ram')
        dskr_idx = fld_info.index('dr')
        dskw_idx = fld_info.index('dw')
        nwr_idx = fld_info.index('tx')
        nww_idx = fld_info.index('rx')
        if m_type=="host":
	    tmp_idx = fld_info.index('tmp')
	    power_idx = fld_info.index('pwr')
	    rrd_logger.debug("tmp poser")

        timeinterval=1
        for data in data_info:
            info1={}
            info={}
            time_info=(int(tim_info) + 300*timeinterval)*1000 #changing timestamp from rrd into javascript timezone to represent time on graph
            timeinterval+=1
            
            
            if g_type=="cpu":
                if data[cpu_idx] != None: 
                    cpu_no=host_cpu.split(" ")
                    info['y']=round((float(data[cpu_idx])*100)/(float(int(cpu_no[0])*5*60*1000000000)),3)   #dividing the rrd value by no of cores*5min(converted into nanoseconds)
                else:
                    info['y']=float(0)

                info['x']=time_info 
                result3.append(info) 
                
            if g_type=="ram":
                if data[mem_idx] != None and  data[mem_idx]>0: 
                    if (int(vm_ram)>1024) or (m_type=='host'):
                        mem=round(float(data[mem_idx])/(1024*1024*1024),2)
                    else:
                        mem=round(float(data[mem_idx])/(1024*1024),2)
                    
                    info['y']=mem
                else:		    
                    info['y']=float(0)
                    
                info['x']=time_info
                result3.append(info) 
            if m_type=="host":
                if g_type=="tmp":
                    if data[tmp_idx] != None and  data[tmp_idx]>0: 
                        info['y']=round(float(data[tmp_idx]),2)
                    else:		    
                        info['y']=float(0)                    
                    info['x']=time_info
                    result3.append(info) 

                if g_type=="power":
                     if data[power_idx] != None and  data[power_idx]>0: 
                    
                         info['y']=data[power_idx]
                     else:		    
                         info['y']=float(0)                    
                     info['x']=time_info
                     result3.append(info) 

            if g_type=="disk":
        
                if data[dskr_idx] != None: 
                    info1['y']=round(float(data[dskr_idx])/(1024*1024),2)
                else:
                    info1['y']=float(0)

                if data[dskw_idx] != None: 
                    info['y']=round(float(data[dskw_idx])/(1024*1024),2)
                else:
                    info['y']=float(0)

                info['x']=time_info 
                info1['x']=time_info 
            
                result1.append(info1) 
                result2.append(info)

            if g_type=="nw":
                if data[nwr_idx] != None: 
                    info1['y']=round(float(data[nwr_idx])/(1024*1024),2)
                else:
                    info1['y']=float(0)
                if data[nww_idx] != None: 
                    info['y']=round(float(data[nww_idx])/(1024*1024),2)
                else:
                    info['y']=float(0)
                
                info['x']=time_info 
                info1['x']=time_info 
                result1.append(info1) 
                result2.append(info)	


    if g_type=='ram' or g_type=='cpu' or g_type=='tmp' or g_type=='power':
	rrd_logger.debug("result3")
        return result3

    if g_type=='nw' or g_type=='disk':
        result.append(result1) 
        result.append(result2)	
	rrd_logger.debug("result")
        return result

#check graph period to display time
def check_graph_period(graph_period):
    if graph_period == 'hour':	
        valueformat="hh:mm TT"
    elif graph_period == 'day':
        valueformat=" hh:mm TT"
    elif graph_period == 'month':
        valueformat="DDMMM"
    elif graph_period == 'week':
        valueformat="DDD,hh:mm TT"
    elif graph_period == 'year':
        valueformat="MMMYY "
    
    return valueformat


#check graph type
def check_graph_type(g_type,vm_ram,m_type):
    title={}
    if g_type=='cpu':
        title['y_title']='cpu(%)'
        title['g_title']="CPU PERFORMANCE"
    if g_type=='disk':
        title['y_title']='disk(MB/s)'
        title['g_title']="DISK PERFORMANCE"
    if g_type=='nw':
        title['y_title']='net(MB/s)'
        title['g_title']="NETWORK PERFORMANCE"
    if g_type=="ram":
       
        if (int(vm_ram)>1024) or (m_type=='host'):
            title['y_title']="ram(GB)"
        else:
            title['y_title']="ram(MB)"
        title['g_title']="MEMORY PERFORMANCE"
    if m_type=='host':
        if g_type=='tmp':
            title['y_title']='t(Degree Celcius)'
            title['g_title']="TEMPERATURE PERFORMANCE"
        if g_type=='power':
            title['y_title']='power(Watt)'
            title['g_title']="POWER PERFORMANCE"
    return title


###############################################################################################################################################

