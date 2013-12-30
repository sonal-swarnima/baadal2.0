BIN_DIR = bin
SRC_DIR = src
UTILS_DIR = utils
LOGS_DIR = logs
DISKS_DIR = disks
TEMP_DIR = temp
CONFIG_DIR = config.ln

SHELL = bash

RUN_COMMAND = run

DIR_BAADAL_INSTALLATION = ../../baadalinstallation

UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_ALTERNATE = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-alternate-amd64.iso
UBUNTU_ALTERNATE_EXTERNAL = http://releases.ubuntu.com/precise/ubuntu-12.04.3-alternate-amd64.iso
UBUNTU_SERVER = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-server-amd64.iso
UBUNTU_SERVER_EXTERNAL = http://releases.ubuntu.com/precise/ubuntu-12.04.3-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER_EXTERNAL)

LIBVIRT = $(UTILS_DIR)/libvirt-1.0.0.tar.gz
LIBVIRT_SOURCE = http://libvirt.org/sources/libvirt-1.0.0.tar.gz

BIN_CONTROLLER = $(BIN_DIR)/controller.sh
BIN_FILER = $(BIN_DIR)/filer.sh
BIN_NAT = $(BIN_DIR)/nat.sh
BIN_SWITCH = $(BIN_DIR)/switch.sh
BIN_SWITCH_EXTERNAL = $(BIN_DIR)/switch_external.sh
BIN_NET_EXTERNAL = $(BIN_DIR)/net_external.sh
BIN_NET_FIX = $(BIN_DIR)/fix_net.sh
BIN_SSH_AUTHORIZED_KEYS = $(BIN_DIR)/authorized_keys

IP_NAT = 10.209.0.1
IP_CONTROLLER = 10.209.0.2
IP_FILER = 10.209.0.3
IP_SANDBOX = 10.209.0.4

$(BIN_DIR):
	mkdir -p $@

$(UTILS_DIR):
	mkdir -p $@

$(LOGS_DIR):
	mkdir -p $@

$(DISKS_DIR):
	mkdir -p $@

$(DIRECTORIES): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR)

$(UBUNTU):
	mkdir -p $(UTILS_DIR)
	wget -c $(UBUNTU_SOURCE) -O $@

$(LIBVIRT):
	mkdir -p $(UTILS_DIR)
	wget -c $(LIBVIRT_SOURCE) -O $@

ubuntu: $(UBUNTU)

libvirt: $(LIBVIRT)


$(BIN_CONTROLLER): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/controller ubuntu keygen-ssh-all
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/controller/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/controller/ks.cfg $(BIN_DIR)/ks.controller.cfg
	cp -R $(SRC_DIR)/controller/transfer $(BIN_DIR)/transfer.controller
	mkdir -p $(BIN_DIR)/transfer.controller/root/.ssh
	cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.controller/root/.ssh
	cp -R $(DIR_BAADAL_INSTALLATION) $(BIN_DIR)/transfer.controller/baadal

$(BIN_FILER): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/filer ubuntu keygen-ssh-all
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/filer/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/filer/ks.cfg $(BIN_DIR)/ks.filer.cfg
	cp -R $(SRC_DIR)/filer/transfer $(BIN_DIR)/transfer.filer
	mkdir -p $(BIN_DIR)/transfer.filer/root/.ssh
	cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.filer/root/.ssh

$(BIN_NAT): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/nat ubuntu keygen-ssh-all
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/nat/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/nat/ks.cfg $(BIN_DIR)/ks.nat.cfg
	cp -R $(SRC_DIR)/nat/transfer $(BIN_DIR)/transfer.nat
	mkdir -p $(BIN_DIR)/transfer.nat/root/.ssh
	cp $(BIN_SSH_AUTHORIZED_KEYS) $(BIN_DIR)/transfer.nat/root/.ssh

$(BIN_SWITCH): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@
	cp $(SRC_DIR)/switch/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/switch/ovs-net.xml $(BIN_DIR)/ovs-net.xml

$(BIN_SWITCH_EXTERNAL): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch-external libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch-external/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@
	cp $(SRC_DIR)/switch-external/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/switch-external/ovs-net-external.xml $(BIN_DIR)/ovs-net-external.xml

$(BIN_NET_EXTERNAL): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/net-external libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/net-external/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@

$(BIN_NET_FIX): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/net-fix
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/net-fix/*.sh > $@
	sed -i '1i#!/bin/$(SHELL)' $@
	sed -i '$$a$(RUN_COMMAND)' $@
	chmod +x $@

controller: $(BIN_CONTROLLER)
	sudo $<

filer: $(BIN_FILER)
	sudo $<

nat: $(BIN_NAT)
	sudo $<

switch: $(BIN_SWITCH)
	sudo $<

switch-external: $(BIN_SWITCH_EXTERNAL)
	sudo $<

net-external: $(BIN_NET_EXTERNAL)
	sudo $<

fix-net: $(BIN_NET_FIX)
	sudo $<

sandbox: switch switch-external nat controller filer

config: clean-config
	mkdir -p $(CONFIG_DIR)
	ln -s ../$(SRC_DIR)/constants.sh $(CONFIG_DIR)/constants.sh
	ln -s ../$(SRC_DIR)/controller/ks.cfg $(CONFIG_DIR)/controller.ks.cfg
	ln -s ../$(SRC_DIR)/filer/ks.cfg $(CONFIG_DIR)/filer.ks.cfg
	ln -s ../$(SRC_DIR)/nat/ks.cfg $(CONFIG_DIR)/nat.ks.cfg
	ln -s ../$(SRC_DIR)/switch/ovs-net.xml $(CONFIG_DIR)/ovs-net.xml
	ln -s ../$(SRC_DIR)/switch-external/ovs-net-external.xml $(CONFIG_DIR)/ovs-net-external.xml
	ln -s ../$(SRC_DIR)/nat/transfer/etc/iptables.conf $(CONFIG_DIR)/nat.iptables.conf
	ln -s ../$(SRC_DIR)/nat/transfer/etc/network/interfaces $(CONFIG_DIR)/nat.interfaces

$(BIN_DIR)/id_rsa.sandbox.pub: ~/.ssh/id_rsa
	cp $<.pub $@
	cat $<.pub >> $(BIN_SSH_AUTHORIZED_KEYS)

$(BIN_DIR)/id_rsa.controller:
	ssh-keygen -q -f $@ -N '' -C 'baadal-controller'
	cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)

$(BIN_DIR)/id_rsa.filer:
	ssh-keygen -q -f $@ -N '' -C 'baadal-filer'
	cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)

$(BIN_DIR)/id_rsa.nat:
	ssh-keygen -q -f $@ -N '' -C 'baadal-nat'
	cat $@.pub >> $(BIN_SSH_AUTHORIZED_KEYS)

~/.ssh/id_rsa:
	ssh-keygen -q -f $@ -N ''

keygen-ssh-sandbox: $(BIN_DIR)/id_rsa.sandbox.pub

keygen-ssh-controller: $(BIN_DIR)/id_rsa.controller

keygen-ssh-filer: $(BIN_DIR)/id_rsa.filer

keygen-ssh-nat: $(BIN_DIR)/id_rsa.nat

keygen-ssh-all: keygen-ssh-sandbox keygen-ssh-controller keygen-ssh-filer keygen-ssh-nat

ssh-nat:
	ssh baadal@$(IP_NAT)

ssh-conroller:
	ssh baadal@$(IP_CONTROLLER)

ssh-filer:
	ssh baadal@$(IP_FILER)

clean-config:
	rm -rf $(CONFIG_DIR)

clean-controller:
	sudo virsh destroy baadal_controller || true
	sudo virsh undefine baadal_controller || true
	sudo rm -f $(BIN_CONTROLLER)
	sudo rm -f $(BIN_DIR)/ks.controller.cfg
	sudo rm -rf $(BIN_DIR)/transfer.controller
	sudo rm -f $(UTILS_DIR)/ubuntu.controller.iso
	sudo rm -f $(DISKS_DIR)/controller.img

clean-filer:
	sudo virsh destroy baadal_filer || true
	sudo virsh undefine baadal_filer || true
	sudo rm -f $(BIN_FILER)
	sudo rm -f $(BIN_DIR)/ks.filer.cfg
	sudo rm -rf $(BIN_DIR)/transfer.filer
	sudo rm -f $(UTILS_DIR)/ubunt.filer.iso
	sudo rm -f $(DISKS_DIR)/filer.img

clean-nat:
	sudo virsh destroy baadal_nat || true
	sudo virsh undefine baadal_nat || true
	sudo rm -f $(BIN_NAT)
	sudo rm -f $(BIN_DIR)/ks.nat.cfg
	sudo rm -rf $(BIN_DIR)/transfer.nat
	sudo rm -f $(UTILS_DIR)/ubunt.nat.iso
	sudo rm -f $(DISKS_DIR)/nat.img

clean-switch:

clean-switch-external:

clean: clean-controller clean-filer clean-nat
	sudo umount $(UTILS_DIR)/iso || true
	sudo rm -rf $(UTILS_DIR)/iso
	sudo rm -rf $(UTILS_DIR)/ubuntuiso
	sudo rm -rf $(BIN_DIR)
	sudo rm -rf $(LOGS_DIR)
	sudo rm -rf $(DISKS_DIR)

cleanall: clean clean-config
	sudo rm -rf $(UTILS_DIR)
