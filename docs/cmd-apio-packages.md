# Apio packages

The command group `apio packages` provides commands to manage the
installation of Apio packages. These are not Python packages, but collections of tools and data required by Apio.

> The list of available packages depends on your operating system and may vary across platforms.

## OPTIONS

```
-h, --help  Show this message and exit.
```

## SUBCOMMANDS

```
apio packages update
apio packages list
```

---

# Apio preferences update

The `apio packages update` command updates installed packages to their latest versions.

## EXAMPLES

```
apio packages update            # Update packages
apio pack upd                   # Same, with shortcuts
apio packages update --force    # Force reinstallation from scratch
apio packages update --verbose  # Provide additional info
```

## OPTIONS

```
-f, --force    Force reinstallation.
-v, --verbose  Show detailed output.
-h, --help     Show this message and exit.
```

## NOTES

- Adding the `--force` option forces the reinstallation of existing
  packages; otherwise, packages that are already installed correctly
  remain unchanged.

- It is recommended to run the 'apio packages update' once in a
  while because it checks the Apio remote server for updated packages with potential fixes and new examples.

---

# Apio preferences list

The `apio packages list` command displays the available and installed Apio packages. The list may vary depending on your operating system.

## EXAMPLES

```
apio packages list
```

## OPTIONS

```
-v, --verbose  Show detailed output.
-h, --help     Show this message and exit.
```
