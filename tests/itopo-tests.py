#!/usr/bin/env python

import os
import sure                     # flake8: noqa
import sys
import unittest

paths = [
    '..',
]
for path in paths:
    sys.path.append(os.path.abspath(path))

from itopo import Controller, Leaf, Spine, Topology

class NodeTest(unittest.TestCase):
    def testRestUrl(self):
        controller = Controller(1)

        (lambda: controller.restUrl).when.called_with().should.throw(
            AssertionError
        )

        controller.oobAddress = '192.168.10.1'
        controller.restUrl.should.equal('https://192.168.10.1:443')

        controller.oobHostName = 'praveek6-bld.insieme.local'
        controller.restUrl.should.equal(
            'https://praveek6-bld.insieme.local:443'
        )

        controller.https = False
        controller.restPort = 80
        controller.restUrl.should.equal('http://praveek6-bld.insieme.local:80')


class TopologyTest(unittest.TestCase):
    def setUp(self):
        self.topo = Topology()

    def testEmptyTopology(self):
        topo = self.topo
        topo.controllers.should.be.empty
        topo.leaves.should.be.empty
        topo.spines.should.be.empty
        list(topo.nodes).should.be.empty
        topo.node.when.called_with(1).should.throw(KeyError)


    def testSmallTopology(self):
        topo = self.topo
        controller = topo.addController(1)
        controller.role.should.equal(Controller.ROLE)
        controller.id.should.equal(1)

        leaf1 = topo.addLeaf(101)
        leaf1.role.should.equal(Leaf.ROLE)
        leaf1.id.should.equal(101)

        leaf2 = topo.addLeaf(102)
        leaf2.id.should.equal(102)

        spine = topo.addSpine(103)
        spine.role.should.equal(Spine.ROLE)
        spine.id.should.equal(103)

        topo.controllers.should.have.length_of(1)
        topo.leaves.should.have.length_of(2)
        topo.spines.should.have.length_of(1)

        topo.node(1).should.be(controller)
        topo.node(101).should.be(leaf1)
        topo.node(102).should.be(leaf2)
        topo.node(103).should.be(spine)
