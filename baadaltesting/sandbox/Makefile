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
BIN_SWITCH = $(BIN_DIR)/switch.sh

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

$(BIN_SWITCH): $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/switch libvirt
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/switch/*.sh > $(BIN_SWITCH)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_SWITCH)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_SWITCH)
	chmod +x $(BIN_SWITCH)
	cp $(SRC_DIR)/switch/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/switch/ovs-net.xml $(BIN_DIR)/ovs-net.xml

controller: $(BIN_CONTROLLER)
	sudo $(BIN_CONTROLLER)

filer: $(BIN_FILER)
	sudo $(BIN_FILER)

switch: $(BIN_SWITCH)
	sudo $(BIN_SWITCH)

sandbox: $(BIN_SWITCH) $(BIN_CONTROLLER) $(BIN_FILER) switch controller filer

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

clean-switch:

clean: clean-controller clean-filer
	sudo rm -rf $(BIN_DIR)
	sudo rm -rf $(LOGS_DIR)
	sudo rm -rf $(DISKS_DIR)

cleanall: clean
	sudo rm -rf $(UTILS_DIR)
