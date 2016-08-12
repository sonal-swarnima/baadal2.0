from helper import get_context_path, get_docker_daemon_address, \
    get_nginx_server_address
from log_handler import logger
from proxy_handler import manageproxy
import docker
import dockerpty
import os
import remote_vm_task as remote_machine
import traceback


def proxieddomain (name) :
    alias = '.baadalgateway.cse.iitd.ac.in'
    address = name +alias;
    return address[1:];         # required name contains '/' at start
    
class Container:
        
    client = None;
    propvalues = ['imageid','created','path','args','exposedports','environment','publishall','ports','hostname',
            'ipaddress','cmd' ,'entrypoint','bindings','volumes','sysinitpath','state']
    
    
    def __init__(self,id,setProp = True,**keywords):
        self.id = id;
        self.properties = {
        
        }
        print("new file updation successful");
        if not (Container.client) :
            cert_path = os.path.join(get_context_path(), 'modules/certs/')
            tls_config = docker.tls.TLSConfig(client_cert=(cert_path+'cert.pem', cert_path+'key.pem'),verify=cert_path+'ca.pem')
            docker_machine = get_docker_daemon_address();
            client = docker.Client(base_url='https://'+docker_machine[0]+':'+docker_machine[1],version='auto', tls=tls_config)
            
            Container.setclient(client);
            logger.debug(client);

        logger.debug(Container.client);
        self.update = Container.client.update_container;
        for key in keywords:
            self.properties[key] = keywords[key];    
        if setProp :
            self.updatedetails();
    

    def stop(self):
        response = Container.client.stop(container = self.id);
        return response;
        # update the db status ...
        
    def rename(self,newname):
        response = Container.client.rename(container = self.id,name = newname);
        return response;
        # update container name
        
    def start(self):
        
        response = Container.client.start(container = self.id);
        self.updatedetails();
        self.addipbyconf();
        return response;
        # update the db status ...
        
    def restart(self,timeout=10):
        response = Container.client.restart(self.id,timeout=timeout);
        #~ self.deleteipconf();
        #~ self.addipconf();
        self.updatedetails();
        self.addipbyconf();
        return response;
        
    def kill(self,signal='SIGKILL'):
        response = Container.client.kill(container=self.id,signal=signal);
        return response;
        # update the db status ...
        
    def resume(self):
        response = Container.client.unpause(self.id);    
        return response;
        # update the db status ...
        
    def logs(self,stdout=True,stderr=True,stream=False,timestamps=9999,follow = False):
        response = Container.client.logs(self.id,stdout=stdout,stream=stream,stderr=stderr,timestamps=timestamps,follow=follow)
        return response;
        
    def remove(self,v=True,link=False,force=False):
        self.stop();
        #container = Container(containerid);    
        #~ self.deleteipconf();
        self.deleteipbyconf();
        #os.system(cmd);    
        response = Container.client.remove_container(self.id,v=v,link=link,force=force);
        return response;
        # update the db status ...
        
    def pause(self):
        response = Container.client.pause(self.id);
        return response;
        # update the db status ...
        
    def stats(self,decode = True ,stream = False):
        response = Container.client.stats(self.id,decode,stream);
        return response;
        
    def top(self,pidargs='aux'):
        response = Container.client.top(self.id,pidargs);
        return response;
        
    def inspect(self):
        response = Container.client.inspect_container(self.id);
        return response;
        
    def updatedetails(self):
        response = self.inspect();
        try:
            
            self.properties['Created'] = response.get('Created');
            self.properties['Path'] = response.get('Path');
            self.properties['Args'] = response.get('Args');
            if (response.get('State')):
                self.properties['State'] =response['State'].get('Status');
            else:
                self.properties['State'] = None;
            self.properties['ImageId'] = response.get('Image');
            self.properties['Name'] = response.get('Name');
            self.properties['Hostname'] = response.get('Config')['Hostname'];
            self.properties['Domainname'] = response.get('Config')['Domainname'];
            self.properties['IPAddress'] = response.get('NetworkSettings')['IPAddress'];
            self.properties['MacAddress'] = response.get('NetworkSettings')['MacAddress'];
            if(response.get('NetworkSettings')):
                self.properties['Ports'] = response['NetworkSettings'].get('Ports');
            else:
                self.properties['Ports'] = None;
            self.properties['Cmd'] = response.get('Config')['Cmd'];
            self.properties['Environment'] = response.get('Config')['Env'];
            self.properties['EntryPoint'] = response.get('Config')['Entrypoint'];
            self.properties['Volumes'] = response.get('Config')['Volumes'];
            self.properties['Bindings'] = response.get('HostConfig')['Binds'];
            self.properties['ImageName'] = response.get('Config')['Image'];    
            self.properties['Memory'] = response.get('HostConfig').get('Memory');
            self.properties['CPUCore'] = response.get('HostConfig').get('CpusetCpus');
            self.properties['ExposedPorts'] =response.get('HostConfig').get('ExposedPorts');
            portdict = response['NetworkSettings'].get('Ports');
            if (portdict):
                for key in portdict:
                    if(portdict[key]):
                        self.properties['ConnectionPath'] = portdict[key][0]["HostIp"] + ":" + portdict[key][0]["HostPort"]
            if (not self.properties.get('ConnectionPath')):
					self.properties['ConnectionPath'] = '10.17.50.26:5556'     
        except Exception as e:
            print(e);
            #traceback.print_exc()

    
    # monitor changes in the filesystem    
    def diff(self):    
        response = Container.client.diff(self.id);
        return response;
        
    def recreate(self,commited = True,refresh = False):
        if not refresh :
            imageid = self.save_template("container restart","Docker automatic api","","temp","");
            print(imageid)
            containerid = Container.client.create_container(image=imageid['Id'],detach = True);
            #Update the db container created ;
            Container.client.start(containerid);
            #Update the db container started;
            #self.stop();
            self.remove();
            #Deleting image created if not commited .....
            if not commited :
                Container.client.remove_image(imageid['Id']);
            return containerid;
        
    def save_template(self,message,author,changes,tag,repository):
        #docker commit will used. Data in volumes will not be saved.Only changes in applications will be reflected.
        if (not repository) :
            repository = self.properties['ImageName'];
        response = Container.client.commit(self.id,tag=tag,message=message,author = author ,changes = changes , repository = repository);
        return response;
        
    def execcmdgenerator(self,cmd='bash'):
        # terminal will be opened ... generator will be returned;
        execid = Container.client.exec_create(container=self.id,cmd=cmd,tty=True,stdout=True,stderr=True);
        generator = Container.client.exec_start(exec_id = execid , detach = False , stream =True , tty = True);    
        return generator;
    
    def execcmd(self,cmd):
        execid = Container.client.exec_create(container=self.id,cmd=cmd,tty=False,stdout=True,stderr=True);
        output = Container.client.exec_start(exec_id = execid , detach = False , stream =True , tty = False);
        string ='';
        for x in output:
            string = string + x;
        return string;
        
    def deleteipbyconf(self):
        filepath = "/etc/nginx/conf.d/" + self.properties['Name'] +".conf";
        cmd = 'rm -f ' + filepath;
        nginx_server = get_nginx_server_address()
        output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print(output)
        cmd = '/etc/init.d/nginx reload';
        output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print(output)
            
    def deleteipconf(self):    
        name = self.properties['Name'];
        domainname = proxieddomain(name);
        filepath = "/etc/nginx/conf.d/default.conf";
        testpath = "./test/test.conf" 
        nginx_server = get_nginx_server_address()
        cmd ="cat " + filepath;
        out1=remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        reverser = manageproxy(out1);
        reverser.removebyip(domainname);
        
        reverser.filedit = reverser.filedit.replace('$' ,'\$');
        cmd = 'echo -e "' + reverser.filedit  + '" > '+ filepath;
        out2 = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        
       
        cmd = '/etc/init.d/nginx reload';
        output =remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print(output)
        
    def addipbyconf(self,updatetc=False):
        ipaddress = self.properties['IPAddress'];
        
        name = self.properties['Name'];
        domainname = proxieddomain(name);
        nginx_server = get_nginx_server_address()
        fulladdress = self.properties['ConnectionPath'];
        logger.debug(fulladdress);
        filepath = "/etc/nginx/conf.d/" + self.properties['Name'] +".conf";
        reverser = manageproxy('');
        reverser.add(reverser.render({'x' : domainname , 'y' : fulladdress}),fulladdress);
        print(reverser.filedit);
        reverser.filedit = reverser.filedit.replace('$' ,'\$');
        cmd = 'echo -e "' + reverser.filedit  + '" > '+ filepath;
        out2 = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print("Output : " +out2);
        cmd = '/etc/init.d/nginx reload';
        output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print(output)
        if(updatetc):
            hostadd = self.properties['ConnectionPath'].split(':')[0] + ' '  + domainname ; 
            cmd ='echo " ' + hostadd + ' " >> /etc/hosts'; 
            logger.debug('Command=> '+cmd)
            logger.debug('Host IP=> ' +hostadd)
            output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
            logger.debug(output)
            
    def addipconf(self,updatetc=False):
        ipaddress = self.properties['IPAddress'];
        
        name = self.properties['Name'];
        domainname = proxieddomain(name);
        
        fulladdress = self.properties['ConnectionPath'];
        filepath = "/etc/nginx/conf.d/default.conf";
        testpath = "./test/test.conf" 
        nginx_server = get_nginx_server_address()
        cmd ="cat " + filepath;
        out1=remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        print(out1);
        reverser = manageproxy(out1);
        
        reverser.add(reverser.render({'x' : domainname , 'y' : fulladdress}),fulladdress);
        
        
        reverser.filedit = reverser.filedit.replace('$' ,'\$');
        cmd = 'echo -e "' + reverser.filedit  + '" > '+ filepath;
        out2 = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        
        cmd = '/etc/init.d/nginx reload';
        output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
        
        if(updatetc):
            hostadd = self.properties['ConnectionPath'].split(':')[0] + ' '  + domainname ; 
            cmd ='echo " ' + hostadd + ' " >> /etc/hosts'; 
            output = remote_machine.execute_remote_cmd(nginx_server[0],nginx_server[1],cmd,nginx_server[2])
            
                
    def execstream(self,cmd='bash',stdout=None,stdin=None,stderr=None):
        self.removeoldexecid();
        dockerpty.exec_command(Container.client,self.id,cmd,True,stdout,stderr,stdin);
    
    def removeoldexecid(self):
        print("called");
                
    @classmethod                         
    def setclient(cls,cli):
        cls.client = cli;
            
#some functions raise docker.errors.APIError take them in try catch block.....
