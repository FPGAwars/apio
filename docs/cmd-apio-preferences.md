# Apio preferences

---

## apio preferences

The `apio preferences` command lets you view and manage user preferences. These settings are stored in the `profile.json` file in the Apio home directory (e.g. `~/.apio`) and apply to all Apio projects.

> To review the available themes on your screen type `apio info themes`.

<h3>Examples</h3>

```
apio preferences -t light       # Set theme for light backgrounds
apio preferences -t dark        # Set theme for dark backgrounds
apio preferences -t no-colors   # Disable color output
apio preferences --list         # Show current preferences
apio pref -t dark               # Using command shortcut
```

<h3>Options</h3>

```
-t, --theme [light|dark|no-colors]  Set color theme
-c, --colors                        List available theme colors
-l, --list                          Show current preferences
-h, --help                          Show help message and exit
```
