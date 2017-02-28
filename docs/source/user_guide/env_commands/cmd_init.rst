.. _cmd_init:

apio init
=========

.. contents::

Usage
-----

.. code::

    apio init [OPTIONS]

Description
-----------

Manage apio projects. In addition to the code, an apio project may include a configuration file **apio.ini** and a Scons script **SConstruct**.

Options
-------

.. program:: apio init

.. option::
    -s, --scons

Create a default SConstruct file. This file can be modified and it will be used instead of the default script.

.. option::
    -b, --board

Create a configuration file with the selected board. This will be the default board used in :ref:`cmd_build`, :ref:`cmd_time` and :ref:`cmd_upload` commands.

.. option::
    -p, --project-dir

Set the target directory for the project.

.. option::
    -y, --sayyes

Automatically answer YES to all the questions.

Examples
--------

1. Create a SConstruct file.

.. code::

  $ apio init --scons
  Creating SConstruct file ...
  File 'SConstruct' has been successfully created!


2. Create an apio.ini file with the icezum board

.. code::

  $ apio init --board icezum
  Creating apio.ini file ...
  File 'apio.ini' has been successfully created!
