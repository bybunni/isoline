"""
Main entry point for the Isoline engine demo.
"""

import os
import pyglet
import argparse
from isoline.core.game import IsolineGame


def main():
    """
    Main entry point for the Isoline engine.
    """
    parser = argparse.ArgumentParser(description="Run the Isoline engine demo.")
    parser.add_argument("--map", type=str, help="Path to a mdmap file to load")
    parser.add_argument(
        "--fullscreen", action="store_true", help="Start in fullscreen mode"
    )
    parser.add_argument("--width", type=int, default=1024, help="Window width")
    parser.add_argument("--height", type=int, default=768, help="Window height")
    args = parser.parse_args()

    # Use example map if none provided
    map_path = args.map
    if not map_path and os.path.exists("docs/mdmap/example.mdmap"):
        map_path = "docs/mdmap/example.mdmap"

    # Create and run the game
    game = IsolineGame(
        width=args.width,
        height=args.height,
        title="Isoline Vector Engine Demo",
        fullscreen=args.fullscreen,
        mdmap_path=map_path,
    )

    # No need to hook up key handlers as they're already defined in the IsolineGame class

    # Run the game
    pyglet.app.run()


if __name__ == "__main__":
    main()
