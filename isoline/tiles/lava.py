"""
Lava Tile

Implements a LavaTile with animated flowing lava and bubbling effects.
"""

import random
import math
from typing import Dict, List

from isoline.vector_tile import VectorTile


class LavaTile(VectorTile):
    """
    Lava tile with vector graphics representation.
    Renders animated flowing lava with bubbling effects.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_bubbles: int = 8,
        num_states: int = 5,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set lava-appropriate colors
        self.outline_color = (80, 0, 0)  # Dark red outline
        self.content_color = (255, 80, 0)  # Bright orange-red
        self.highlight_color = (255, 200, 0)  # Yellow-orange for hotspots
        
        # Number of bubbles and their positions
        self.num_bubbles = num_bubbles
        self.bubble_positions = []
        
        # Pre-generate bubble positions
        for _ in range(self.num_bubbles):
            x = random.uniform(0.2, 0.8) * width
            y = random.uniform(0.2, 0.8) * height
            size = random.uniform(3, 8)  # Bubble size
            self.bubble_positions.append((x, y, size))
            
        # Create flow lines - these are the main "veins" of lava flow
        self.flow_lines = []
        num_flows = random.randint(3, 6)
        
        for _ in range(num_flows):
            # Create a random curved flow line with 3-5 points
            num_points = random.randint(3, 5)
            flow_line = []
            
            # Start at a random edge point
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x = random.uniform(0.2, 0.8) * width
                y = height
            elif edge == 'bottom':
                x = random.uniform(0.2, 0.8) * width
                y = 0
            elif edge == 'left':
                x = 0
                y = random.uniform(0.2, 0.8) * height
            else:  # right
                x = width
                y = random.uniform(0.2, 0.8) * height
                
            flow_line.append((x, y))
            
            # Create intermediate points for the flow
            for i in range(1, num_points - 1):
                x = random.uniform(0.2, 0.8) * width
                y = random.uniform(0.2, 0.8) * height
                flow_line.append((x, y))
            
            # End at a different random edge point
            end_edge = random.choice(['top', 'bottom', 'left', 'right'])
            while end_edge == edge:  # Make sure it's not the same as the start
                end_edge = random.choice(['top', 'bottom', 'left', 'right'])
                
            if end_edge == 'top':
                x = random.uniform(0.2, 0.8) * width
                y = height
            elif end_edge == 'bottom':
                x = random.uniform(0.2, 0.8) * width
                y = 0
            elif end_edge == 'left':
                x = 0
                y = random.uniform(0.2, 0.8) * height
            else:  # right
                x = width
                y = random.uniform(0.2, 0.8) * height
                
            flow_line.append((x, y))
            self.flow_lines.append(flow_line)
        
        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for flowing lava with bubbling effects.
        
        Args:
            state: The animation state (used to vary flow and bubble animations)
            
        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []
        
        # Calculate animation factors based on state
        if len(self.states) <= 1:
            bubble_factor = 1.0
            flow_factor = 0.0
        else:
            # Use state to create bubble pulsing
            bubble_angle = (state / (len(self.states) - 1)) * 2 * math.pi
            bubble_factor = 0.7 + 0.3 * math.sin(bubble_angle)
            
            # Use state to animate flow direction
            flow_factor = state / (len(self.states) - 1)
        
        # Draw lava background (cracks and surface)
        # These are irregular lines that fill the tile to represent lava surface
        num_cracks = 12
        for i in range(num_cracks):
            # Create an irregular line that changes slightly with animation state
            start_x = random.uniform(0.1, 0.3) * self.width
            start_y = (i / num_cracks) * self.height
            
            # Add some variation based on state
            start_x += math.sin(state * 0.5 + i) * 2.0
            
            end_x = random.uniform(0.7, 0.9) * self.width
            end_y = start_y + random.uniform(-5, 5)
            
            # Add some variation based on state
            end_x += math.cos(state * 0.5 + i) * 2.0
            
            # Create crack line
            vertices.extend([start_x, start_y, end_x, end_y])
            
            # Create color with variation - darker cracks
            r = min(255, int(self.content_color[0] * (0.6 + 0.2 * math.sin(i + state * 0.3))))
            g = min(255, int(self.content_color[1] * (0.6 + 0.2 * math.sin(i + state * 0.3))))
            b = min(255, int(self.content_color[2] * (0.6 + 0.2 * math.sin(i + state * 0.3))))
            
            crack_color = (r, g, b)
            colors.extend(crack_color * 2)  # 2 vertices per line
        
        # Draw lava flows (veins of brighter lava)
        for flow_line in self.flow_lines:
            for i in range(len(flow_line) - 1):
                x1, y1 = flow_line[i]
                x2, y2 = flow_line[i + 1]
                
                # Animate flow direction with state
                direction = 1 if i % 2 == 0 else -1
                x1_offset = direction * math.sin(flow_factor * math.pi * 2) * 3
                y1_offset = direction * math.cos(flow_factor * math.pi * 2) * 1.5
                
                x2_offset = -direction * math.sin(flow_factor * math.pi * 2) * 3
                y2_offset = -direction * math.cos(flow_factor * math.pi * 2) * 1.5
                
                # Draw the flow segment
                vertices.extend([x1 + x1_offset, y1 + y1_offset, x2 + x2_offset, y2 + y2_offset])
                
                # Brighter color for flows
                brightness = 0.8 + 0.2 * math.sin(state / len(self.states) * math.pi * 2)
                flow_color = (
                    min(255, int(self.highlight_color[0] * brightness)),
                    min(255, int(self.highlight_color[1] * brightness)),
                    min(255, int(self.highlight_color[2] * brightness))
                )
                colors.extend(flow_color * 2)  # 2 vertices per line
        
        # Draw bubbles (bright spots that pulse with animation)
        for bubble_x, bubble_y, bubble_size in self.bubble_positions:
            # Calculate bubble animation
            # Bubbles grow and shrink based on state, and also shift position slightly
            current_size = bubble_size * bubble_factor
            
            # Generate a unique phase offset for each bubble
            phase_offset = hash(f"{bubble_x:.1f}_{bubble_y:.1f}") % 100 / 100.0
            bubble_phase = (flow_factor + phase_offset) % 1.0
            
            # Move bubble upward based on phase (bubbles rise)
            bubble_y_offset = bubble_phase * self.height * 0.1
            if bubble_y + bubble_y_offset > self.height:
                # Reset bubble at bottom when it reaches the top
                bubble_y_offset = -(self.height * 0.9)
                
            # Draw bubble as a small cross (simpler than a circle for vector graphics)
            vertices.extend([
                bubble_x - current_size, bubble_y + bubble_y_offset,
                bubble_x + current_size, bubble_y + bubble_y_offset
            ])
            vertices.extend([
                bubble_x, bubble_y + bubble_y_offset - current_size,
                bubble_x, bubble_y + bubble_y_offset + current_size
            ])
            
            # Very bright color for bubbles
            brightness = 0.8 + 0.2 * math.sin((state / len(self.states) + phase_offset) * math.pi * 4)
            bubble_color = (
                255,  # Always maximum red
                min(255, int(240 * brightness)),
                min(255, int(100 * brightness))
            )
            
            # Add colors for both lines of the cross
            colors.extend(bubble_color * 4)  # 4 vertices total
            
        return {"vertices": vertices, "colors": colors}
