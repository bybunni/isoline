"""
Isoline Main Application

Entry point for the isometric vector graphics engine.
"""

import os
import sys
import argparse
import math
import pyglet
from pyglet.gl import *
from pyglet.window import key, FPSDisplay
from pyglet.math import Mat4, Vec3

from isoline.renderer import IsometricRenderer


class IsolineApp(pyglet.window.Window):
    """Main application window for Isoline engine"""

    def __init__(self, width=800, height=600, title="Isoline Engine"):
        super().__init__(width, height, title, resizable=True)

        # Setup OpenGL with minimal state setup
        glClearColor(
            0.0, 0.0, 0.0, 1.0
        )  # Black background for contrast with green lines

        # Skip the projection matrix setup - we'll use pyglet's defaults

        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable line smoothing if available
        try:
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        except:
            print("Line smoothing not available, continuing without it")

        # Set line width for visible lines (use a valid width)
        try:
            glLineWidth(2.0)  # Use 2.0 for more visible lines
        except Exception as e:
            print(f"Error setting line width: {e}")

        # Create renderer
        self.renderer = IsometricRenderer()

        # Set viewport size in renderer for culling optimization
        self.renderer.set_viewport_size(width, height)

        # Set default map offset to center of screen
        self.center_map()

        # Navigation controls
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.pan_speed = 5

        # Setup update event
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

        # FPS display in the top-left corner
        self.fps_display = FPSDisplay(self)
        self.fps_display.label.x = 10
        self.fps_display.label.y = self.height - 30
        self.fps_display.label.font_size = 14

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
        # Get current offsets
        x_offset = self.renderer.x_offset
        y_offset = self.renderer.y_offset

        # Handle keyboard navigation
        if self.keys[key.UP]:
            y_offset -= self.pan_speed
        if self.keys[key.DOWN]:
            y_offset += self.pan_speed
        if self.keys[key.LEFT]:
            x_offset += self.pan_speed
        if self.keys[key.RIGHT]:
            x_offset -= self.pan_speed

        # Set the new offset using the proper method that triggers a batch rebuild
        if x_offset != self.renderer.x_offset or y_offset != self.renderer.y_offset:
            self.renderer.set_offset(x_offset, y_offset)

        # Reset to center with spacebar
        if self.keys[key.SPACE]:
            self.center_map()

        # Update tile animations
        self.renderer.update_animation(dt)

        # Animation control keys
        if self.keys[key.A] and not hasattr(self, "animation_toggle_cooldown"):
            self.renderer.enable_animation(not self.renderer.animation_enabled)
            print(
                f"Animation {'enabled' if self.renderer.animation_enabled else 'disabled'}"
            )
            self.animation_toggle_cooldown = 0.5  # Cooldown to prevent multiple toggles

        # Speed controls
        if self.keys[key.EQUAL] and not hasattr(
            self, "speed_change_cooldown"
        ):  # Plus key (=)
            # Speed up animation (reduce frame time)
            self.renderer.set_animation_speed(
                max(0.05, self.renderer.animation_frame_time * 0.8)
            )
            print(f"Animation speed: {1.0/self.renderer.animation_frame_time:.2f} FPS")
            self.speed_change_cooldown = 0.3

        if self.keys[key.MINUS] and not hasattr(self, "speed_change_cooldown"):
            # Slow down animation (increase frame time)
            self.renderer.set_animation_speed(
                min(2.0, self.renderer.animation_frame_time * 1.2)
            )
            print(f"Animation speed: {1.0/self.renderer.animation_frame_time:.2f} FPS")
            self.speed_change_cooldown = 0.3

        # Handle cooldowns
        if hasattr(self, "animation_toggle_cooldown"):
            self.animation_toggle_cooldown -= dt
            if self.animation_toggle_cooldown <= 0:
                delattr(self, "animation_toggle_cooldown")

        if hasattr(self, "speed_change_cooldown"):
            self.speed_change_cooldown -= dt
            if self.speed_change_cooldown <= 0:
                delattr(self, "speed_change_cooldown")

        # Log FPS every second
        if hasattr(self, "fps_log_timer"):
            self.fps_log_timer += dt
            if self.fps_log_timer >= 1.0:
                # Safely get FPS value from fps_display object
                text_parts = self.fps_display.label.text.split()
                fps = text_parts[-1] if len(text_parts) > 0 else "N/A"
                print(f"Current FPS: {fps}")
                self.fps_log_timer = 0
        else:
            self.fps_log_timer = 0

    def on_draw(self):
        """Render the scene"""
        self.clear()

        # Render the map
        self.renderer.render()

        # Draw the FPS counter
        self.fps_display.draw()

    def on_resize(self, width, height):
        """Handle window resize"""
        # Modern OpenGL approach using pyglet's default handling
        super().on_resize(width, height)

        # Update FPS display position
        self.fps_display.label.y = height - 30

        # Skip updating the OpenGL projection - we'll use pyglet's defaults

        # Update renderer viewport size for culling optimization
        self.renderer.set_viewport_size(width, height)

        # Re-center map
        self.center_map()

        return pyglet.event.EVENT_HANDLED

    def on_key_press(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        elif symbol == key.H:
            # Display help
            print("\nIsoline Controls:")
            print("  Arrow Keys: Pan the map")
            print("  Space: Center the map")
            print("  A: Toggle animation")
            print("  +/-: Increase/decrease animation speed")
            print("  H: Show this help")
            print("  ESC: Exit\n")
        return pyglet.event.EVENT_HANDLED

    def cleanup(self):
        """Clean up resources"""
        self.renderer.cleanup()


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Isoline Engine - Isometric Vector Graphics Engine"
    )
    parser.add_argument("--map", "-m", type=str, help="Path to the map file (.mdmap)")
    args = parser.parse_args()

    # Create the application window
    app = IsolineApp()

    # Find the map file
    if args.map:
        # Use the provided map path
        if os.path.isabs(args.map):
            map_path = args.map
        else:
            # Relative path - check if it's a path relative to current directory
            if os.path.exists(args.map):
                map_path = os.path.abspath(args.map)
            else:
                # Check if it's in the maps directory
                project_root = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
                maps_dir = os.path.join(project_root, "maps")
                map_path = os.path.join(maps_dir, args.map)

                # If no extension provided, add .mdmap extension
                if not os.path.splitext(map_path)[1]:
                    map_path += ".mdmap"
    else:
        # Default map - look for default.mdmap in maps directory first
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        maps_dir = os.path.join(project_root, "maps")
        default_map = os.path.join(maps_dir, "default.mdmap")

        if os.path.exists(default_map):
            map_path = default_map
        else:
            # Fallback to the original grass map in the isoline package
            current_dir = os.path.dirname(os.path.abspath(__file__))
            map_path = os.path.join(current_dir, "grass.mdmap")

    print(f"Loading map: {map_path}")

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
