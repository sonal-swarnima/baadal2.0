BAADAL_LOCAL_DIR = ~/.baadal
BIN_DIR = $(BAADAL_LOCAL_DIR)/bin
SRC_DIR = src
UTILS_DIR = utils
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

BAADAL_TRANSFER_TAR = $(UTILS_LOCAL_DIR)/baadal.tar

PROFILE = iitd
# Please update this ip address after migration is complete, and make
# sure it's reachable from any (all) subnets of IITD including hostels.
PROFILE_PPA = http://10.237.20.240/openvswitch
  
HOST_ID = 1
  
UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_ALTERNATE = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-alternate-amd64.iso
UBUNTU_ALTERNATE_EXTERNAL = http://releases.ubuntu.com/precise/ubuntu-12.04.3-alternate-amd64.iso
UBUNTU_SERVER = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-server-amd64.iso
UBUNTU_SERVER_EXTERNAL = http://releases.ubuntu.com/precise/ubuntu-12.04.3-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER)

LIBVIRT = $(UTILS_DIR)/libvirt-1.2.1.tar.gz
LIBVIRT_SOURCE = http://libvirt.org/sources/libvirt-1.2.1.tar.gz
LIBVIRTPYTHON = $(UTILS_DIR)/libvirt-python
LIBVIRTPYTHON_SOURCE = https://github.com/utkarshsins/baadal-libvirt-python.git

VIRTMANAGER = $(UTILS_DIR)/virt-manager-0.10.0.tar.gz
VIRTMANAGER_SOURCE = https://git.fedorahosted.org/cgit/virt-manager.git/snapshot/virt-manager-0.10.0.tar.gz

BIN_CONFIGURE=$(BIN_DIR)/configure.sh
BIN_CONTROLLER = $(BIN_DIR)/controller.sh
BIN_CONTROLLER_SETUP = $(BIN_DIR)/controller-setup.sh
BIN_FILER = $(BIN_DIR)/filer.sh
BIN_FILER_SETUP = $(BIN_DIR)/filer-setup.sh
BIN_NAT = $(BIN_DIR)/nat.sh
BIN_NAT_SETUP = $(BIN_DIR)/nat-setup.sh
BIN_HOST = $(BIN_DIR)/host.$(HOST_ID).sh
BIN_HOST_SETUP = $(BIN_DIR)/host-setup.sh
BIN_SWITCH = $(BIN_DIR)/switch.sh
BIN_SSH_AUTHORIZED_KEYS = $(BIN_DIR)/authorized_keys

CONFIGURE = $(BAADAL_LOCAL_DIR)/configure

$(BIN_DIR):
	@ mkdir -p $@

$(BAADAL_LOCAL_DIR):
	@ mkdir -p $@

$(UTILS_DIR):
	@ mkdir -p $@

$(UTILS_LOCAL_DIR):
	@ mkdir -p $@
  
$(LOGS_DIR):
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
  
$(LIBVIRTPYTHON):
	@ mkdir -p $(UTILS_DIR)
	@ git clone $(LIBVIRTPYTHON_SOURCE) $@ || (rm $@ && false)

$(VIRTMANAGER):
	@ mkdir -p $(UTILS_DIR)
	@ wget -c $(VIRTMANAGER_SOURCE) -O $@ || (rm $@ && false)

ubuntu: $(UBUNTU)
  
libvirt: $(LIBVIRT) $(LIBVIRTPYTHON)

virtmanager: $(VIRTMANAGER)

utils: ubuntu libvirt virtmanager

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
	if [[ "$(PROFILE)" == "iitd" ]]; then \
		add-apt-repository -y 'deb [arch=amd64] $(PROFILE_PPA) precise main';\
		wget $(PROFILE_PPA)/key.gpg; \
		cat key.gpg | apt-key add - ;\
		rm key.gpg ;\
		else \
			add-apt-repository -y ppa:ivoks/ovs-saucy ;\
		fi
	apt-get update || true
	apt-get -y install openvswitch-common=1.10.2-0ubuntu2~cloud0
	apt-get -y install openvswitch-pki=1.10.2-0ubuntu2~cloud0
	apt-get -y install openvswitch-controller=1.10.2-0ubuntu2~cloud0
	apt-get -y install openvswitch-datapath-dkms=1.10.2-0ubuntu2~cloud0
	apt-get -y install openvswitch-switch=1.10.2-0ubuntu2~cloud0
	apt-get -y install python-openvswitch=1.10.2-0ubuntu2~cloud0

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
  
$(BIN_FILER): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/filer ubuntu filer-transfer
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/filer/*.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/filer/ks.cfg $(BIN_DIR)/ks.filer.cfg
  
$(BIN_NAT): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/nat ubuntu nat-transfer
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/nat/install.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
	@ cp $(SRC_DIR)/nat/ks.cfg $(BIN_DIR)/ks.nat.cfg
  
$(BIN_HOST): $(BIN_DIR) $(UTILS_LOCAL_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/host ubuntu keygen-ssh-all
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/host/*.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@
  
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
  
filer: $(BIN_FILER)
	@ sudo $<

filer-setup: $(BIN_FILER_SETUP)
	@ sudo apt-get install nfs-kernel-server
	@ sudo $<
  
nat: $(BIN_NAT)
	@ sudo $<

nat-setup: $(BIN_NAT_SETUP)
	@ sudo $<

host: $(BIN_HOST)
	sudo HOST_ID=$(HOST_ID) $<

host-setup: $(BIN_HOST_SETUP)
	@ sudo HOST_INTERFACE=$$INTERFACE $<
  
switch: $(BIN_SWITCH)
	@ sudo VIRTMANAGER_INSTALL=$$VIRTMANAGER_INSTALL LIBVIRT_INSTALL=$$LIBVIRT_INSTALL INTERFACE=$$INTERFACE DNS=$$DNS $<
  
nat-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/nat/transfer $(BIN_DIR)/transfer.nat
	@ mkdir -p $(BIN_DIR)/transfer.nat/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.nat/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.nat $(BIN_DIR)/transfer.nat/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.nat.pub $(BIN_DIR)/transfer.nat/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.nat/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.nat/baadal/baadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.nat/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.nat/root/.baadal

controller-transfer: $(BAADAL_TRANSFER_TAR) $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/controller/transfer $(BIN_DIR)/transfer.controller
	@ mkdir -p $(BIN_DIR)/transfer.controller/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.controller/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.controller $(BIN_DIR)/transfer.controller/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.controller.pub $(BIN_DIR)/transfer.controller/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.controller/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.controller/baadal/baadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.controller/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.controller/root/.baadal

filer-transfer: $(CONFIG_DIR) keygen-ssh-all
	@ cp -R $(SRC_DIR)/filer/transfer $(BIN_DIR)/transfer.filer
	@ mkdir -p $(BIN_DIR)/transfer.filer/root/.ssh
	@ cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.filer/root/.ssh
	@ cp $(BIN_DIR)/id_rsa.filer $(BIN_DIR)/transfer.filer/root/.ssh/id_rsa
	@ cp $(BIN_DIR)/id_rsa.filer.pub $(BIN_DIR)/transfer.filer/root/.ssh/id_rsa.pub
	@ mkdir -p $(BIN_DIR)/transfer.filer/baadal
	@ cp $(BAADAL_TRANSFER_TAR) $(BIN_DIR)/transfer.filer/baadal/baadal.tar
	@ mkdir -p $(BIN_DIR)/transfer.filer/root/.baadal
	@ cp -R $(CONFIG_DIR) $(BIN_DIR)/transfer.filer/root/.baadal

$(BIN_CONTROLLER_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/controller $(SRC_DIR)/controller/*
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/controller/controller-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_NAT_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/nat $(SRC_DIR)/nat/*
	@ mkdir -p $(BIN_DIR)/transfer.nat/baadal
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/nat/nat-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_HOST_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/host $(SRC_DIR)/host/*
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/host/host-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

$(BIN_FILER_SETUP): $(BIN_DIR) $(LOGS_DIR) $(SRC_DIR)/filer $(SRC_DIR)/filer/*
	@ mkdir -p $(BIN_DIR)/transfer.filer/baadal
	@ cat $(SRC_DIR)/*.sh $(SRC_DIR)/filer/filer-setup.sh > $@
	@ sed -i '1i#!/bin/$(SHELL)' $@
	@ sed -i '$$a$(RUN_COMMAND)' $@
	@ chmod +x $@

sources-list-setup:
	@ sudo cp $(SRC_DIR)/common/sources.$(PROFILE) /etc/apt/sources.list 2>/dev/null || true

sandbox: switch nat controller filer

configure: $(BIN_CONFIGURE)
	@ $(BIN_CONFIGURE)
  
$(BIN_DIR)/id_rsa.sandbox.pub: ~/.ssh/id_rsa
	@ cp $<.pub $@
	@ cat $<.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.controller:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-controller'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.filer:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-filer'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
$(BIN_DIR)/id_rsa.nat:
	@ ssh-keygen -q -f $@ -N '' -C 'baadal-nat'
	@ cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)
  
~/.ssh/id_rsa:
	@ ssh-keygen -q -f $@ -N ''
  
keygen-ssh-sandbox: $(BIN_DIR)/id_rsa.sandbox.pub
  
keygen-ssh-controller: $(BIN_DIR)/id_rsa.controller
  
keygen-ssh-filer: $(BIN_DIR)/id_rsa.filer
  
keygen-ssh-nat: $(BIN_DIR)/id_rsa.nat
  
keygen-ssh-all: keygen-ssh-sandbox keygen-ssh-controller keygen-ssh-filer keygen-ssh-nat
  
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
  
clean-filer:
	sudo virsh destroy baadal_filer || true
	sudo virsh undefine baadal_filer || true
	sudo rm -f $(BIN_FILER)
	sudo rm -f $(BIN_DIR)/ks.filer.cfg
	sudo rm -rf $(BIN_DIR)/transfer.filer
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.filer.iso
	sudo rm -f $(DISKS_DIR)/filer.img
  
clean-nat:
	sudo virsh destroy baadal_nat || true
	sudo virsh undefine baadal_nat || true
	sudo rm -f $(BIN_NAT)
	sudo rm -f $(BIN_DIR)/ks.nat.cfg
	sudo rm -rf $(BIN_DIR)/transfer.nat
	sudo rm -f $(UTILS_LOCAL_DIR)/ubuntu.nat.iso
	sudo rm -f $(DISKS_DIR)/nat.img
  
clean-host:
	sudo virsh destroy baadal_host_$(HOST_ID) || true
	sudo virsh undefine baadal_host_$(HOST_ID) || true
	sudo rm -f $(BIN_HOST)
	sudo rm -f $(DISKS_DIR)/host.$(HOST_ID).img

clean-transfer-tar:
	sudo rm -f $(BAADAL_TRANSFER_TAR)

clean: clean-config clean-controller clean-filer clean-nat clean-transfer-tar
	sudo umount $(UTILS_DIR)/iso || true
	sudo rm -rf $(UTILS_DIR)/iso
	sudo rm -rf $(UTILS_DIR)/ubuntuiso
	sudo rm -rf $(BIN_DIR)
	sudo rm -rf $(LOGS_DIR)
	sudo rm -rf $(DISKS_DIR)
  
clean-all: clean clean-config
	sudo rm -rf $(UTILS_DIR)
