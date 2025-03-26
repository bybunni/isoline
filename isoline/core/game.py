"""
Main game class for the Isoline engine.
"""

import pyglet
from pyglet.window import key
from isoline.core.isometric import IsometricProjection
from isoline.graphics.vector_renderer import VectorRenderer
from isoline.utils.mdmap_parser import MDMapParser


class IsolineGame(pyglet.window.Window):
    """
    Main game class for the Isoline engine.
    """

    def __init__(
        self,
        width=800,
        height=600,
        title="Isoline Game",
        tile_width=128,
        tile_height=64,
        fullscreen=False,
        resizable=True,
        vsync=True,
        mdmap_path=None,
    ):
        """
        Initialize the game.

        Args:
            width: Window width
            height: Window height
            title: Window title
            tile_width: Width of a tile in pixels
            tile_height: Height of a tile in pixels
            fullscreen: Whether to start in fullscreen mode
            resizable: Whether the window can be resized
            vsync: Whether to use vsync
            mdmap_path: Path to a mdmap file to load
        """
        super().__init__(
            width,
            height,
            title,
            fullscreen=fullscreen,
            resizable=resizable,
            vsync=vsync,
        )

        # Set up isometric projection
        self.iso_projection = IsometricProjection(tile_width, tile_height)

        # Set up renderer
        self.renderer = VectorRenderer(self.iso_projection)

        # Set up camera
        self.camera_x = width // 2
        self.camera_y = height // 2

        # Set up keyboard state
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)

        # Camera movement speed
        self.camera_speed = 200  # pixels per second

        # Set background color (dark for CRT look)
        pyglet.gl.glClearColor(0, 0.05, 0, 1)

        # Set up fps display
        self.fps_display = pyglet.window.FPSDisplay(self)

        # Initialize map
        self.mdmap = None
        if mdmap_path:
            self.load_map(mdmap_path)

        # Schedule update
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def load_map(self, mdmap_path):
        """
        Load a map from a mdmap file.

        Args:
            mdmap_path: Path to the mdmap file
        """
        parser = MDMapParser()
        self.mdmap = parser.parse_file(mdmap_path)

    def on_draw(self):
        """
        Draw the game.
        """
        self.clear()

        # Draw the map if loaded
        if self.mdmap:
            self.renderer.clear()

            # Create new lines with camera offset applied
            width, height = self.mdmap.size
            self.renderer.draw_ground_plane(self.mdmap)

            # Apply camera position to shapes after drawing
            for line in self.renderer.lines:
                line.x += self.camera_x
                line.y += self.camera_y

            # Also apply to glow lines
            for line in self.renderer.glow_lines:
                line.x += self.camera_x
                line.y += self.camera_y

            self.renderer.render()

        # Draw FPS
        self.fps_display.draw()

        # Draw help text
        self.draw_help_text()

    def draw_help_text(self):
        """Draw help text for controls."""
        help_text = [
            "Controls:",
            "WASD: Move camera",
            "Arrow keys: Move camera",
            "ESC: Quit",
        ]

        y = self.height - 20
        for line in help_text:
            label = pyglet.text.Label(
                line, font_name="Arial", font_size=10, x=10, y=y, color=(0, 255, 0, 128)
            )
            label.draw()
            y -= 15

    def on_key_press(self, symbol, modifiers):
        """
        Handle key press events.

        Args:
            symbol: Key symbol
            modifiers: Key modifiers
        """
        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_resize(self, width, height):
        """
        Handle window resize event.

        Args:
            width: New window width
            height: New window height
        """
        super().on_resize(width, height)
        self.camera_x = width // 2
        self.camera_y = height // 2

    def update(self, dt):
        """
        Update the game state.

        Args:
            dt: Time since last update
        """
        # Update the renderer for CRT effects
        self.renderer.update(dt)

        # Handle camera movement
        move_x = 0
        move_y = 0

        if self.keys[key.W] or self.keys[key.UP]:
            move_y -= 1  # Inverted: Camera moves up, view moves down
        if self.keys[key.S] or self.keys[key.DOWN]:
            move_y += 1  # Inverted: Camera moves down, view moves up
        if self.keys[key.A] or self.keys[key.LEFT]:
            move_x += 1  # Inverted: Camera moves left, view moves right
        if self.keys[key.D] or self.keys[key.RIGHT]:
            move_x -= 1  # Inverted: Camera moves right, view moves left

        # Apply movement
        self.camera_x += move_x * self.camera_speed * dt
        self.camera_y += move_y * self.camera_speed * dt
