#!/usr/bin/env python

# Copyright (c) 2015 Cisco Systems, Inc. All rights reserved.

import itopo
import pyaci
import socket
import sys
import yaml
import getpass


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generates an ACI Fabric topology')

    parser.add_argument('hostNameOrIP', nargs=1,
                        help='Hostname or IP address of APIC')
    parser.add_argument('-P', '--port', type=int, default=80,
                            help='Port of the APIC')

    parser.add_argument('-u', '--user', default='admin',
                        help='APIC Username')
    parser.add_argument('-p', '--password', default='ins3965!',
                        help='APIC password')
    
    parser.add_argument('-S', '--https', default=None,
                        help='use HTTPS', action='store_true')
    parser.add_argument('-o', '--output', default="yaml",
                        help='Display format (xml, json, yaml)')

    args = parser.parse_args()

    if args.password is None:
        args.password = getpass.getpass('Enter {} password for {}: '.format(
            args.user, args.host[0]))

    return args

def main():
    args = parse_args()

    nodeUrl = '{}://{}:{}'.format('https' if args.https else 'http', 
                                  args.hostNameOrIP[0], args.port)

    apic = pyaci.Node(nodeUrl)
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

    if args.output == 'yaml':
        print topo.toYaml()
    elif args.output == 'json':
        print topo.toJson()
    elif args.output == 'xml':
        print topo.toXml()

if __name__ == '__main__':
    main()
