# Copyright (c) 2014 Cisco Systems, Inc. All rights reserved.

from collections import defaultdict
import os
import yaml

try:
    import pyaci
except ImportError:
    hasPyaci = False
else:
    hasPyaci = True


class Element(object):
    pass


class Node(Element):
    @staticmethod
    def new(id, role):
        roleTypes = [Controller, Leaf, Spine]
        node = {cls.ROLE: cls for cls in roleTypes}[role](id)
        node.role = role
        return node

    def __init__(self, id):
        self._id = int(id)

        self._attributes = {
            'podId': 1,
            'name': 'node-{}'.format(id),
            'role': None,
            'serial': None,
            'tepAddress': None,
            'inbAddress': None,
            'oobAddress': None,
            'oobHostName': None,
            'restPort': 443,
            'https': True,
        }

        for key, value in self._attributes.iteritems():
            setattr(self, key, value)

        self._api = None

    @property
    def id(self):
        return self._id

    @property
    def restUrl(self):
        if self.oobHostName is not None:
            host = self.oobHostName
        elif self.oobAddress is not None:
            host = self.oobAddress
        else:
            assert False
        return '{}://{}:{}'.format(
            'https' if self.https else 'http', host, self.restPort)

    @property
    def api(self):
        if not hasPyaci:
            raise UserWarning('pyaci module is not available')
        if self._api is None:
            self._api = pyaci.Node(self.restUrl)
        return self._api

    def toDict(self):
        return {key: getattr(self, key) for key in self._attributes
                if getattr(self, key) is not None}

    def fromDict(self, data):
        for key in self._attributes:
            if key in data:
                setattr(self, key, data[key])
        return self

    def toYaml(self):
        return yaml.safe_dump(self.toDict(), default_flow_style=False,
                              encoding='utf-8', allow_unicode=True)


class Controller(Node):
    ROLE = 'controller'


class Leaf(Node):
    ROLE = 'leaf'


class Spine(Node):
    ROLE = 'spine'


# TODO (2015-04-24, Praveen Kumar): Add support for the following:
# - FEX
# - Blade switch
# - Hypervisor
# - Router


class Topology(object):
    def __init__(self):
        self._nodesByRole = defaultdict(list)
        self._nodesById = {}
        self._nodesByPodId = defaultdict(list)

    def addNode(self, id, role):
        assert id not in self._nodesById
        node = Node.new(id, role)
        self._addNode(node)
        return node

    def addController(self, id):
        return self.addNode(id, Controller.ROLE)

    @property
    def controllers(self):
        return self._nodesByRole[Controller.ROLE]

    def addLeaf(self, id):
        return self.addNode(id, Leaf.ROLE)

    @property
    def leaves(self):
        return self._nodesByRole[Leaf.ROLE]

    def addSpine(self, id):
        return self.addNode(id, Spine.ROLE)

    @property
    def spines(self):
        return self._nodesByRole[Spine.ROLE]

    @property
    def nodes(self):
        return self._nodesById.itervalues()

    def node(self, id):
        return self._nodesById[id]

    def toDict(self):
        return {'nodes': {node.id: node.toDict() for node in self.nodes}}

    def fromDict(self, data):
        if 'key' in data:
            self.key = data['key']
        for nodeId, nodeData in data['nodes'].iteritems():
            node = self.addNode(nodeId, nodeData['role'])
            node.fromDict(nodeData)
        return self

    def toYaml(self):
        return yaml.safe_dump(self.toDict(), default_flow_style=False,
                              encoding='utf-8', allow_unicode=True)

    def _addNode(self, node):
        self._nodesByRole[node.role].append(node)
        self._nodesById[node.id] = node
        self._nodesByPodId[node.podId].append(node)

    # TODO (2015-04-24, Praveen Kumar): Add an API to add links.


class Loader(object):
    def __init__(self, rcPath='~/.itoporc'):
        self._rcPath = os.path.expanduser(rcPath)
        if os.path.isfile(self._rcPath):
            with open(self._rcPath, 'r') as rc:
                rcData = yaml.load(rc)
        else:
            assert False
        self._repos = rcData['repos']
        self._defaultKey = rcData['defaultKey']
        self._topos = {}

    def topology(self, key=None):
        if key is None:
            key = self._defaultKey

        for repo in self._repos:
            topoFile = os.path.join(os.path.expanduser(repo),
                                    '{}.yml'.format(key))
            if not os.path.isfile(topoFile):
                continue
            with open(topoFile) as f:
                topo = Topology()
                topo.fromDict(yaml.load(f))
                return topo

        assert False
