"""
Isometric Renderer

Handles rendering of isometric maps using OpenGL.
Optimized version with improved caching and incremental updates.
"""

import os
import pyglet
from pyglet.gl import *
from typing import Dict, List, Optional, Tuple, Set, Any
import math

from isoline.map_parser import MDMap, parse_mdmap
from isoline.tile_renderer import VectorTile, create_tile


class IsometricRenderer:
    """
    Handles rendering of isometric maps using vector graphics.

    Uses the 2:1 tile ratio for optimal rendering as specified
    in the SRD.

    Performance optimized with:
    - View frustum culling
    - Minimal batch rebuilding
    - Vertex array caching
    """

    def __init__(self, tile_width: int = 100, tile_height: int = 50):
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.map_data: Optional[MDMap] = None
        self.tile_cache: Dict[str, VectorTile] = {}
        self.x_offset = 0
        self.y_offset = 0

        # Batch for efficient rendering - VBOs will be added here
        self.batch = pyglet.graphics.Batch()

        # Track tile instances associated with grid positions for updates
        # Maps (layer_name, grid_x, grid_y) -> (tile_type, screen_x, screen_y)
        self.current_positions = {}

        # Track visible region for culling
        self.viewport_width = 800  # Default, will be updated on resize
        self.viewport_height = 600  # Default, will be updated on resize

        # Track which grid positions need updates (VBO recreation/deletion)
        self.needs_rebuild = False
        self.dirty_tiles: Set[Tuple[str, int, int]] = set()  # Layer, x, y grid coords

        # Animation settings
        self.animation_enabled = True
        self.animation_frame_time = 0.25  # Seconds between animation frames
        self.animation_time_elapsed = 0  # Time tracker for animation

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
            self.needs_rebuild = True
            return True
        except Exception as e:
            print(f"Error loading map: {e}")
            return False

    def _init_tiles(self):
        """Initialize tile cache for the loaded map"""
        # Clear existing cache and ensure all old VBOs are deleted
        self.cleanup()

        if not self.map_data:
            return

        # Find all unique tile types in the map
        unique_tiles = set()
        for layer_name, layer_data in self.map_data.layers.items():
            for y, row in enumerate(layer_data.grid):
                for x, cell in enumerate(row):
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
        """
        Set the rendering offset for the map.
        This optimized version handles both large and small camera movements appropriately.
        """
        if x == self.x_offset and y == self.y_offset:
            return

        # Save old offset for calculating position deltas
        old_x_offset = self.x_offset
        old_y_offset = self.y_offset

        # Update offsets
        self.x_offset = x
        self.y_offset = y

        # A significant camera move invalidates all current VBO positions
        # Mark for full rebuild - cleanup happens in _rebuild_batch
        if (
            abs(x - old_x_offset) > self.viewport_width // 2
            or abs(y - old_y_offset) > self.viewport_height // 2
        ):
            # Force a full rebuild
            self.needs_rebuild = True
        else:
            # For small movements, mark all current positions as dirty for incremental updates
            for pos_key in list(self.current_positions.keys()):
                # Mark grid positions as dirty. _update_dirty_tiles will handle VBO management.
                self.dirty_tiles.add(pos_key)

    def set_viewport_size(self, width: int, height: int):
        """Update the viewport size for culling calculations"""
        self.viewport_width = width
        self.viewport_height = height
        self.needs_rebuild = True  # Rebuild with new culling bounds

    def _rebuild_batch(self):
        """
        Rebuild the rendering batch with current positions.
        This optimized version supports incremental updates and culling.
        """
        if not self.map_data or not self.map_data.header:
            return

        if self.needs_rebuild:
            # Create a new batch
            old_batch = self.batch
            self.batch = pyglet.graphics.Batch()

            # --- VBO Cleanup ---
            # Before rebuilding, ensure all VBOs associated with the *old* batch
            # are deleted from the GPU and tile instances.
            for tile in self.tile_cache.values():
                tile.delete()  # This clears tile._active_vertex_lists
            # --- End VBO Cleanup ---

            self.current_positions.clear()
            self.dirty_tiles.clear()

            # Add all tiles to the batch at their current positions
            for layer_name in self.map_data.header.layers:
                self._add_layer_to_batch(layer_name)

            self.needs_rebuild = False
        elif self.dirty_tiles:
            # Incremental update - only update tiles that have been marked as dirty
            self._update_dirty_tiles()
            self.dirty_tiles.clear()

    def _add_layer_to_batch(self, layer_name: str):
        """
        Add a specific layer to the batch with view frustum culling.
        Only adds tiles that are potentially visible on screen.
        """
        layer = self.map_data.get_layer(layer_name)
        if not layer or not self.map_data.header:
            return

        # Get dimensions
        width = self.map_data.header.width
        height = self.map_data.header.height

        # Calculate starting position based on map dimensions
        x_start = self.x_offset
        y_start = self.y_offset

        # Calculate visible region bounds with padding
        # The padding ensures tiles that are partially visible are still rendered
        padding = max(self.tile_width, self.tile_height) * 2

        # Add each tile to the batch if potentially visible
        for y in range(height):
            for x in range(width):
                tile_type = layer.grid[y][x]
                if tile_type in self.tile_cache:
                    # Calculate isometric screen position
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

                    # --- DEBUG PRINT: Visibility Check ---
                    is_visible = self._is_potentially_visible(
                        x_screen, y_screen, padding
                    )
                    if x < 2 and y < 2:  # Print only first few tiles
                        print(
                            f"Checking visibility for grid ({x},{y}): screen=({x_screen:.1f},{y_screen:.1f}), viewport=({self.viewport_width},{self.viewport_height}), padding={padding:.1f}, visible={is_visible}"
                        )
                    # --- END DEBUG ---

                    # Only add tiles that are potentially visible (with padding)
                    if is_visible:
                        # --- DEBUG PRINT: Screen Coordinates (if visible) ---
                        if x < 2 and y < 2:  # Print only first few tiles per layer
                            print(
                                f"Adding tile {tile_type} at grid ({x},{y}) -> screen ({x_screen:.1f},{y_screen:.1f})"
                            )
                        # --- END DEBUG ---

                        # Add VBO to batch and track grid position <-> screen position
                        position_key = (layer_name, x, y)
                        # add_to_batch now handles VBO creation/management internally
                        self.tile_cache[tile_type].add_to_batch(
                            x_screen, y_screen, self.batch
                        )
                        self.current_positions[position_key] = (
                            tile_type,
                            x_screen,
                            y_screen,
                        )

    def _is_potentially_visible(
        self, x_screen: float, y_screen: float, padding: float
    ) -> bool:
        """
        Check if a tile at the given screen position is potentially visible.
        Uses viewport size and padding to determine visibility.
        """
        # Simple rectangular bounds check with padding
        return (
            x_screen + self.tile_width + padding >= 0
            and x_screen - padding <= self.viewport_width
            and y_screen + self.tile_height + padding >= 0
            and y_screen - padding <= self.viewport_height
        )

    def _update_dirty_tiles(self):
        """
        Update only the tiles corresponding to dirty grid positions.
        Handles deleting old VBOs and adding new ones at updated positions/states.
        """
        if not self.map_data or not self.map_data.header:
            return

        # For each dirty grid position, update the corresponding tile's VBO
        for position_key in self.dirty_tiles:
            layer_name, x, y = position_key

            # Get the tile type and instance for this grid position
            layer = self.map_data.get_layer(layer_name)
            if not layer:
                continue

            tile_type = layer.grid[y][x]
            if tile_type not in self.tile_cache:
                continue

            tile = self.tile_cache[tile_type]

            # Calculate new screen position
            new_x_screen = (
                self.x_offset + (x * self.tile_width // 2) - (y * self.tile_width // 2)
            )
            new_y_screen = (
                self.y_offset
                + (x * self.tile_height // 2)
                + (y * self.tile_height // 2)
            )

            new_screen_pos_key = (new_x_screen, new_y_screen)

            # --- VBO Management ---
            # Check if there was a VBO at the *old* screen position for this grid position
            if position_key in self.current_positions:
                old_tile_type, old_x, old_y = self.current_positions[position_key]
                old_screen_pos_key = (old_x, old_y)
                # Get the corresponding tile instance (should be the same tile object)
                old_tile = self.tile_cache.get(old_tile_type)
                if old_tile:
                    # Delete the VBO at the *old* screen position
                    old_tile.delete_vbo_at_position(old_screen_pos_key)
            # --- End VBO Management ---

            # Add VBO at the *new* position if potentially visible
            if self._is_potentially_visible(
                new_x_screen, new_y_screen, max(self.tile_width, self.tile_height) * 2
            ):
                tile.add_to_batch(new_x_screen, new_y_screen, self.batch)
                self.current_positions[position_key] = (
                    tile_type,
                    new_x_screen,
                    new_y_screen,
                )
            else:
                # Tile is no longer visible, ensure its removed from tracking
                if position_key in self.current_positions:
                    del self.current_positions[position_key]

    def update_animation(self, dt: float):
        """
        Update tile animations based on elapsed time.

        Args:
            dt: Time elapsed since last update in seconds
        """
        if not self.animation_enabled:
            return

        # Accumulate time
        self.animation_time_elapsed += dt

        # Check if we should advance animation frame
        if self.animation_time_elapsed >= self.animation_frame_time:
            # Reset timer
            self.animation_time_elapsed = 0

            # Advance animation state for all tiles in cache
            animated_tiles_updated = False
            for tile_type, tile in self.tile_cache.items():
                if tile.animated:
                    tile.advance_state()
                    animated_tiles_updated = True

            # If any animated tiles were updated, mark all their positions as dirty
            if animated_tiles_updated:  # Mark the *grid position* as dirty
                for pos_key, (tile_type, _, _) in self.current_positions.items():
                    tile = self.tile_cache.get(tile_type)
                    if tile and tile.animated:
                        self.dirty_tiles.add(pos_key)

    def render(self):
        """
        Render the isometric map.
        This optimized version updates only what's needed before rendering.
        """
        if not self.map_data or not self.map_data.header:
            return

        # Update batch if needed (offset changed or map loaded)
        if self.needs_rebuild or self.dirty_tiles:
            self._rebuild_batch()

        # Setup OpenGL state for rendering - minimizing state changes
        # We only set these states once per frame
        try:
            # Temporarily comment out state changes for debugging
            # glEnable(GL_BLEND)
            # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            # glLineWidth(3.0) # Keep line width thicker for visibility if it works
            # Set back to 1.0 as 3.0 caused GL_INVALID_VALUE
            glLineWidth(1.0)
            pass  # Keep the try/except structure
        except:
            pass  # Continue if OpenGL features not available

        # Draw all tiles with a single batch draw call
        self.batch.draw()

        # Reset OpenGL state
        try:
            # Temporarily comment out state changes for debugging
            # glDisable(GL_BLEND)
            pass  # Keep the try/except structure
        except:
            pass

    def set_animation_speed(self, frame_time: float):
        """
        Set the animation speed by specifying time between frames.

        Args:
            frame_time: Time in seconds between animation frames
        """
        self.animation_frame_time = max(0.05, frame_time)  # Enforce minimum frame time

    def enable_animation(self, enabled: bool = True):
        """
        Enable or disable animation.

        Args:
            enabled: Whether animation should be enabled
        """
        self.animation_enabled = enabled

    def cleanup(self):
        """Clean up OpenGL resources"""
        for tile in self.tile_cache.values():
            tile.delete()  # Ensure all VBOs are deleted
        self.tile_cache.clear()
        self.current_positions.clear()
        self.dirty_tiles.clear()
        self.batch = pyglet.graphics.Batch()
