The files in this directory are executed by the scons child process and
not by the apio process itself, with stdout and stderr pipes that allows
the apio process to read the output. 

As a result:
* A breakpoint in this code will not stop when running the apio process.
  To debug code here, set the system env var below, run the apio command
  that invoks scons and connect to it via the Visual Studio Code python
  debugger.

```
# Linux and mac osx.
export APIO_SCONS_DEBUGGER=

# Windows
set APIO_SCONS_DEBUGGER=
```

* Print messages with color need to be performed with 
  secho(...., color=True) otherwise it will be stripped automatically
  by click due to the piped output. The the info/warning/error functions
  in scons_util.py.
