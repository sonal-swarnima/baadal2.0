import os
import datetime
c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=850)
i=1
fact=1
print datetime.datetime.now()
while(e_time>=datetime.datetime.now()):
    #os.system("sysbench --test=mutex --memory-total-size=1G --memory-oper=read run ")
   # os.system("sysbench --test=mutex --memory-total-size=1G --memory-oper=read cleanup ")
   some_str = ' ' * 512000000


