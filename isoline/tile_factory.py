"""
Tile Factory

Factory function for creating different tile types.
"""

from typing import Optional
from isoline.vector_tile import VectorTile
from isoline.grass_tile import GrassTile
from isoline.water_tile import WaterTile


def create_tile(tile_type: str, width: int = 100, height: int = 50) -> VectorTile:
    """Factory function to create the appropriate tile type"""
    if tile_type in ["G", "g"]:  # Grass (support both upper and lowercase)
        return GrassTile(width, height, num_states=5)
    elif tile_type in ["W", "w"]:  # Water (support both upper and lowercase)
        return WaterTile(width, height, num_states=5)
    else:
        raise ValueError(f"Unknown tile type: {tile_type}")
