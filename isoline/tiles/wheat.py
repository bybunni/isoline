"""
Wheat Field Tile

Implements a WheatFieldTile with animated swaying wheat stalks.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class WheatFieldTile(VectorTile):
    """
    Wheat field tile with vector graphics representation.
    Renders wheat stalks with animated rippling/swaying effects.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_stalks: int = 30,
        num_states: int = 5,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set wheat-appropriate colors
        self.outline_color = (120, 100, 40)  # Darker wheat outline
        self.stalk_color = (220, 190, 100)   # Golden wheat color
        self.head_color = (240, 210, 120)    # Lighter color for wheat heads
        self.soil_color = (120, 90, 60)      # Brown for soil
        
        # Number of wheat stalks and their positions
        self.num_stalks = num_stalks
        self.stalk_data = []
        
        # Pre-generate stalk positions and characteristics
        for _ in range(self.num_stalks):
            x = random.uniform(0.1, 0.9) * width
            y = random.uniform(0.1, 0.9) * height
            height_stalk = random.uniform(8, 15)  # Stalk height
            lean_angle = random.uniform(-0.1, 0.1)  # Base leaning angle in radians
            head_size = random.uniform(2, 3.5)  # Size of wheat head
            
            # Unique phase for wave-like animation
            phase = random.uniform(0, math.pi * 2)
            
            # Sway amplitude - how much the stalk moves
            # Using a smaller range (0.4-0.8) for more subtle movement
            sway_factor = random.uniform(0.4, 0.8)
            
            self.stalk_data.append((x, y, height_stalk, lean_angle, head_size, phase, sway_factor))
        
        # Generate soil furrows (rows in the soil)
        self.furrows = []
        num_furrows = random.randint(6, 8)
        
        for i in range(num_furrows):
            # Starting points for furrow
            y_pos = (i / num_furrows) * height
            x_start = random.uniform(0, width * 0.1)
            x_end = width - random.uniform(0, width * 0.1)
            
            # Add some wavy variation
            y_variation = []
            num_segments = random.randint(3, 5)
            for j in range(num_segments + 1):
                # Create gentle undulation in furrow
                y_var = random.uniform(-2, 2)
                y_variation.append(y_var)
                
            self.furrows.append((x_start, x_end, y_pos, y_variation, num_segments))
        
        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for wheat field with animated stalks.
        
        Args:
            state: The animation state (used for rippling wave effect)
            
        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []
        
        # Calculate animation factors based on state
        if len(self.states) <= 1:
            wave_factor = 0.0
        else:
            # Use animation state to create a rippling wave effect across the field
            wave_angle = (state / (len(self.states) - 1)) * 2 * math.pi
            wave_factor = math.sin(wave_angle)
        
        # Draw soil and furrows first
        for x_start, x_end, y_base, y_variations, num_segments in self.furrows:
            # Draw segments to create the furrow
            segment_length = (x_end - x_start) / num_segments
            
            for i in range(num_segments):
                x1 = x_start + i * segment_length
                x2 = x_start + (i + 1) * segment_length
                
                # Apply y variation for natural look
                y1 = y_base + y_variations[i]
                y2 = y_base + y_variations[i + 1]
                
                # Add slight animation to furrows
                y1 += wave_factor * 0.5 * math.sin(x1 / self.width * math.pi)
                y2 += wave_factor * 0.5 * math.sin(x2 / self.width * math.pi)
                
                # Draw furrow segment
                vertices.extend([x1, y1, x2, y2])
                
                # Vary the color slightly for visual interest
                darkness = 0.9 + 0.1 * math.sin(i + state * 0.1)
                furrow_color = (
                    int(self.soil_color[0] * darkness),
                    int(self.soil_color[1] * darkness),
                    int(self.soil_color[2] * darkness)
                )
                colors.extend(furrow_color * 2)  # 2 vertices per line
        
        # Draw wheat stalks
        for x, y, height_stalk, lean_angle, head_size, phase, sway_factor in self.stalk_data:
            # Calculate wave effect - stalks move in a wave pattern across the field
            # Using position-dependent phase creates a rippling effect
            position_phase = (x / self.width) * math.pi * 2
            
            # Calculate current sway angle with reduced amplitude
            # Limit the maximum sway to make it more realistic
            # Use a much smaller multiplier (0.15 instead of 1.0) to reduce the sway angle
            sway_angle = lean_angle + sway_factor * 0.15 * wave_factor * math.sin(position_phase + phase)
            
            # Calculate top of stalk position with sway
            stalk_top_x = x + math.sin(sway_angle) * height_stalk
            stalk_top_y = y + math.cos(sway_angle) * height_stalk
            
            # Draw stalk (main stem)
            vertices.extend([x, y, stalk_top_x, stalk_top_y])
            colors.extend(self.stalk_color * 2)  # 2 vertices for stalk
            
            # Draw wheat head (a small shape at the top of the stalk)
            # For simplicity, we'll use a small cross shape
            vertices.extend([
                stalk_top_x - head_size * 0.5, stalk_top_y,
                stalk_top_x + head_size * 0.5, stalk_top_y
            ])
            
            # Create angled lines for wheat grains
            angle1 = sway_angle + math.pi/4
            angle2 = sway_angle - math.pi/4
            
            vertices.extend([
                stalk_top_x, stalk_top_y,
                stalk_top_x + math.sin(angle1) * head_size, 
                stalk_top_y + math.cos(angle1) * head_size
            ])
            
            vertices.extend([
                stalk_top_x, stalk_top_y,
                stalk_top_x + math.sin(angle2) * head_size, 
                stalk_top_y + math.cos(angle2) * head_size
            ])
            
            # Wheat head color
            colors.extend(self.head_color * 6)  # 6 vertices for wheat head (3 lines)
            
            # Optional: Add some small lines to represent awns (the bristles on wheat)
            # These are small decorative details that make it look more wheat-like
            num_awns = 3
            for i in range(num_awns):
                awn_angle = sway_angle + math.pi/3 - (i / (num_awns-1)) * 2 * math.pi/3
                
                awn_length = head_size * 0.7
                
                awn_x = stalk_top_x + math.sin(awn_angle) * awn_length
                awn_y = stalk_top_y + math.cos(awn_angle) * awn_length
                
                vertices.extend([stalk_top_x, stalk_top_y, awn_x, awn_y])
                
                # Use a slightly more golden color for the awns
                awn_color = (min(255, self.head_color[0] + 10), 
                             min(255, self.head_color[1] + 5),
                             self.head_color[2])
                colors.extend(awn_color * 2)  # 2 vertices per awn
            
        return {"vertices": vertices, "colors": colors}
