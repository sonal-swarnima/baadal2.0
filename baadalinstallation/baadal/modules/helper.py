# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    global auth; auth = gluon.tools.Auth()
    global db; db = gluon.sql.DAL()
    global session; session = gluon.globals.Session()
    import logger
###################################################################################
import os,libvirt,commands
from gluon import current  # @Reimport

def is_moderator():
    if (current.auth.user.username in ['mohan','sonals','ssalaria','sbansal']) or ('admin' in current.auth.user_groups.values()):
        return True
    return False    

def is_faculty():
    if (current.auth.user.username in ['mohan','sonals','ssalaria','sbansal']) or ('faculty' in current.auth.user_groups.values()):
        return True
    return False    

def get_config_file():

    import ConfigParser    
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(), 'static/config-db.cfg'));
    return config

def get_context_path():

    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path

def get_date():
    import datetime
    return datetime.datetime.now()


def get_vm_template_config():
    from xml.dom import minidom

    xmldoc = minidom.parse(os.path.join(get_context_path(), 'static/vm_template_config.xml'))
    return xmldoc


def give_datastore():
    datastores = db(db.datastore.id >= 0).select()
    if(len(datastores) == 0):
        return None
    minused = datastores[0]
    #for d in datastores:
        #if(d.used < minused.used):minused=d
    return minused

def get_constant(constant_name):
    constant = db(db.constants.name == constant_name).select(db.constants.value)[0]['value']
    return constant

def set_constant(constant_name, constant_value):
    db(db.constants.name == constant_name).update(value = constant_value)
    return

def new_mac_ip(vmcount):
    vmcount = int(vmcount)
    mac = get_constant('mac_range') + str(int(vmcount/100)) + ":" + str(vmcount-int(vmcount/100)*100)
    ip = get_constant('ip_range') + str(int(1+vmcount/100)) + "." + str(vmcount-int(vmcount/100)*100)
    port = str(int(get_constant('vncport_range')) + vmcount)
    return(mac,ip,port)

def check_vm_with_same_name(vmname):
    found = False
    vms = db(db.vm_data.id >= 0).select()
    for vm in vms:
        if vmname == vm.vm_name: 
            found = True
    return found


def computeeffres(RAM, vCPU, runlevel):
    effram = 1024
    effcpu = 1
    divideby = 1
    if(runlevel == 0): 
        divideby=0
    elif(runlevel == 1): 
        divideby=1
    elif(runlevel == 2): 
        divideby=2
    elif(runlevel == 3): 
        divideby=4
    if(divideby != 0):
        if(RAM/divideby >= 1024):
            effram = RAM/divideby
        if(vCPU/divideby >= 1): 
            effcpu = vCPU/divideby
    if(divideby == 0):
        effram = 0
        effcpu = 0
    return (effram, effcpu)

def check_if_vm_defined(hostip, vmname):
    domains=[]    # It will contain the domain information of all the available domains
    exists = False
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+ hostip +'/system')
        ids = conn.listDomainsID()
        for _id in ids:
            domains.append(conn.lookupByID(_id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            if(vmname == dom.name()):
                exists=True
        return exists
        conn.close()
    except:
        return False

def attach_disk(vmname, size):
   
    vm = db(db.vm_data.vm_name == vmname).select()[0]
    out = "Error attaching disk"
    try:
        conn = libvirt.open("qemu+ssh://root@" + vm.host_id.ip + "/system")
        dom = conn.lookupByName(vmname)
        alreadyattached = len(db(db.attached_disks.vm_id == vm.id).select(db.attached_disks.id))
        if(dom.isActive() != 1):
            out="Cannot attach disk to inactive domain."
            return out
        else:
            diskpath= get_constant('vmfiles_path') + get_constant('datastore_int')+vm.datastore.name+"/"+vmname+"/"+vmname+str(alreadyattached
                      +1)+ ".raw"
            logger.debug("Above IF")
            if not os.path.exists (get_constant('vmfiles_path')+ get_constant('datastore_int') + vm.datastore_id.ds_name+ '/' +vmname):
                logger.debug("Making Directory")          
                os.makedirs(get_constant('vmfiles_path') + get_constant('datastore_int') + vm.datastore_id.ds_name+'/'+vmname)
           
            command= "qemu-img create -f raw "+ diskpath+ " " + str(size) + "G"
            logger.debug(command)
            out = commands.getstatusoutput(command)
            logger.debug(out)
            command = "ssh root@"+vm.host_id.host_ip + " virsh attach-disk " + vmname + " " + diskpath + " vd" + chr(97+alreadyattached+1) + " --type disk"
            logger.debug(command)
            out = commands.getstatusoutput(command)
            logger.debug(out)
            xmlfile = dom.XMLDesc(0)
            dom = conn.defineXML(xmlfile)
            out1 = dom.isActive()
            logger.debug(out1)
            if(out1 == 1): 
                logger.debug("Most probably the disk has been attached successfully. Reboot your vm to see it.")
        conn.close()
        return str(out)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        out = "Some Error Occured\n"+msg
        logger.error(out)
        return str(out) 

def get_fullname(_user_id):
    row = current.db(current.db.user.id==_user_id).select().first()    
    return row['first_name'] + ' ' + row['last_name']
