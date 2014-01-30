function run
{
  check_root
  
  hostname="$(uname -n)"
  if [ "$hostname" != "$FILER_HOSTNAME" ]
  then
    $ECHO_ER Hostname not found equal to $FILER_HOSTNAME. This script should be run on FILER.
    $ECHO_ER Please correct the hostname or check the underlying system before running.
    exit 1
  fi

  # Install NFS server
  package_install nfs-kernel-server
  package_install portmap
  
  # Add mode nfs
  kernelmod_modprobe nfs
  
  # create NFS directories
  mkdir /var/nfs/
  mkdir /var/nfs/vm_images/
  mkdir /var/nfs/vm_templates/
  mkdir /var/nfs/vm_deleted/
  mkdir /var/nfs/vm_rrds/
  mkdir /var/nfs/vm_extra_disks/

  # Change ownership rights
  chown nobody:nogroup -R /var/nfs/

  # Configuration of exporting directory
  echo -e "/var/nfs/ $NETWORK_INTERNAL_IP_FILER/$NETWORK_BITS(rw,no_subtree_check,sync,no_root_squash)" >> /etc/exports
  exportfs -a

  # Restart services
  service_restart nfs-kernel-server
  service_restart idmapd
}
