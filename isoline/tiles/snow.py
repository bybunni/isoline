"""
Snow Tile

Implements a SnowTile with animated falling snowflakes and drifting effects.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class SnowTile(VectorTile):
    """
    Snow tile with vector graphics representation.
    Renders snow with falling snowflakes and wind drift animation.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_snowflakes: int = 15,
        num_states: int = 5,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set snow-appropriate colors
        self.outline_color = (200, 210, 220)  # Subtle blue-gray outline
        self.content_color = (240, 245, 250)  # Almost white with hint of blue
        self.shadow_color = (200, 220, 235)   # Light blue for shadows
        
        # Number of snowflakes and their positions
        self.num_snowflakes = num_snowflakes
        self.snowflake_data = []
        
        # Pre-generate snowflake positions
        for _ in range(self.num_snowflakes):
            x = random.uniform(0.1, 0.9) * width
            y = random.uniform(0.1, 0.9) * height
            size = random.uniform(1.5, 3.5)  # Snowflake size variation
            rotation = random.uniform(0, math.pi * 2)  # Initial rotation
            fall_speed = random.uniform(0.5, 1.5)  # Vertical speed factor
            drift_factor = random.uniform(0.3, 1.0)  # Wind drift factor
            self.snowflake_data.append((x, y, size, rotation, fall_speed, drift_factor))
            
        # Create snow drifts - curves along the edges of the tile
        self.snow_drifts = []
        num_drifts = random.randint(3, 5)
        
        # Create several snow drifts (curved lines showing snow accumulation)
        for i in range(num_drifts):
            # Each drift is a sequence of points forming a curved line
            drift = []
            
            # Determine which edge this drift is near
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            
            # Number of points in this drift line
            num_points = random.randint(5, 8)
            
            # Create a curved drift line along the chosen edge
            for j in range(num_points):
                if edge == 'top':
                    x = (j / (num_points - 1)) * width
                    # Vary the height but keep near the top edge
                    y = height - random.uniform(0, height * 0.15)
                elif edge == 'bottom':
                    x = (j / (num_points - 1)) * width
                    # Vary the height but keep near the bottom edge
                    y = random.uniform(0, height * 0.15)
                elif edge == 'left':
                    y = (j / (num_points - 1)) * height
                    # Vary the width but keep near the left edge
                    x = random.uniform(0, width * 0.15)
                else:  # right
                    y = (j / (num_points - 1)) * height
                    # Vary the width but keep near the right edge
                    x = width - random.uniform(0, width * 0.15)
                
                # Add some random variation to create more natural curves
                if edge in ['top', 'bottom']:
                    x += random.uniform(-width * 0.05, width * 0.05)
                else:
                    y += random.uniform(-height * 0.05, height * 0.05)
                
                drift.append((x, y))
                
            self.snow_drifts.append(drift)
        
        # Set up animation states
        self.set_states(num_states)
    
    def _create_snowflake(self, x, y, size, rotation, vertices, colors):
        """Helper method to create a snowflake at the given position"""
        # Create a simple asterisk-like snowflake
        # Main cross
        vertices.extend([
            x - size, y,
            x + size, y
        ])
        vertices.extend([
            x, y - size,
            x, y + size
        ])
        
        # Diagonal arms (rotated 45 degrees)
        diag_size = size * 0.7  # Slightly shorter than the main cross
        vertices.extend([
            x - diag_size * math.cos(rotation), y - diag_size * math.sin(rotation),
            x + diag_size * math.cos(rotation), y + diag_size * math.sin(rotation)
        ])
        vertices.extend([
            x - diag_size * math.sin(rotation), y + diag_size * math.cos(rotation),
            x + diag_size * math.sin(rotation), y - diag_size * math.cos(rotation)
        ])
        
        # Use bright white color for all snowflake lines
        bright_white = (255, 255, 255)
        colors.extend(bright_white * 8)  # 8 vertices total (4 lines)
    
    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for snow with animated snowfall.
        
        Args:
            state: The animation state (used to animate falling snow and wind)
            
        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []
        
        # Calculate animation factors based on state
        if len(self.states) <= 1:
            drift_factor = 0.0
            fall_factor = 0.0
        else:
            # Wind drift animation - use sine wave for natural back-and-forth
            wind_angle = (state / (len(self.states) - 1)) * 2 * math.pi
            drift_factor = math.sin(wind_angle)
            
            # Falling snow animation - increases with each state
            fall_factor = (state / (len(self.states) - 1))
        
        # Draw base snow layer (simple lines to create texture)
        num_lines = 20
        for i in range(num_lines):
            # Create short horizontal lines with slight variation
            x1 = random.uniform(0.1, 0.4) * self.width
            y1 = (i / num_lines) * self.height
            
            # Add small variations based on state to simulate subtle shifting
            x1 += math.sin(state * 0.2 + i * 0.5) * 1.5
            y1 += math.cos(state * 0.2 + i * 0.3) * 1.0
            
            # Line length varies slightly
            length = random.uniform(5, 15)
            x2 = x1 + length
            y2 = y1 + random.uniform(-1, 1)
            
            # Create snow texture line
            vertices.extend([x1, y1, x2, y2])
            
            # Create color with variation - slightly different shades of white
            brightness = 0.95 + 0.05 * math.sin(i + state * 0.1)
            snow_color = (
                int(self.content_color[0] * brightness),
                int(self.content_color[1] * brightness),
                int(self.content_color[2] * brightness)
            )
            
            colors.extend(snow_color * 2)  # 2 vertices per line
        
        # Draw snow drifts (edges with accumulated snow)
        for drift in self.snow_drifts:
            # Draw connected line segments for each drift
            for i in range(len(drift) - 1):
                x1, y1 = drift[i]
                x2, y2 = drift[i + 1]
                
                # Add subtle animation to the drifts
                # More movement near the edges, less in the middle
                edge_factor = min(abs(x1 - self.width/2), abs(x2 - self.width/2)) / (self.width/2)
                drift_amplitude = edge_factor * 1.5
                
                # Apply the drift motion
                y1_offset = drift_amplitude * math.sin(drift_factor * math.pi * 2 + i * 0.5)
                y2_offset = drift_amplitude * math.sin(drift_factor * math.pi * 2 + (i+1) * 0.5)
                
                # Draw the drift segment
                vertices.extend([x1, y1 + y1_offset, x2, y2 + y2_offset])
                
                # Slightly brighter white for drifts
                drift_color = (245, 250, 255)  # Nearly pure white
                colors.extend(drift_color * 2)  # 2 vertices per line
        
        # Draw snowflakes (falling with wind effect)
        for base_x, base_y, size, rotation, fall_speed, drift_speed in self.snowflake_data:
            # Calculate snowflake position based on animation state
            # Snowflakes fall downward and drift with the wind
            fall_distance = fall_speed * fall_factor * self.height
            drift_distance = drift_speed * drift_factor * (self.width * 0.1)
            
            # Calculate current position with wrapping for continuous animation
            current_y = (base_y - fall_distance) % self.height
            current_x = (base_x + drift_distance) % self.width
            
            # Adjust rotation based on state
            current_rotation = rotation + (state / len(self.states)) * math.pi
            
            # Add the snowflake to our vertex data
            self._create_snowflake(current_x, current_y, size, current_rotation, vertices, colors)
            
        return {"vertices": vertices, "colors": colors}
