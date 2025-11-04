# Apio graph

---

## apio graph

The `apio graph` command generates a graphical representation of the hardware
design and then opens it in a graphical viewer.

<h3>Examples</h3>

```
apio graph               # Generate an SVG file (default)
apio graph --no-viewer   # Suppress the graphical viewer.
apio graph --svg         # Generate an SVG file
apio graph --pdf         # Generate a PDF file
apio graph --png         # Generate a PNG file
apio graph -t my_module  # Graph the 'my_module' module
```

<h3>Options</h3>

```
--svg                   Generate an SVG file (default)
--png                   Generate a PNG file
--pdf                   Generate a PDF file
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-t, --top-module name   Set the top-level module to graph
-n, --no-viewer         Do not open graph viewer
-v, --verbose           Show detailed output
-h, --help              Show help message and exit
```

<h3>Notes</h3>

- On Windows, run `explorer _build/default/graph.svg` to view the graph.
  If your environment name is different from `default`, adjust the path accordingly.
- On macOS, use `open _build/default/graph.svg`.

<h3>Example output</h3>

![](assets/apio-graph.svg)
