function run
{
  check_root
  package_update_db
  package_install qemu-kvm
  package_install libvirt-bin
  package_install ubuntu-vm-builder
}

