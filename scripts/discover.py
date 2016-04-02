#!/usr/bin/env python

# Copyright (c) 2015 Cisco Systems, Inc. All rights reserved.

from pprint import pprint
import itopo
import pyaci
import socket
import sys
import yaml


def main():
    apic = pyaci.Node('https://{}:{}'.format(sys.argv[1], sys.argv[2]))
    apic.methods.Login('admin', 'ins3965!').POST()

    mos = apic.methods.ResolveClass('topSystem').GET()
    topo = itopo.Topology()
    for mo in mos:
        node = topo.addNode(mo.id, mo.role)

        node.name = mo.name
        node.serial = mo.serial
        node.tepAddress = mo.address
        node.inbAddress = mo.inbMgmtAddr
        node.oobAddress = mo.oobMgmtAddr

        if node.oobAddress != '0.0.0.0':
            try:
                host, _, _ = socket.gethostbyaddr(node.oobAddress)
            except socket.herror:
                pass
            else:
                node.oobHostName = host

    # print itopo.Topology().fromDict(topo.toDict()).toYaml()

    # loader = itopo.Loader()
    # print loader.topology().toYaml()
    print topo.toYaml()


if __name__ == '__main__':
    main()
