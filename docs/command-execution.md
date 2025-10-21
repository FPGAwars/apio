This page describes the operations performed during the execution of a typical Apio command, with the goal of outlining the principles of how Apio works.

The command we chose is `apio build` because it demonstrates most of the key concepts in Apio's design.

## The example command

We are using the command `apio build` with the Apio example `alhambra-ii/blinky`.

Creating the project:

```shell
mkdir test-project
cd test-project
apio examples fetch alhambra-ii/blinky
```

Running the example:

```shell
apio clean
apio build
```

## 1. Starting the Apio process

To be compatible with PyInstaller, Apio has a single entry point in `apio/__main__.py`, which is used for two kinds of invocations: as the main Apio command and as the SCons subprocess.

When `main()` starts for the `apio build` command, it examines the command line passed to it, determines that this is not an invocation as a SCons subprocess, and calls the Apio top-level Click command function `apio_top_cli()`.

## 2. Dispatching the 'build' command

The function `apio_top_cli()` is decorated with `@apio.group`, indicating that it is a 'group' Click command containing subcommands listed in the `subgroups` attribute of the decorator.

When `apio_top_cli()` is called from `main()`, Click magic is invoked behind the scenes, eventually causing the invocation of the function `cli()` in `apio_build.py`, which handles the `build` command under the top-level `apio` command.

> Click also passes to the build handler values of options it may find on the command line such as `--verbose`, but this is not the case with our simple example where the command line is just `apio build`.

> The `@click.command()` decoration of the `build` handler indicates that it is an actual command that performs work rather than a group that contains subcommands.

## 3. Creating an ApioContext

Most Apio commands begin by creating an `ApioContext` instance, which provides access to project settings, the user profile, configuration, and resources.

```python
apio_ctx = ApioContext(
    project_policy=ProjectPolicy.PROJECT_REQUIRED,
    config_policy=RemoteConfigPolicy.CACHED_OK,
    packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    project_dir_arg=project_dir,
    env_arg=env,
)
```

The instantiation is governed by three configuration enum values, `ProjectPolicy`, `RemoteConfigPolicy` and `PackagesPolicy`, which the `apio build` command specifies as follows:

The project policy is `PROJECT_REQUIRED`, which means an `apio.ini` file is required and that project-related information, such as resolved `apio.ini` environment variables and options, will be loaded.

The remote config policy is `CACHED_OK`, indicating that using remote config information cached in the `~/.apio/profile.json` file is acceptable. The context creation logic may try to fetch a fresh config if the cached one is too old but will fall back to the cached version if needed.

The packages policy is `ENSURE_PACKAGES` which cause the ApioContext initialization to ensure that the apio
packages are installed properly, fixing and downloading them if necessary.

> The expiration time of the cached remote config is controlled by a parameter in the resource file `apio/resources/config.jsonc`.

> Instantiating the `ApioContext` also initializes the console output in `apio_console.py` with the color and theme preferences from the profile file.

## 4. Invoking the SCons manager

Once the `apio build` command has created the `ApioContext` instance, it is ready to start performing the command-specific logic. In this case, it creates an Apio `SConsManager` instance and calls its `build()` method with the values of the `apio build` command line options.

```python
scons = SConsManager(apio_ctx)

exit_code = scons.build(
    Verbosity(all=verbose, synth=verbose_synth, pnr=verbose_pnr)
)
```

> The class `SConsManager` has a dedicated method for each Apio command that needs to invoke the SCons subprocess; in this case, we use the `build()` method to invoke the build functionality of the SCons subprocess.

## 5. Creating the SCons parameters proto

To invoke the SCons subprocess, the SConsManager collects the parameters needed for that specific SCons target, populates a protocol buffer of type `SconsParams`, and serializes it in text mode into a file called `scons.params` in the build directory for the SCons subprocess to find and deserialize.

> The SCons manager passes parameters such as `fpga_id` in the protocol buffer because the `ApioContext` class is not used in the SCons subprocess, only in the parent Apio process.

> The `timestamp` is also passed in the SCons command line to verify that the SCons subprocess picked the correct params file.

> Running Apio with `APIO_DEBUG=3` provides a detailed list of the parameters passed to the SCons subprocess.

Sample `scons.params` file

```proto
timestamp: "07174143800"
arch: ICE40
fpga_info {
  fpga_id: "ice40hx4k-tq144-8k"
  part_num: "ICE40HX4K-TQ144"
  size: "8k"
  ice40 {
    type: "hx8k"
    pack: "tq144:4k"
  }
}
verbosity {
  all: false
  synth: false
  pnr: false
}
environment {
  platform_id: "darwin-arm64"
  is_windows: false
  terminal_mode: FORCE_TERMINAL
  theme_name: "light"
  debug_level: 0
  yosys_path: "/Users/user/.apio/packages/oss-cad-suite/share/yosys"
  trellis_path: "/Users/user/.apio/packages/oss-cad-suite/share/trellis"
}
apio_env_params {
  env_name: "default"
  board_id: "alhambra-ii"
  top_module: "Test"
}
```

## 6. Invoking the scons subprocess

Once the SCons manager creates and saves the parameters file `scons.params`, it invokes the SCons processor, which runs as a subprocess.

```
<python-interpreter-path>
   -m SCons
   -Q build
   -f /Volumes/projects/apio-dev/repo/apio/scons/SConstruct
   params=_build/default/scons.params
   timestamp=07175539149
```

The first arguments specify the Python interpreter that runs the Apio process. When running as a PyInstaller binary, this is replaced with the Apio binary since a Python interpreter is not used. In this case, the condition in the `__main__.py` module detects that this is a SCons invocation and calls the SCons main.

The flag `-f` specifies the landing SConstruct script and contains the path to a copy of the file `/apio/scons/SConstruct` in this Apio repository.

`params` passes the file `scons.params` with the SCons parameters, and `timestamp` is the same value set in the params file.

## 7. Executing SConstruct

When the SCons subprocess is invoked, it lands in `apio/scons/SConstruct`, which is an SCons script file. The functionality in the `SConstruct` script is minimal, as it immediately switches to plain Python code by invoking the Apio SCons handler `SConsHandler.start()`.

> The SConstruct file also contains the subprocess rendezvous point, where a remote VCS debugger is attached when debugging the SCons subprocess.

## 8. SCons subprocess initialization

When the static method `SConsHandler.start()` is called, it initializes the SCons subprocess by performing these steps:

1. Deserializing the protocol buffer parameters from `scons.proto`.

2. Initializing the text console output in `apio_console.py` with the color preferences and theme.

3. Creating an `ApioEnv` object, which contains the SCons invocation context and is passed around, similar to the `ApioContext` in the parent Apio process.

4. Instantiating an architecture plugin object for the current architecture; in our example, it's a `PluginIce40` instance.

5. Creating an `SConsHandler` instance with the Apio environment and plugin and calling its `execute()` method.

> The `ApioEnv`, which is Apio-specific, should not be confused with the standard SCons `SConsEnvironment` class.

## 9. Defining SCons targets and builders

When the `execute()` method of the `SConsHandler` instance is invoked, it dispatches a target registration method for the requested target. In our example of `apio build`, it dispatches this:

```
if target == "build":
   self._register_build_target(synth_srcs)
```

The `_register_build_target()` method adds to the SCons environment definitions of targets, builders, and dependencies to perform the build operation. The method uses the selected architecture plugin; in our case, `PluginIce40` generates definitions that are architecture-specific.

In our example, targets and builders perform these operations:

- A `yosys` command to synthesize the design.

- A `nextpnr-ice40` command for the place-and-route operation.

- An `icepack` command to generate the bitstream file.

## 10. SCons execution

When the `SConsHandler` completes adding the targets, builders, and dependencies to the SCons environment, it returns, which also causes an exit from the `SConstruct` script. This triggers automatic execution of the commands by SCons. When SCons completes the execution, the SCons subprocess exits, and the execution of `apio build` is completed.

## 11. SCons output filter

While the SCons subprocess is running, its stdout and stderr outputs are piped to the `scons_filter.py` module in the parent Apio process. That module receives the SCons subprocess output in real time and outputs it to the console while modifying certain lines, for example, adding green or red colors to lines that indicate success or failure.

> The `scons_filter.py` module also contains logic to correctly handle progress bars and progress counters from FPGA programming utilities executed by the SCons subprocess. These progress trackers require special considerations because they are timing-dependent and use the '\r' terminators.