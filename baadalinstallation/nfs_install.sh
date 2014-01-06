#!/bin/bash

# Install NFS server
apt-get install nfs-kernel-server portmap
# Add mode nfs
modprobe nfs

# create NFS base directory
mkdir /var/nfs/

# Change ownership rights
chown nobody:nogroup /var/nfs

# Configuration of exporting directory
echo -e "/var/nfs 10.0.0.0/13(rw,fsid=0,no_subtree_check,sync)" >> /etc/exports
exportfs -a

# Restart services
service nfs-kernel-server restart
service idmapd restart
