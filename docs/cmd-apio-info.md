# Apio info

The `apio info` command group displays additional information about Apio and your system.

## OPTIONS

`  -h, --help  Show this message and exit.`

## SUBCOMMANDS

```
  apio info platforms
  apio info system
  apio info colors
```

---

# Apio info platforms

The command `apio info platforms` lists the platform IDs supported by Apio and highlights your system's effective ID.

> [Advanced] The automatic platform ID detection of Apio can be overridden by defining a different platform ID using the `APIO_PLATFORM` environment variable, though this is generally not recommended.

## EXAMPLES

```
apio info platforms   # List supported platform IDs
```

## OPTIONS

```
-h, --help  Show this message and exit
```

---

# Apio info system

The `apio info system` command displays general information about your system and Apio installation. Useful for diagnosing setup or environment issues.

> [Advanced] The default location of the Apio home directory—where it saves preferences and packages—is `.apio` under your home directory. This can be changed using the `APIO_HOME` environment variable.

## EXAMPLES

```
apio info system   # Show system information
```

## OPTIONS

```
-h, --help  Show this message and exit
```

---

# Apio info colors

The `apio info colors` command shows how ANSI colors are rendered on your system, which helps diagnose color-related issues.  
It uses one of three output libraries: Rich, Click, or Python's built-in `print()`.

## EXAMPLES

```
apio info colors          # Rich library output (default)
apio info colors --rich   # Rich library output (same as above)
apio info colors --click  # Click library output
apio info colors --print  # Python's print() output
apio sys col -p           # Using shortcut
```

## OPTIONS

```
-r, --rich   Output using the Rich library
-c, --click  Output using the Click library
-p, --print  Output using Python's print()
-h, --help   Show this message and exit
```
