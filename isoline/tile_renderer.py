"""
Tile Renderer

Handles rendering of individual tiles using vector graphics
in the style of old monochrome green CRTs.

Optimized version with vertex array caching and batch rendering.
"""

import random
import numpy as np
import pyglet
from pyglet import shapes
from pyglet.gl import *
from typing import List, Tuple, Dict, Any, Optional


class VectorTile:
    """Base class for vector-drawn tiles with optimized rendering"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Default colors
        self.outline_color = (0, 51, 0)  # Dark green
        self.content_color = (0, 204, 0)  # Bright green
        
        # Create outline points
        self.outline_points = [
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0),
        ]
        
        # Cache for vertex data (for OpenGL/VBO optimization)
        self._vertex_data_cache: Optional[Dict[str, Any]] = None
        
        # For faster rendering, we'll use a vertex buffer approach
        # Shapes will still be stored for compatibility
        self.shapes_by_position: Dict[Tuple[float, float], List[shapes.ShapeBase]] = {}
        
        # Vertex groups for efficient rendering
        self.vertex_groups_by_position: Dict[Tuple[float, float], List[pyglet.graphics.vertexdomain.VertexList]] = {}
    
    def _create_vertex_data(self) -> Dict[str, Any]:
        """
        Generate and cache vertex data for efficient rendering.
        Returns cached data structure with vertices and colors.
        This method should be called once and results cached.
        """
        if self._vertex_data_cache is not None:
            return self._vertex_data_cache
            
        # For outline vertices (lines)
        outline_vertices = []
        outline_colors = []
        
        # Process outline points
        for i in range(len(self.outline_points) - 1):
            x1, y1 = self.outline_points[i]
            x2, y2 = self.outline_points[i + 1]
            outline_vertices.extend([x1, y1, x2, y2])
            outline_colors.extend(self.outline_color * 2)  # Each vertex needs a color
            
        # Get content vertices/colors from subclasses
        content_data = self._create_content_vertex_data()
        
        # Cache the data
        self._vertex_data_cache = {
            'outline_vertices': outline_vertices,
            'outline_colors': outline_colors,
            'content_vertices': content_data.get('vertices', []),
            'content_colors': content_data.get('colors', [])
        }
        
        return self._vertex_data_cache
    
    def _create_content_vertex_data(self) -> Dict[str, List[float]]:
        """
        Generate content vertex data - override in subclasses.
        Returns a dict with 'vertices' and 'colors' lists.
        """
        return {'vertices': [], 'colors': []}

    def create_shapes_for_batch(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[shapes.ShapeBase]:
        """
        Legacy method that creates shapes for the tile at given position and adds to batch.
        Maintained for compatibility but optimized implementations should use add_vertex_lists_to_batch.
        """
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
    
    def add_vertex_lists_to_batch(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[pyglet.graphics.vertexdomain.VertexList]:
        """
        Add this tile to a rendering batch using efficient vertex lists.
        For Pyglet 2.1.3, this now uses shapes.Line objects added to the batch.
        The batch.draw() method will be called later to render everything.
        """
        vertex_data = self._create_vertex_data()
        # We'll return vertex lists for compatibility, even though we're using shapes now
        vertex_lists = []
        shape_objects = []
        
        # Process outline points - create Line objects for each segment
        for i in range(len(self.outline_points) - 1):
            x1, y1 = self.outline_points[i]
            x2, y2 = self.outline_points[i + 1]
            line = shapes.Line(
                x1 + x, y1 + y, x2 + x, y2 + y, 
                color=self.outline_color, 
                batch=batch
            )
            shape_objects.append(line)
            
        # Process content vertices - create Line objects for content vertex data
        if vertex_data['content_vertices']:
            content_vertices = []
            content_colors = vertex_data['content_colors']
            
            # Extract and transform content vertices
            for i in range(0, len(vertex_data['content_vertices']), 2):
                vx = vertex_data['content_vertices'][i] + x
                vy = vertex_data['content_vertices'][i+1] + y
                content_vertices.append((vx, vy))
            
            # Create Line objects for content
            for i in range(0, len(content_vertices) - 1, 2):
                if i + 1 < len(content_vertices):  # Ensure we have a pair of points
                    x1, y1 = content_vertices[i]
                    x2, y2 = content_vertices[i + 1]
                    
                    # Get the color for this line - use content_color if color data not available
                    color = self.content_color
                    if i//2 * 3 + 2 < len(content_colors):
                        color = (content_colors[i//2 * 3], 
                                content_colors[i//2 * 3 + 1], 
                                content_colors[i//2 * 3 + 2])
                    
                    line = shapes.Line(x1, y1, x2, y2, color=color, batch=batch)
                    shape_objects.append(line)
        
        # Store the shapes in the shapes_by_position dict for later cleanup
        pos_key = (x, y)
        self.shapes_by_position[pos_key] = shape_objects
        
        return vertex_lists
    
    def add_to_batch(self, x: float, y: float, batch: pyglet.graphics.Batch):
        """
        Add this tile to a rendering batch at the specified position.
        This version uses shapes added to batches for Pyglet 2.1.3 compatibility.
        """
        # Use tuple of position as a key
        pos_key = (x, y)
        
        # Clean up existing vertex lists if any
        if pos_key in self.vertex_groups_by_position:
            for vlist in self.vertex_groups_by_position[pos_key]:
                vlist.delete()
            self.vertex_groups_by_position[pos_key] = []
        
        # Clean up existing shapes at this position
        if pos_key in self.shapes_by_position:
            for shape in self.shapes_by_position[pos_key]:
                shape.delete()
            self.shapes_by_position[pos_key] = []
        
        # Create shapes and vertex lists for this position and add to batch
        vertex_lists = self.add_vertex_lists_to_batch(x, y, batch)
        self.vertex_groups_by_position[pos_key] = vertex_lists
    
    def delete(self):
        """Clean up all resources"""
        # Delete all vertex lists
        for vlists in self.vertex_groups_by_position.values():
            for vlist in vlists:
                vlist.delete()
        self.vertex_groups_by_position.clear()
        
        # Delete all shapes
        for shapes_list in self.shapes_by_position.values():
            for shape in shapes_list:
                shape.delete()
        self.shapes_by_position.clear()
        
        # Clear the cache
        self._vertex_data_cache = None


class GrassTile(VectorTile):
    """
    Grass tile with vector graphics representation.
    Optimized version using vertex data caching.
    """

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
    
    def _create_content_vertex_data(self) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for grass blades.
        This is called once per tile type and cached.
        """
        vertices = []
        colors = []
        
        # Create grass blade vertices
        for blade_x, blade_y, height in self.blade_positions:
            # Each blade is a line from (x,y) to (x,y+height)
            vertices.extend([blade_x, blade_y, blade_x, blade_y + height])
            # Add colors for each vertex
            colors.extend(self.content_color * 2)  # 2 vertices per blade
            
        return {
            'vertices': vertices,
            'colors': colors
        }
    
    def _create_content_shapes(self, x: float, y: float, batch: pyglet.graphics.Batch) -> List[shapes.ShapeBase]:
        """
        Legacy method for grass blades as vertical lines.
        Maintained for compatibility but optimized implementations
        should use the vertex data approach.
        """
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
