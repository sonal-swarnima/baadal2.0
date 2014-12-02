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
import os, re, time, rrdtool, libvirt
from xml.etree import ElementTree
from log_handler import rrd_logger
from gluon import IMG, URL, current
from helper import get_constant, get_context_path, execute_remote_cmd

VM_UTIL_10_MINS = 1
VM_UTIL_24_HOURS = 2
VM_UTIL_ONE_WEEK = 3
VM_UTIL_ONE_MNTH = 4
VM_UTIL_ONE_YEAR = 5

STEP         = 300
TIME_DIFF_MS = 550

def get_rrd_file(identity):

    rrd_file = get_constant("vmfiles_path") + os.sep + get_constant("vm_rrds_dir") + os.sep + identity + ".rrd"
    return rrd_file

""""Generate graph for given RRD file and period"""
def create_graph(rrd_file_name, graph_type, rrd_file_path, graph_period):

    rrd_logger.debug(rrd_file_name+" : "+graph_type+" : "+rrd_file_path+" : "+graph_period)
    #rrd_file = rrd_file_name + '.rrd'       

    #shutil.copyfile(rrd_file_path, rrd_file)
    graph_file = rrd_file_name + "_" + graph_type + ".png"
    graph_file_dir = os.path.join(get_context_path(), 'static' + get_constant('graph_file_dir'))
    graph_file_path = graph_file_dir + os.sep + graph_file

    start_time = None
    consolidation = 'MIN'
    ds = ds1 = ds2 = None
    line = line1 = line2 = None

    
    if graph_period == 'hour':
        start_time = 'now - ' + str(24*60*60)
    elif graph_period == 'day':
        start_time = '-1w'
    elif graph_period == 'month':
        start_time = '-1y'
    elif graph_period == 'week':
        start_time = '-1m'
    elif graph_period == 'year':
        start_time = '-5y'
  
    if ((graph_type == 'ram') or (graph_type == 'cpu')):

        if graph_type == 'ram':
            ds = 'DEF:ram=' + rrd_file_path + ':ram:' + consolidation
            line = 'LINE1:ram#0000FF:Memory'
            graph_type += " (Bytes/Sec)"
            upper_limit = ""
        elif graph_type == 'cpu':
            ds = 'DEF:cpu=' + rrd_file_path + ':cpu:' + consolidation
            line = 'LINE1:cpu#0000FF:CPU'
            graph_type += " (%)"
            upper_limit = "-u 100"
                
        rrdtool.graph(graph_file_path, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', ' ' + rrd_file_name, ds, line, "-l 0 --alt-y-grid -L 6" + upper_limit )

    else:

        if graph_type == 'nw':
            ds1 = 'DEF:nwr=' + rrd_file_path + ':tx:' + consolidation
            ds2 = 'DEF:nww=' + rrd_file_path + ':rx:' + consolidation
            line1 = 'LINE1:nwr#0000FF:Transmit'
            line2 = 'LINE1:nww#FF7410:Receive'

        elif graph_type == 'disk':
            ds1 = 'DEF:diskr=' + rrd_file_path + ':dr:' + consolidation
            ds2 = 'DEF:diskw=' + rrd_file_path + ':dw:' + consolidation
            line1 = 'LINE1:diskr#0000FF:DiskRead'
            line2 = 'LINE1:diskw#FF7410:DiskWrite'

        graph_type += " (Bytes/Sec)"

        rrdtool.graph(graph_file_path, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', ' ' + rrd_file_name, ds1, ds2, line1, line2, "-l 0 --alt-y-grid -L 6" )

    rrd_logger.debug(graph_file_path)

    if os.path.exists(graph_file_path):
        return True
    else:
        return False
    
""""Fetch graph for given RRD file and period"""
def get_performance_graph(graph_type, vm, graph_period):

    error = None
    img = IMG(_src = URL("static" , "images/no_graph.jpg") , _style = "height:100px")

    try:
        rrd_file = get_rrd_file(vm)
  
        if os.path.exists(rrd_file):
            if create_graph(vm, graph_type, rrd_file, graph_period):   
                img_pos = "images/vm_graphs/" + vm + "_" + graph_type + ".png"
                img = IMG(_src = URL("static", img_pos), _style = "height:100%")
                rrd_logger.info("Graph created successfully")
            else:
                rrd_logger.warn("Unable to create graph from rrd file!!!")
                error = "Unable to create graph from rrd file"
        else:
            rrd_logger.warn("VMs RRD File Unavailable!!!")
            error = "VMs RRD File Unavailable!!!"
    except: 
        rrd_logger.warn("Error occured while creating graph.")
        import sys, traceback
        etype, value, tb = sys.exc_info()
        error = ''.join(traceback.format_exception(etype, value, tb, 10))
        rrd_logger.debug(error)

    finally:
        if error != None:
            return error
        else:
            rrd_logger.info("Returning image.")
            return img


""""Fetch RRD data to display in tabular format"""
def fetch_rrd_data(rrd_file_name, period=VM_UTIL_24_HOURS):
    rrd_file = get_rrd_file(rrd_file_name)

    start_time = 'now-' + str(24*60*60)
    end_time = 'now'
    
    if period == VM_UTIL_10_MINS:
        start_time = 'now-' + str(10*60)
    elif period == VM_UTIL_ONE_WEEK:
        start_time = '-1w'
    elif period == VM_UTIL_ONE_MNTH:
        start_time = '-1m'
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
    
    return (sum(mem_data)/float(len(mem_data)) if len(mem_data) > 0 else 0, 
            sum(cpu_data)/float(len(cpu_data)) if len(cpu_data) > 0 else 0, 
            sum(dskr_data)/float(len(dskr_data)) if len(dskr_data) > 0 else 0,
            sum(dskw_data)/float(len(dskw_data)) if len(dskw_data) > 0 else 0,
            sum(nwr_data)/float(len(nwr_data)) if len(nwr_data) > 0 else 0,
            sum(nww_data)/float(len(nww_data)) if len(nww_data) > 0 else 0)
   
"""Create the RRD file"""
def create_rrd(rrd_file):

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
def get_dom_mem_usage(dom_name, host):

    rrd_logger.debug("Fetching memory usage of domain %s defined on host %s" % (dom_name, host))

    cmd = "output=`ps -ef --sort=start_time | grep '%s.qcow2' | grep -v grep | awk '{print $2}'`;smem -c 'pid pss'| grep $output | awk '{print $2}'" % dom_name
    #"ps aux | grep '\-name " + dom_name + " ' | grep kvm"
    output = execute_remote_cmd(host, "root", cmd, None, True)
    return (int(output[0]))*1024 #return memory in Bytes by default

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

    dom_memusage   = get_dom_mem_usage(dom.name(), host_ip)
    dom_nw_usage   = get_dom_nw_usage(dom)
    dom_disk_usage = get_dom_disk_usage(dom)

    dom_stats =      {'rx'     : dom_nw_usage[0]}
    dom_stats.update({'tx'     : dom_nw_usage[1]})
    dom_stats.update({'diskr'   : dom_disk_usage[0]})
    dom_stats.update({'diskw'   : dom_disk_usage[1]})
    dom_stats.update({'memory'  : dom_memusage})
    dom_stats.update({'cputime' : dom.info()[4]})
    dom_stats.update({'cpus'    : dom.info()[3]})

    rrd_logger.info(dom_stats)
    rrd_logger.warn("As we get VM mem usage info from rrs size of the process running on host therefore it is observed that the memused is sometimes greater than max mem specified in case when the VM uses memory near to its mam memory")

    return dom_stats

def get_actual_usage(dom_obj, host_ip):


    dom_name = dom_obj.name()

    dom_stats = get_current_dom_resource_usage(dom_obj, host_ip)

    """Fetch previous domain stat value from cache"""
    prev_dom_stats = current.cache.disk(str(dom_name), lambda:dom_stats, 86400)  # @UndefinedVariable
    rrd_logger.debug(prev_dom_stats)
        
    #calulate usage
    usage = {'ram'      : dom_stats['memory']} #ram in Bytes usage
    usage.update({'cpu' : (dom_stats['cputime'] - prev_dom_stats['cputime'])/(float(prev_dom_stats['cpus'])*10000000*STEP)}) #percent cpu usage
    usage.update({'tx'  : (dom_stats['tx'] - prev_dom_stats['tx'])}) #in KBytes
    usage.update({'rx'  : (dom_stats['rx'] - prev_dom_stats['rx'])}) #in KBytes
    usage.update({'dr'  : (dom_stats['diskr'] - prev_dom_stats['diskr'])}) #in KBytes
    usage.update({'dw'  : (dom_stats['diskw'] - prev_dom_stats['diskw'])}) #in KBytes

    current.cache.disk.clear(str(dom_name))  # @UndefinedVariable

    """Cache the current CPU utilization, so that difference can be calculated in next instance"""
    latest_dom_stats = current.cache.disk(str(dom_name), lambda:dom_stats, 86400)        # @UndefinedVariable
    rrd_logger.debug(latest_dom_stats)
   
    return usage 

"""Uses iostat tool to capture CPU statistics of host"""
def get_host_cpu_usage(host_ip):

    command = "iostat -c | sed '1,2d'"
    command_output = execute_remote_cmd(host_ip, 'root', command, None,  True)
    rrd_logger.debug(type(command_output))
    cpu_stats = re.split('\s+', command_output[1])
    rrd_logger.debug(cpu_stats)
    rrd_logger.info("CPU stats of host %s is %s" % ( host_ip, (cpu_stats[1] + cpu_stats[2] + cpu_stats[3])))
    return (float(cpu_stats[1]) + float(cpu_stats[2]) + float(cpu_stats[3]))

"""Uses iostat tool to capture input/output statistics for host"""
def get_host_disk_usage(host_ip):

    command = "iostat -d | sed '1,2d'"
    command_output = execute_remote_cmd(host_ip, 'root', command, None, True)
    disk_stats = re.split('\s+', command_output[1])
    rrd_logger.info("Disk stats of host %s is dr: %s dw: %s" % (host_ip, disk_stats[2], disk_stats[3]))  
    return [float(disk_stats[2]), float(disk_stats[3])]

"""Uses top command to capture memory usage for host"""
def get_host_mem_usage(host_ip):

    command = "top -b -n1 | grep 'Mem'"
    command_output = execute_remote_cmd(host_ip, 'root', command, None, True)
    mem_stats = re.split('\s+', command_output[0])[3]
    used_mem_in_kb = int(mem_stats[:-1])
    rrd_logger.info("Mem stats of host %s is %s" % (host_ip, used_mem_in_kb))
    return used_mem_in_kb

"""Uses ifconfig command to capture network usage for host"""
def get_host_nw_usage(host_ip):

    command = "ifconfig baadal-br-int | grep 'RX bytes:'"
    command_output = execute_remote_cmd(host_ip, 'root', command, None, True)
    nw_stats = re.split('\s+', command_output[0])
    rx = int(re.split(':', nw_stats[2])[1])
    tx = int(re.split(':', nw_stats[6])[1])
    rrd_logger.info("Disk stats of host %s is rx: %s tx: %s" % (host_ip, rx, tx))
    return [rx, tx]

def get_host_resources_usage(host_ip):

    host_cpu_usage = get_host_cpu_usage(host_ip)
    host_disk_usage = get_host_disk_usage(host_ip)
    host_mem_usage = get_host_mem_usage(host_ip)
    host_nw_usage = get_host_nw_usage(host_ip)

    host_usage = {'cpu' : host_cpu_usage} #percent cpu usage
    host_usage.update({'dr' : host_disk_usage[0]*1024}) #Bytes/s
    host_usage.update({'dw' : host_disk_usage[1]*1024})
    host_usage.update({'ram' : host_mem_usage*1024}) #Bytes
    host_usage.update({'rx' : host_nw_usage[0]}) #in Bytes
    host_usage.update({'tx' : host_nw_usage[1]}) #in Bytes

    rrd_logger.info("Host %s stats:  %s" % (host_ip, host_usage))
    return host_usage


def update_host_rrd(host_ip):

    try:
   
        rrd_file = get_rrd_file(host_ip.replace(".","_"))
        timestamp_now = time.time()

        if not (os.path.exists(rrd_file)):

            rrd_logger.warn("RRD file (%s) does not exists" % (rrd_file))
            rrd_logger.warn("Creating new RRD file")
            create_rrd(rrd_file)
       
        else:

            host_stats = get_host_resources_usage(host_ip)
            rrdtool.update(rrd_file, "%s:%s:%s:%s:%s:%s:%s" % (timestamp_now, host_stats['cpu'], host_stats['ram'], host_stats['dr'], host_stats['dw'], host_stats['tx'], host_stats['rx']))
 
    except Exception, e:
 
        rrd_logger.debug("Error occured while creating/updating rrd for host: %s" % (host_ip))
        rrd_logger.debug(e)

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


def update_rrd(host_ip):

        #UPDATE HOST RRD
        rrd_logger.info("Startiing rrd updation for host %s" % (host_ip))
        update_host_rrd(host_ip)
        rrd_logger.info("Ending rrd updation for host %s" % (host_ip))


        #UPDATE RRD for ALL VMs on GIVEN HOST

        rrd_logger.info("Startiing rrd updation for VMs on host %s" % (host_ip))

        hypervisor_conn = None

        try:

            hypervisor_conn = libvirt.openReadOnly("qemu+ssh://root@" + host_ip + "/system")
            rrd_logger.debug(hypervisor_conn.getHostname())

            active_dom_ids  = hypervisor_conn.listDomainsID()
            all_dom_objs    = hypervisor_conn.listAllDomains()

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

            if hypervisor_conn:
                hypervisor_conn.close()

