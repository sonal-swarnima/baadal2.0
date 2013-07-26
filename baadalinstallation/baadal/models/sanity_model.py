# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################
import libvirt
from libvirt import *  # @UnusedWildImport

def vminfotostate(intstate):

    if(intstate == VIR_DOMAIN_NOSTATE): state="No_State"
    elif(intstate == VIR_DOMAIN_RUNNING):state="Running"
    elif(intstate == VIR_DOMAIN_BLOCKED):state="Blocked"
    elif(intstate == VIR_DOMAIN_PAUSED):state="Paused"
    elif(intstate == VIR_DOMAIN_SHUTDOWN):state="Being_Shut_Down"
    elif(intstate == VIR_DOMAIN_SHUTOFF):state="Off"
    elif(intstate == VIR_DOMAIN_CRASHED):state="Crashed"
    else: state="Unknown"

    return state


def check_sanity():
    vmcheck=[]
    hosts=db(db.host.status == HOST_STATUS_UP).select()
    for host in hosts:
        try:
            #Establish a read only remote connection to libvirtd
            #find out all domains running and not running
            #Since it might result in an error add an exception handler
            conn = libvirt.openReadOnly('qemu+ssh://root@'+host.host_ip+'/system')
            domains=[]
            ids = conn.listDomainsID()
            for _id in ids:
                domains.append(conn.lookupByID(_id))
            names = conn.listDefinedDomains()
            for name in names:
                domains.append(conn.lookupByName(name))
            for dom in domains:
                try:
                    name = dom.name()
                    vm = db(db.vm_data.vm_name == name).select(db.vm_data.id,db.vm_data.host_id,db.vm_data.vm_name).first()
                    status=vminfotostate(dom.info()[0])
                    if(vm):
                        if(vm.host_id != host.id):
                            vmcheck.append({'host':host.host_name,'vmname':vm.vm_name,'status':status,'operation':'Moved from '+vm.host_id.host_name+' to '+host.host_name})#Bad VMs
                            db(db.vm_data.vm_name==name).update(host_id=host.id)
                        else:
                            vmcheck.append({'host':host.host_name,'vmname':vm.vm_name,'status':status,'operation':'Is on expected host '+vm.host_id.host_name})#Good VMs
                    else:
                        vmcheck.append({'host':host.host_name,'vmname':dom.name(),'status':status,'operation':'Orphan, VM is not in database'})#Orphan VMs
                    dom=""
                except Exception as e:
                    logger.error(e)
                    if(vm):
                        vmcheck.append({'vmname':vm.vm_name,'host':'Unknown','status':'Unknown','operation':'Some Error Occured'})

            domains=[]
            names=[]
            print conn.close()
        except:pass
    return vmcheck
