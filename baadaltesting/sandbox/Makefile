BIN_DIR = bin
SRC_DIR = src
UTILS_DIR = utils
LOGS_DIR = logs
DISKS_DIR = disks
TEMP_DIR = temp

SHELL = bash

RUN_COMMAND = run

UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_DESKTOP = http://releases.ubuntu.com/precise/ubuntu-12.04.3-alternate-amd64.iso
UBUNTU_ALTERNATE = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-alternate-amd64.iso
UBUNTU_SERVER = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER)

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

$(UBUNTU): $(UTILS_DIR)
	wget -c $(UBUNTU_SOURCE) -O $@

$(LIBVIRT): $(UTILS_DIR)
	wget -c $(LIBVIRT_SOURCE) -O $@

controller: $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/$@ $(UBUNTU)
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/$@/*.sh > $(BIN_CONTROLLER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_CONTROLLER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_CONTROLLER)
	chmod +x $(BIN_CONTROLLER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/$@/ks.cfg $(BIN_DIR)/ks.$@.cfg

filer: $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/$@ $(UBUNTU)
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/$@/*.sh > $(BIN_FILER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_FILER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_FILER)
	chmod +x $(BIN_FILER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/$@/ks.cfg $(BIN_DIR)/ks.$@.cfg

switch: $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(SRC_DIR)/$@ $(LIBVIRT)
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/$@/*.sh > $(BIN_SWITCH)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_SWITCH)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_SWITCH)
	chmod +x $(BIN_SWITCH)
	cp $(SRC_DIR)/$@/openvswitch-switch $(BIN_DIR)/openvswitch-switch
	cp $(SRC_DIR)/$@/ovs-ifup $(BIN_DIR)/ovs-ifup
	cp $(SRC_DIR)/$@/ovs-ifdown $(BIN_DIR)/ovs-ifdown
	cp $(SRC_DIR)/$@/ovs-net.xml $(BIN_DIR)/ovs-net.xml

clean-controller:
	virsh destroy baadal_controller || true
	virsh undefine baadal_controller || true
	rm -f $(BIN_CONTROLLER)
	rm -f $(BIN_DIR)/ks.controller.cfg
	rm -f $(UTILS_DIR)/ubuntu.controller.iso
	rm -f $(DISKS_DIR)/controller.img

clean-filer:
	virsh destroy baadal_filer || true
	virsh undefine baadal_filer || true
	rm -f $(BIN_FILER)
	rm -f $(BIN_DIR)/ks.filer.cfg
	rm -f $(UTILS_DIR)/ubunt.filer.iso
	rm -f $(DISKS_DIR)/filer.img

clean-switch:

clean: clean-controller clean-filer
	rm -rf $(BIN_DIR)
	rm -rf $(LOGS_DIR)
	rm -rf $(DISKS_DIR)

cleanall: clean
	rm -rf $(UTILS_DIR)
