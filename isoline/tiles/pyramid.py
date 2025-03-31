"""
Pyramid Tile

Implements a PyramidTile with a geometric pyramid shape.
"""

import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class PyramidTile(VectorTile):
    """
    Pyramid tile with vector graphics representation.
    Renders a geometric pyramid with triangular sides.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_states: int = 1,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set a sandstone-like outline color
        self.outline_color = (204, 153, 102)  # Sandy/stone color
        self.content_color = (230, 190, 138)  # Lighter sandstone for faces
        self.shadow_color = (179, 134, 89)   # Darker sandstone for shadows
        
        # Calculate the pyramid peak height - make it proportional to the tile size
        self.peak_height = height * 1.5
        
        # Set up animation states (even static pyramids can have states for effects)
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for a geometric pyramid.

        Args:
            state: The animation state (can be used for lighting effects)

        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []

        # Define key points of the pyramid
        # Base rectangle corners (adjust to be within tile bounds)
        margin = self.width * 0.2  # 20% margin from the edge
        base_margin_y = self.height * 0.3  # 30% margin from the edge for y

        # Base vertices (bottom face)
        front_left = (margin, base_margin_y)  
        front_right = (self.width - margin, base_margin_y)
        back_left = (margin, self.height - base_margin_y)
        back_right = (self.width - margin, self.height - base_margin_y)
        
        # Peak (centered horizontally, and positioned at a height above the tile)
        peak_x = self.width / 2
        peak_y = self.height / 2
        
        # Calculate lighting effect based on state if animated
        # This can create a subtle shimmering/sunlight effect on the pyramid
        light_factor = 1.0
        if len(self.states) > 1:
            # Vary lighting slightly based on state
            light_factor = 0.9 + (state / (len(self.states) - 1)) * 0.2
            
        # Create each triangular face of the pyramid
        # Front face
        front_face_color = (
            min(255, int(self.content_color[0] * light_factor)),
            min(255, int(self.content_color[1] * light_factor)),
            min(255, int(self.content_color[2] * light_factor))
        )
        vertices.extend([
            front_left[0], front_left[1],
            front_right[0], front_right[1],
            peak_x, peak_y
        ])
        colors.extend(front_face_color * 3)  # 3 vertices in this triangle
        
        # Left face - slightly darker for shadow effect
        left_face_color = (
            min(255, int(self.shadow_color[0] * light_factor * 0.9)),
            min(255, int(self.shadow_color[1] * light_factor * 0.9)),
            min(255, int(self.shadow_color[2] * light_factor * 0.9))
        )
        vertices.extend([
            front_left[0], front_left[1],
            back_left[0], back_left[1],
            peak_x, peak_y
        ])
        colors.extend(left_face_color * 3)
        
        # Right face - slightly brighter
        right_face_color = (
            min(255, int(self.content_color[0] * light_factor * 1.1)),
            min(255, int(self.content_color[1] * light_factor * 1.1)),
            min(255, int(self.content_color[2] * light_factor * 1.1))
        )
        vertices.extend([
            front_right[0], front_right[1],
            back_right[0], back_right[1],
            peak_x, peak_y
        ])
        colors.extend(right_face_color * 3)
        
        # Back face
        back_face_color = (
            min(255, int(self.shadow_color[0] * light_factor)),
            min(255, int(self.shadow_color[1] * light_factor)),
            min(255, int(self.shadow_color[2] * light_factor))
        )
        vertices.extend([
            back_left[0], back_left[1],
            back_right[0], back_right[1],
            peak_x, peak_y
        ])
        colors.extend(back_face_color * 3)
        
        # Base of pyramid (optional - creates a flat bottom face)
        base_color = (
            min(255, int(self.content_color[0] * 0.8)),
            min(255, int(self.content_color[1] * 0.8)),
            min(255, int(self.content_color[2] * 0.8))
        )
        vertices.extend([
            front_left[0], front_left[1],
            front_right[0], front_right[1],
            back_right[0], back_right[1]
        ])
        colors.extend(base_color * 3)
        
        vertices.extend([
            front_left[0], front_left[1],
            back_left[0], back_left[1],
            back_right[0], back_right[1]
        ])
        colors.extend(base_color * 3)

        return {"vertices": vertices, "colors": colors}
