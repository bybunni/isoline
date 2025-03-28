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

# --- Configuration ---
TILE_WIDTH = 100
TILE_HEIGHT = 50

# Default rendering group if none is specified
_default_group = pyglet.graphics.Group()

class VectorTile:
    """Base class for vector-drawn tiles with optimized rendering and animation support"""

    def __init__(self, width: int = 100, height: int = 50):
        self.width = width
        self.height = height

        # Default colors
        self.outline_color = (0, 51, 0, 255)  # Dark green (RGBA)
        self.content_color = (0, 204, 0, 255) # Bright green (RGBA)

        # Create outline points (relative to 0,0)
        # Adjusted for pyglet's coordinate system (bottom-left origin)
        # These points define the shape, translation happens later.
        half_w = self.width // 2
        half_h = self.height // 2
        self.outline_points_relative = [
            (half_w, 0),        # Top point
            (self.width, half_h), # Right point
            (half_w, self.height),# Bottom point
            (0, half_h),        # Left point
        ]

        # Animation state tracking
        self.states = [0]  # Default has only a single state (0)
        self.current_state_index = 0
        self.animated = False

        # Cache for vertex data (raw vertices/colors relative to 0,0)
        # Organized by state: state_index -> {'vertices': [...], 'colors': [...]}
        self._vertex_data_cache: Dict[int, Dict[str, List[float]]] = {}

        # Cache for generated VertexList objects (managed by batch)
        # Organized by state: state_index -> VertexList (if generated)
        self._vertex_list_cache: Dict[int, Optional[pyglet.graphics.vertexdomain.VertexList]] = {}
        
        # Track active vertex lists added to the batch, keyed by position
        self._active_vertex_lists: Dict[Tuple[float, float], pyglet.graphics.vertexdomain.VertexList] = {}
        # Track which state is displayed at which position
        self.state_by_position: Dict[Tuple[float, float], int] = {}

        # Define standard attribute names and formats used by this tile type
        self._attribute_formats = {
            'vertices': {'format': ('f', 2), 'usage': 'static', 'location': 0},
            'colors': {'format': ('B', 4), 'usage': 'static', 'location': 1}
        }
        # Use attribute formats directly as domain attributes
        self._domain_attributes = self._attribute_formats

    def _create_vertex_data(self, state: Optional[int] = None) -> Dict[str, List[float]]:
        """
        Generate and cache vertex data (vertices and colors) relative to (0,0)
        for a specific animation state.

        Args:
            state: The animation state to generate vertex data for.
                   If None, uses the current state.

        Returns:
            Dict with 'vertices' and 'colors' lists for the requested state.
        """
        if state is None:
            state = self.states[self.current_state_index]

        if state in self._vertex_data_cache:
            return self._vertex_data_cache[state]

        all_vertices = []
        all_colors = []

        # Process outline points (4 lines forming the diamond)
        num_outline_points = len(self.outline_points_relative)
        for i in range(num_outline_points):
            x1, y1 = self.outline_points_relative[i]
            x2, y2 = self.outline_points_relative[(i + 1) % num_outline_points] # Wrap around
            all_vertices.extend([x1, y1, x2, y2])
            all_colors.extend(self.outline_color * 2) # RGBA for each vertex

        # Get content vertices/colors from subclasses (relative to 0,0)
        content_data = self._create_content_vertex_data(state)
        
        # Ensure content vertices and colors are valid lists
        content_vertices = content_data.get('vertices', [])
        content_colors = content_data.get('colors', [])
        
        # Check consistency
        if len(content_vertices) % 2 != 0:
             print(f"Warning: Odd number of content vertex coordinates for state {state} in {type(self).__name__}")
             # Optionally truncate or handle error
             content_vertices = content_vertices[:len(content_vertices)//2 * 2]
        
        num_content_verts_expected = len(content_vertices) // 2
        num_content_colors_components_expected = num_content_verts_expected * 4 # RGBA
        
        if len(content_colors) != num_content_colors_components_expected:
             print(f"Warning: Mismatch between content vertices ({num_content_verts_expected}) and color components ({len(content_colors)}, expected {num_content_colors_components_expected}) for state {state} in {type(self).__name__}")
             # Fallback: Use default content color if colors are incorrect
             content_colors = self.content_color * num_content_verts_expected

        all_vertices.extend(content_vertices)
        all_colors.extend(content_colors)
        
        # Cache the combined data for this state
        vertex_data = {
            'vertices': all_vertices,
            'colors': all_colors,
        }
        self._vertex_data_cache[state] = vertex_data
        self._vertex_list_cache[state] = None # Invalidate VertexList cache

        return vertex_data

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate content vertex data (relative to 0,0) - override in subclasses.

        Args:
            state: The animation state to generate content for

        Returns:
            A dict with 'vertices' and 'colors' (RGBA) lists.
        """
        return {'vertices': [], 'colors': []}

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
        # Clear vertex data and vertex list caches
        self._vertex_data_cache = {}
        self._vertex_list_cache = {}

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

    def add_to_batch(self, x: float, y: float, batch: pyglet.graphics.Batch):
        """
        Add this tile to a rendering batch at the specified screen position using VBOs.
        Manages VertexList creation, deletion, and updates based on position and state.
        """
        pos_key = (x, y)
        current_state = self.get_current_state()

        # --- Cleanup Logic ---
        # If there's already a VBO at this position:
        if pos_key in self._active_vertex_lists:
            # If the state hasn't changed, we don't need to do anything
            if self.state_by_position.get(pos_key) == current_state:
                return 
            # If the state *has* changed, delete the old VBO for this position
            else:
                self.delete_vbo_at_position(pos_key)

        # --- VBO Creation/Addition Logic ---
        # Get vertex data for the current state (creates if not cached)
        vertex_data = self._create_vertex_data(current_state)
        vertices = vertex_data.get('vertices', [])
        colors = vertex_data.get('colors', [])

        if not vertices:
            # print(f"Warning: No vertices found for state {current_state} in {type(self).__name__} at {pos_key}")
            return # Nothing to render

        # Calculate number of vertices
        num_vertices = len(vertices) // 2

        # Translate vertices to the target screen position (x, y)
        translated_vertices = []
        for i in range(0, len(vertices), 2):
            vx, vy = vertices[i], vertices[i+1]
            translated_vertices.extend([vx + x, vy + y])
            
        # Check consistency before adding to batch
        if len(translated_vertices) != num_vertices * 2:
             print(f"Error: Vertex translation mismatch for state {current_state} in {type(self).__name__}")
             return
        if len(colors) != num_vertices * 4: # RGBA
             print(f"Error: Color data mismatch for state {current_state} in {type(self).__name__}")
             # Fallback colors if mismatch
             colors = self.outline_color * (len(self.outline_points_relative) * 2) + \
                      self.content_color * (num_vertices - len(self.outline_points_relative) * 2)
             if len(colors) != num_vertices * 4: # Final check
                 print(f"Error: Fallback color generation failed for state {current_state} in {type(self).__name__}")
                 return


        # Add the translated vertices and colors to the batch
        # GL_LINES draws lines between pairs of vertices (v0-v1, v2-v3, etc.)
        try:
            # Get the appropriate domain from the batch for our drawing mode and attributes
            domain = batch.get_domain(
                indexed=False,         # Not using indexed drawing
                instanced=False,       # Not using instanced drawing
                mode=GL_LINES,         # Drawing mode
                group=_default_group,  # Use the default group
                attributes=self._domain_attributes # Vertex layout
            )
            
            # Create the vertex list within the obtained domain, passing data via keyword args
            colors_bytes = bytes(colors) # Convert color list to bytes
            vertex_list = domain.vertex_list(
                num_vertices,
                vertices=translated_vertices, # Use keyword arg 'vertices'
                colors=colors_bytes           # Use keyword arg 'colors' with bytes data
            )
            # Store the reference to the new vertex list
            self._active_vertex_lists[pos_key] = vertex_list
            self.state_by_position[pos_key] = current_state
        except Exception as e:
             print(f"Error adding to batch for {type(self).__name__} at {pos_key}: {e}")
             # Attempt to clean up if VBO was partially created or state is inconsistent
             if pos_key in self._active_vertex_lists:
                 self.delete_vbo_at_position(pos_key)


    def delete_vbo_at_position(self, pos_key: Tuple[float, float]):
        """Safely delete the VertexList associated with a specific position."""
        if pos_key in self._active_vertex_lists:
            try:
                self._active_vertex_lists[pos_key].delete()
            except Exception as e:
                print(f"Error deleting VBO at {pos_key}: {e}")
            del self._active_vertex_lists[pos_key]
            
        if pos_key in self.state_by_position:
             del self.state_by_position[pos_key]


    def delete(self):
        """Clean up all active VertexLists associated with this tile instance."""
        # Delete all vertex lists managed by this tile instance
        for vlist in list(self._active_vertex_lists.values()): # Iterate over a copy
             try:
                 vlist.delete()
             except Exception as e:
                 print(f"Error during tile cleanup deleting VBO: {e}")
        self._active_vertex_lists.clear()
        self.state_by_position.clear()
        
        # Clear caches (optional, depends if tile instance is reused)
        # self._vertex_data_cache = {} 
        # self._vertex_list_cache = {}


class GrassTile(VectorTile):
    """
    Grass tile with vector graphics representation.
    Optimized version using vertex data caching.
    Supports animation with swaying grass.
    """

    def __init__(self, width: int = 100, height: int = 50, num_blades: int = 30, num_states: int = 5):
        self.num_blades = num_blades
        # Blade positions relative to tile origin (0,0) using adjusted coordinates
        half_w = width // 2
        half_h = height // 2
        
        self.blade_details = [] # Store (x_base, y_base, height, sway_multiplier)

        for _ in range(self.num_blades):
            # Generate base positions within the diamond shape roughly
            # Using polar coordinates might be better, but random within bounds is simpler
            rand_x = random.uniform(0, width)
            rand_y = random.uniform(0, height)
            
            # Simple check to keep most blades within the diamond - adjust as needed
            # Check if the point is inside the diamond defined by outline_points_relative
            # This check isn't perfect but helps concentrate blades
            is_inside = True # Assume inside for simplicity here, proper check is complex
            
            if is_inside:
                 height_blade = random.uniform(5, 15)  # Blade height
                 # Store a unique sway multiplier per blade based on hash
                 sway_multiplier = ((hash(f"{rand_x:.1f}_{rand_y:.1f}") % 100) / 100.0 - 0.5) * 2.0
                 self.blade_details.append((rand_x, rand_y, height_blade, sway_multiplier))

        # Call parent constructor
        super().__init__(width, height)

        # Set up animation states
        self.set_states(num_states)

    def _create_content_vertex_data(self, state: int = 0) -> Dict[str, List[float]]:
        """
        Generate efficient vertex data for grass blades (relative to 0,0).
        Different states create a swaying animation effect.

        Args:
            state: The animation state (used to vary blade angles)

        Returns:
            Dict with 'vertices' and 'colors' (RGBA) lists for the specified state
        """
        vertices = []
        colors = []

        # Determine the sway factor based on animation state
        max_sway = 3.0  # Maximum pixel offset for swaying
        sway_factor = 0
        if self.animated and len(self.states) > 1:
            # Use sine wave for smooth transitions across states
            angle = (state / (len(self.states))) * 2 * math.pi # Cycle through 2*pi over all states
            sway_factor = math.sin(angle) * max_sway

        # Calculate vertex positions for each blade based on state
        for x_base, y_base, height, sway_multiplier in self.blade_details:
            blade_sway = sway_factor * sway_multiplier
            
            # Each blade is a line from (x_base, y_base) to (x_base + blade_sway, y_base + height)
            vertices.extend([x_base, y_base, x_base + blade_sway, y_base + height])

            # Determine color (RGBA)
            green_factor = 1.0
            if self.animated and len(self.states) > 1:
                # Subtle brightness variation based on animation state (peak brightness in middle states)
                mid_point = len(self.states) / 2.0
                distance_from_mid = abs(state - mid_point)
                # Normalize distance (0 at mid, 1 at ends), then invert
                brightness_mod = 1.0 - (distance_from_mid / mid_point) 
                green_factor = 0.9 + (brightness_mod * 0.2) # Range 0.9 to 1.1

            green = min(255, int(self.content_color[1] * green_factor))
            # Use RGBA format
            blade_color = (self.content_color[0], green, self.content_color[2], self.content_color[3]) 

            # Add color for each vertex in the line (RGBA tuple * 2)
            colors.extend(blade_color * 2) 
            
        return {
            'vertices': vertices,
            'colors': colors
        }

    # Removed _create_content_shapes (legacy method)


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type == "G" or tile_type == "g":  # Grass (support both upper and lowercase)
        return GrassTile(width, height, num_states=5)  # Create animated grass by default
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
