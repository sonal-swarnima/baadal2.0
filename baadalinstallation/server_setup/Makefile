BAADAL_LOCAL_DIR = ~/.baadal
BIN_DIR = $(BAADAL_LOCAL_DIR)/bin
SRC_DIR = src
UTILS_DIR = $(DIR_BAADAL_ROOT)/baadaltesting/sandbox/utils
LOGS_DIR = $(BAADAL_LOCAL_DIR)/logs
DISKS_DIR = $(BAADAL_LOCAL_DIR)/disks
TEMP_DIR = $(BAADAL_LOCAL_DIR)/temp
CONFIG_DIR = $(BAADAL_LOCAL_DIR)/config
UTILS_LOCAL_DIR = $(BAADAL_LOCAL_DIR)/utils

SHELL = bash
RUN_COMMAND = run

DIR_BAADAL_CURRENT = $(shell pwd)
DIR_BAADAL_ROOT = $(shell pwd)/../..
DIR_BAADAL_INSTALLATION = $(DIR_BAADAL_ROOT)/baadalinstallation

BAADAL_TRANSFER_TAR = $(UTILS_LOCAL_DIR)/newbaadal.tar

PROFILE = iitd
# Please update this ip address after migration is complete, and make
# sure it's reachable from any (all) subnets of IITD including mysqlels.
#PROFILE_PPA = http://10.208.20.131/openvswitch
PROFILE_PPA = http://10.237.22.42/openvswitch
  
UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_ALTERNATE = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu14.04/ubuntu-14.04-desktop-amd64.iso
UBUNTU_ALTERNATE_EXTERNAL = http://releases.ubuntu.com/trusty/ubuntu-14.04-alternate-amd64.iso
UBUNTU_SERVER = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu14.04/ubuntu-14.04-server-amd64.iso
UBUNTU_SERVER_EXTERNAL = http://releases.ubuntu.com/trusty/ubuntu-14.04-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER)

LIBVIRT = $(UTILS_DIR)/libvirt-1.2.6.tar.gz
LIBVIRT_SOURCE = http://libvirt.org/sources/libvirt-1.2.6.tar.gz

CFENGINE = $(UTILS_DIR)/cfengine-community_3.6.3-1_amd64.deb
CFENGINE_SOURCE = http://s3.amazonaws.com/cfengine.package-repos/community_binaries/cfengine-community_3.6.3-1_amd64.deb

LIBVIRTPYTHON = $(UTILS_DIR)/libvirt-python-1.2.6
LIBVIRTPYTHON_SOURCE = http://libvirt.org/sources/python/libvirt-python-1.2.6.tar.gz
LIBVIRTPYTHON_TAR=libvirt-python-1.2.6.tar.gz

VIRTMANAGER = $(UTILS_DIR)/virt-manager-0.10.0.tar.gz
VIRTMANAGER_SOURCE = https://git.fedorahosted.org/cgit/virt-manager.git/snapshot/virt-manager-0.10.0.tar.gz

BIN_CONFIGURE=$(BIN_DIR)/configure.sh

BIN_CONTROLLER = $(BIN_DIR)/controller.sh
BIN_CONTROLLER_SETUP = $(BIN_DIR)/controller-setup.sh

BIN_PXE = $(BIN_DIR)/pxe_dhcp.sh
BIN_PXE_SETUP = $(BIN_DIR)/pxe_dhcp-setup.sh

BIN_CFENGINE = $(BIN_DIR)/cfengine.sh
BIN_CFENGINE_SETUP = $(BIN_DIR)/cfengine-setup.sh

BIN_MYSQL = $(BIN_DIR)/mysql.sh
BIN_MYSQL_SETUP = $(BIN_DIR)/mysql-setup.sh

BIN_SWITCH = $(BIN_DIR)/switch.sh
BIN_SSH_AUTHORIZED_KEYS = $(BIN_DIR)/authorized_keys

CONFIGURE = $(BAADAL_LOCAL_DIR)/configure

$(BIN_DIR):
	@ mkdir -p $@

$(BAADAL_LOCAL_DIR):
	@ mkdir -p $@

$(UTILS_DIR): $(LOGS_DIR) 
	@ echo 'keerti' 
	@ mkdir -p $@

$(UTILS_LOCAL_DIR):
	@ mkdir -p $@
  
$(LOGS_DIR):
	@ echo "keerti123"
	@ mkdir -p $@
  
$(DISKS_DIR):
	@ mkdir -p $@
  
$(CONFIG_DIR):
	@ mkdir -p $@
  
directories: $(BIN_DIR) $(BAADAL_LOCAL_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(CONFIG_DIR)
  
$(UBUNTU):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(UBUNTU_SOURCE) -O $@ || (rm $@ && false)
  
$(LIBVIRT):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(LIBVIRT_SOURCE) -O $@ || (rm $@ && false)
  
$(LIBVIRTPYTHON_TAR):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(LIBVIRTPYTHON_SOURCE) -O $(UTILS_DIR)/$@ || (rm $@ && false)
	@ cd $(UTILS_DIR) ; tar -xvzf $(LIBVIRTPYTHON_TAR)  1>/dev/null  


$(VIRTMANAGER):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(VIRTMANAGER_SOURCE) -O $@ || (rm $@ && false)

$(CFENGINE):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(CFENGINE_SOURCE) -O $@ || (rm $@ && false)


ubuntu: $(UBUNTU)
  
libvirt: $(LIBVIRT) $(LIBVIRTPYTHON_TAR)

virtmanager: $(VIRTMANAGER)

cfengine: $(CFENGINE)

utils: ubuntu libvirt virtmanager cfengine

$(BAADAL_TRANSFER_TAR):
	@ mkdir -p $(UTILS_LOCAL_DIR)
	@ sudo umount $(UTILS_DIR)/iso 1>/dev/null 2>/dev/null || true
	@ sudo rm -rf $(UTILS_DIR)/iso 1>/dev/null 2>/dev/null || true
	@ sudo rm -rf $(UTILS_DIR)/ubuntuiso 1>/dev/null 2>/dev/null || true
	@ ln -s $(DIR_BAADAL_ROOT) $(BIN_DIR)/baadal || true
	cd $(BIN_DIR) ;	tar -chvf $@ baadal 1>/dev/null
	@ rm $(BIN_DIR)/baadal

baadal-transfer-tar: $(BAADAL_TRANSFER_TAR)

$(CONFIGURE):
	@ mkdir -p $@

# TODO
# There may be more ways of doing this.
# Is one way necessarily better than the other? Yes, obviously.
# Is this the better way? No.
openvswitch: sources-list-setup
	apt-get update || true
	apt-get -y install python-software-properties
	apt-get -y install openvswitch-switch
	apt-get -y install openvswitch-common=2.0.2-0ubuntu0.14.04.1
	apt-get -y install openvswitch-pki=2.0.2-0ubuntu0.14.04.1
	apt-get -y install openvswitch-controller=2.0.2-0ubuntu0.14.04.1
	apt-get -y install openvswitch-datapath-dkms=2.0.2-0ubuntu0.14.04.1
	apt-get -y install openvswitch-switch=2.0.2-0ubuntu0.14.04.1
	apt-get -y install python-openvswitch=2.0.2-0ubuntu0.14.04.1

$(BIN_CONFIGURE): $(BIN_DIR) $(LOGS_DIR) $(UTILS_LOCAL_DIR) $(SRC_DIR)/configure/*
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/configure/*.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
  
$(BIN_CONTROLLER): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/controller ubuntu controller-transfer
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/controller/*.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/controller/ks.cfg $(BIN_DIR)/ks.controller.cfg
  
$(BIN_PXE): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(DISKS_DIR) $(SRC_DIR)/pxe_dhcp ubuntu pxe_dhcp-transfer
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/pxe_dhcp/*.sh > $@	
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/pxe_dhcp/ks.cfg $(BIN_DIR)/ks.pxe_dhcp.cfg
  
$(BIN_CFENGINE): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/cfengine ubuntu cfengine-transfer
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/cfengine/install.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/cfengine/ks.cfg $(BIN_DIR)/ks.cfengine.cfg
  
$(BIN_MYSQL): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/mysql ubuntu mysql-transfer 
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/mysql/install.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/mysql/ks.cfg $(BIN_DIR)/ks.mysql.cfg
  
$(BIN_SWITCH): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch libvirt
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch/*.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/switch/ovs-net-internal.xml $(BIN_DIR)/ovs-net-internal.xml
	@ cp $(SRC_DIR)/switch/ovs-net-external.xml $(BIN_DIR)/ovs-net-external.xml
  
controller: $(BIN_CONTROLLER)
	@ sudo $<

controller-setup: $(BIN_CONTROLLER_SETUP)
	@ sudo DNS=$$DNS CONTROLLER_INTERFACE=$$INTERFACE $<
  
pxe_dhcp: $(BIN_PXE)
	@ sudo $<

pxe_dhcp-setup: $(BIN_PXE_SETUP)
	@ sudo apt-get install nfs-kernel-server
	@ sudo $<
  
cfengine: $(BIN_CFENGINE)
	@ sudo $<

cfengine-setup: $(BIN_CFENGINE_SETUP)
	@ sudo $<

mysql: $(BIN_MYSQL)
	sudo $<

mysql-setup: $(BIN_MYSQL_SETUP)
	@ sudo $<
  
switch: $(BIN_SWITCH)
	@ sudo VIRTMANAGER_INSTALL=$$VIRTMANAGER_INSTALL LIBVIRT_INSTALL=$$LIBVIRT_INSTALL INTERFACE=$$INTERFACE DNS=$$DNS $<
  
cfengine-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/cfengine/transfer $(BIN_DIR)/transfer.cfengine
	@ mkdir -p $(BIN_DIR)/transfer.cfengine/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.cfengine/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.cfengine $(BIN_DIR)/transfer.cfengine/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.cfengine.pub $(BIN_DIR)/transfer.cfengine/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.cfengine/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.cfengine/baadal/newbaadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.cfengine/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.cfengine/root/.baadal

mysql-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/mysql/transfer $(BIN_DIR)/transfer.mysql
	@ mkdir -p $(BIN_DIR)/transfer.mysql/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.mysql/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.mysql $(BIN_DIR)/transfer.mysql/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.mysql.pub $(BIN_DIR)/transfer.mysql/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.mysql/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.mysql/baadal/newbaadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.mysql/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.mysql/root/.baadal


controller-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/controller/transfer $(BIN_DIR)/transfer.controller
	@ mkdir -p $(BIN_DIR)/transfer.controller/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.controller/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.controller $(BIN_DIR)/transfer.controller/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.controller.pub $(BIN_DIR)/transfer.controller/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.controller/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.controller/baadal/newbaadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.controller/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.controller/root/.baadal

#changed by keerti
pxe_dhcp-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/pxe_dhcp/transfer $(BIN_DIR)/transfer.pxe_dhcp
	@ mkdir -p $(BIN_DIR)/transfer.pxe_dhcp/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.pxe_dhcp/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.pxe_dhcp $(BIN_DIR)/transfer.pxe_dhcp/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.pxe_dhcp.pub $(BIN_DIR)/transfer.pxe_dhcp/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.pxe_dhcp/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.pxe_dhcp/baadal/newbaadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.pxe_dhcp/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.pxe_dhcp/root/.baadal

$(BIN_CONTROLLER_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/controller $(SRC_DIR)/controller/*
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/controller/controller-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_CFENGINE_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/cfengine $(SRC_DIR)/cfengine/*
	@ mkdir -p $(BIN_DIR)/transfer.cfengine/baadal
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/cfengine/cfengine-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_MYSQL_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/mysql $(SRC_DIR)/mysql/*
	@ mkdir -p $(BIN_DIR)/transfer.mysql/baadal
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/mysql/mysql-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_PXE_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/pxe_dhcp $(SRC_DIR)/pxe_dhcp/*
	@ mkdir -p $(BIN_DIR)/transfer.pxe_dhcp/baadal
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/pxe_dhcp/pxe_dhcp-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

sources-list-setup:
	@ sudo cp $(SRC_DIR)/sources.$(PROFILE) /etc/apt/sources.list 2>/dev/null || true

sandbox: switch controller pxe_dhcp cfengine mysql

configure: $(BIN_CONFIGURE)
	@ $(BIN_CONFIGURE)
  
$(BIN_DIR)/id_rsa.sandbox.pub: ~/.ssh/id_rsa
	@ cp $<.pub $@
	@ cat $<.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.controller:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-controller'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.pxe_dhcp:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-pxe-dhcp'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.cfengine:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-cfengine'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)

$(BIN_DIR)/id_rsa.mysql:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-mysql'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
~/.ssh/id_rsa:
	@ ssh-keygen -q -f $@ -N ''
  
keygen-ssh-sandbox: $(BIN_DIR)/id_rsa.sandbox.pub
  
keygen-ssh-controller: $(BIN_DIR)/id_rsa.controller
  
keygen-ssh-pxe_dhcp: $(BIN_DIR)/id_rsa.pxe_dhcp
  
keygen-ssh-cfengine: $(BIN_DIR)/id_rsa.cfengine

keygen-ssh-mysql: $(BIN_DIR)/id_rsa.mysql
  
keygen-ssh-all: keygen-ssh-sandbox keygen-ssh-controller keygen-ssh-pxe_dhcp keygen-ssh-cfengine keygen-ssh-mysql

  
clean-config:
	rm -rf $(CONFIGURE)
  
clean-controller:
	sudo virsh destroy baadal_controller || true
	sudo virsh undefine baadal_controller || true
	sudo rm -f $(BIN_CONTROLLER)
	sudo rm -f $(BIN_DIR)/ks.controller.cfg
	sudo rm -rf $(BIN_DIR)/transfer.controller
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.controller.iso
	sudo rm -f $(DISKS_DIR)/controller.img
  
clean-pxe_dhcp:
	sudo virsh destroy baadal_pxe_dhcp || true
	sudo virsh undefine baadal_pxe_dhcp || true
	sudo rm -f $(BIN_PXE)
	sudo rm -f $(BIN_DIR)/ks.pxe_dhcp.cfg
	sudo rm -rf $(BIN_DIR)/transfer.pxe_dhcp
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.pxe_dhcp.iso
	sudo rm -f $(DISKS_DIR)/pxe_dhcp.img
  
clean-cfengine:
	sudo virsh destroy baadal_cfengine || true
	sudo virsh undefine baadal_cfengine || true
	sudo rm -f $(BIN_CFENGINE)
	sudo rm -f $(BIN_DIR)/ks.cfengine.cfg
	sudo rm -rf $(BIN_DIR)/transfer.cfengine
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.cfengine.iso
	sudo rm -f $(DISKS_DIR)/cfengine.img
  
clean-mysql:
	sudo virsh destroy baadal_mysql || true
	sudo virsh undefine baadal_mysql || true
	sudo rm -f $(BIN_MYSQL)
	sudo rm -f $(DISKS_DIR)/mysql.img
	sudo rm -rf $(BIN_DIR)/transfer.mysql
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.mysql.iso
	sudo rm -f $(DISKS_DIR)/mysql.img

clean-transfer-tar:
	sudo rm -f $(BAADAL_TRANSFER_TAR)

clean-setup: clean-config clean-controller clean-pxe_dhcp clean-cfengine clean-mysql clean-transfer-tar
	sudo umount $(UTILS_DIR)/iso || true
	sudo rm -rf $(UTILS_DIR)/iso
	sudo rm -rf $(UTILS_DIR)/ubuntuiso
	sudo rm -rf $(BIN_DIR)
	sudo rm -rf $(LOGS_DIR)
	sudo rm -rf $(DISKS_DIR)
  
clean-all: clean clean-config
	sudo rm -rf $(UTILS_DIR)
