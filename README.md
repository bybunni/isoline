# Isoline

A vector graphics isometric game engine built on pyglet, inspired by retro monochrome CRT vector graphics.

## Features

- Isometric vector graphics rendering
- mdmap file format support for easy map creation
- Monochrome green CRT aesthetic
- Reusable engine architecture for various games

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/isoline.git
cd isoline

# Install in development mode
pip install -e .
```

## Usage

```bash
# Run with default example map
python -m isoline.main

# Run with a specific map
python -m isoline.main --map path/to/your.mdmap

# Run in fullscreen
python -m isoline.main --fullscreen
```

## Map Format

Isoline uses the mdmap format for defining game maps. See the [mdmap specification](docs/mdmap/mdmap.md) for details.

Example:

```
# Level: Vector Test
Size: 10x10
Layers:
  - terrain

[legend: terrain]
G = Grass
M = Mountain
W = Water
B = Bridge

[layer: terrain]
~~~~~~~~
GGGGGGGGGG
GGGGMMGGGG
GGMMMMGGGG
GGGMMGGGGG
WWWBBWWWWW
WWWBBWWWWW
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
GGGGGGGGGG
~~~~~~~~
```

## License

MIT 