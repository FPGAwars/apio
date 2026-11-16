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
apio packages install
apio packages list
```

---

## apio packages install

The `apio packages install` command installs installed packages to their latest versions.

<h3>Examples</h3>

```
apio packages install            # Install packages
apio pack upd                    # Same, with shortcuts
apio packages install --force    # Force reinstallation from scratch
apio packages install --verbose  # Provide additional info
apio packages install --cached-ok  # Allow cached remote config
```

<h3>Options</h3>

```
-f, --force    Force reinstallation.
-v, --verbose  Show detailed output.
--cached-ok    Allow cached remote config when offline.
-h, --help     Show this message and exit.
```

<h3>Notes</h3>

- With `--cached-ok`, a recent cached remote config is reused. If the cache
  needs refreshing and the refresh fails, Apio warns and uses the cached
  config. This allows an offline invocation to succeed when all packages
  already match that config. Without a usable cache, or when packages need
  downloading (including with `--force`), the command still fails offline.
  Without `--cached-ok`, a fresh remote config is always required.

- Adding the `--force` option forces the reinstallation of existing
  packages; otherwise, packages that are already installed correctly
  remain unchanged.

- It is recommended to run the 'apio packages install' once in a
  while because it checks the Apio remote server for installed packages with potential fixes and new examples.

---

## apio packages list

The `apio packages list` command displays the available and installed Apio packages. The list may vary depending on your operating system.

The option `--check` causes the command to fail and exit with an error
status code if the packages are not installed properly.

<h3>Examples</h3>

```
apio packages list          # Just report
apio packages list --check  # Also fail if packages unhealthy
```

<h3>Options</h3>

```
-c, --check  Error on unhealthy packages.
-h, --help   Show this message and exit.
```
