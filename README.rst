========================================================
Python Bindings for Managing Cisco ACI Fabric Topologies
========================================================

Introduction
------------

`itopo` provides Python bindings for represeting, and accessing information
about Cisco ACI Fabric topologies.

Installation
------------

Clone this repository, and install it locally.

.. code-block::

   git clone <url>
   pip install ./itopo


If you are one of the developers of `itopo`, you can install it in editable mode.

.. code-block::

   git clone <url>
   pip install -e './itopo[test]'
   cd itopo
   nosetests


Topology File
-------------

`itopo` stores information about a topology in a YAML file. A sample topology
file looks like this.

.. code-block:: yaml

    nodes:
      1:
        https: true
        inbAddress: 192.168.11.1
        name: apic1
        oobAddress: 192.168.10.1
        oobHostName: ifav61-ifc1.insieme.local
        podId: 1
        restPort: 443
        role: controller
        serial: Not Specified
        tepAddress: 10.0.0.1
      101:
        https: true
        inbAddress: 0.0.0.0
        name: leaf1
        oobAddress: ifav61-leaf1.insieme.local
        podId: 1
        restPort: 443
        role: leaf
        serial: TEP-1-101
        tepAddress: 10.0.56.95


Topologies Repository
---------------------

A repository is a directory that contains one or more topologies file.


User Configuration
------------------

User configuration is expected to be in `~/.itoporc`. A sample configuration looks like this.

.. code-block:: yaml

   repos: [~/itopos]

   defaultKey: praveek6-bld

Usage
-----

.. code-block:: python

    >>> import itopo
    >>> loader = itopo.Loader()
    >>> ifav61 = loader.topology(key='ifav61')
    >>> for node in ifav61.nodes:
    ...     print node.id, node.oobHostName
    ...
    1 ifav61-ifc1.insieme.local
    101 None
    >>> len(ifav61.controllers)
    1
    >>> len(ifav61.leaves)
