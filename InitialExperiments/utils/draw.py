import os

# Required for Graphviz tool
os.environ['PATH'] += os.pathsep + 'G:\\Programe\\Graphviz\\bin'

from typing import Dict

import graphviz


def generate_tree_diagram(tree: Dict, filename: str):
    dot = graphviz.Digraph()

    def build_tree(node, parent_node=None, edge_label=None):
        if isinstance(node, Dict):
            # For attribute nodes, it is the only property.
            current_node_label = list(node.keys())[0]
            dot.node(str(id(node)), label=current_node_label)

            if parent_node:
                dot.edge(str(id(parent_node)), str(id(node)), label=edge_label)

            for value, child_node in node[current_node_label].items():
                build_tree(child_node, node, value)

        elif isinstance(node, str):
            current_node_label = f"Class: {node}"
            dot.node(str(id(node)), label=current_node_label, shape="box")

            if parent_node:
                dot.edge(str(id(parent_node)), str(id(node)), label=edge_label)

    build_tree(tree)
    dot.format = 'svg'
    return dot.render(filename, view=False)
