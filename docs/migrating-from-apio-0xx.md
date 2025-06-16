# Migrating from Apio 0.x.x

Apio 1.x.x introduces many improvements compared to Apio 0.x.x. Many of the changes were done in a backward compatible way, but some do require user attention. On this page, we outline the main changes from a compatibility point of view to help users migrate their projects successfully to Apio 1.x.x.

## Uninstall Apio 0.x.x

It is recommended to first delete Apio 0.x.x before installing Apio 1.x.x. The steps to do so are:

1. Delete the Apio Python package `pip uninstall apio`

2. Delete the directory `.apio` under the user home directory. That directory contains packages and other transient files used by Apio.

## Create project file `apio.ini`

Apio 1.x.x requires a project file called `apio.ini` in the directory of each Apio project. Make sure your project has a text file called `apio.ini` with the content below, replace _<board>_ with the id of your board (e.g. `alhambra-ii`) and replace _<my-module>_ with the name of the top Verilog module of your project (e.g. `Blinky`).

```
[env:default]
board = <board>
main-module = <my-module>
```

## Delete calls to the verilog function `$dumpfile()`.

Remove from your testbenches all calls to the Verilog function `$dumpfile()`. The location of the generated simulation files is now automatically controlled by Apio.

## Know the new commands

The hierarchy and names of some Apio commands were changed in Apio 1.x.x, and the table below will help you migrate from the old to the new commands. You can also use the `-h` option for detailed information on any command level, for example `apio -h`, `apio devices -h`, and `apio devices usb -h`.

| Apio 0.x.x                   | Apio 1.x.x                  | Comments                     |
| :--------------------------- | :-------------------------- | :--------------------------- |
| `apio boards --fpga`         | `apio fpgas`                | List supported FPGAs         |
| `apio boards --list`         | `apio boards`               | List supported boards        |
| `apio drivers --ftdi-enable` | `apio drivers install ftdi` | Install FTDI driver          |
| `apio examples --files`      | `apio examples fetch`       | Fetch an example             |
| `apio examples --list`       | `apio examples list`        | List examples                |
| `apio init`                  | `apio create`               | Create an apio.ini file      |
| `apio install --all`         | `apio packages update`      | Install Apio packages        |
| `apio install --list`        | `apio packages list`        | List installed apio packages |
| `apio system --lsftdi`       | `apio devices usb`          | List FTDI and USB devices    |
| `apio system --lsserial`     | `apio devices serial`       | List serial ports            |
| `apio time`                  | `apio report`               | Report design timing.        |
| `apio verify`                | `apio lint`                 | Verify the source code.      |
