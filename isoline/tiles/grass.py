"""
Grass Tile

Implements a GrassTile with animated grass blades.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class GrassTile(VectorTile):
    """
    Grass tile with vector graphics representation.
    Optimized version using vertex data caching.
    Supports animation with swaying grass.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_blades: int = 15,
        num_states: int = 5,
    ):
        self.num_blades = num_blades
        # Random seed ensures same grass pattern for each tile instance
        self.blade_positions = []

        # Pre-generate blade positions
        for _ in range(self.num_blades):
            x = random.uniform(0.25, 0.75) * width
            y = random.uniform(0.25, 0.75) * height
            height_blade = random.uniform(5, 15)  # Blade height
            self.blade_positions.append((x, y, height_blade))

        # Call parent constructor
        super().__init__(width, height)
        
        # Set a faint green outline color
        self.outline_color = (34, 85, 34)  # Muted dark green outline

        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for grass blades.
        Different states create a swaying animation effect.

        Args:
            state: The animation state (used to vary blade angles)

        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []

        # Determine the sway factor based on animation state
        # This creates a gentle swaying pattern across animation frames
        max_sway = 3.0  # Maximum pixel offset for swaying
        if len(self.states) <= 1:
            sway_factor = 0
        else:
            # Calculate a unique sway factor for each state
            # Use sine wave to create smooth transitions
            angle = (state / (len(self.states) - 1)) * 2 * math.pi
            sway_factor = math.sin(angle) * max_sway

        # Draw grass blades with varying heights and sway angles
        for blade_x, blade_y, height in self.blade_positions:
            # Clamp the grass blade root to be within tile boundaries
            base_x = max(0, min(blade_x, self.width))
            base_y = max(0, min(blade_y, self.height))

            # Apply a unique sway to each blade based on its original position and the current state
            # Using hash of original position ensures consistent sway direction for each blade
            blade_sway = (
                sway_factor
                * (((hash(f"{blade_x:.1f}_{blade_y:.1f}") % 100) / 100.0) - 0.5)
                * 2.0
            )
            
            # Clamp the blade sway so the tip stays within horizontal boundaries relative to the clamped root
            max_sway_left = base_x  # maximum left offset from the clamped root
            max_sway_right = self.width - base_x  # maximum right offset from the clamped root
            adjusted_sway = max(-max_sway_left, min(blade_sway, max_sway_right))

            # Adjust blade height to ensure the tip does not exceed vertical boundary
            adjusted_height = min(height, self.height - base_y)

            # Each blade is a line from its clamped root to the tip with adjusted sway and height
            vertices.extend([base_x, base_y, base_x + adjusted_sway, base_y + adjusted_height])

            # Slightly randomize green shade for visual interest
            # Make the green slightly brighter in middle animation states for subtle effect
            green_factor = 1.0
            if len(self.states) > 1:
                mid_state = len(self.states) // 2
                distance_from_mid = abs(state - mid_state)
                green_factor = 1.0 - (distance_from_mid / (len(self.states) * 2))

            green = min(255, int(204 * (0.9 + green_factor * 0.2)))
            blade_color = (0, green, 0)

            # Add color for each vertex in the line (2 vertices per blade)
            colors.extend(blade_color * 2)

        return {"vertices": vertices, "colors": colors}
