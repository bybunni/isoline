"""
Tile Renderer

Handles rendering of individual tiles using vector graphics
in the style of old monochrome green CRTs.
"""

import random
import numpy as np
import pyglet
from pyglet import shapes


class VectorTile:
    """Base class for vector-drawn tiles"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Default colors
        self.outline_color = (0, 51, 0)  # Dark green
        self.content_color = (0, 204, 0)  # Bright green

        # Initialize shapes
        self._create_shapes()

    def _create_shapes(self):
        """Generate shapes for the tile - override in subclasses"""
        # Create outline points
        self.outline_points = [
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0),
        ]

        # Create content shapes - override in subclasses
        self.content_shapes = []

    def draw(self, x: float, y: float):
        """Draw the tile at the specified position"""
        # Draw outline
        for i in range(len(self.outline_points) - 1):
            x1, y1 = self.outline_points[i]
            x2, y2 = self.outline_points[i + 1]
            line = shapes.Line(x1 + x, y1 + y, x2 + x, y2 + y, color=self.outline_color)
            line.draw()

        # Draw content shapes
        for shape in self.content_shapes:
            # Adjust position of each shape
            shape.x += x
            shape.y += y
            shape.draw()
            # Reset position for next time
            shape.x -= x
            shape.y -= y

    def delete(self):
        """Clean up resources"""
        pass  # No explicit resources to clean up


class GrassTile(VectorTile):
    """Grass tile with vector graphics representation"""

    def __init__(self, width: int = 100, height: int = 50, num_blades: int = 30):
        self.num_blades = num_blades
        # Call parent constructor which will set up colors and then call _create_shapes
        super().__init__(width, height)

    def _create_shapes(self):
        """Generate grass blades as vertical lines"""
        # First create the outline
        super()._create_shapes()

        # Create grass blade shapes
        self.content_shapes = []
        for _ in range(self.num_blades):
            x = random.uniform(0.1, 0.9) * self.width
            y = random.uniform(0.1, 0.9) * self.height
            height = random.uniform(5, 15)  # Blade height

            # Line constructor parameters: x1, y1, x2, y2, color
            blade = shapes.Line(
                x, y, x, y + height, color=self.content_color, thickness=1.5
            )
            self.content_shapes.append(blade)


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type == "G":  # Grass
        return GrassTile(width, height)
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
