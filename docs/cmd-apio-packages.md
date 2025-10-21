# Apio packages

---

## apio packages

The command group `apio packages` provides commands to manage the
installation of Apio packages. These are not Python packages, but collections of tools and data required by Apio.

> The list of available packages depends on your operating system and may vary across platforms.

<h3>Options</h3>

```
-h, --help  Show this message and exit.
```

<h3>Subcommands</h3>

```
apio packages update
apio packages list
```

---

## apio packages update

The `apio packages update` command updates installed packages to their latest versions.

<h3>Examples</h3>

```
apio packages update            # Update packages
apio pack upd                   # Same, with shortcuts
apio packages update --force    # Force reinstallation from scratch
apio packages update --verbose  # Provide additional info
```

<h3>Options</h3>

```
-f, --force    Force reinstallation.
-v, --verbose  Show detailed output.
-h, --help     Show this message and exit.
```

<h3>Notes</h3>

- Adding the `--force` option forces the reinstallation of existing
  packages; otherwise, packages that are already installed correctly
  remain unchanged.

- It is recommended to run the 'apio packages update' once in a
  while because it checks the Apio remote server for updated packages with potential fixes and new examples.

---

## apio packages list

The `apio packages list` command displays the available and installed Apio packages. The list may vary depending on your operating system.

<h3>Examples</h3>

```
apio packages list
```

<h3>Options</h3>

```
-v, --verbose  Show detailed output.
-h, --help     Show this message and exit.
```
