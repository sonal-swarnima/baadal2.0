BIN_DIR = bin
SRC_DIR = src
UTILS_DIR = utils
LOGS_DIR = logs
DISKS_DIR = disks
TEMP_DIR = temp

SHELL = bash

RUN_COMMAND = run

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


$(BIN_CONTROLLER): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/controller ubuntu
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/controller/*.sh > $(BIN_CONTROLLER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_CONTROLLER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_CONTROLLER)
	chmod +x $(BIN_CONTROLLER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/controller/ks.cfg $(BIN_DIR)/ks.controller.cfg

$(BIN_FILER): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/filer ubuntu
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/filer/*.sh > $(BIN_FILER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_FILER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_FILER)
	chmod +x $(BIN_FILER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/filer/ks.cfg $(BIN_DIR)/ks.filer.cfg

$(BIN_NAT): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/nat ubuntu
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/nat/*.sh > $(BIN_NAT)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_NAT)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_NAT)
	chmod +x $(BIN_NAT)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/nat/ks.cfg $(BIN_DIR)/ks.nat.cfg

$(BIN_SWITCH): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch/*.sh > $(BIN_SWITCH)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_SWITCH)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_SWITCH)
	chmod +x $(BIN_SWITCH)
	cp $(SRC_DIR)/switch/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/switch/ovs-net.xml $(BIN_DIR)/ovs-net.xml

$(BIN_SWITCH_EXTERNAL): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch-external libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch-external/*.sh > $(BIN_SWITCH_EXTERNAL)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_SWITCH_EXTERNAL)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_SWITCH_EXTERNAL)
	chmod +x $(BIN_SWITCH_EXTERNAL)
	cp $(SRC_DIR)/switch-external/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/switch-external/ovs-net-external.xml $(BIN_DIR)/ovs-net-external.xml

controller: $(BIN_CONTROLLER)
	sudo $(BIN_CONTROLLER)

filer: $(BIN_FILER)
	sudo $(BIN_FILER)

nat: $(BIN_NAT)
	sudo $(BIN_NAT)

switch: $(BIN_SWITCH)
	sudo $(BIN_SWITCH)

switch-external: $(BIN_SWITCH_EXTERNAL)
	sudo $(BIN_SWITCH_EXTERNAL)

sandbox: $(BIN_SWITCH) $(BIN_CONTROLLER) $(BIN_FILER) switch switch-external nat controller filer

clean-controller:
	sudo virsh destroy baadal_controller || true
	sudo virsh undefine baadal_controller || true
	sudo rm -f $(BIN_CONTROLLER)
	sudo rm -f $(BIN_DIR)/ks.controller.cfg
	sudo rm -f $(UTILS_DIR)/ubuntu.controller.iso
	sudo rm -f $(DISKS_DIR)/controller.img

clean-filer:
	sudo virsh destroy baadal_filer || true
	sudo virsh undefine baadal_filer || true
	sudo rm -f $(BIN_FILER)
	sudo rm -f $(BIN_DIR)/ks.filer.cfg
	sudo rm -f $(UTILS_DIR)/ubunt.filer.iso
	sudo rm -f $(DISKS_DIR)/filer.img

clean-nat:
	sudo virsh destroy baadal_nat || true
	sudo virsh undefine baadal_nat || true
	sudo rm -f $(BIN_FILER)
	sudo rm -f $(BIN_DIR)/ks.nat.cfg
	sudo rm -f $(UTILS_DIR)/ubunt.nat.iso
	sudo rm -f $(DISKS_DIR)/nat.img

clean-switch:

clean-switch-external:

clean: clean-controller clean-filer clean-nat
	sudo rm -rf $(BIN_DIR)
	sudo rm -rf $(LOGS_DIR)
	sudo rm -rf $(DISKS_DIR)

cleanall: clean
	sudo rm -rf $(UTILS_DIR)
