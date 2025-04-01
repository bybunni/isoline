"""
Box Stack Tile

Implements a BoxStackTile with 3D stacked crates/containers.
"""

import random
import math
from typing import Dict, List, Tuple

from isoline.vector_tile import VectorTile


class BoxStackTile(VectorTile):
    """
    Box Stack tile with vector graphics representation.
    Renders stacked boxes/crates with 3D perspective.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_states: int = 3,
    ):
        # Call parent constructor
        super().__init__(width, height)
        
        # Set box-appropriate colors
        self.outline_color = (50, 50, 50)    # Dark gray outline
        self.box_colors = [
            (180, 130, 80),   # Brown wooden crate
            (150, 150, 150),  # Gray metal container
            (80, 120, 160),   # Blue shipping container
            (160, 80, 80),    # Red shipping container
        ]
        
        # Generate a random stack layout
        self.boxes = []
        
        # Define box dimensions
        self.min_box_width = width * 0.2
        self.max_box_width = width * 0.45
        self.min_box_height = height * 0.15
        self.max_box_height = height * 0.3
        self.min_box_depth = width * 0.2
        self.max_box_depth = width * 0.4
        
        # How many layers of boxes
        self.num_layers = random.randint(1, 3)
        
        # Generate boxes for each layer (bottom to top)
        total_height = 0
        for layer in range(self.num_layers):
            # Each layer can have 1-2 boxes side by side
            boxes_in_layer = random.randint(1, 2) if layer < self.num_layers - 1 else 1
            
            # Boxes in this layer
            layer_boxes = []
            
            # If this is not the bottom layer, make sure boxes are supported by boxes below
            available_width = width if layer == 0 else width * 0.8
            start_x = (width - available_width) / 2
            
            # Divide available width among boxes
            box_width = available_width / boxes_in_layer
            
            for i in range(boxes_in_layer):
                # Create a box with random dimensions
                box_w = random.uniform(self.min_box_width, min(self.max_box_width, box_width * 0.9))
                box_h = random.uniform(self.min_box_height, self.max_box_height)
                box_d = random.uniform(self.min_box_depth, self.max_box_depth)
                
                # Position box within its allocated space
                pos_x = start_x + (i * box_width) + (box_width - box_w) / 2
                pos_y = total_height
                
                # Choose a random color for this box
                color_idx = random.randint(0, len(self.box_colors) - 1)
                
                # Generate details for the box (markings, edges, etc)
                has_horizontal_line = random.random() > 0.5
                has_vertical_line = random.random() > 0.5
                
                # Add box to the layer
                layer_boxes.append((pos_x, pos_y, box_w, box_h, box_d, color_idx, 
                                    has_horizontal_line, has_vertical_line))
            
            # Add all boxes in this layer to the stack
            self.boxes.extend(layer_boxes)
            
            # Update the total height for the next layer
            total_height += max([box[3] for box in layer_boxes])  # Max height of boxes in this layer
        
        # Set up animation states - subtle movement to simulate shifting boxes
        self.set_states(num_states)

    def _create_box(self, x, y, width, height, depth, color_idx, has_h_line, has_v_line, 
                   state: int, vertices: List[float], colors: List[int]):
        """Helper method to create a single box with 3D perspective"""
        # Determine box color
        box_color = self.box_colors[color_idx]
        
        # Calculate lighting variations for different faces
        top_face_color = box_color  # Original color for top face
        
        # Right side is slightly darker (30% darker)
        right_face_color = (
            int(box_color[0] * 0.7),
            int(box_color[1] * 0.7),
            int(box_color[2] * 0.7)
        )
        
        # Left side is slightly lighter (15% darker)
        left_face_color = (
            int(box_color[0] * 0.85),
            int(box_color[1] * 0.85),
            int(box_color[2] * 0.85)
        )
        
        # Apply a subtle animation effect - boxes shift slightly based on state
        if self.states and len(self.states) > 1:
            # Calculate a subtle offset for the animation
            # Boxes should appear to shift/settle slightly
            animation_scale = 0.01  # Very small movement, just enough to be visible
            offset_x = math.sin(state / (len(self.states) - 1) * math.pi * 2) * width * animation_scale
            offset_y = math.cos(state / (len(self.states) - 1) * math.pi * 2) * height * animation_scale
        else:
            offset_x, offset_y = 0, 0
        
        # Apply the offset
        x += offset_x
        y += offset_y
        
        # Calculate 3D perspective points for the box
        # We'll draw an isometric-style box
        
        # Front face (rectangle)
        front_bl = (x, y)  # bottom-left
        front_br = (x + width, y)  # bottom-right
        front_tr = (x + width, y + height)  # top-right
        front_tl = (x, y + height)  # top-left
        
        # Top face (skewed rectangle)
        top_fl = (x, y + height)  # front-left
        top_fr = (x + width, y + height)  # front-right
        top_br = (x + width + depth*0.5, y + height + depth*0.25)  # back-right
        top_bl = (x + depth*0.5, y + height + depth*0.25)  # back-left
        
        # Right face (skewed rectangle)
        right_fb = (x + width, y)  # front-bottom
        right_ft = (x + width, y + height)  # front-top
        right_bt = (x + width + depth*0.5, y + height + depth*0.25)  # back-top
        right_bb = (x + width + depth*0.5, y + depth*0.25)  # back-bottom
        
        # Draw front face (use lines for outline)
        vertices.extend([
            front_bl[0], front_bl[1], front_br[0], front_br[1],  # bottom
            front_br[0], front_br[1], front_tr[0], front_tr[1],  # right
            front_tr[0], front_tr[1], front_tl[0], front_tl[1],  # top
            front_tl[0], front_tl[1], front_bl[0], front_bl[1]   # left
        ])
        colors.extend(self.outline_color * 8)  # 8 vertices for outline
        
        # Draw top face
        vertices.extend([
            top_fl[0], top_fl[1], top_fr[0], top_fr[1],  # front
            top_fr[0], top_fr[1], top_br[0], top_br[1],  # right
            top_br[0], top_br[1], top_bl[0], top_bl[1],  # back
            top_bl[0], top_bl[1], top_fl[0], top_fl[1]   # left
        ])
        colors.extend(self.outline_color * 8)  # 8 vertices for outline
        
        # Draw right face
        vertices.extend([
            right_fb[0], right_fb[1], right_ft[0], right_ft[1],  # front
            right_ft[0], right_ft[1], right_bt[0], right_bt[1],  # top
            right_bt[0], right_bt[1], right_bb[0], right_bb[1],  # back
            right_bb[0], right_bb[1], right_fb[0], right_fb[1]   # bottom
        ])
        colors.extend(self.outline_color * 8)  # 8 vertices for outline
        
        # Add detail lines if enabled
        if has_h_line:
            # Add horizontal line across the front face at 1/3 of the height
            line_height = y + height / 3
            vertices.extend([
                front_bl[0], line_height, front_br[0], line_height
            ])
            colors.extend(self.outline_color * 2)  # 2 vertices
            
        if has_v_line:
            # Add vertical line on the front face at center
            line_x = x + width / 2
            vertices.extend([
                line_x, front_bl[1], line_x, front_tl[1]
            ])
            colors.extend(self.outline_color * 2)  # 2 vertices
        
        # Fill the faces with color
        # We'll use triangles to fill each face
        
        # Front face (two triangles)
        vertices.extend([
            front_bl[0], front_bl[1], front_br[0], front_br[1], front_tr[0], front_tr[1],  # bottom-right triangle
            front_bl[0], front_bl[1], front_tr[0], front_tr[1], front_tl[0], front_tl[1]   # top-left triangle
        ])
        colors.extend(box_color * 6)  # 6 vertices
        
        # Top face (two triangles)
        vertices.extend([
            top_fl[0], top_fl[1], top_fr[0], top_fr[1], top_br[0], top_br[1],  # right triangle
            top_fl[0], top_fl[1], top_br[0], top_br[1], top_bl[0], top_bl[1]   # left triangle
        ])
        colors.extend(top_face_color * 6)  # 6 vertices
        
        # Right face (two triangles)
        vertices.extend([
            right_fb[0], right_fb[1], right_ft[0], right_ft[1], right_bt[0], right_bt[1],  # top triangle
            right_fb[0], right_fb[1], right_bt[0], right_bt[1], right_bb[0], right_bb[1]   # bottom triangle
        ])
        colors.extend(right_face_color * 6)  # 6 vertices
    
    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for box stack.
        
        Args:
            state: The animation state
            
        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []
        
        # Draw each box in the stack
        # Start from the furthest box (back) and move forward for proper layering
        for box in self.boxes:
            x, y, width, height, depth, color_idx, has_h_line, has_v_line = box
            self._create_box(x, y, width, height, depth, color_idx, has_h_line, has_v_line, 
                            state, vertices, colors)
        
        return {"vertices": vertices, "colors": colors}
