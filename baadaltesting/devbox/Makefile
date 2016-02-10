SRC_DIR = src
UTILS_DIR = utils

SHELL = bash
RUN_COMMAND = run

PROFILE = iitd
# Please update this ip address after migration is complete, and make
# sure it's reachable from any (all) subnets of IITD including hostels.
#PROFILE_PPA = http://10.208.20.131/openvswitch
#PROFILE_PPA = http://10.237.22.42/openvswitch
  
UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_ALTERNATE = http://repo.iitd.ac.in/ubuntu-releases/trusty/ubuntu-14.04.2-server-amd64.iso
UBUNTU_ALTERNATE_EXTERNAL = http://releases.ubuntu.com/trusty/ubuntu-14.04-alternate-amd64.iso
UBUNTU_SERVER = http://repo.iitd.ac.in/ubuntu-releases/trusty/ubuntu-14.04.2-server-amd64.iso
UBUNTU_SERVER_EXTERNAL = http://releases.ubuntu.com/trusty/ubuntu-14.04-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER)

LIBVIRT = $(UTILS_DIR)/libvirt-1.2.6.tar.gz
LIBVIRT_SOURCE = http://libvirt.org/sources/libvirt-1.2.6.tar.gz

LIBVIRTPYTHON = $(UTILS_DIR)/libvirt-python-1.2.6
LIBVIRTPYTHON_SOURCE = http://libvirt.org/sources/python/libvirt-python-1.2.6.tar.gz
LIBVIRTPYTHON_TAR=$(UTILS_DIR)/libvirt-python-1.2.6.tar.gz

VIRTMANAGER = $(UTILS_DIR)/virt-manager-0.10.0.tar.gz
VIRTMANAGER_SOURCE = https://git.fedorahosted.org/cgit/virt-manager.git/snapshot/virt-manager-0.10.0.tar.gz


$(UTILS_DIR):
	@ mkdir -p $@

$(UBUNTU):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(UBUNTU_SOURCE) -O $@ || (rm $@ && false)
  
$(LIBVIRT):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(LIBVIRT_SOURCE) -O $@ || (rm $@ && false)
  
$(LIBVIRTPYTHON_TAR):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(LIBVIRTPYTHON_SOURCE) -O $@ || (rm $@ && false)
	@ tar -xvzf $(LIBVIRTPYTHON_TAR) -C $(UTILS_DIR)/ 1>/dev/null  


$(VIRTMANAGER):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(VIRTMANAGER_SOURCE) -O $@ || (rm $@ && false)

ubuntu: $(UBUNTU)
  
libvirt: $(LIBVIRT) $(LIBVIRTPYTHON_TAR)

virtmanager: $(VIRTMANAGER)

utils: ubuntu libvirt virtmanager


# TODO
# There may be more ways of doing this.
# Is one way necessarily better than the other? Yes, obviously.
# Is this the better way? No.
openvswitch: sources-list-setup
	@ apt-get update || true
	@ apt-get -y install python-software-properties
	@ apt-get -y install openvswitch-switch

  
devbox-setup:
	@ cd $(SRC_DIR); \
	 ./devbox-setup.sh
  
sources-list-setup:
	@ sudo cp $(SRC_DIR)/sources.$(PROFILE) /etc/apt/sources.list 2>/dev/null || true

devbox: openvswitch devbox-setup
  
#clean-devbox:
