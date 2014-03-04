Setup:



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


NOTE: On every host Virtual Machines of multiple organisations may run. The traffic between Virtual Machines of different organizations will be seperated by creating separate Security Domains(VLanS) for an organization (or a group or organizations) on a host system. This is acheived by configuring the physical switch and thorugh Open vSwitch Software on the host machine. Open vSwitch software and its configurations are automatically setup when the host is installed through the PXE-Server. All the prerequisites needs to be configured manually as of now.

