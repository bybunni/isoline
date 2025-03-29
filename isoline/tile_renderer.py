"""
Tile Renderer

Handles rendering of individual tiles using vector graphics
in the style of old monochrome green CRTs.

Optimized version with vertex array caching, batch rendering, and animation support.
"""

import random
import math
import numpy as np
import pyglet
from pyglet import shapes
from pyglet.gl import *
from typing import List, Tuple, Dict, Any, Optional, Union


class VectorTile:
    """Base class for vector-drawn tiles with optimized rendering and animation support"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Default colors
        self.outline_color = (0, 102, 0)  # Brighter green outline
        self.content_color = (0, 204, 0)  # Bright green

        # Create outline points
        self.outline_points = [
            (0, 0),
            (self.width, 0),
            (self.width, self.height),
            (0, self.height),
            (0, 0),
        ]

        # Animation state tracking
        self.states = [0]  # Default has only a single state (0)
        self.current_state_index = 0
        self.animated = False

        # Cache for vertex data (for OpenGL/VBO optimization)
        # Now organized by state: state_index -> vertex_data
        self._vertex_data_cache: Dict[int, Dict[str, Any]] = {}

        # For faster rendering, we'll use a vertex buffer approach
        # Shapes will still be stored for compatibility
        self.shapes_by_position: Dict[Tuple[float, float], List[shapes.ShapeBase]] = {}

        # Vertex groups for efficient rendering
        self.vertex_groups_by_position: Dict[
            Tuple[float, float], List[pyglet.graphics.vertexdomain.VertexList]
        ] = {}

        # Track which state is displayed at which position
        self.state_by_position: Dict[Tuple[float, float], int] = {}

    def _create_vertex_data(self, state: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate and cache vertex data for efficient rendering.
        Returns cached data structure with vertices and colors.

        Args:
            state: The animation state to generate vertex data for.
                  If None, uses the current state.

        Returns:
            Dict with vertex data for the requested state
        """
        # Use current state if none specified
        if state is None:
            state = self.states[self.current_state_index]

        # Return from cache if available for this state
        if state in self._vertex_data_cache:
            return self._vertex_data_cache[state]

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
        content_data = self._create_content_vertex_data(state)

        # Cache the data for this state
        self._vertex_data_cache[state] = {
            "outline_vertices": outline_vertices,
            "outline_colors": outline_colors,
            "content_vertices": content_data.get("vertices", []),
            "content_colors": content_data.get("colors", []),
        }

        return self._vertex_data_cache[state]

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate content vertex data - override in subclasses.

        Args:
            state: The animation state to generate content for

        Returns:
            A dict with 'vertices' and 'colors' lists.
        """
        return {"vertices": [], "colors": []}

    def set_states(self, num_states: int):
        """
        Configure the tile to have multiple animation states.

        Args:
            num_states: The number of animation states
        """
        if num_states <= 0:
            raise ValueError("Number of states must be positive")

        self.states = list(range(num_states))
        self.animated = num_states > 1
        # Clear any existing cache
        self._vertex_data_cache = {}

    def advance_state(self):
        """Advance to the next animation state, cycling back to the first if needed"""
        if not self.animated or not self.states:
            return

        # Advance to next state
        self.current_state_index = (self.current_state_index + 1) % len(self.states)

    def get_current_state(self) -> int:
        """Get the current animation state value"""
        if not self.states:
            return 0
        return self.states[self.current_state_index]

    def add_shapes_to_batch(
        self, x: float, y: float, batch: pyglet.graphics.Batch
    ) -> List[shapes.ShapeBase]:
        """
        Create shape objects for this tile and add them to the rendering batch.
        For Pyglet 2.x, this creates shapes.Line objects which add themselves
        to the batch upon creation.
        The created shapes are stored for later cleanup.

        Args:
            x: The screen x-coordinate for the tile's origin.
            y: The screen y-coordinate for the tile's origin.
            batch: The pyglet graphics batch to add shapes to.

        Returns:
            A list of the created shape objects (primarily for potential tracking,
            though direct use might be limited as shapes are managed via batch).
        """
        current_state = self.get_current_state()
        vertex_data = self._create_vertex_data(current_state)

        # Store the created shapes
        shape_objects = []

        # Calculate the vertices of the isometric diamond
        top_vx, top_vy = x, y
        left_vx = x - self.width / 2
        left_vy = y - self.height / 2
        right_vx = x + self.width / 2
        right_vy = y - self.height / 2
        bottom_vx = x
        bottom_vy = y - self.height

        # Define the points for the outline lines
        outline_points = [
            (top_vx, top_vy),
            (right_vx, right_vy),
            (right_vx, right_vy),
            (bottom_vx, bottom_vy),
            (bottom_vx, bottom_vy),
            (left_vx, left_vy),
            (left_vx, left_vy),
            (top_vx, top_vy),
        ]

        # Draw the outline using individual lines connecting the vertices
        for i in range(0, len(outline_points), 2):
            x1, y1 = outline_points[i]
            x2, y2 = outline_points[i + 1]
            line = shapes.Line(
                x1, y1, x2, y2, thickness=1.0, color=self.outline_color, batch=batch
            )
            shape_objects.append(line)

        # Calculate the bottom-left corner of the bounding box *only* for content placement
        bottom_left_x = x - self.width / 2
        bottom_left_y = y - self.height

        # Process content vertices - create Line objects for content vertex data
        if vertex_data["content_vertices"]:
            # Prepare list to store absolute screen coordinates for content vertices
            content_screen_coords = []
            content_colors = vertex_data["content_colors"]

            # Extract and transform content vertices to absolute screen coordinates
            for i in range(0, len(vertex_data["content_vertices"]), 2):
                vx_local = vertex_data["content_vertices"][i]
                vy_local = vertex_data["content_vertices"][i + 1]
                # Offset local vertex by the calculated screen bottom-left corner
                vx_screen = vx_local + bottom_left_x
                vy_screen = vy_local + bottom_left_y
                content_screen_coords.append((vx_screen, vy_screen))

            # Create Line objects for content using absolute screen coordinates
            # Assuming content vertices are defined as pairs forming lines
            for i in range(0, len(content_screen_coords) - 1, 2):
                if i + 1 < len(
                    content_screen_coords
                ):  # Ensure we have a pair of points
                    x1_screen, y1_screen = content_screen_coords[i]
                    x2_screen, y2_screen = content_screen_coords[i + 1]

                    # Get the color for this line - use content_color if color data not available
                    color = self.content_color
                    # Ensure color indexing matches vertex pair indexing
                    color_index = (i // 2) * 3  # Base index for RGB color tuple
                    if color_index + 2 < len(content_colors):
                        color = (
                            content_colors[color_index],
                            content_colors[color_index + 1],
                            content_colors[color_index + 2],
                        )

                    line = shapes.Line(
                        x1_screen,
                        y1_screen,
                        x2_screen,
                        y2_screen,
                        color=color,
                        batch=batch,
                    )
                    shape_objects.append(line)

        # Store the shapes in the shapes_by_position dict for later cleanup
        # Use the original top-vertex coordinates (x, y) as the key, as this is what the renderer uses
        pos_key = (x, y)
        self.shapes_by_position[pos_key] = shape_objects

        # Track which state is at this position
        self.state_by_position[pos_key] = current_state

        # Return the shapes created
        return shape_objects

    def add_to_batch(self, x: float, y: float, batch: pyglet.graphics.Batch):
        """
        Add this tile to a rendering batch at the specified position.
        This version uses shapes added to batches for Pyglet 2.1.3 compatibility.
        """
        # Use tuple of position as a key
        pos_key = (x, y)

        # Clean up existing vertex lists if any (though this might be unused now)
        if pos_key in self.vertex_groups_by_position:
            for vlist in self.vertex_groups_by_position[pos_key]:
                vlist.delete()
            self.vertex_groups_by_position[pos_key] = []

        # Clean up existing shapes at this position
        if pos_key in self.shapes_by_position:
            for shape in self.shapes_by_position[pos_key]:
                shape.delete()
            self.shapes_by_position[pos_key] = []

        # Create shapes for this position and add them to batch
        # Note: The shapes add themselves to the batch during creation
        created_shapes = self.add_shapes_to_batch(x, y, batch)
        # Although vertex_groups might be less relevant now, keep structure for potential future use or refactoring
        self.vertex_groups_by_position[pos_key] = (
            []
        )  # Clear/reset vertex list tracking for this position

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
        self._vertex_data_cache = {}


class GrassTile(VectorTile):
    """
    Grass tile with vector graphics representation.
    Optimized version using vertex data caching.
    Supports animation with swaying grass.
    """

    def __init__(
        self,
        width: int = 100,
        height: int = 50,
        num_blades: int = 30,
        num_states: int = 5,
    ):
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

        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for grass blades.
        Different states create a swaying animation effect.

        Args:
            state: The animation state (used to vary blade angles)

        Returns:
            Dict with vertices and colors for the specified state
        """
        vertices = []
        colors = []

        # Determine the sway factor based on animation state
        # This creates a gentle swaying pattern across animation frames
        max_sway = 3.0  # Maximum pixel offset for swaying
        if len(self.states) <= 1:
            sway_factor = 0
        else:
            # Calculate a unique sway factor for each state
            # Use sine wave to create smooth transitions
            angle = (state / (len(self.states) - 1)) * 2 * math.pi
            sway_factor = math.sin(angle) * max_sway

        # Draw grass blades with varying heights and sway angles
        for blade_x, blade_y, height in self.blade_positions:
            # Apply a unique sway to each blade based on its position and the current state
            # Using hash of position ensures consistent sway direction for each blade
            blade_sway = (
                sway_factor
                * ((hash(f"{blade_x:.1f}_{blade_y:.1f}") % 100) / 100.0 - 0.5)
                * 2.0
            )

            # Each blade is a line with a slight angle varying by state
            vertices.extend([blade_x, blade_y, blade_x + blade_sway, blade_y + height])

            # Slightly randomize green shade for visual interest
            # Make the green slightly brighter in middle animation states for subtle effect
            green_factor = 1.0
            if len(self.states) > 1:
                # Subtle brightness variation based on animation state
                mid_state = len(self.states) // 2
                distance_from_mid = abs(state - mid_state)
                green_factor = 1.0 - (distance_from_mid / (len(self.states) * 2))
                green_factor = 0.9 + (
                    green_factor * 0.2
                )  # Limit the effect (0.9-1.1 range)

            green = min(255, int(204 * green_factor))
            blade_color = (0, green, 0)

            # Add color for each vertex in the line
            colors.extend(blade_color * 2)  # 2 vertices per line

        return {"vertices": vertices, "colors": colors}


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type == "G" or tile_type == "g":  # Grass (support both upper and lowercase)
        return GrassTile(
            width, height, num_states=5
        )  # Create animated grass by default
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
