# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import URL,IMG, H3
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import os
import shutil
import time

import rrdtool

from helper import is_moderator, get_constant, get_context_path

def get_rrd_file(vm_name):

    rrd_file = get_constant("vmfiles_path") + os.sep + get_constant("vm_rrds_dir") + os.sep + vm_name + ".rrd"
    return rrd_file

def create_graph(vm_name, graph_type, rrd_file_path, graph_period):

    logger.debug(vm_name+" : "+graph_type+" : "+rrd_file_path+" : "+graph_period)
    rrd_file = vm_name + '.rrd'       

    shutil.copyfile(rrd_file_path, rrd_file)
    graph_file = vm_name + "_" + graph_type + ".png"

    start_time = None
    grid = None
    consolidation = 'AVERAGE'
    ds = ds1 = ds2 = None
    line = line1 = line2 = None
    
    if graph_period == 'hour':
        start_time = 'now - ' + str(24 * HOURS)
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
                logger.info("Graph created successfully")
            else:
                logger.warn("Unable to create graph from rrd file!!!")
                error = H3("Unable to create graph from rrd file")
        else:
            logger.warn("VMs RRD File Unavailable!!!")
            error = "VMs RRD File Unavailable!!!"
    except: 
        logger.warn("Error occured while creating graph.")
        error = logger.exception()

    finally:
        if (is_moderator() and (error != None)):
            return H3(error)
        else:
            logger.info("Returning image.")
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
