import sys,time,commands,traceback

task_type = {'install' : install

}

counter = 0
while True:
    db.commit()
    try:
        processes = db(db.task_queue.status == 0).select()
        print "No. of processes in queue: " + str(len(processes))

        if (len(processes) >= 1):

            try:
                print "Current date and time: " + str(commands.getstatusoutput('date')[1])
                process = processes[0]
                db(db.task_queue_event.task_id == process['id'].update(attention_time = putdate())   
                print "Starting to execute " + str(process)
                task[process['task_type']](process['id'],process['vm_id'])
                db.commit()
                print "Task done"

            except Exception as e:
                print "Exception thrown: " + str(e)
                etype, value, tb = sys.exc_info()
                msg = ''.join(traceback.format_exception(etype,value,tb,10))
                db(db.task_queue_event.task_id == process['id']).update(status = -1, error = msg, end_time = putdate())
                db(db.task_queue.id == process['id']).update(status = -1)

        else:

            if (counter % 12 == 0):
                print "Current date and time: " + str(commands.getstatusoutput('date')[1])
                print "Syncing vm runlevels and their actual state..."
                allvms = db(db.vm_data.vm_id >= 0).select(db.vm_data.vm_name, db.vm_data.current_run_level)
                for vm in allvms:
                    print "Working on " + vm.vm_name
                    try:
                        runlevel = get_actual_vm_level(vm.vm_name)
                    except Exception as e:
                        print "Exception thrown: " + str(e)
                        etype, value, tb = sys.exc_info()
                        msg = ''.join(traceback.format_exception(etype,value,tb,10))
                        print "Error message: " + str(msg)

                        if(vm.current_run_level != runlevel):
                            print "Updating runlevel of " + vm.vm_name + "to" + str(level)
                            db(db.vm_data.vm_name).update(current_run_level = runlevel)
        
          
            counter = counter + 1
            print "Taking a break"
            time.sleep(10)
    except:
        
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype,value,tb,10))
        print "Error message: " + str(msg)
        time.sleep(10)










                

            
  
            
                
                
