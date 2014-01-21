Prerequisites: nfs-server, firewall(including NAT/PAT), physical switch, authentication service(preferably ldap-kerberos)

1. Checkout latest code from https://github.com/apoorvemohan/newbaadal.git
2. Checkout ubuntu-12.04-server-amd64 from http://releases.ubuntu.com/precise/ubuntu-12.04.3-server-amd64.iso
3. Edit /newbaadal/baadalinstallation/installation.cfg as per your requirements
4. Rename and Edit /newbaadal/baadalinstallation/baadal/static/{baadalapp_db.cfg | baadalapp_ldap.cfg} -> baadalapp.cfg as per your requirements (this should be same as that specified in the /newbaadal/baadalinstallation/installation.cfg file)
5. Execute /newbaadal/baadalinstallation/installation.sh
6. The above script will install the controller(GUI & Backend), dhcp-server and pxe-server on the your system.
7. Plug the host to the switch and install them using PXE setup.
8. Mount the nfs-server on the hosts and  controller.


Hardware Networking Setup:



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

