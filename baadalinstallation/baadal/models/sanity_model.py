# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

def vminfotostate(intstate):
    logger.debug(intstate)

    if(intstate==0):  state="No_State"
    elif(intstate==1):state="Running"
    elif(intstate==2):state="Blocked"
    elif(intstate==3):state="Paused"
    elif(intstate==4):state="Being_Shut_Down"
    elif(intstate==5):state="Off"
    elif(intstate==6):state="Crashed"
    else: state="Unknown"

    logger.debug(state)
    return state


def check_sanity():
    import libvirt
    vmcheck=[]
    hosts=db(db.host.status == HOST_STATUS_UP).select()
    logger.debug(hosts)
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
                    logger.debug(name)
                    logger.debug(dom.info()[0])
                    vm = db(db.vm_data.vm_name == name).select(db.vm_data.id,db.vm_data.host_id,db.vm_data.vm_name).first()
                    logger.debug(vm)
                    status=vminfotostate(dom.info()[0])
                    logger.debug(status)
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
