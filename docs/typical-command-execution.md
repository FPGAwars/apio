This page describes the operations performed during the execution of a typical Apio command, with the goal of outlining the principles of how Apio works.

The command we chose is `apio build` because it demonstrates most of the key concepts in Apio's design.

## The examples command

We are using the command `apio build` with the Apio example `alhambra-ii/blinky`.

Creating the project:

```
mkdir test-project
cd test-project
apio examples fetch alhambra-ii/blinky
```

Running the example:

```
apio clean
apio build
```

## 1. Starting the Apio process

To be compatible with PyInstaller, Apio has a single entry point in `apio/__main__.py` which is used for two kinds of invocations: as the main Apio command and as the SCons subprocess.

When `main()` starts for the `apio build` command, it examines the command line passed to it, realizes that this is not an invocation as a SCons subprocess, and calls the Apio top-level Click command function `apio_top_cli()`.

## 2. Dispatching the 'build' command

The function `apio_top_cli()` is decorated with `@apio.group`, which indicates that it is a 'group' Click command containing subcommands that are listed in the `subgroups` attribute of the decorator.

When `apio_top_cli()` is called from `main()`, Click magic is invoked behind the scenes, which eventually causes the invocation of the function `cli()` in `apio_build.py`, which is the handler of the `build` command under the top-level `apio` command.

> Click also passes to the build handler values of options it may find on the command line such as `--verbose`, but this is not the case with our simple example where the command line is just `apio build`.

> The `@click.command()` decoration of the `build` handler indicates that it is an actual command that performs work rather than a group that contains subcommands.

## 3. Creating an ApioContext

Most Apio commands begin by creating an `ApioContext` instance, which provides
access to project settings, the user profile, configuration, and resources.

The instantiation is governed by two configuration enum values,
`ProjectPolicy` and `RemoteConfigPolicy`, which the `apio build` command
specifies as follows:

The project policy is `PROJECT_REQUIRED`, which means an `apio.ini` file
is required and that project-related information, such as resolved `apio.ini`
environment variables and options, will be loaded.

The remote config policy is `CACHED_OK`, which indicates that using remote
config information cached in the `~/.apio/profile.json` file is acceptable.
The context creation logic may try to fetch a fresh config if the cached one
is too old but will fall back to the cached version if needed.

> The expiration time of the cached remote config is controlled by
> a parameter in the resource file `apio/resources/config.jsonc`.

## 4. Invoking the SCons manager

TBD

## 5. Creating the SCons parameters proto

TBD

## 6. Invoking the scons subprocess

TBD

## 7. Executing SConstruct

TBD

## 8. SCons subprocess initialization

TBD

## 9. Defining SCons targets and builders

TBD

## 10. SCons execution

TBD

## 11. SCons output filter

TBD
