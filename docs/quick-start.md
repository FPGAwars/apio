# Apio quick start

In this page, we will go through the steps of creating, validating, and uploading a design to an FPGA board. We will use the Alhambra-ii FPGA board, but the process is the same for all supported boards.

---

## Step 1: Installing Apio

The first step in using Apio is installing it. You can use either the [Python-based installation](python-based-installation.md) or the [Standalone installation](standalone-installation.md). When done, continue to step 2 below.

---

## Step 2: Creating an Apio project

Let's make an empty directory and populate it with the example `alhambra-ii/getting-started`.

> For more information about `apio examples`, type `apio examples -h`.

```
# Make an empty project directory
$ mkdir project
$ cd project

# Fetch example files
project$ apio examples fetch alhambra-ii/getting-started

# List the project files
project$ tree .
.
├── apio.ini
├── main_tb.gtkw
├── main_tb.v
├── main.v
└── pinout.pcf
```

The files in this Apio project are:

| Name           | Description                                             |
| :------------- | :------------------------------------------------------ |
| `apio.ini`     | The Apio project file.                                  |
| `main.v`       | Verilog source code.                                    |
| `pinout.pcf`   | ICE40 pin assignments.                                  |
| `main_tb.v`    | A Verilog testbench for testing `main.v`.               |
| `main_tb.gtkw` | Saved GTKWAVE configuration for simulating `main_tb.v`. |

---

## Step 3: Verifying the source code

To verify the source code, we use two commands: `apio lint` and `apio build`. The first scans the code for various errors and nitpicks, while the second actually builds it.

> For more information about the commands, type `apio lint -h` and `apio build -h`.

```
project$ apio lint

project$ apio build
```

If you encounter any problems with the code, fix them and repeat.

---

## Step 4: Simulating the design

To simulate the design, we use the command `apio sim`, which runs a simulation of the testbench and shows its results in a graphical GTKWAVE window. The `main_tb.gtkw` contains the GTKWAVE configuration, and you should save it each time you make changes in GTKWAVE that you want to keep.

> For more information about `apio sim`, type `apio sim -h`.

```
project$ apio sim
```

![](assets/sim-gtkwave.png)

---

## Step 5: Running tests

The command `apio test` runs all the testbenches it finds in the project in batch mode without a graphical view like `apio sim`. The command fails if any of the testbenches has an error or exits with the `$fatal` function, typically due to a failing assertion.

> For more information about `apio test`, type `apio test -h`.

```
project$ apio test

Testbench main_tb.v
...
main_tb.v:45: $finish called at 966000 (1ps)
```

---

## Step 6: Programming the FPGA board

In this step, we build the project if needed and upload it to the FPGA board. With some systems and boards, this requires driver installation using the `apio drivers install` command, while others work out of the box. To test if the board is accessible, we will try to list it with the `apio devices` command. Since Alhambra-ii uses plain USB rather than a serial port, we will try to list it using the command `apio devices usb`.

```
project$ apio devices usb

USB Devices
┌───────────┬─────────┬──────────────┬───────────────────┬────────────┬─────────┐
│ VID:PID   │ BUS:DEV │ MANUFACTURER │ DESCRIPTION       │ SERIAL-NUM │ TYPE    │
├───────────┼─────────┼──────────────┼───────────────────┼────────────┼─────────┤
│ 0403:6010 │   0:3   │ AlhambraBits │ Alhambra II v1.0A │            │ FT2232H │
└───────────┴─────────┴──────────────┴───────────────────┴────────────┴─────────┘
Found 1 USB device
```

We are in luck; the device's manufacturer and description strings are listed correctly, which means that the device is accessible to Apio and doesn't require an additional driver. We are ready to program the FPGA.

```
project$ apio upload
...
Selecting USB device:
- FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]
- DEVICE [0403:6010, 0:3], [AlhambraBits] [Alhambra II v1.0A] []
...
Erasing: [==================================================] 100.00%
Writing: [==================================================] 100.00%
Reading: [==================================================] 100.00%

Done
```

The example now runs on the FPGA board, and two LEDs should be flashing alternately.

---

This concludes the Apio quick start guide. We suggest reviewing the [Video tutorial](video-tutorial.md) or going directly to the [Python-based installation](python-based-installation.md) or [Standalone installation](standalone-installation.md) sections.
