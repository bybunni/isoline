"""
Water Tile

Implements a WaterTile with animated waves.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class WaterTile(VectorTile):
    """
    Water tile with animated waves.
    """
    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_states: int = 5
    ):
        # Call parent constructor
        super().__init__(width, height)
        # Use a water-blue color for the outline
        self.outline_color = (0, 51, 102) # Darker blue outline
        self.content_color = (0, 102, 204) # Water blue content
        self.set_states(num_states)
        # Randomize starting frame
        self.current_state_index = random.randint(0, num_states - 1)
    
    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate vertex data for animated water.
        This example creates a simple sine-wave across the tile width.
        The vertex data should represent GL_LINES, so pairs of points.
        
        Args:
            state: The animation state for water rippling.
        
        Returns:
            A dict with 'vertices' and 'colors' lists.
        """
        vertices = []
        colors = []
        num_segments = 10 # Number of line segments for the wave
        wave_amplitude = 3.0  # Controls the vertical wave displacement
        
        # Compute phase offset based on state for animation
        if len(self.states) > 1:
            phase = (state / (len(self.states) - 1)) * 2 * math.pi
        else:
            phase = 0
            
        # Define the points for the wave line segments
        for i in range(num_segments):
            x1 = i * (self.width / num_segments)
            x2 = (i + 1) * (self.width / num_segments)
            
            # Calculate y-coordinates using sine function with phase shift
            y1 = self.height / 2 + math.sin(phase + (i / num_segments) * math.pi * 2) * wave_amplitude
            y2 = self.height / 2 + math.sin(phase + ((i + 1) / num_segments) * math.pi * 2) * wave_amplitude
            
            # Clamp y-coordinates to stay within tile height
            y1 = max(0, min(y1, self.height))
            y2 = max(0, min(y2, self.height))

            vertices.extend([x1, y1, x2, y2])
            
            # Use the content color for all segments
            colors.extend(self.content_color * 2) # Two vertices per line segment

        return {"vertices": vertices, "colors": colors}
