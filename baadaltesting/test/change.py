import sys
import shutil
import os

current_dir=os.getcwd()
print current_dir
db_conf_path=str(current_dir) + '/db.conf'
print db_conf_path
temp_conf_path= str(current_dir) + '/temp.conf'
print current_dir
fh = open(db_conf_path,"r+")

f = open(temp_conf_path,"w+")
line=fh.readlines()
IP_ADDR=str(sys.argv[1])
data="host_ip:" + str(IP_ADDR)
for row in line:

   if "host_ip" in row:
	f.write(data)
	f.write("\n")
   else:
	f.write(row)
f.close()
fh.close()  

shutil.move(db_conf_path, temp_conf_path)
