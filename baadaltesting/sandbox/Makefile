BIN_DIR = bin
SRC_DIR = src
BIN_BASE = $(BIN_DIR)/base.sh

SHELL = bash

RUN_COMMAND = run

bin:
	mkdir -p $(BIN_DIR)

base: bin $(SRC_DIR)/base
	cat $(SRC_DIR)/*.sh $(SRC_DIR)/base/*.sh > $(BIN_BASE)
	sed -i '1i#!/bin/$(SHELL)' $(BIN_BASE)
	sed -i '$$a$(RUN_COMMAND)' $(BIN_BASE)
	chmod +x $(BIN_BASE)
