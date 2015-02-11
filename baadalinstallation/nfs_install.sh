#!/bin/bash

# Install NFS server
apt-get -y install nfs-kernel-server portmap
# Add mode nfs
modprobe nfs

# create NFS base directory
mkdir /var/nfs/

# Change ownership rights
chown nobody:nogroup /var/nfs

# Configuration of exporting directory
echo -e "/var/nfs 10.0.0.0/13(rw,no_subtree_check,sync,no_root_squash)" >> /etc/exports
exportfs -a

# Restart services
service nfs-kernel-server restart
service idmapd restart
