Baadal Testing Sandbox
===============================================
This sandbox installation script is tested on Ubuntu-12.04-LTS-Server

Pre-requisites
-----------------------------------------------
* __make libvirt__ - for downloading libvirt source
* __make ubuntu__ - for downloading ubuntu iso
* __make configure__ - for configuring the sandbox system

Setup Instructions
-----------------------------------------------
* __make configure__ - required to initialise some configurations required by the sandbox system, the IP address required is the starting address you would like to use for the internal sandbox network.

* __make sandbox__ - should set up ovs switch on sandbox system, create virtual machines for NAT, Controller, Filer  
        
* __make switch__ - set up ovs switches on sandbox system (installs ovs) (can be automatically done through make sandbox)

* __make nat__ - set up virtual machine for NAT
* __make clean-nat__ - virtual machine NAT will be deleted along with its disk image and binaries that create NAT vm
  
* __make controller__ - set up virtual machine for Controller
* __make clean-controller__ - virtual machine Controller will be deleted along with its disk image and binaries that create Controller vm

* __make filer__ - set up virtual machine for Filer
* __make clean-filer__ - virtual machine Filer will be deleted along with its disk image and binaries that create Filer vm

* __make host HOST_ID=1__ - set up virtual machine for Host (requires controller vm to be up and running for pxe-boot) (HOST_ID can be between 1 to 5)
* __make clean-host HOST_ID=1__ - virtual machine HOST will be deleted along with its disk image and binaries that create Host vm

* __make clean__ - remove virtual machines created by __make sandbox__ and delete associated data and binaries

Post Installation Instructions
------------------------------------------------
* __README__ regarding Controller configuration can be found [here](https://github.com/apoorvemohan/newbaadal/tree/master). 

  It is reccomended that these configurations are made before setting up sandbox as the files are copied into the sandbox during sandbox setup. Otherwise these files are found in __/baadal__ in respective VMs and can be updated there.
* Once the VMs are created use __virsh__ to make changes to them
* Do not run any __make clean-\*__ if you don't wish to loose the data of the vm
* After installation of OS on these VMs (Host, Controller, Filer), ssh into them and run installation scripts located in __/baadal__

Default Values
------------------------------------------------
These values can be configured in __src/constants.sh__

__Login Credentials__
All virtual machines
* __username__ : baadal
* __password__ : baadal
* __root access__ : __sudo su__ from baadal

__Internal IPs__ - These values could be changed using __make configure__
* Sandbox System - 10.0.0.1
* Controller System - 10.0.0.2
* NAT System - 10.0.0.3
* Filer System - 10.0.0.4
* Internal Gateway - NAT System (10.0.0.3)

__External IPs__
* Sandbox System - baadal-br-ext (DHCP)
* NAT System - eth0 (DHCP)
* Other systems are not connected to external network directly

Fix External Network on Sandbox system
-------------------------------------------------
The external network on sandbox system should not stop working, but in case it does run the following in your shell

__$ ovs-vsctl del-port eth0__

This will disconnect eth0 from sandbox environment. NAT will be connected to an external virtual bridge on sandbox but that bridge will not be connected to your external network.
