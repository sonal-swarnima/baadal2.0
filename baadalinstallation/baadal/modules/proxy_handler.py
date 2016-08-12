from quik import Template


class manageproxy:

	def __init__(self,filestr):
		self.filedit = filestr;

	template1 = r"""
	 upstream   @x {
		 server  @y ;
	 }

	  server {
		listen 80 ;
		gzip_types text/plain text/css application/json application/x-javascript
				   text/xml application/xml application/xml+rss text/javascript;

		server_name @x;

		location / {
			proxy_pass http://@x;
			include /etc/nginx/proxy_params;
		}
	}
	"""
	template2 = r"""
	
	upstream   @x {
		 server  @y ;
	 }

	  server {
		listen 80 ;
		gzip_types text/plain text/css application/json application/x-javascript
				   text/xml application/xml application/xml+rss text/javascript;
		 charset UTF-8;
		server_name @x;

		location / {
			proxy_pass http://@x;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;   
			 proxy_set_header X-NginX-Proxy true;    
			 proxy_set_header Host $host;   
			  proxy_set_header X-Forwarded-Proto $scheme;   
			 proxy_redirect off; 
		}
	}
	"""
	@classmethod
	def settemp(cls,newtemp):
		cls.template1 = newtemp;
	
	def render(self,dictto):
		temp = Template(manageproxy.template2)
		return temp.render(dictto)
	
	def add(self,string,hostname):
		
		self.delete(string);
		self.removebyip(hostname)			
		self.filedit += string 

	def delete(self,string):
		self.filedit = self.filedit.replace(string,"");
		
	def update(self,oldstr,newstr):
		self.filedit = self.filedit.replace(oldstr,newstr);
	
	def removebyip(self,ip):
		mystring = self.filedit;
		mylist = mystring.split("upstream   ");
		for i in range(0,len(mylist)):
			
			
			if mylist[i].find(ip) != -1:
				mylist[i]="";
		newstring ="";	
		print(mylist);	
		for i in range(0,len(mylist)):
			
			if i != len(mylist) -1:
				if mylist[i+1] != ""  :
					newstring  += mylist[i] +"upstream   ";	
				else:
					newstring  += mylist[i];	
					#print(newstring)
			else:
				newstring  += mylist[i];	
		#print(newstring);			
		self.filedit = newstring;
			
	def updatedomain(self,oldomain=None,newdomain=None,oldhost = None,newhost=None):
		mystring = self.filedit;
		mylist = mystring.split("upstream   ");
		for i in range(0,len(mylist)):
			
			mylist[i]=mylist[i].replace(oldomain,newdomain);
			if(oldhost):
				if mylist[i].find(oldhost) != -1:
					mylist[i]=mylist[i].replace(oldhost,newhost);
		newstring ="";	
		print(mylist);	
		for i in range(0,len(mylist)):
			if mylist[i] != ""  :
				if i != len(mylist) -1:
					newstring  += mylist[i] +"upstream   ";	
				else:
					newstring  += mylist[i] +"";	
		print(newstring);			
		self.filedit = newstring;

initialstring = """# If we receive X-Forwarded-Proto, pass it through; otherwise, pass along the
# scheme used to connect to this server
map $http_x_forwarded_proto $proxy_x_forwarded_proto {
  default $http_x_forwarded_proto;
  ''      $scheme;
}
# If we receive Upgrade, set Connection to "upgrade"; otherwise, delete any
# Connection header that may have been passed to this server
map $http_upgrade $proxy_connection {
  default upgrade;
  '' close;
}
gzip_types text/plain text/css application/javascript application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript;
log_format vhost '$host $remote_addr - $remote_user [$time_local] '
                 '"$request" $status $body_bytes_sent '
                 '"$http_referer" "$http_user_agent"';
access_log off;
# HTTP 1.1 support
proxy_http_version 1.1;
proxy_buffering off;
proxy_set_header Host $http_host;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $proxy_connection;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $proxy_x_forwarded_proto;
    server_names_hash_bucket_size 64;

server {
        server_name _; # This is just an invalid value which will never trigger on a real hostname.
        listen 80;
        access_log /var/log/nginx/access.log vhost;
        return 503;
}
""";
