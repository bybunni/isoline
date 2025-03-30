"""
Sand Tile

Implements a SandTile with subtle grain animation for beaches, river banks, or deserts.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class SandTile(VectorTile):
    """
    Sand tile with subtle grain animation.
    Can be used for beaches, river banks, or desert environments.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_grains: int = 15,
        num_states: int = 1,  # Set to 1 for static (non-animated) tile
    ):
        self.num_grains = num_grains
        # Random seed ensures same sand grain pattern for each tile instance
        self.grain_positions = []

        # Pre-generate grain positions
        for _ in range(self.num_grains):
            x = random.uniform(0.1, 0.9) * width
            y = random.uniform(0.1, 0.9) * height
            size = random.uniform(1.5, 3.0)  # Grain size
            self.grain_positions.append((x, y, size))

        # Call parent constructor
        super().__init__(width, height)
        
        # Set sand-specific colors with faint outline
        self.outline_color = (139, 115, 85)  # Muted sandy brown outline
        self.content_color = (237, 201, 175)  # Desert sand color
        
        # Set to a single state (static, not animated)
        self.set_states(1)
        self.animated = False  # Explicitly mark as non-animated

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for sand grains.
        This is a static (non-animated) implementation with a single frame.

        Args:
            state: The animation state (ignored in this static implementation)

        Returns:
            Dict with vertices and colors for sand grains
        """
        vertices = []
        colors = []

        # No shifting in static implementation
        shift_x = 0
        shift_y = 0

        # Draw sand grains with varying positions based on animation state
        for grain_x, grain_y, size in self.grain_positions:
            # For static implementation, no shifting is applied
            # Just use the original grain positions
            shifted_x = grain_x
            shifted_y = grain_y
            
            # Draw a small dot for each sand grain
            # Using a very small "+" shape to represent grains
            half_size = size / 2.0
            
            # Horizontal line of the +
            vertices.extend([
                shifted_x - half_size, shifted_y,
                shifted_x + half_size, shifted_y
            ])
            
            # Vertical line of the +
            vertices.extend([
                shifted_x, shifted_y - half_size,
                shifted_x, shifted_y + half_size
            ])

            # Vary the sand color slightly for visual interest
            # Subtle variation in the yellow/brown tone
            color_r = 230 + random.randint(-20, 10)
            color_g = 190 + random.randint(-15, 15)
            color_b = 140 + random.randint(-10, 20)
                
            grain_color = (color_r, color_g, color_b)
            
            # Add colors for the 4 vertices (2 lines with 2 points each)
            colors.extend(grain_color * 4)

        return {"vertices": vertices, "colors": colors}
