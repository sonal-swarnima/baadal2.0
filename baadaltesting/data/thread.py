from multiprocessing import Pool
import datetime

c_time=datetime.datetime.now()
e_time=c_time + datetime.timedelta(seconds=600)
def f(x):
    # Put any cpu (only) consuming operation here. 
    while e_time>=datetime.datetime.now():
        x * x

# decide how many cpus you need to load with.
no_of_cpu_to_be_consumed = 6

p = Pool(processes=no_of_cpu_to_be_consumed)
p.map(f, range(no_of_cpu_to_be_consumed))


