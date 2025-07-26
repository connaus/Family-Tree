from enum import StrEnum
import streamlit_mermaid as stmd


class Orientation(StrEnum):
    TD = "TD"
    LR = "LR"


class Mermaid:

    def __init__(
        self,
        orientation: Orientation = Orientation.LR,
        ancestor_colour: str = "#228B22",
        width="auto",
    ) -> None:

        self.orientation = orientation
        self.ancestor_colour = ancestor_colour
        self.width = width
        self.nodes: list[str] = []
        self.node_names: list[str] = []
        self.edges: list[str] = []
        self.ancestor: list[str] = []

    def add_node(self, name: str, label: str, ancestor: bool = False) -> None:
        """add a node to the graph. names must be unique. Labels will be displayed. Ancestors will be coloured"""
        name = name.replace(" ", "")
        self.node_names.append(name)
        self.nodes.append(f'{name}(["{label}"])')
        if ancestor:
            self.ancestor.append(name)

    def add_edge(self, name_from: str, name_to: str, spouse: bool = False) -> None:
        """add an edge between two existing nodes. The line wil be dotted if it is a spouse"""
        name_from = name_from.replace(" ", "")
        name_to = name_to.replace(" ", "")
        if name_from not in self.node_names:
            raise ValueError(
                f"The node {name_from} is not a recognised node. Use add_node to add it."
            )
        if name_to not in self.node_names:
            raise ValueError(
                f"The node {name_to} is not a recognised node. Use add_node to add it."
            )
        if spouse:
            self.edges.append(f"{name_from} -.-> {name_to}")
        else:
            self.edges.append(f"{name_from} --> {name_to}")

    def __call__(self) -> None:
        code = f"graph {self.orientation}"
        code += "\n"
        code += "\n".join(self.nodes)
        code += "\n"
        code += "\n".join(self.edges)
        code += "\n"
        if self.ancestor:
            code += f"classDef desc fill:{self.ancestor_colour},stroke:#333;\n"
            code += f"class {','.join(self.ancestor)} desc"
        print(code)
        stmd.st_mermaid(code, width=self.width)
