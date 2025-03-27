"""
Tile Renderer

Handles rendering of individual tiles using vector graphics
in the style of old monochrome green CRTs.
"""

import random
import numpy as np
import pyglet
from pyglet import shapes
from typing import List, Tuple


class VectorTile:
    """Base class for vector-drawn tiles"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Default colors
        self.outline_color = (0, 51, 0)  # Dark green
        self.content_color = (0, 204, 0)  # Bright green
        
        # Shapes will be stored for each position where tile is drawn
        self.shapes_by_position = {}
        
        # Create outline points
        self.outline_points = [
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0),
        ]

    def create_shapes_for_batch(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[shapes.ShapeBase]:
        """Create shapes for the tile at given position and add to batch"""
        tile_shapes = []
        
        # Create outline shapes
        for i in range(len(self.outline_points) - 1):
            x1, y1 = self.outline_points[i]
            x2, y2 = self.outline_points[i + 1]
            line = shapes.Line(
                x1 + x, y1 + y, x2 + x, y2 + y, 
                color=self.outline_color, 
                batch=batch
            )
            tile_shapes.append(line)
            
        # Create content shapes (implemented by subclasses)
        content_shapes = self._create_content_shapes(x, y, batch)
        tile_shapes.extend(content_shapes)
        
        return tile_shapes
    
    def _create_content_shapes(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[shapes.ShapeBase]:
        """Generate content shapes for the tile - override in subclasses"""
        return []
    
    def add_to_batch(self, x: float, y: float, batch: pyglet.graphics.Batch):
        """Add this tile to a rendering batch at the specified position"""
        # Use tuple of position as a key
        pos_key = (x, y)
        
        # Always recreate shapes for this position to ensure camera movement works
        # Delete old shapes at this position if they exist
        if pos_key in self.shapes_by_position:
            for shape in self.shapes_by_position[pos_key]:
                shape.delete()
        
        # Create new shapes for the current position
        shapes_list = self.create_shapes_for_batch(x, y, batch)
        self.shapes_by_position[pos_key] = shapes_list
    
    def delete(self):
        """Clean up resources"""
        # Delete all shapes for all positions
        for shapes_list in self.shapes_by_position.values():
            for shape in shapes_list:
                shape.delete()
        self.shapes_by_position.clear()


class GrassTile(VectorTile):
    """Grass tile with vector graphics representation"""

    def __init__(self, width: int = 100, height: int = 50, num_blades: int = 30):
        self.num_blades = num_blades
        # Random seed ensures same grass pattern for each tile instance
        self.blade_positions = []
        
        # Pre-generate blade positions
        for _ in range(self.num_blades):
            x = random.uniform(0.1, 0.9) * width
            y = random.uniform(0.1, 0.9) * height
            height_blade = random.uniform(5, 15)  # Blade height
            self.blade_positions.append((x, y, height_blade))
            
        # Call parent constructor
        super().__init__(width, height)
    
    def _create_content_shapes(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[shapes.ShapeBase]:
        """Generate grass blades as vertical lines"""
        content_shapes = []
        
        # Create grass blade shapes
        for blade_x, blade_y, height in self.blade_positions:
            # Line constructor parameters: x1, y1, x2, y2, color, batch
            blade = shapes.Line(
                blade_x + x, blade_y + y, 
                blade_x + x, blade_y + y + height, 
                color=self.content_color, 
                thickness=1.5,
                batch=batch
            )
            content_shapes.append(blade)
            
        return content_shapes


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type == "G":  # Grass
        return GrassTile(width, height)
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
