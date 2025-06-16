# Apio preferences

The `apio preferences` command lets you view and manage user preferences. These settings are stored in the `profile.json` file in the Apio home directory (e.g. `~/.apio`) and apply to all Apio projects.

## EXAMPLES

```
apio preferences -t light       # Set theme for light backgrounds
apio preferences -t dark        # Set theme for dark backgrounds
apio preferences -t no-colors   # Disable color output
apio preferences --list         # Show current preferences
apio pref -t dark               # Using command shortcut
```

## OPTIONS

```
-t, --theme [light|dark|no-colors]  Set color theme
-c, --colors                        List available theme colors
-l, --list                          Show current preferences
-h, --help                          Show help message and exit
```
