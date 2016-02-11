# apio

Experimental open source micro-ecosystem for open FPGAs. Based on [platformio](https://github.com/platformio/platformio)

It includes scons, pre-build static toolchain-icestorm and icestick rules file installation. Also clean, build, upload commands using scons.

## Install

For development
```bash
sudo apt-get install libftdi1
sudo pip install apio
```

## Execute

```bash
apio install
```

```bash
apio clean
apio build
apio upload
```
