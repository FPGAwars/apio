The files in this directory are executed by the scons child process and
not by the apio process itself, with stdout and stderr pipes that allows
the apio process to read the output. 

As a result:
* A breakpoint in this code will not stop when running the apio process.
  The workaround is to run the scons subprocess indepedently for testing
  (see scons_run.py in this directory)).

* Print messages with color need to be performed with 
  click.secho(...., color=True) otherwise it will be stripped automatically
  by click due to the piped output. The the info/warning/error functions
  in scons_util.py.
