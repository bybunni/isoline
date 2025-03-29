# Isoline

Isoline is a retro-inspired isometric game engine that renders all graphics using vector primitives in the style of old monochrome green CRTs. Built with Python and Pyglet, it provides a modern implementation of classic isometric rendering techniques while maintaining a distinctive visual aesthetic.

## Features

- **Isometric Rendering**: Implements proper isometric projection with the optimal 2:1 tile ratio
- **Vector Graphics**: All game elements are drawn using vector primitives (lines) rather than sprites, via `pyglet.shapes`
- **Tile Animation**: Supports multi-state tile animations (e.g., swaying grass)
- **Custom Map Format**: Supports the MDMap format (.mdmap) for defining multi-layered isometric levels
- **Green Monochrome Aesthetic**: Captures the look and feel of vintage monochrome displays
- **Layer System**: Supports multiple map layers (terrain, units, items, etc.)
- **Performance Optimizations**: Utilizes efficient rendering techniques:
    - **Batch Rendering**: Groups draw calls using `pyglet.graphics.Batch`
    - **Vertex Caching**: Caches vertex data per tile state
    - **View Frustum Culling**: Only renders tiles potentially visible on screen
    - **Incremental Updates**: Rebuilds only necessary parts of the batch when changes occur (e.g., animation, minor camera movement)

## Installation

### Prerequisites

- Python 3.8+
- Pyglet 2.0+
- NumPy

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/isoline.git
   cd isoline
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pyglet numpy
   ```

## Usage

### Running the Demo

To run the default map example:

```bash
python -m isoline.main
```

To run a specific map file:

```bash
python -m isoline.main --map maps/terrain.mdmap
# Or use the short option format
python -m isoline.main -m terrain
```

The `--map` argument accepts:
- Full absolute paths to .mdmap files
- Relative paths from the current directory
- Simple map names (with or without .mdmap extension) that will be searched for in the maps/ directory

### Controls

- **Arrow Keys**: Navigate around the map
- **Spacebar**: Reset view to center
- **Escape**: Exit the application

### Creating Custom Maps

Isoline uses the MDMap format for defining isometric maps. Create a file with the `.mdmap` extension following this structure:

```
# Level: Your Level Name
Size: 10x10
Layers:
  - terrain
  - collision
  - units

[legend: terrain]
G = Grass
# Example legend - add other tile types here
# W = Water
# M = Mountain

[layer: terrain]
~~~~~~~~\
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
~~~~~~~~

# Add other layers below, matching the 'Layers' list
# [layer: collision]
# ...
```

See `maps/small_grass.mdmap` for a simple example.

## Architecture

Isoline follows a modular architecture with clear separation of concerns:

### Component Overview

1. **Map Parser (`map_parser.py`)**
   - Handles loading and parsing of MDMap files
   - Creates structured representation of maps with layers, legends, and grid data

2. **Tile Renderer (`tile_renderer.py`)**
   - Defines the base `VectorTile` class and specialized tile types (e.g., `GrassTile`)
   - Implements vector-based drawing for each tile type using `pyglet.shapes` (primarily `shapes.Line`)
   - Supports multiple animation states per tile
   - Caches generated vertex data per animation state for efficiency

3. **Isometric Renderer (`renderer.py`)**
   - Manages the rendering of complete isometric maps
   - Handles layer ordering and composition
   - Implements isometric projection formulas to place tiles
   - Manages tile instance caching and state
   - Coordinates tile animations based on timing
   - Optimizes rendering via view frustum culling and incremental batch updates (`dirty_tiles` system)

4. **Main Application (`main.py`)**
   - Creates the application window and handles user input (keyboard controls)
   - Coordinates between the renderer and user interaction
   - Manages application lifecycle

### Key Design Principles

- **Separation of Concerns**: Each module has a specific responsibility
- **Extensibility**: Easily add new tile types by extending the `VectorTile` class
- **Performance**: Uses efficient rendering techniques like batching and caching
- **Modularity**: Components interact through well-defined interfaces

## Mathematical Foundation

The isometric projection uses the following formulas to convert grid coordinates to screen coordinates:

```
x_screen = x_start + (x * TILE_WIDTH/2) - (y * TILE_WIDTH/2)
y_screen = y_start + (x * TILE_HEIGHT/2) + (y * TILE_HEIGHT/2)
```

Where:
- `x`, `y` are grid cell coordinates
- `TILE_WIDTH`, `TILE_HEIGHT` are the dimensions of a tile (using 2:1 ratio)
- `x_start`, `y_start` are the screen position offsets

## Future Plans

- Additional tile types (water, mountain, roads, etc.)
- Pathfinding for units
- Advanced lighting effects
- Editable map interface
- Game object interaction system
- Audio support with retro-inspired sound effects

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by classic isometric games like SimCity, Civilization, and Ultima
- Documentation on isometric projection techniques
- The Pyglet community for their excellent graphics library 