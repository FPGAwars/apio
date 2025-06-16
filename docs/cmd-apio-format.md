# Apio format

The `apio format` command formats project source files to ensure consistent
style without changing their behavior. You can format specific files or let
it format all project files by default.

> File paths are always relative to the project directory, even when using `--project-dir`.

## EXAMPLES

```
apio format                    # Format all source files.
apio format -v                 # Format all files with verbose output.
apio format main.v main_tb.v   # Format the two files.
```

## OPTIONS

```
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-v, --verbose           Show detailed output
-h, --help              Show help message and exit
```

## CUSTOMIZATION

The format command utilizes the format tool from the Verible project,
which can be configured using the `format-verible-options` setting in `apio.ini`. For example:

```
format-verible-options =
    --column_limit=80
    --indentation_spaces=4
```

For a full list of Verible formatter flags, refer to the documentation
page online or use the command `apio raw -- verible-verilog-format --helpful`.

## PROTECTING CODE

Sections of source code can be protected from formatting using the Verible formatter directives:

```
// verilog_format: off
... untouched code ...
// verilog_format: on
```
