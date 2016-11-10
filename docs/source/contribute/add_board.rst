.. add_board

Add a new board
===============

In order to support a new board based on FPGA Lattice iCE40 family, follow these steps:

1. Find your FPGA in `fpgas.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/fpgas.json>`_. This file contains all FPGAs supported by the `Icestorm <http://www.clifford.at/icestorm>`_ project.

2. Find or add your programmer in `programmers.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/fpgas.json>`_

3. Add your board in `boards.json <https://github.com/FPGAwars/apio/blob/develop/apio/resources/fpgas.json>`_ with the following format:

  * board key

    * ``fpga``: FPGA key
    * ``programmer``

      * ``type``: programmer key
      * ``extra_args``: more programmer args (optional)

    * ``check``

      * ``ftdi-desc``: FTDI label description substring. Check \`apio system --lsftdi\`
      * ``platform``: system platform. E.g. linux_armv7l, windows, etc. (optional)

  For example:

  .. code::

    "icoboard": {
      "fpga": "iCE40-HX8K-CT256",
      "programmer": {
        "type": "icoprog"
      },
      "check": {
        "platform": "linux_armv7l"
      }
    }

  .. code::

    "kefir": {
      "fpga": "iCE40-HX4K-TQ144",
      "programmer": {
        "type": "iceprog",
        "extra_args": "-I B"
      },
      "check": {
        "ftdi-desc": "Milk JTAG:u"
      }
    }

  .. note::

    For more detailed configuration `SConstruct file <https://github.com/FPGAwars/apio/blob/develop/apio/resources/SConstruct>`_ can be edited. Also more apio packages and drivers' configuration methods can be added for a full-integration.
