# -*- coding: utf-8 -*-
###################################################################################
import shutil
import time
import rrdtool
import libvirt
from xml.etree import ElementTree

from gluon import H3, IMG, URL

from helper import *  # @UnusedWildImport
from host_helper import HOST_STATUS_UP

TIME_DIFF_MS = 300
VM_UTIL_24_HOURS = 1
VM_UTIL_ONE_WEEK = 2
VM_UTIL_ONE_MNTH = 3
VM_UTIL_ONE_YEAR = 4

def get_rrd_file(vm_name):

    rrd_file = get_constant("vmfiles_path") + os.sep + get_constant("vm_rrds_dir") + os.sep + vm_name + ".rrd"
    return rrd_file

def create_graph(vm_name, graph_type, rrd_file_path, graph_period):

    current.logger.debug(vm_name+" : "+graph_type+" : "+rrd_file_path+" : "+graph_period)
    rrd_file = vm_name + '.rrd'       

    shutil.copyfile(rrd_file_path, rrd_file)
    graph_file = vm_name + "_" + graph_type + ".png"

    start_time = None
    grid = None
    consolidation = 'AVERAGE'
    ds = ds1 = ds2 = None
    line = line1 = line2 = None
    
    if graph_period == 'hour':
        start_time = 'now - ' + str(24*60*60)
        grid = 'HOUR:1:HOUR:1:HOUR:1:0:%k'
        consolidation = 'MIN'
    elif graph_period == 'day':
        start_time = '-1w'
        grid = 'DAY:1:DAY:1:DAY:1:86400:%a'
    elif graph_period == 'month':
        start_time = '-1y'
        grid = 'MONTH:1:MONTH:1:MONTH:1:2592000:%b'
    elif graph_period == 'week':
        start_time = '-1m'
        grid = 'WEEK:1:WEEK:1:WEEK:1:604800:Week %W'
    elif graph_period == 'year':
        start_time = '-5y'
        grid = 'YEAR:1:YEAR:1:YEAR:1:31536000:%Y'
  
    if ((graph_type == 'ram') or (graph_type == 'cpu')):

        if graph_type == 'ram':
            ds = 'DEF:ram=' + vm_name + '.rrd:memory:' + consolidation
            line = 'LINE1:ram#0000FF:Memory'
        elif graph_type == 'cpu':
            ds = 'DEF:cpu=' + vm_name + '.rrd:cpuusage:' + consolidation
            line = 'LINE1:cpu#0000FF:CPU'
                
        rrdtool.graph(graph_file, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', 'VM Name: ' + vm_name, '--x-grid', grid, ds, line)

    else:

        if graph_type == 'nw':
            ds1 = 'DEF:nwr=' + vm_name + '.rrd:nwr:' + consolidation
            ds2 = 'DEF:nww=' + vm_name + '.rrd:nww:' + consolidation
            line1 = 'LINE1:nwr#0000FF:Receive'
            line2 = 'LINE2:nww#FF7410:Transmit'

        elif graph_type == 'disk':
            ds1 = 'DEF:diskr=' + vm_name + '.rrd:diskr:' + consolidation
            ds2 = 'DEF:diskw=' + vm_name + '.rrd:diskw:' + consolidation
            line1 = 'LINE1:diskr#0000FF:DiskRead'
            line2 = 'LINE2:diskw#FF7410:DiskWrite'

        rrdtool.graph(graph_file, '--start', start_time, '--end', 'now', '--vertical-label', graph_type, '--watermark', time.asctime(), '-t', 'VM Name: ' + vm_name, '--x-grid', grid, ds1, ds2, line1, line2)

    graph_file_dir = os.path.join(get_context_path(), 'static' + get_constant('graph_file_dir'))
    shutil.copy2(graph_file, graph_file_dir)

    if os.path.exists(graph_file_dir + os.sep + graph_file):
        return True
    else:
        return False
    
def get_performance_graph(graph_type, vm, graph_period):

    error = None
    img = IMG(_src = URL("static" , "images/no_graph.jpg") , _style = "height:100px")

    try:
        rrd_file = get_rrd_file(vm)
  
        if os.path.exists(rrd_file):
            if create_graph(vm, graph_type, rrd_file, graph_period):   
                img_pos = "images/vm_graphs/" + vm + "_" + graph_type + ".png"
                img = IMG(_src = URL("static", img_pos), _style = "height:100%")
                current.logger.info("Graph created successfully")
            else:
                current.logger.warn("Unable to create graph from rrd file!!!")
                error = H3("Unable to create graph from rrd file")
        else:
            current.logger.warn("VMs RRD File Unavailable!!!")
            error = "VMs RRD File Unavailable!!!"
    except: 
        current.logger.warn("Error occured while creating graph.")
        error = log_exception()

    finally:
        if (is_moderator() and (error != None)):
            return H3(error)
        else:
            current.logger.info("Returning image.")
            return img

def fetch_rrd_data(vm_identity, period=VM_UTIL_24_HOURS):
    rrd_file = get_rrd_file(vm_identity)

    start_time = 'now - ' + str(24 * HOURS)
    end_time = 'now'
    
    if period == VM_UTIL_ONE_WEEK:
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
#         time_info = rrd_ret[0]
        fld_info = rrd_ret[1]
        data_info = rrd_ret[2]
        cpu_idx = fld_info.index('cpuusage')
        mem_idx = fld_info.index('memory')
        dskr_idx = fld_info.index('diskr')
        dskw_idx = fld_info.index('diskw')
        nwr_idx = fld_info.index('nwr')
        nww_idx = fld_info.index('nww')
        
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
    
def create_rrd(rrd_file):

    ret = rrdtool.create( rrd_file, "--start", str(int(time.time())),
        "DS:cputime:GAUGE:%s:0:U"  % str(TIME_DIFF_MS),
        "DS:cpuusage:GAUGE:%s:0:U" % str(TIME_DIFF_MS),
        "DS:memory:GAUGE:%s:0:U"   % str(TIME_DIFF_MS),
        "DS:diskr:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:diskw:GAUGE:%s:0:U"    % str(TIME_DIFF_MS),
        "DS:nwr:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:nww:GAUGE:%s:0:U"      % str(TIME_DIFF_MS),
        "DS:cpus:GAUGE:%s:0:U"     % str(TIME_DIFF_MS),
        "RRA:MIN:0:1:525600",
        "RRA:AVERAGE:0:12:43800",
        "RRA:AVERAGE:0:2016:261",
        "RRA:AVERAGE:0:43200:61",
        "RRA:AVERAGE:0:105120:5")
    
    if ret:
        current.logger.warn(rrdtool.error())    

    current.logger.info("RRD Created")

def get_dom_mem_usage(dom_name, host):
    current.logger.debug("fetching memory usage of domain %s defined on host %s" % (dom_name, host))
    
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='root', password='')
    cmd = "ps aux | grep '\-name " + dom_name + " -uuid'"
    stdin, stdout, stderr = ssh.exec_command(cmd)  # @UnusedVariable
    output = stdout.readlines()
    ssh.close()

    if len(output) == 3:
        return int(re.split('\s+', output[0])[5])
    else:
        current.logger.warn("Unable to fetch memory usage details for dom %s" % (dom_name))

def get_dom_nw_usage(dom_obj):

    tree = ElementTree.fromstring(dom_obj.XMLDesc(0))
    nwr = 0
    nww = 0

    for target in tree.findall("devices/interface/target"):
        device = target.get("dev")
        stats  = dom_obj.interfaceStats(device)
        nwr   += stats[0]
        nww   += stats[4]

    current.logger.info("%s%s" % (nwr, nww))

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
    
    current.logger.info("rreq: %s bytesr: %s wreq: %s bytesw: %s" % (rreq, bytesr, wreq, bytesw))

    return [bytesr, bytesw]

def get_dom_info(dom_id, host_ip, conn):
    dom            = conn.lookupByID(dom_id)
    dom_name       = dom.name()
    dom_info       = dom.info()
    dom_maxmem     = dom_info[1]
    dom_cpus       = dom_info[3]
    dom_cputime    = dom_info[4]
    dom_memusage   = get_dom_mem_usage(dom_name, host_ip)
    dom_nw_usage   = get_dom_nw_usage(dom)
    dom_nwr        = dom_nw_usage[0]
    dom_nww        = dom_nw_usage[1]
    dom_disk_usage = get_dom_disk_usage(dom)
    dom_diskr      = dom_disk_usage[0]
    dom_diskw      = dom_disk_usage[1]

    current.logger.info(dom_name)
    current.logger.warn("As we get VM mem usage info from rrs size of the process running on host therefore it is observed that the memused is sometimes greater than max mem specified in case when the VM uses memory near to its mam memory")

    return [dom_name, dom_maxmem, dom_memusage, dom_cputime, dom_cpus, dom_nwr, dom_nww, dom_diskr, dom_diskw]

def get_rrd_file_abs_path(dom_name):
        return get_constant('vmfiles_path') + os.sep + get_constant('vm_rrds_dir') + os.sep + dom_name + ".rrd"

def calculate_cpu_usage(rrd_file, time_now, cputime, n_cores):
    
    current.logger.debug('time_now: '+ str(time_now))
    rrd_ret =rrdtool.fetch(rrd_file, 'MIN', '--start', 'now-%s'%(str(TIME_DIFF_MS*2)))
    time_info = rrd_ret[0]
    current.logger.debug('time_info: '+ str(time_info))
    data_info = rrd_ret[2]
    current.logger.debug('data_info: '+ str(data_info))
    cputime1 = data_info[0][0]
    current.logger.debug('cputime1: '+ str(cputime1))
    current.logger.debug('n_cores: '+ str(n_cores))

    if cputime1 == None: return 0
    
    cpu_time_diff = cputime - cputime1
    time_diff = time_now - time_info[0]
    
    current.logger.debug('time_diff: '+ str(time_diff))
    
    cpu_usage = 100 * cpu_time_diff / (time_diff * n_cores * 1000000000)
    current.logger.debug('cpu_usage: '+ str(cpu_usage))
    
    return cpu_usage

def update_rrd():

    active_host_list = current.db(current.db.host.status == HOST_STATUS_UP).select(current.db.host.host_ip)
    current.logger.debug(active_host_list)
    
    for host in active_host_list:
    
        conn = None
        try:
            host_ip = host['host_ip']
            conn = libvirt.open("qemu+ssh://root@" + host_ip + "/system")
            current.logger.debug(conn.getHostname())
            
            active_dom_ids = conn.listDomainsID()
            current.logger.debug(active_dom_ids)
            for dom_id in active_dom_ids:
            
                try:
                
                    dom_info = get_dom_info(dom_id, host_ip, conn)
                    timestamp_now = int(time.time())
                    current.logger.info(dom_info)
                    rrd_file = get_rrd_file_abs_path(dom_info[0])
                    
                    if not (os.path.exists(rrd_file)):
                        current.logger.warn("RRD file does not exists")
                        current.logger.warn("Creating new RRD file")
                        create_rrd(rrd_file)
                        time.sleep(1)
                    
                    cpu_usage = calculate_cpu_usage(rrd_file, timestamp_now, dom_info[3], dom_info[4])
                    ret = rrdtool.update(rrd_file, 
                                str(timestamp_now) + ":" + 
                                str(dom_info[3]) + ":" + 
                                str(cpu_usage) + ":" + 
                                str(dom_info[2]) + ":" + 
                                str(dom_info[7]) + ":" + 
                                str(dom_info[8]) + ":" + 
                                str(dom_info[5]) + ":" + 
                                str(dom_info[6]) + ":" + 
                                str(dom_info[4]) )

                    if ret:
                        current.logger.warn("Error while Updating %s.rrd" % (dom_info[0]))
                        current.logger.warn(rrdtool.error())
                    else:
                        current.logger.info("rrd updated successfully.")
                except:
                    current.logger.exception("Error occured while creating/updating rrd.")
                    pass

        except:
            current.logger.exception("Error occured while creating/updating rrd or host.")           
            pass
        finally: 
            if conn:
                conn.close()
