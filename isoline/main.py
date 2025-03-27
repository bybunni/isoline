"""
Isoline Main Application

Entry point for the isometric vector graphics engine.
"""

import os
import sys
import pyglet
from pyglet.gl import *
from pyglet.window import key
from pyglet.math import Mat4, Vec3

from isoline.renderer import IsometricRenderer


class IsolineApp(pyglet.window.Window):
    """Main application window for Isoline engine"""

    def __init__(self, width=800, height=600, title="Isoline Engine"):
        super().__init__(width, height, title, resizable=True)

        # Setup OpenGL
        glClearColor(0.05, 0.05, 0.05, 1.0)  # Dark background

        # Enable line smoothing if available
        try:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        except:
            print("Line smoothing not available, continuing without it")

        # Create renderer
        self.renderer = IsometricRenderer()

        # Set default map offset to center of screen
        self.center_map()

        # Navigation controls
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.pan_speed = 5

        # Setup update event
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def center_map(self):
        """Center the map in the window"""
        self.renderer.set_offset(self.width // 2, self.height // 2)

    def load_map(self, map_path):
        """Load a map file"""
        success = self.renderer.load_map(map_path)
        if success:
            self.center_map()
            print(f"Loaded map: {map_path}")
        return success

    def update(self, dt):
        """Update game state"""
        # Handle keyboard navigation
        if self.keys[key.UP]:
            self.renderer.y_offset += self.pan_speed
        if self.keys[key.DOWN]:
            self.renderer.y_offset -= self.pan_speed
        if self.keys[key.LEFT]:
            self.renderer.x_offset += self.pan_speed
        if self.keys[key.RIGHT]:
            self.renderer.x_offset -= self.pan_speed

        # Reset to center with spacebar
        if self.keys[key.SPACE]:
            self.center_map()

    def on_draw(self):
        """Render the scene"""
        self.clear()

        # Pyglet automatically sets up a 2D projection for us
        # Just render the map
        self.renderer.render()

    def on_resize(self, width, height):
        """Handle window resize"""
        # Modern OpenGL approach using pyglet's default handling
        super().on_resize(width, height)

        # Re-center map
        self.center_map()

        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        return pyglet.event.EVENT_HANDLED

    def cleanup(self):
        """Clean up resources"""
        self.renderer.cleanup()


def main():
    """Main entry point"""
    # Create the application window
    app = IsolineApp()

    # Find the map file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_path = os.path.join(current_dir, "grass.mdmap")

    # Load the map
    if not app.load_map(map_path):
        print(f"Error: Could not load map at {map_path}")
        return 1

    # Start the application
    try:
        pyglet.app.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        app.cleanup()

    return 0


if __name__ == "__main__":
    sys.exit(main())
