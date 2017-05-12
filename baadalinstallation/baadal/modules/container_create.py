from cont_handler import Container ,addip
from gluon import current
from helper import get_context_path, get_docker_daemon_address, \
    get_nginx_server_address, log_exception , config
from images import getImageProfile
from log_handler import logger
import docker
import os
import random
import remote_vm_task as remote_machine

cert_path = os.path.join(get_context_path(), 'modules/certs/')
tls_config = docker.tls.TLSConfig(client_cert=(cert_path+'cert.pem', cert_path+'key.pem'),verify=cert_path+'ca.pem')

docker_machine = get_docker_daemon_address()
client = docker.Client(base_url='https://'+docker_machine[0]+':'+docker_machine[1],version='auto', tls=tls_config)
Container.setclient(client)


def proxieddomain (name) :
    #alias = '.baadalgateway.cse.iitd.ac.in'
    alias ='.apps.iitd.ac.in'
    address = name +alias
    return address[1:]       # required name contains '/' at start


def install_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In install_container() function...")
        cont_details = current.db.container_data[cont_id]
        logger.debug(cont_details)
#         user_name = current.auth.user.username
#         mount_hostvolumes = '/root/user/'+ cont_details.owner_id.username +'/'+cont_details.name
        memory = str(cont_details.RAM)+'M'
        
        ret = install_container(
                                cont_details.name,
                                cont_details.image_id,
                                
                                cont_details.env_vars,
                                cont_details.vCPU,
                                memory,
                                True)
        logger.debug(ret)
        message = ("Container %s created successfully." % cont_details.name)
        cont_details.update_record(UUID=ret['Id'], status=current.VM_STATUS_RUNNING)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())

    
def start_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In start_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.start()
        cont_details.update_record(status=current.VM_STATUS_RUNNING)
        message = "Container started successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def stop_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In stop_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.stop()
        cont_details.update_record(status=current.VM_STATUS_SHUTDOWN)
        message = "Container stopped successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def suspend_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In suspend_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.pause()
        cont_details.update_record(status=current.VM_STATUS_SUSPENDED)
        message = "Container suspended successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def resume_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In resume_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.resume()
        cont_details.update_record(status=current.VM_STATUS_RUNNING)
        message = "Container resumed successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def delete_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In delete_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.remove()
        del current.db.container_data[cont_id]
        message = "Container deleted successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def recreate_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In recreate_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.remove()

#         mount_hostvolumes = '/root/user/'+ cont_details.owner_id.username +'/'+cont_details.name
        memory = str(cont_details.RAM)+'M'
        
        ret = install_container(
                                cont_details.name,
                                cont_details.image_id,
                                
                                cont_details.env_vars,
                                cont_details.vCPU,
                                memory,
                                True)
        logger.debug(ret)
        message = ("Container %s re-created successfully." % cont_details.name)
        cont_details.update_record(UUID=ret['Id'], status=current.VM_STATUS_RUNNING)
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())


def restart_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In restart_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID,setProp=False)
        container.restart()
        cont_details.update_record(status=current.VM_STATUS_RUNNING)
        message = "Container restarted successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())

def backup_cont(parameters):
    try:
        cont_id = parameters['cont_id']
        logger.debug("In backup_container() function...")
        cont_details = current.db.container_data[cont_id]
        container = Container(cont_details.UUID)
        container.backup(cont_details.owner_id.username)
        message = "Container commited successfully."
        return (current.TASK_QUEUE_STATUS_SUCCESS, message)                    
    except:
        logger.debug("Task Status: FAILED Error: %s " % log_exception())
        return (current.TASK_QUEUE_STATUS_FAILED, log_exception())

def scale(name,uuid,templateid,env,cpushare,memory,scaleconstant):
    uuids=[uuid]
    
    imageprofile = getImageProfile(templateid)
    for num in range(1,scaleconstant):
        uuid=install_container(name+'-ins'+str(num),templateid,env,cpushare,memory,False,False)
        uuids.append(uuid)
    port = imageprofile['port']
    if( port) :    
        addip(name,uuids)

def install_container(name,templateid,env,cpushare,memory,portmap=False,setnginx=True,restart_policy='no'):
    imageprofile = getImageProfile(templateid)
    nodes = get_node_to_deploy()
    nodeindex = get_node_pack(nodes,memory,1)
    port = imageprofile['port']
    if (port):
        portmap = True 
    if(not env):
        env = {'constraint:node=':nodes[nodeindex]['Name']}
    else:
        env['constraint:node='] =nodes[nodeindex]['Name']
    env['TERM'] = 'xterm'
    if(imageprofile['updatemysql'] ):
        extrahosts = {'mysql':config.get("DOCKER_CONF","mysql_machine_ip")}
    else :
        extrahosts = None
    ulimits=[]
    import docker.utils
    ulimits.append(docker.utils.Ulimit(Name='NPROC',Soft=500,Hard=1000))
    ulimits.append(docker.utils.Ulimit(Name='NOFILE',Soft=4000,Hard=8000))
    hostconfig = client.create_host_config(publish_all_ports = portmap,mem_limit = memory,cap_drop=imageprofile['permissiondrop'],cap_add=imageprofile['permissionadd'],links  = imageprofile['links'],extra_hosts=extrahosts,restart_policy={'Name':restart_policy,'MaximumRetryCount':5},ulimits=ulimits)
    try: 
        containerid = client.create_container(name=name,image = imageprofile['Id'] , command = imageprofile['cmd'],
                              environment = env , detach = True ,cpu_shares=cpushare,
                             host_config = hostconfig )
    except docker.errors as e:
        print (e) 
        return       
    # Update the db -- container in created state.....
    try:                     
        response = client.start(container = containerid['Id'])  # @UnusedVariable
        # Update the db -- container in running state
    except Exception as e:
        logger.debug(e)
    if( port and setnginx) :
        container = Container(containerid)    
        container.addipbyconf()    
    return containerid

def get_random_string(length=8,allowed_chars='abcdefghijklmnopqrstuvwxyz'):
    return ''.join(random.choice(allowed_chars) for i in range(length))        # @UnusedVariable


    
def garbage_collector():
    
    #Delete volumes no longer necessary
    nginx_server = get_nginx_server_address()
    vollist = client.volumes(filters = { 'dangling' : True})
    volarray =  vollist.get('Volumes')
    print (vollist['Volumes'])
    if volarray:
        for volume in vollist['Volumes']:
            try:
                client.remove_volume(name = volume['Name'])
            except Exception as e:
                print (e) 
                
    #Delete remaining nginx conf
    
    conlist = client.containers(all = True)
    namelist = ['default']
    for container in conlist:
        namelist.append(container['Names'][0].split("/")[2])
        #~ namelist.append(container['Names'][0].split("/")[1])
    print(namelist)    
    cmd = "ls /etc/nginx/conf.d/"    
    output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
    strlist = output.split("\n")
    print(strlist)
    
    todellist =[]
    for i in range(0,len(strlist)-1):
        name = strlist[i].split(".")[0]
        if not name in namelist:
            todellist.append(name)
    print(todellist)        
    for name in todellist:
        cmd = "rm -f /etc/nginx/conf.d/"+name+".conf"     
        output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
    
    #Delete any mysql database whose app is missing
    '''datalist= ['information_schema','sys','mysql','performance_schema']
    datalist.append(namelist)
    cmd = """bash -c "mypassword='my-secret-pw' /var/lib/mysql/mysql.sh -l" """ 
    container = Container('f966820cf4a0')
    output = container.execcmd(cmd)
    strlist = output.split("\n")
    print(strlist)
    for i in range(3,len(strlist)-1):
        name = strlist[i].split(".")[0]
        if not name in datalist:
            todellist.append(name)    
    print(todellist)
    
    for name in todellist:
        cmd = """bash -c "mypassword='my-secret-pw' /var/lib/mysql/mysql.sh -r """ + name + ' "  '    
        print(cmd)
        container.execcmd(cmd)
    container = 'None'
    '''
    #Delete any containers not in database
    #print('not implemented')
    
def get_node_to_deploy():
    templist = client.info()
    
    
    nodes=[]
    nodenumber =-1
    for x in templist['SystemStatus'] :
        tear=x[0].split(' ')
        tocheck=tear[len(tear)-1]
        
        if (len(tear)>1):
            if (len(tear) == 2):
                nodenumber +=1
                
                nodes.append({'Name':tear[1],'IP':x[1]})
                continue
            if tocheck =='Status' :
                nodes[nodenumber]['Status'] = x[1]
            elif tocheck =='ID':
                nodes[nodenumber]['Id'] = x[1]
            elif tocheck =='Containers':
                nodes[nodenumber]['Containers'] = x[1]
            elif tocheck =='CPUs':
                nodes[nodenumber]['Reserved CPUs'] = x[1]
            elif tocheck =='Memory':
                nodes[nodenumber]['Reserved Memory'] = x[1]
            elif tocheck =='Labels':
                tempar = x[1].split(", ")
                nodes[nodenumber]['Labels'] ={}
                for item in tempar:
                    splitar = item.split("=")
                    nodes[nodenumber]['Labels'][splitar[0]]=splitar[1]
            elif tocheck =='ServerVersion':
                nodes[nodenumber]['ServerVersion'] = x[1]
            elif tocheck =='UpdatedAt':
                nodes[nodenumber]['UpdatedAt'] = x[1]
            else :
                continue
                #nodenumber +=1
    return nodes

def get_node_pack(nodes,memory,strategy=1):
# strategy at 1 represents binpack strategy
    minimummem=1000
    minimumnode=0
    for idx ,node in enumerate(nodes):
        memarray = node['Reserved Memory'].split(" / ")
        tmparray = memarray[0].split(" ")
        if (tmparray[1]=='GiB'):
            used = float(tmparray[0])*1024
        else :
            used = float(tmparray[0])
     
        tmparray = memarray[1].split(" ")
      
        if (tmparray[1]=='GiB'):
            total = float(tmparray[0])*1024
        else :
            total = float(tmparray[0])
      
        if (used + float(memory[:-1]) < total and strategy ==1 ):
            return idx
        else :
            if (used / total < minimummem):
              
                minimummem = used /total
                minimumnode= idx
            else:
                continue
    return minimumnode

def listallcontainerswithnodes():
    
    lista=list_container( showall=True)
    nodes=get_node_to_deploy()
#     logger.debug(lista)
#     logger.debug(nodes)
    for x in lista:
        hostcontainer = x['Names'][0].split("/")[1]
        for y in nodes:
            if(y['Name'] == hostcontainer):
                if(y.get('Containerlist')):
                    y['Containerlist'].append(x)
                    break
                else:
                    y['Containerlist']=[]
                    y['Containerlist'].append(x)
                    break
    return nodes
       

    
def list_container(showall):

    containerlist = client.containers(all=showall,size=True)
    logger.debug(containerlist)
    keystodisplay = ["Image","Created","Names" , "Id", "State" , "Command" ,"Status","Ports","Size"]
    newlist = []
    for x in containerlist:
        containerex = x
        containerlimited  = {}
        for key,value in containerex.items():
            if ( key in keystodisplay):
                containerlimited[key] = value
        newlist.append(containerlimited)   
    #logger.debug(newlist)
    return newlist
