.. _cmd_config:

apio config
===========

.. contents::

Usage
-----

.. code::

    apio config [OPTIONS]

Description
-----------

Apio configuration commands.

Options
-------

.. program:: apio config

.. option::
    -l, --list

List all configuration parameters

.. option::
    -e, --exe [default|native]

Configure executables: `default` selects apio packages, `native` selects native binaries (except system package)

.. note::

   In **debian** systems, if /etc/apio.json defines a new APIO_PKG_DIR, this new path will be used to load the packages.

+--------------------------+------+-------+----------+
| **Mode**                 | **default**  |**native**|
+--------------------------+------+-------+----------+
| /ect/apio.json           | No   | Yes   |          |
+--------------------------+------+-------+----------+
| Load installed packages  | Yes  | Yes * | No       |
+--------------------------+------+-------+----------+
| Check installed packages | Yes  | Yes **| No       |
+--------------------------+------+-------+----------+

\* load APIO_PKG_DIR from /etc/apio.json

\*\* Suggest message `apt-get install apio-[pkg]`

Examples
--------

1. Show all configuration parameters

.. code::

  $ apio config --list
  Executable mode: default

2. Enable native mode for executable binaries

.. code::

  $ apio config --exe native
  Executable mode updated: native
