"""
Forest Tile

Implements a ForestTile with stylized trees and animated swaying foliage.
"""

import random
import math
from typing import Dict, List, Tuple

from isoline.vector_tile import VectorTile


class ForestTile(VectorTile):
    """
    Forest tile with vector graphics representation.
    Renders stylized trees with animated swaying foliage.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_trees: int = 5,
        num_states: int = 5,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set forest-appropriate colors
        self.outline_color = (25, 60, 25)  # Dark green outline
        self.trunk_color = (95, 65, 30)     # Brown for trunks
        self.foliage_color = (40, 120, 40)  # Green for foliage
        self.highlight_color = (65, 160, 65)  # Lighter green for highlights
        self.ground_color = (50, 90, 30)    # Darker green for ground
        
        # Number of trees and their positions
        self.num_trees = num_trees
        self.tree_data = []
        
        # Pre-generate tree positions and characteristics
        margin = width * 0.1  # Keep trees away from edges
        
        for _ in range(self.num_trees):
            # Tree position
            x = random.uniform(margin, width - margin)
            y = random.uniform(margin, height - margin)
            
            # Tree size
            trunk_height = random.uniform(10, 20)
            trunk_width = random.uniform(1.5, 3.0)
            
            # Tree shape
            tree_type = random.choice(['pine', 'deciduous'])
            
            # Foliage characteristics
            if tree_type == 'pine':
                # Pine trees have triangular layers
                num_layers = random.randint(2, 4)
                layer_widths = []
                for i in range(num_layers):
                    # Layers get narrower toward the top
                    layer_factor = 1.0 - (i / num_layers) * 0.5
                    layer_widths.append(random.uniform(7, 12) * layer_factor)
            else:
                # Deciduous trees have a more rounded canopy
                num_layers = 1
                layer_widths = [random.uniform(8, 15)]
            
            # Unique phase for animation
            phase = random.uniform(0, math.pi * 2)
            
            # Sway amplitude - how much the foliage moves
            sway_factor = random.uniform(0.8, 1.2)
            
            self.tree_data.append((x, y, trunk_height, trunk_width, tree_type, 
                                   num_layers, layer_widths, phase, sway_factor))
        
        # Generate some ground details (grass tufts, small plants)
        self.ground_details = []
        num_details = random.randint(10, 15)
        
        for _ in range(num_details):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            size = random.uniform(1, 3)
            detail_type = random.choice(['tuft', 'plant'])
            self.ground_details.append((x, y, size, detail_type))
        
        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for forest with animated trees.
        
        Args:
            state: The animation state (used to animate swaying foliage)
            
        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []
        
        # Calculate animation factor based on state
        if len(self.states) <= 1:
            sway_factor = 0.0
        else:
            # Use sine wave to create natural swaying motion
            sway_angle = (state / (len(self.states) - 1)) * 2 * math.pi
            sway_factor = math.sin(sway_angle)
        
        # Draw ground details first (they'll be behind the trees)
        for x, y, size, detail_type in self.ground_details:
            if detail_type == 'tuft':
                # Simple grass tuft (3 short lines)
                for i in range(3):
                    angle = (i / 3) * math.pi + random.uniform(-0.2, 0.2)
                    # Add slight animation to grass
                    angle += sway_factor * 0.2
                    
                    dx = math.cos(angle) * size
                    dy = math.sin(angle) * size
                    
                    vertices.extend([x, y, x + dx, y + dy])
                    
                    # Vary the green shade slightly
                    green_shade = (
                        self.ground_color[0],
                        self.ground_color[1] + random.randint(-10, 10),
                        self.ground_color[2]
                    )
                    colors.extend(green_shade * 2)  # 2 vertices per line
            else:  # plant
                # Small plant (simple cross)
                vertices.extend([x - size, y, x + size, y])  # Horizontal line
                vertices.extend([x, y - size, x, y + size])  # Vertical line
                
                # Slightly brighter than ground
                plant_color = (
                    self.ground_color[0],
                    min(255, self.ground_color[1] + 20),
                    self.ground_color[2]
                )
                colors.extend(plant_color * 4)  # 4 vertices total
        
        # Draw each tree
        for (x, y, trunk_height, trunk_width, tree_type, num_layers, 
             layer_widths, phase, tree_sway_factor) in self.tree_data:
            
            # Calculate current sway based on animation state and this tree's phase
            current_sway = sway_factor * tree_sway_factor
            
            # Apply a unique phase to each tree so they don't all sway together
            current_sway *= math.cos(phase + (state / len(self.states)) * math.pi)
            
            # Draw tree trunk
            trunk_top_y = y + trunk_height
            
            # Left side of trunk
            vertices.extend([
                x - trunk_width/2, y,  # Bottom left
                x - trunk_width/2, trunk_top_y  # Top left
            ])
            
            # Right side of trunk
            vertices.extend([
                x + trunk_width/2, y,  # Bottom right
                x + trunk_width/2, trunk_top_y  # Top right
            ])
            
            # Add trunk color
            colors.extend(self.trunk_color * 4)  # 4 vertices for trunk
            
            # Draw foliage based on tree type
            if tree_type == 'pine':
                # Draw triangular layers for pine tree
                for i in range(num_layers):
                    layer_width = layer_widths[i]
                    
                    # Calculate height of this layer - higher layers are placed above lower ones
                    layer_y = trunk_top_y + (i * layer_width * 0.8)
                    
                    # Apply sway effect - more at the top, less at the bottom
                    # This creates a realistic bending effect
                    sway_x = current_sway * (i + 1) * 1.5
                    
                    # Draw triangle for this layer
                    vertices.extend([
                        x - layer_width/2 + sway_x * 0.7, layer_y,  # Bottom left
                        x + layer_width/2 + sway_x * 0.7, layer_y,  # Bottom right
                        x + sway_x, layer_y + layer_width  # Top point
                    ])
                    
                    # Vary the color slightly for each layer - higher layers are lighter
                    brightness = 1.0 + (i / num_layers) * 0.2
                    layer_color = (
                        min(255, int(self.foliage_color[0] * brightness)),
                        min(255, int(self.foliage_color[1] * brightness)),
                        min(255, int(self.foliage_color[2] * brightness))
                    )
                    colors.extend(layer_color * 3)  # 3 vertices per triangle
            else:  # deciduous
                # Draw a more rounded canopy for deciduous tree
                layer_width = layer_widths[0]
                
                # Apply sway effect
                sway_x = current_sway * 3.0
                
                # Create several "wedges" to form a rounded canopy
                num_wedges = 7
                for i in range(num_wedges):
                    angle_start = (i / num_wedges) * math.pi * 2
                    angle_end = ((i+1) / num_wedges) * math.pi * 2
                    
                    # Calculate points for the wedge
                    dx1 = math.cos(angle_start) * layer_width/2
                    dy1 = math.sin(angle_start) * layer_width/2
                    
                    dx2 = math.cos(angle_end) * layer_width/2
                    dy2 = math.sin(angle_end) * layer_width/2
                    
                    # Apply more sway to the top of the canopy, less to the sides
                    sway_x1 = sway_x * math.sin(angle_start)
                    sway_x2 = sway_x * math.sin(angle_end)
                    
                    canopy_y = trunk_top_y + layer_width * 0.3
                    
                    # Draw a triangle for each wedge of the canopy
                    vertices.extend([
                        x, canopy_y,  # Center point
                        x + dx1 + sway_x1, canopy_y + dy1,  # Outer edge point 1
                        x + dx2 + sway_x2, canopy_y + dy2   # Outer edge point 2
                    ])
                    
                    # Vary the color based on angle to create simple lighting effect
                    brightness = 0.9 + 0.2 * math.sin(angle_start)
                    wedge_color = (
                        min(255, int(self.foliage_color[0] * brightness)),
                        min(255, int(self.foliage_color[1] * brightness)),
                        min(255, int(self.foliage_color[2] * brightness))
                    )
                    colors.extend(wedge_color * 3)  # 3 vertices per wedge
            
        return {"vertices": vertices, "colors": colors}
