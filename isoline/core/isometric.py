"""
Isometric projection utilities for the Isoline engine.
"""


class IsometricProjection:
    """
    Handles conversion between map coordinates and screen coordinates
    using standard isometric projection.
    """

    def __init__(self, tile_width=128, tile_height=64):
        """
        Initialize the isometric projection with tile dimensions.

        Args:
            tile_width: Width of a tile in pixels (default: 128)
            tile_height: Height of a tile in pixels (default: 64)
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tile_width_half = tile_width // 2
        self.tile_height_half = tile_height // 2

    def map_to_screen(self, map_x, map_y):
        """
        Convert map coordinates to screen coordinates.

        Args:
            map_x: X position in map coordinates
            map_y: Y position in map coordinates

        Returns:
            tuple: (screen_x, screen_y)
        """
        screen_x = (map_x - map_y) * self.tile_width_half
        screen_y = (map_x + map_y) * self.tile_height_half
        return screen_x, screen_y

    def screen_to_map(self, screen_x, screen_y):
        """
        Convert screen coordinates to map coordinates.

        Args:
            screen_x: X position in screen coordinates
            screen_y: Y position in screen coordinates

        Returns:
            tuple: (map_x, map_y)
        """
        map_x = (screen_x / self.tile_width_half + screen_y / self.tile_height_half) / 2
        map_y = (screen_y / self.tile_height_half - screen_x / self.tile_width_half) / 2
        return map_x, map_y

    def map_to_screen_vector(self, start_map_x, start_map_y, end_map_x, end_map_y):
        """
        Convert a vector from map coordinates to screen coordinates.

        Args:
            start_map_x: Starting X position in map coordinates
            start_map_y: Starting Y position in map coordinates
            end_map_x: Ending X position in map coordinates
            end_map_y: Ending Y position in map coordinates

        Returns:
            tuple: (start_screen_x, start_screen_y, end_screen_x, end_screen_y)
        """
        start_screen_x, start_screen_y = self.map_to_screen(start_map_x, start_map_y)
        end_screen_x, end_screen_y = self.map_to_screen(end_map_x, end_map_y)
        return start_screen_x, start_screen_y, end_screen_x, end_screen_y
