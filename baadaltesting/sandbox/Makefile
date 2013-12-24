BIN_DIR = bin
SRC_DIR = src
UTILS_DIR = utils
LOGS_DIR = logs
DISKS_DIR = disks

SHELL = bash

RUN_COMMAND = run

UBUNTU = $(UTILS_DIR)/ubuntu.iso
UBUNTU_DESKTOP = http://releases.ubuntu.com/precise/ubuntu-12.04.3-alternate-amd64.iso
UBUNTU_ALTERNATE = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-alternate-amd64.iso
UBUNTU_SERVER = http://mirror.cse.iitd.ernet.in/cdimages/ubuntu12.04/ubuntu-12.04.1-server-amd64.iso
UBUNTU_SOURCE = $(UBUNTU_SERVER)

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

BIN_CONTROLLER = $(BIN_DIR)/controller.sh
controller: $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/$@ $(UBUNTU)
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/$@/*.sh > $(BIN_CONTROLLER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_CONTROLLER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_CONTROLLER)
	chmod +x $(BIN_CONTROLLER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/$@/ks.cfg $(BIN_DIR)/ks.$@.cfg

BIN_FILER = $(BIN_DIR)/filer.sh
filer: $(BIN_DIR) $(UTILS_DIR) $(LOGS_DIR) $(DISKS_DIR) $(SRC_DIR)/$@ $(UBUNTU)
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/$@/*.sh > $(BIN_FILER)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_FILER)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_FILER)
	chmod +x $(BIN_FILER)
	# cp $(SRC_DIR)/controller/preseed.cfg $(BIN_DIR)/preseed.cfg
	cp $(SRC_DIR)/$@/ks.cfg $(BIN_DIR)/ks.$@.cfg

clean:
	rm -rf $(BIN_DIR)
	rm -rf $(LOGS_DIR)
	rm -rf $(DISKS_DIR)

cleanall: clean
	rm -rf $(UTILS_DIR)
