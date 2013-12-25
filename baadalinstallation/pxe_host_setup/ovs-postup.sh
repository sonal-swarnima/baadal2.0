#!/bin/sh
ovs-vsctl add-br vlan10 br0 10
ovs-vsctl add-br vlan20 br0 20
ovs-vsctl set port eth0 tag=1
ovs-vsctl set port eth0 trunk=10,20

