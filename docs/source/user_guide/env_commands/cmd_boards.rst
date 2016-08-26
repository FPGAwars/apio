.. _cmd_boards:

apio boards
===========

.. contents::

Usage
-----

.. code-block:: bash

    apio boards [OPTIONS]


Description
-----------


Options
-------

.. program:: apio boards

.. option::
    -l, --list

List supported boards

.. option::
    -f, --fpga

List supported FPGAs


Examples
--------

1. Show all available boards

.. code-block:: bash

    $ apio boards --list

    Supported boards:

    ------------------------------------------------------
    Board         FPGA                 Type  Size  Pack
    ------------------------------------------------------
    iCE40-HX8K    iCE40-HX8K-CT256     hx    8k    ct256
    icestick      iCE40-HX1K-TQ144     hx    1k    tq144
    icezum        iCE40-HX1K-TQ144     hx    1k    tq144
    go-board      iCE40-HX1K-VQ100     hx    1k    vq100

2. Show all available FPGAs

.. code-block:: bash

  $ apio boards --fpga

  Supported FPGAs:

  --------------------------------------------
  FPGA                  Type  Size  Pack
  --------------------------------------------
  iCE40-LP4K-CM121      lp    8k    cm121:4k
  iCE40-HX1K-VQ100      hx    1k    vq100
  iCE40-HX1K-TQ144      hx    1k    tq144
  iCE40-HX1K-CB132      hx    1k    cb132
  iCE40-LP1K-CM81       lp    1k    cm81
  iCE40-HX8K-CT256      hx    8k    ct256
  iCE40-LP4K-CM81       lp    8k    cm81:4k
  iCE40-LP8K-CM225      lp    8k    cm225
  iCE40-LP1K-CM49       lp    1k    cm49
  iCE40-LP1K-CB81       lp    1k    cb81
  iCE40-HX8K-CM225      hx    8k    cm225
  iCE40-HX8K-CB132      hx    8k    cb132
  iCE40-LP4K-CM225      lp    8k    cm225:4k
  iCE40-LP1K-SWG16TR    lp    1k    swg16tr
  iCE40-LP1K-QN84       lp    1k    qn84
  iCE40-LP1K-CB121      lp    1k    cb121
  iCE40-LP1K-CM121      lp    1k    cm121
  iCE40-HX4K-CB132      hx    8k    cb132:4k
  iCE40-LP8K-CM81       lp    8k    cm81
  iCE40-LP1K-CM36       lp    1k    cm36
  iCE40-HX4K-TQ144      hx    8k    tq144:4k
  iCE40-LP8K-CM121      lp    8k    cm121
