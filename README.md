# Isoline

Isoline is a retro-inspired isometric game engine that renders all graphics using vector primitives in the style of old monochrome green CRTs. Built with Python and Pyglet, it provides a modern implementation of classic isometric rendering techniques while maintaining a distinctive visual aesthetic.

## Features

- **Isometric Rendering**: Implements proper isometric projection with the optimal 2:1 tile ratio
- **Vector Graphics**: All game elements are drawn using vector primitives rather than sprites
- **Custom Map Format**: Supports the MDMap format (.mdmap) for defining multi-layered isometric levels
- **Green Monochrome Aesthetic**: Captures the look and feel of vintage monochrome displays
- **Layer System**: Supports multiple map layers (terrain, units, items, etc.)

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

To run the basic grass field example:

```bash
python run_isoline.py
```

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
W = Water
M = Mountain

[layer: terrain]
~~~~~~~~
GGGGGGGGGG
GGGGGGGGGG
GGMMMMMGGG
GGMMMMMGGG
GGMMMMMGGG
GGGWWWGGGG
GGGWWWGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
~~~~~~~~
```

See `isoline/grass.mdmap` for a simple example.

## Architecture

Isoline follows a modular architecture with clear separation of concerns:

### Component Overview

1. **Map Parser (`map_parser.py`)**
   - Handles loading and parsing of MDMap files
   - Creates structured representation of maps with layers, legends, and grid data

2. **Tile Renderer (`tile_renderer.py`)**
   - Defines the base `VectorTile` class and specialized tile types
   - Implements vector-based drawing for each tile type
   - Uses Pyglet's shapes module for efficient vector rendering

3. **Isometric Renderer (`renderer.py`)**
   - Manages the rendering of complete isometric maps
   - Handles layer ordering and composition
   - Implements isometric projection formulas
   - Manages tile caching for performance

4. **Main Application (`main.py`)**
   - Creates the application window and handles user input
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
- Animation support for dynamic elements
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