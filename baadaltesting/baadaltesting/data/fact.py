import datetime
c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=60)
print c_time
print e_time
fact=1
i=1
print datetime.datetime.now()
while(e_time>=datetime.datetime.now()):
    fact=fact*i
    i+=1
print fact
