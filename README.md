Baadal
============

Baadal is a cloud orchestration software for academic and scientific environments. It is based on open technologies like Linux, KVM, libvirt, OpenVSwitch, Apache, MySQL, and web2py. 

Workflows are implemented expected in academic and research environments, where a user or student can request a VM, a faculty supervisor can approve it, and an administrator can commission it. 

Baadal supports multiple organizations sharing a cloud infrastructure, and thus has a provision for an organization-level administrator. 

Baadal is a multi-tenant implementation, which means that different organizations are isolated from each other against network and system-level security attacks.

Features
--------

Some of the main features of Baadal are:
* Facilities for suspend, resume, shutdown, power off, power on and specifying resource requirement of virtual machines.
* Dynamic resource utilization monitoring.
* Dynamic resource scheduling and power management.
* Fault tolerence: Checkpoint / Restart Mechanism
* Environment-friendly: Migrating existing services onto cloud will help in reduction of existing power consumption by 10%.
* Hypervisor-agnostic: Support for multiple hypervisors. (KVM, Xen, VMWare)
* Secure: Multiple layers of security to prevent un-authorized access. 
* Common authentication: Users across organizations can log-in to Baadal using the authentication details of their organization.
* Easy to install: A simple installation mechanism. Can even be  installed as a sandbox on a single system for experimental setup. 


Installation setup
------------------

                                Internet
                                   |
                                   |
                              Firewall(NAT)
                                   |
                                   |
                                Switch
                                   |
                                   |_ Controller
                                   |
                                   |
                                   |_ Nfs-Server
                                   |
                                   |
                                   |_ Hosts


`NOTE:` On every host Virtual Machines of multiple organisations may run. The traffic between Virtual Machines of different organizations will be seperated by creating separate Security Domains(VLanS) for an organization (or a group or organizations) on a host system. This is acheived by configuring the physical switch and thorugh Open vSwitch Software on the host machine. Open vSwitch software and its configurations are automatically setup when the host is installed through the PXE-Server. All the prerequisites needs to be configured manually as of now.

Version Support
---------------

- Libvirt **1.2.9**
- Qemu **2.0**
- Openvswitch **2.0.2**
- Ubuntu **14.04** (For sandbox script)

