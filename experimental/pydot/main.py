import pydot


# dot_file_path = "original-graph.dot"  # Replace with your actual file path


def replace_edge_source(graph, old_edge, new_src):
    """
    Replaces old_edge with a new edge that has the same destination,
    label, style, color etc., but uses new_src as source.

    Args:
        graph:     pydot.Dot or pydot.Graph instance
        old_edge:  the pydot.Edge object to replace
        new_src:   string – the new source node name
    """
    # Get current destination (must keep it)
    dst = old_edge.get_destination()

    # Copy all attributes (color, style, label, penwidth, arrowhead, etc.)
    attributes = old_edge.get_attributes().copy()

    # Also preserve the most commonly used dedicated properties
    # (these are sometimes stored separately)
    label = old_edge.get_label()
    color = old_edge.get_color()
    style = old_edge.get_style()
    penwidth = old_edge.get_penwidth()
    arrowhead = old_edge.get_arrowhead()
    arrowtail = old_edge.get_arrowtail()
    dir_ = old_edge.get_dir()  # 'forward', 'back', 'both', 'none'

    # print(f"*** {dir_=}")

    # Remove the original edge
    # Using the object reference is safest (handles multi-edge cases better)
    # graph.del_edge(old_edge)
    graph.del_edge(old_edge.get_source(), old_edge.get_destination())

    # Create and configure the new edge
    new_edge = pydot.Edge(
        src=new_src,
        dst=dst,
        #label=label,
        #color=color,
        # style=style,
        # penwidth=penwidth,
        # arrowhead=arrowhead,
        # arrowtail=arrowtail,
        # dir=dir_,
        **attributes,  # includes everything else
    )

    # Add it back to the graph
    graph.add_edge(new_edge)

    return new_edge


# Parse the .dot file
graphs = pydot.graph_from_dot_file("original-graph.dot")
# print(f"{type(graphs)=}")
# print(f"{graphs=}")
assert len(graphs) == 1

graph = graphs[0]
# print(f"{type(graph)=}")
# print(f"{graph=}")

# Maps "n22" -> sys_clk node..
global_map = {}

# Get all nodes (returns list of pydot.Node objects)
for node in graph.get_nodes():
    name = node.get_name().strip('"')  # node names are often quoted
    label = node.get_attributes().get("label", "")

    # print(f"Processing node: {name} (label: {label})")

    # print(f"Node:  {label=} {name=}")

    label = label.strip('"').strip("'")

    if label in ["sys_clk", "sys_reset", "red_led", "green_led"]:
        assert label not in global_map, label
        global_map[name] = node

# print(f"{global_map=}")

# # Modify attributes
# node.set_label(f"Modified: {label}")
# node.set_shape("box")                      # common shapes: box, ellipse, circle, diamond, etc.
# node.set_color("red")
# node.set_style("filled")
# node.set_fillcolor("lightblue")

# # Or set any arbitrary Graphviz attribute
# node.set_attributes({"fontname": "Arial", "fontsize": "12"})

# Counters to assign ids for each global net.
counters_map = new_dict = {key: 0 for key in global_map}

# # Get all edges (returns list of pydot.Edge objects)
for edge in graph.get_edges():
    src = edge.get_source().strip('"')
    dst = edge.get_destination().strip('"')

    src_parts = src.split(":")
    base_src_name = src_parts[0]
    # print(f"{src_parts=}")
    if base_src_name in global_map:

        # print(f"edge: {src=} → {dst=}")
        # print("In global map")
        n = counters_map[base_src_name] + 1
        counters_map[base_src_name] = n
        new_base_src_name = f"{base_src_name}_{n:03d}"
        new_src_parts = src_parts.copy()
        new_src_parts[0] = new_base_src_name
        new_node_name = ":".join(new_src_parts)
        # print(f"{new_src_parts}")
        # print(f"{new_node_name}")

        # -- Add a clone floating node.
        original_node = global_map[base_src_name]
        new_node = pydot.Node(
            name=new_node_name,
            #shape=original_node.get_shape(),
            #label=original_node.get_label(),
            **original_node.get_attributes(),
        )

        graph.add_node(new_node)

        # -- Replace the edge to have the new src

        replace_edge_source(graph, edge, new_node_name)

# graph.write_dot("modified-graph.dot")

dot_source = graph.to_string()

with open("modified-graph.dot", "w", encoding="utf-8") as f:
    f.write(dot_source)

    # Modify edge attributes
    # edge.set_label("new label")
    # edge.set_color("blue")
    # edge.set_style("dashed")
    # edge.set_arrowhead("normal")
    # edge.set_penwidth("2.0")

    # # Add or override any attribute
    # edge.set_attributes({"weight": "1.5", "dir": "both"})
