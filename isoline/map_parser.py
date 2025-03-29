"""
MDMap Parser

Handles loading and parsing of MDMap format files (.mdmap)
based on the specification in docs/mdmap/mdmap.md
"""

import re
from typing import Dict, List, Tuple, Optional


class MDMapHeader:
    """Header information for an MDMap file"""

    def __init__(self, name: str, width: int, height: int, layers: List[str]):
        self.name = name
        self.width = width
        self.height = height
        self.layers = layers


class LayerLegend:
    """Legend mapping for a layer in an MDMap file"""

    def __init__(self):
        self.mappings: Dict[str, str] = {}

    def add_mapping(self, key: str, description: str):
        self.mappings[key] = description

    def get_description(self, key: str) -> Optional[str]:
        return self.mappings.get(key)


class LayerData:
    """Layer data for an MDMap file"""

    def __init__(self, layer_type: str):
        self.type = layer_type
        self.grid: List[List[str]] = []
        self.legend = LayerLegend()

    def set_grid(self, grid: List[List[str]]):
        self.grid = grid


class MDMap:
    """Representation of an MDMap file"""

    def __init__(self):
        self.header: Optional[MDMapHeader] = None
        self.layers: Dict[str, LayerData] = {}

    def get_layer(self, layer_name: str) -> Optional[LayerData]:
        return self.layers.get(layer_name)


def parse_mdmap(file_path: str) -> MDMap:
    """
    Parse an MDMap file and return a structured representation.

    Args:
        file_path: Path to the .mdmap file

    Returns:
        MDMap: Structured representation of the map file
    """
    with open(file_path, "r") as f:
        content = f.read()

    mdmap = MDMap()

    # Parse header
    name_match = re.search(r"# Level: (.+)", content)
    size_match = re.search(r"Size: (\d+)x(\d+)", content)
    layers_section = re.search(r"Layers:\s+((?:  - \w+\s*)+)", content)

    if name_match and size_match and layers_section:
        name = name_match.group(1)
        width = int(size_match.group(1))
        height = int(size_match.group(2))

        # Extract layers
        layers_text = layers_section.group(1)
        layers = re.findall(r"- (\w+)", layers_text)

        mdmap.header = MDMapHeader(name, width, height, layers)

        # Initialize layer objects
        for layer_name in layers:
            mdmap.layers[layer_name] = LayerData(layer_name)
    else:
        raise ValueError("Invalid MDMap header format")

    # Parse legends
    legend_sections = re.finditer(
        r"\[legend: (\w+)\](.*?)(?=\[|\Z)", content, re.DOTALL
    )
    for match in legend_sections:
        layer_name = match.group(1)
        legend_content = match.group(2).strip()

        if layer_name in mdmap.layers:
            legend = mdmap.layers[layer_name].legend
            for line in legend_content.split("\n"):
                line = line.strip()
                if line and "=" in line:
                    key, description = line.split("=", 1)
                    legend.add_mapping(key.strip(), description.strip())

    # Parse layer data
    layer_sections = re.finditer(r"\[layer: (\w+)\]\s+~+\s+(.*?)~+", content, re.DOTALL)
    for match in layer_sections:
        layer_name = match.group(1)
        grid_text = match.group(2).strip()

        if layer_name in mdmap.layers:
            grid_rows = [list(row) for row in grid_text.split("\n")]
            mdmap.layers[layer_name].set_grid(grid_rows)

    # Validate dimensions
    for layer_name, layer in mdmap.layers.items():
        if layer.grid:
            if len(layer.grid) != mdmap.header.height:
                raise ValueError(
                    f"Layer {layer_name} height {len(layer.grid)} doesn't match header height {mdmap.header.height}"
                )

            for i, row in enumerate(layer.grid):
                if len(row) != mdmap.header.width:
                    raise ValueError(
                        f"Layer {layer_name} row {i} width {len(row)} doesn't match header width {mdmap.header.width}"
                    )

    return mdmap
