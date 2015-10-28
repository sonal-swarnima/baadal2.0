#!/bin/bash

cd /home/www-data/web2py
su www-data -c "python web2py.py -K baadal:vm_task,baadal:vm_sanity,baadal:host_task,baadal:vm_rrd,baadal:snapshot_task &"

