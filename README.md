# apio

Experimental open source micro-ecosystem for open FPGAs. Based on [platformio](https://github.com/platformio/platformio). It includes scons, pre-built static toolchain-icestorm and icestick rules file auto-installation. Also clean, build, upload commands using scons.

## Install

```bash
sudo apt-get install libftdi1
sudo pip install apio
```

## Execute

```bash
apio install
apio uninstall
```

```bash
apio clean
apio build
apio upload
apio time
apio sim
```
