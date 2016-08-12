import dockerpty
class Container:
	client = 0;
	propvalues = ['imageid','created','path','args','exposedports','environment','publishall','ports','hostname',
			'ipaddress','cmd' ,'entrypoint','bindings','volumes','sysinitpath','state']
	
	
	def __init__(self,_id,setProp = True,**keywords):
		self.id = _id;
		self.properties = {
		
		}
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
		return response;
		# update the db status ...
		
	def restart(self,timeout=10):
		response = Container.client.restart(self.id,timeout=timeout);
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
		response = Container.client.stats(self,pidargs);
		return response;
		
	def inspect(self):
		response = Container.client.inspect_container(self.id);
		return response;
		
	def updatedetails(self):
		response = self.inspect();
		self.properties['Created'] = response['Created'];
		self.properties['Path'] = response['Path'];
		self.properties['Args'] = response['Args'];
		self.properties['State'] = response['State']['Status'];
		self.properties['ImageId'] = response['Image'];
		self.properties['Name'] = response['Name'];
		self.properties['Hostname'] = response['Config']['Hostname'];
		self.properties['Domainname'] = response['Config']['Domainname'];
		self.properties['IPAddress'] = response['NetworkSettings']['IPAddress'];
		self.properties['MacAddress'] = response['NetworkSettings']['MacAddress'];
		self.properties['Ports'] = response['NetworkSettings']['Ports'];
		self.properties['ExposedPorts'] = response['Config']['ExposedPorts'];
		self.properties['Cmd'] = response['Config']['Cmd'];
		self.properties['Environment'] = response['Config']['Env'];
		self.properties['EntryPoint'] = response['Config']['Entrypoint'];
		self.properties['Volumes'] = response['Config']['Volumes'];
		self.properties['Bindings'] = response['HostConfig']['Binds'];
		self.properties['ImageName'] = response['Config']['Image'];	
		self.properties['Memory'] = response['HostConfig']['Memory']
		self.properties['CPUCore'] = response['HostConfig']['CpusetCpus']
	
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
		
	def execcmd(self,cmd):
		# terminal will be opened ... generator will be returned;
		execid = Container.client.exec_create(container=self.id,cmd=cmd,tty=True,stdout=True,stderr=True);
		generator = Container.client.exec_start(exec_id = execid , detach = False , stream =True , tty = True);	
		return generator;
		
	def execstream(self,cmd,stdout=None,stdin=None,stderr=None):
		self.removeoldexecid();
		dockerpty.exec_command(Container.client,self.id,cmd,True,stdout,stderr,stdin);
	
	def removeoldexecid(self):
		print("called");
				
	@classmethod		 				
	def setclient(cls,cli):
		cls.client = cli;
			
#some functions raise docker.errors.APIError take them in try catch block.....
