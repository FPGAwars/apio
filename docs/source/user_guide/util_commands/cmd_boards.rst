.. _cmd_boards:

apio boards
===========

.. contents::

Usage
-----

.. code::

    apio boards [OPTIONS]

Description
-----------

Show FPGA boards information.

All supported boards:

HX1K

* `IceZUM Alhambra <https://github.com/FPGAwars/icezum>`_
* `Nandland Go board <https://www.nandland.com/goboard/introduction.html>`_
* `iCEstick Evaluation Kit <http://www.latticesemi.com/icestick>`_

HX8K

* `Alhambra II <https://github.com/FPGAwars/Alhambra-II-FPGA>`_
* `BlackIce <https://hackaday.io/project/12930-blackice-low-cost-open-hardware-fpga-dev-board>`_
* `BlackIce II <https://github.com/mystorm-org/BlackIce-II>`_
* `CAT board <https://hackaday.io/project/7982-cat-board>`_
* `icoBOARD 1.0 <http://icoboard.org/icoboard-1-0.html>`_
* `Kéfir I <http://fpgalibre.sourceforge.net/Kefir/>`_
* `iCE40-HX8K Breakout Board <http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/iCE40HX8KBreakoutBoard>`_

LP8K

* `TinyFPGA B2 <https://tinyfpga.com/b-series-guide.html>`_
* `TinyFPGA BX <https://tinyfpga.com/bx/guide.html>`_

UP5K

* `UPDuino v1.0 <http://gnarlygrey.atspace.cc/development-platform.html#upduino>`_
* `UPDuino v2.0 <http://gnarlygrey.atspace.cc/development-platform.html#upduino_v2>`_
* `iCEBreaker <https://github.com/icebreaker-fpga/icebreaker>`_
* `iCEBreaker bitsy <https://github.com/icebreaker-fpga/icebreaker>`_
* `FPGA 101 Workshop Badge Board <https://github.com/mmicko/workshop_badge>`_
* `iCE40 UltraPlus Breakout Board <http://www.latticesemi.com/en/Products/DevelopmentBoardsAndKits/iCE40UltraPlusBreakoutBoard>`_

.. note::

  All supported FPGAs are shown in `Project IceStorm web page <http://www.clifford.at/icestorm>`_

Options
-------

.. program:: apio boards

.. option::
    -l, --list

List all supported boards.

.. option::
    -f, --fpga

List all supported FPGAs.


Examples
--------

1. Show all available boards

.. code::

  $ apio boards --list

  Supported boards:

  ----------------------------------------------------------
  Board            FPGA                 Type  Size  Pack
  ----------------------------------------------------------
  Alchitry-Cu      iCE40-HX8K-CB132     hx    8k    cb132
  Cat-board        iCE40-HX8K-CT256     hx    8k    ct256
  TinyFPGA-B2      iCE40-LP8K-CM81      lp    8k    cm81
  TinyFPGA-BX      iCE40-LP8K-CM81      lp    8k    cm81
  alhambra-ii      iCE40-HX4K-TQ144     hx    8k    tq144:4k
  blackice         iCE40-HX4K-TQ144     hx    8k    tq144:4k
  blackice-ii      iCE40-HX4K-TQ144     hx    8k    tq144:4k
  fomu             iCE40-UP5K-UWG30     up    5k    uwg30
  fpga101          iCE40-UP5K-SG48      up    5k    sg48
  go-board         iCE40-HX1K-VQ100     hx    1k    vq100
  iCE40-HX8K       iCE40-HX8K-CT256     hx    8k    ct256
  iCE40-UP5K       iCE40-UP5K-SG48      up    5k    sg48
  iCEBreaker       iCE40-UP5K-SG48      up    5k    sg48
  iCEBreaker-bitsy iCE40-UP5K-SG48      up    5k    sg48
  iceblink40-hx1k  iCE40-HX1K-VQ100     hx    1k    vq100
  icestick         iCE40-HX1K-TQ144     hx    1k    tq144
  icezum           iCE40-HX1K-TQ144     hx    1k    tq144
  icoboard         iCE40-HX8K-CT256     hx    8k    ct256
  kefir            iCE40-HX4K-TQ144     hx    8k    tq144:4k
  upduino          iCE40-UP5K-SG48      up    5k    sg48
  upduino2         iCE40-UP5K-SG48      up    5k    sg48

2. Show all available FPGAs

.. code::

  $ apio boards --fpga

  Supported FPGAs:

  --------------------------------------------
  FPGA                  Type  Size  Pack
  --------------------------------------------
  iCE40-HX1K-CB132      hx    1k    cb132
  iCE40-HX1K-TQ144      hx    1k    tq144
  iCE40-HX1K-VQ100      hx    1k    vq100
  iCE40-HX4K-BG121      hx    8k    bg121:4k
  iCE40-HX4K-CB132      hx    8k    cb132:4k
  iCE40-HX4K-TQ144      hx    8k    tq144:4k
  iCE40-HX8K-BG121      hx    8k    bg121
  iCE40-HX8K-CB132      hx    8k    cb132
  iCE40-HX8K-CM225      hx    8k    cm225
  iCE40-HX8K-CT256      hx    8k    ct256
  iCE40-LP1K-CB121      lp    1k    cb121
  iCE40-LP1K-CB81       lp    1k    cb81
  iCE40-LP1K-CM121      lp    1k    cm121
  iCE40-LP1K-CM36       lp    1k    cm36
  iCE40-LP1K-CM49       lp    1k    cm49
  iCE40-LP1K-CM81       lp    1k    cm81
  iCE40-LP1K-QN84       lp    1k    qn84
  iCE40-LP1K-SWG16TR    lp    1k    swg16tr
  iCE40-LP384-CM36      lp    384   cm36
  iCE40-LP384-CM49      lp    384   cm49
  iCE40-LP384-QN32      lp    384   qn32
  iCE40-LP4K-CM121      lp    8k    cm121:4k
  iCE40-LP4K-CM225      lp    8k    cm225:4k
  iCE40-LP4K-CM81       lp    8k    cm81:4k
  iCE40-LP8K-CM121      lp    8k    cm121
  iCE40-LP8K-CM225      lp    8k    cm225
  iCE40-LP8K-CM81       lp    8k    cm81
  iCE40-UP3K-UWG30      up    5k    uwg30
  iCE40-UP5K-SG48       up    5k    sg48
  iCE40-UP5K-UWG30      up    5k    uwg30
