"""
Isometric Renderer

Handles rendering of isometric maps using OpenGL.
"""

import os
import pyglet
from pyglet.gl import *
from typing import Dict, List, Optional, Tuple

from isoline.map_parser import MDMap, parse_mdmap
from isoline.tile_renderer import VectorTile, create_tile


class IsometricRenderer:
    """
    Handles rendering of isometric maps using vector graphics.

    Uses the 2:1 tile ratio for optimal rendering as specified
    in the SRD.
    """

    def __init__(self, tile_width: int = 100, tile_height: int = 50):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.map_data: Optional[MDMap] = None
        self.tile_cache: Dict[str, VectorTile] = {}
        self.x_offset = 0
        self.y_offset = 0

    def load_map(self, map_path: str) -> bool:
        """
        Load an MDMap file.

        Args:
            map_path: Path to the .mdmap file

        Returns:
            bool: True if the map was loaded successfully
        """
        try:
            self.map_data = parse_mdmap(map_path)
            self._init_tiles()
            return True
        except Exception as e:
            print(f"Error loading map: {e}")
            return False

    def _init_tiles(self):
        """Initialize tile cache for the loaded map"""
        # Clear existing cache
        for tile in self.tile_cache.values():
            tile.delete()
        self.tile_cache.clear()

        if not self.map_data:
            return

        # Find all unique tile types in the map
        unique_tiles = set()
        for layer_name, layer_data in self.map_data.layers.items():
            for row in layer_data.grid:
                for cell in row:
                    if cell != ".":  # Skip empty cells
                        unique_tiles.add(cell)

        # Create and cache tiles
        for tile_type in unique_tiles:
            try:
                self.tile_cache[tile_type] = create_tile(
                    tile_type, self.tile_width, self.tile_height
                )
            except ValueError as e:
                print(f"Warning: {e}")

    def set_offset(self, x: int, y: int):
        """Set the rendering offset for the map"""
        self.x_offset = x
        self.y_offset = y

    def render(self):
        """Render the isometric map"""
        if not self.map_data or not self.map_data.header:
            return

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Setup OpenGL state for rendering
        try:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        except:
            pass  # Continue without blending if not available

        try:
            glLineWidth(1.0)
        except:
            pass  # Continue without line width if not available

        # Render each layer in order
        for layer_name in self.map_data.header.layers:
            layer = self.map_data.get_layer(layer_name)
            if not layer:
                continue

            self._render_layer(layer_name)

        # Reset OpenGL state
        try:
            glDisable(GL_BLEND)
        except:
            pass

    def _render_layer(self, layer_name: str):
        """Render a specific layer of the map"""
        layer = self.map_data.get_layer(layer_name)
        if not layer or not self.map_data.header:
            return

        # Get dimensions
        width = self.map_data.header.width
        height = self.map_data.header.height

        # Calculate starting position based on map dimensions
        # Center the map on screen
        x_start = self.x_offset
        y_start = self.y_offset

        # Render each tile
        for y in range(height):
            for x in range(width):
                tile_type = layer.grid[y][x]
                if tile_type in self.tile_cache:
                    # Calculate isometric position using the formulas from SRD:
                    # x_screen = x_start + (x * TILE_WIDTH/2) - (y * TILE_WIDTH/2)
                    # y_screen = y_start + (x * TILE_HEIGHT/2) + (y * TILE_HEIGHT/2)
                    x_screen = (
                        x_start
                        + (x * self.tile_width // 2)
                        - (y * self.tile_width // 2)
                    )
                    y_screen = (
                        y_start
                        + (x * self.tile_height // 2)
                        + (y * self.tile_height // 2)
                    )

                    # Draw the tile
                    self.tile_cache[tile_type].draw(x_screen, y_screen)

    def cleanup(self):
        """Clean up OpenGL resources"""
        for tile in self.tile_cache.values():
            tile.delete()
        self.tile_cache.clear()
