# Apio command line

This page explains the principles and general options of using the Apio command line. For
specific commands, see the respective command description.

---

## Apio command tree

Apio commands are organized as a command tree rooted at `apio`. Some commands, such as `apio build`, have only two levels, while others, like `apio drivers install ftdi`, have three or more. To explore available commands at each level, use the `-h` option (short for `--help`) with any command.

For example

```
  apio -h
  apio info -h
  apio info cli -h
```

---

## Apio command options

Most Apio commands have options that let you control their behavior. For example, the command 'apio build' has options to control the verbosity of its output:

```
apio build --verbose
apio build --verbose-synth
```

To list the options for a command, run it with the `-h` option. For example:

```
apio build -h
```

---

## Apio command shortcuts

When typing apio commands, it's sufficient to type enough of each command to make the selection unambiguous. For example, these commands below are equivalent.

```
apio preferences
apio pref
apio pr
```

However, `apio p` is ambiguous because it matches both `apio preferences` and `apio packages`.

---

## Apio shell auto completion

Apio's command line processor is based on the Python Click package which supports auto completion with some shells. Although it worked as a proof of concept, this feature is experimental and not guaranteed to function reliably. More information is available in the Click documentation: <https://tinyurl.com/click-shell-completion>
