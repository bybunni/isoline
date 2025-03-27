"""
Vector graphics renderer for isometric tiles.
"""

import pyglet
import math
import random
from pyglet.graphics import Group


class VectorRenderer:
    """
    Renders isometric tiles using vector graphics.
    """

    def __init__(self, projection, batch=None, color=(0, 255, 0, 255)):
        """
        Initialize the vector renderer.

        Args:
            projection: IsometricProjection instance
            batch: Optional pyglet.graphics.Batch for drawing
            color: RGBA color tuple for vector lines (default: green)
        """
        self.iso_projection = projection
        self.batch = batch or pyglet.graphics.Batch()
        self.color = color
        self.base_color = color
        self.ground_group = Group(order=0)
        self.object_group = Group(order=1)
        self.glow_group = Group(order=2)
        self.lines = []
        self.glow_lines = []
        self.time = 0
        
        # Register tile renderers
        self.tile_renderers = {
            "G": self._render_grass,
            "M": self._render_box,
            "W": self._render_water,
            "B": self._render_bridge,
        }

    def set_color(self, color):
        """
        Set the color for subsequent vector drawing operations.

        Args:
            color: RGBA color tuple
        """
        self.color = color

    def reset_color(self):
        """Reset color to base color."""
        self.color = self.base_color

    def draw_line(self, x1, y1, x2, y2, group=None, with_glow=True):
        """
        Draw a line in map coordinates.

        Args:
            x1, y1: Start point in map coordinates
            x2, y2: End point in map coordinates
            group: Rendering group (defaults to object_group)
            with_glow: Whether to add a glow effect
        """
        sx1, sy1, sx2, sy2 = self.iso_projection.map_to_screen_vector(x1, y1, x2, y2)

        line = pyglet.shapes.Line(
            sx1,
            sy1,
            sx2,
            sy2,
            thickness=1.0,
            color=self.color[:3],
            batch=self.batch,
            group=group or self.object_group,
        )

        if len(self.color) > 3:
            line.opacity = self.color[3]

        self.lines.append(line)

        # Add glow effect for CRT look
        if with_glow and random.random() < 0.2:  # Only some lines glow
            glow = pyglet.shapes.Line(
                sx1,
                sy1,
                sx2,
                sy2,
                thickness=2.0,  # Thicker for glow
                color=self.color[:3],
                batch=self.batch,
                group=self.glow_group,
            )

            # Reduced opacity for glow
            glow.opacity = 50 if len(self.color) > 3 else 50
            self.glow_lines.append(glow)

        return line

    def draw_isometric_tile_outline(self, x, y, group=None):
        """
        Draw the outline of an isometric tile.

        Args:
            x, y: Tile position in map coordinates
            group: Rendering group (defaults to ground_group)
        """
        if group is None:
            group = self.ground_group
        
        # Draw the diamond shape of the tile
        self.draw_line(x, y, x + 1, y, group)  # Top-right edge
        self.draw_line(x + 1, y, x + 1, y + 1, group)  # Right-bottom edge
        self.draw_line(x + 1, y + 1, x, y + 1, group)  # Bottom-left edge
        self.draw_line(x, y + 1, x, y, group)  # Left-top edge

    def draw_grid(self, width, height, group=None):
        """
        Draw a grid of isometric tiles.

        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            group: Rendering group (defaults to ground_group)
        """
        for y in range(height):
            for x in range(width):
                self.draw_isometric_tile_outline(x, y, group)

    def draw_ground_plane(self, mdmap_data, layer="terrain"):
        """
        Draw the ground plane based on mdmap data.

        Args:
            mdmap_data: MDMapParser instance with parsed data
            layer: Layer name to use for the ground plane
        """
        width, height = mdmap_data.size

        # First draw grid for all tiles
        self.draw_grid(width, height, self.ground_group)

        # Then draw specialized visuals for each tile type
        for y in range(height):
            for x in range(width):
                tile_char = mdmap_data.get_tile(layer, x, y)
                if tile_char:
                    self.draw_tile_by_type(x, y, tile_char, mdmap_data, layer)

    def _render_grass(self, x, y, group=None):
        """
        Render a grass tile with cross lines.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
        """
        group = group or self.ground_group
        # Draw some cross lines to indicate grass
        self.draw_line(x, y, x + 1, y + 1, group)
        self.draw_line(x + 1, y, x, y + 1, group)
    
    def _render_box(self, x, y, group=None):
        """
        Render an isometric box using vector lines.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
        """
        group = group or self.ground_group
        
        # Box dimensions (scaled to fit within a tile)
        width = 0.7
        depth = 0.7
        height = 0.7
        
        # Center offset for the tile
        center_x = x + 0.5 - width/2
        center_y = y + 0.5 - depth/2
        
        # Define the vertices of the box (front face)
        front_bl = (center_x, center_y, 0)
        front_br = (center_x + width, center_y, 0)
        front_tl = (center_x, center_y, height)
        front_tr = (center_x + width, center_y, height)
        
        # Back face vertices
        back_bl = (center_x, center_y + depth, 0)
        back_br = (center_x + width, center_y + depth, 0)
        back_tl = (center_x, center_y + depth, height)
        back_tr = (center_x + width, center_y + depth, height)
        
        # Draw front face
        self.draw_line(front_bl[0], front_bl[1], front_br[0], front_br[1], group)
        self.draw_line(front_bl[0], front_bl[1], front_tl[0], front_tl[1], group)
        self.draw_line(front_br[0], front_br[1], front_tr[0], front_tr[1], group)
        self.draw_line(front_tl[0], front_tl[1], front_tr[0], front_tr[1], group)
        
        # Draw back face
        self.draw_line(back_bl[0], back_bl[1], back_br[0], back_br[1], group)
        self.draw_line(back_bl[0], back_bl[1], back_tl[0], back_tl[1], group)
        self.draw_line(back_br[0], back_br[1], back_tr[0], back_tr[1], group)
        self.draw_line(back_tl[0], back_tl[1], back_tr[0], back_tr[1], group)
        
        # Draw connecting edges
        self.draw_line(front_bl[0], front_bl[1], back_bl[0], back_bl[1], group)
        self.draw_line(front_br[0], front_br[1], back_br[0], back_br[1], group)
        self.draw_line(front_tl[0], front_tl[1], back_tl[0], back_tl[1], group)
        self.draw_line(front_tr[0], front_tr[1], back_tr[0], back_tr[1], group)

    def _render_cone(self, x, y, group=None, segments=12):
        """
        Render an isometric cone using vector lines.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
            segments: Number of segments to use for the circular base (default: 12)
        """
        group = group or self.ground_group
        
        # Define cone parameters
        radius = 0.35  # radius of the circular base
        height = 0.7   # height of the cone
        
        # Center offset for the tile
        center_x = x + 0.5
        center_y = y + 0.5
        
        # Draw the base circle segments
        for i in range(segments):
            angle1 = 2 * math.pi * i / segments
            angle2 = 2 * math.pi * (i + 1) / segments
            
            # Calculate base circle points
            x1 = center_x + radius * math.cos(angle1)
            y1 = center_y + radius * math.sin(angle1)
            x2 = center_x + radius * math.cos(angle2)
            y2 = center_y + radius * math.sin(angle2)
            
            # Draw base circle segment
            self.draw_line(x1, y1, x2, y2, group)
            
            # Draw line from base to apex
            self.draw_line(x1, y1, center_x, center_y, group)

    def _render_mountain(self, x, y, group=None):
        """
        Render a mountain tile with a proper isometric pyramid.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
        """
        group = group or self.ground_group
        
        # Define pyramid parameters in 3D space
        w = 0.7  # width of the square base (x-axis)
        h = 0.7  # height of the pyramid (z-axis)
        
        # Center offset for the tile
        center_x, center_y = x + 0.5, y + 0.5
        
        # Convert 3D coordinates to 2D isometric view
        # Formula: X = (x - y) * (√3/2), Y = (x + y) * (1/2) - z  [Note: Adjusted below]
        sqrt3_2 = 0.866  # √3/2
        
        # Define 3D coordinates for base corners (rotated square to form a diamond)
        base_3d = [
            (0, -w/2, 0),   # Top vertex
            (w/2, 0, 0),    # Right vertex
            (0, w/2, 0),    # Bottom vertex
            (-w/2, 0, 0)    # Left vertex
        ]
        
        # Apex at the center of the base but elevated
        apex_3d = (0, 0, h)
        
        # Project 3D points to 2D isometric view
        # Note: Inverted the z-coordinate sign previously to point up, now adjusted for proper alignment
        base_iso = [
            ((x3d - y3d) * sqrt3_2 + center_x, (x3d + y3d) * 0.5 + z3d + center_y)
            for x3d, y3d, z3d in base_3d
        ]
        
        # Project apex
        apex_iso = (
            (apex_3d[0] - apex_3d[1]) * sqrt3_2 + center_x,
            (apex_3d[0] + apex_3d[1]) * 0.5 + apex_3d[2] + center_y
        )
        
        # Draw the base edges
        for i in range(4):
            self.draw_line(
                base_iso[i][0], base_iso[i][1],
                base_iso[(i+1)%4][0], base_iso[(i+1)%4][1],
                group
            )
        
        # Draw lines from each corner to the apex
        for corner_x, corner_y in base_iso:
            self.draw_line(corner_x, corner_y, apex_iso[0], apex_iso[1], group)
    
    def _render_water(self, x, y, group=None):
        """
        Render a water tile with horizontal lines.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
        """
        group = group or self.ground_group
        # Draw horizontal lines for water
        for i in range(1, 4):
            offset = i * 0.25
            self.draw_line(x, y + offset, x + 1, y + offset, group)
    
    def _render_bridge(self, x, y, group=None):
        """
        Render a bridge tile with vertical planks.
        
        Args:
            x, y: Tile position in map coordinates
            group: Rendering group
        """
        group = group or self.ground_group
        # Draw bridge planks
        for i in range(1, 4):
            offset = i * 0.25
            self.draw_line(x + offset, y, x + offset, y + 1, group)
            
    def draw_tile_by_type(self, x, y, tile_char, mdmap_data, layer):
        """
        Draw specialized tile visuals based on tile type.

        Args:
            x, y: Tile position in map coordinates
            tile_char: Character representing the tile type
            mdmap_data: MDMapParser instance
            layer: Layer name
        """
        # Get the meaning from the mdmap data (could be used for additional rendering logic)
        meaning = mdmap_data.get_tile_meaning(layer, tile_char)
        
        # Look up the renderer function from our dictionary
        renderer = self.tile_renderers.get(tile_char)
        
        # If we have a registered renderer for this tile type, use it
        if renderer:
            renderer(x, y, self.ground_group)
        else:
            # Default behavior for unknown tile types - just draw the outline
            self.draw_isometric_tile_outline(x, y, self.ground_group)

    def update(self, dt):
        """
        Update the renderer.

        Args:
            dt: Time since last update
        """
        self.time += dt

        # Flicker effect for CRT look
        for line in self.lines:
            # Only some lines flicker
            if random.random() < 0.01:
                intensity = random.uniform(0.85, 1.0)
                line.opacity = int(line.opacity * intensity)

        # Glow effect pulse
        for glow in self.glow_lines:
            # Make the glow pulse
            pulse = (math.sin(self.time * 5 + random.random()) + 1) * 0.5  # 0 to 1
            glow.opacity = int(30 + pulse * 30)  # 30 to 60

    def render(self):
        """
        Render the batch.
        """
        self.batch.draw()

    def clear(self):
        """
        Clear all lines.
        """
        self.lines = []
        self.glow_lines = []
        self.batch = pyglet.graphics.Batch()
