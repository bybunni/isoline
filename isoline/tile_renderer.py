"""
Tile Renderer

Handles rendering of individual tiles using vector graphics
in the style of old monochrome green CRTs.

Optimized version with vertex array caching, batch rendering, and animation support.

This module re-exports all tile-related classes and functions from their individual modules
for backward compatibility.
"""

# Re-export everything for backward compatibility
from isoline.vector_tile import VectorTile
from isoline.grass_tile import GrassTile
from isoline.water_tile import WaterTile
from isoline.tile_factory import create_tile

__all__ = ['VectorTile', 'GrassTile', 'WaterTile', 'create_tile']
