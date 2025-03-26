"""
Parser for the mdmap file format.
"""

import re
from collections import defaultdict


class MDMapParser:
    """
    Parser for mdmap level files.
    """

    def __init__(self):
        self.level_name = None
        self.size = (0, 0)
        self.layers = []
        self.legends = defaultdict(dict)
        self.layer_data = {}

    def parse_file(self, file_path):
        """
        Parse a mdmap file.

        Args:
            file_path: Path to the mdmap file

        Returns:
            self: Returns self for method chaining
        """
        with open(file_path, "r") as f:
            content = f.read()

        return self.parse_string(content)

    def parse_string(self, content):
        """
        Parse mdmap content from a string.

        Args:
            content: String containing mdmap content

        Returns:
            self: Returns self for method chaining
        """
        lines = content.splitlines()

        # Parse header
        for i, line in enumerate(lines):
            if line.startswith("# Level:"):
                self.level_name = line[8:].strip()
            elif line.startswith("Size:"):
                size_text = line[5:].strip()
                width, height = size_text.split("x")
                self.size = (int(width), int(height))
            elif line.startswith("Layers:"):
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith("-"):
                    layer_name = lines[j].strip()[1:].strip()
                    self.layers.append(layer_name)
                    j += 1

        # Parse legends and layers
        i = 0
        while i < len(lines):
            line = lines[i]

            # Parse legend
            legend_match = re.match(r"\[legend: (\w+)\]", line)
            if legend_match:
                layer_name = legend_match.group(1)
                i += 1
                while i < len(lines) and not lines[i].startswith("["):
                    if "=" in lines[i]:
                        key, value = lines[i].split("=", 1)
                        self.legends[layer_name][key.strip()] = value.strip()
                    i += 1
                continue

            # Parse layer
            layer_match = re.match(r"\[layer: (\w+)\]", line)
            if layer_match:
                layer_name = layer_match.group(1)
                if layer_name in self.layers:
                    i += 1
                    if i < len(lines) and lines[i].strip() == "~~~~~~~~":
                        i += 1
                        layer_data = []
                        while i < len(lines) and lines[i].strip() != "~~~~~~~~":
                            layer_data.append(lines[i])
                            i += 1
                        self.layer_data[layer_name] = layer_data

            i += 1

        return self

    def get_tile(self, layer, x, y):
        """
        Get the tile character at the specified coordinates.

        Args:
            layer: Layer name
            x: X coordinate
            y: Y coordinate

        Returns:
            str: Character at the specified position, or None if out of bounds
        """
        if layer not in self.layer_data:
            return None

        layer_grid = self.layer_data[layer]
        if y < 0 or y >= len(layer_grid) or x < 0 or x >= len(layer_grid[y]):
            return None

        return layer_grid[y][x]

    def get_tile_meaning(self, layer, tile_char):
        """
        Get the meaning of a tile character from the legend.

        Args:
            layer: Layer name
            tile_char: Tile character

        Returns:
            str: Meaning of the tile character, or None if not found
        """
        if layer not in self.legends or tile_char not in self.legends[layer]:
            return None

        return self.legends[layer][tile_char]
