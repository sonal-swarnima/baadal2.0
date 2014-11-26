#!/bin/sh
sudo apt-get update  # To get the latest package lists
sudo apt-get install -y python-pip
sudo apt-get install -y python-MySQLdb
sudo pip install selenium  
sudo apt-get install -y python-paramiko
sudo apt-get install -y xvfb
sudo pip install netperf
sudo apt-get install sysbench
sudo apt-get install -y xserver-xephyr
sudo apt-get install -y tightvncserver
sudo pip install pyvirtualdisplay


