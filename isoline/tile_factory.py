"""
Tile Factory

Factory function for creating different tile types.
"""

from typing import Optional
from isoline.vector_tile import VectorTile
from isoline.tiles.grass import GrassTile
from isoline.tiles.water import WaterTile
from isoline.tiles.sand import SandTile
from isoline.tiles.pyramid import PyramidTile
from isoline.tiles.lava import LavaTile
from isoline.tiles.snow import SnowTile
from isoline.tiles.forest import ForestTile
from isoline.tiles.wheat import WheatFieldTile
from isoline.tiles.boxstack import BoxStackTile


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type in ["G", "g"]:  # Grass (support both upper and lowercase)
        return GrassTile(width, height, num_states=5)
    elif tile_type in ["W", "w"]:  # Water (support both upper and lowercase)
        return WaterTile(width, height, num_states=5)
    elif tile_type in ["S", "s"]:  # Sand (support both upper and lowercase)
        return SandTile(width, height, num_states=1)
    elif tile_type in ["P", "p"]:  # Pyramid (support both upper and lowercase)
        return PyramidTile(width, height, num_states=3)
    elif tile_type in ["L", "l"]:  # Lava (support both upper and lowercase)
        return LavaTile(width, height, num_states=5)
    elif tile_type in ["N", "n"]:  # Snow (support both upper and lowercase)
        return SnowTile(width, height, num_states=5)
    elif tile_type in ["F", "f"]:  # Forest (support both upper and lowercase)
        return ForestTile(width, height, num_states=5)
    elif tile_type in ["H", "h"]:  # Wheat Field (support both upper and lowercase)
        return WheatFieldTile(width, height, num_states=5)
    elif tile_type in ["B", "b"]:  # Box Stack (support both upper and lowercase)
        return BoxStackTile(width, height, num_states=3)
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
