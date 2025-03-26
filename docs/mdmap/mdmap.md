*.mdmap Level File Format Specification

Version: 1.0
Author: You, probably high on parser design

📄 Overview
The .mdmap format defines an isometric game level using plaintext in a Markdown-inspired syntax. It supports multiple 2D grid-aligned layers, each representing a different aspect of the game world (terrain, units, loot, etc). Designed for:

Human readability/editability
Agentic AI parsing
Clear, deterministic layer composition
🧱 File Structure
Each level file is divided into the following sections:

Header
Legends (Optional)
Layer Blocks
1. Header
The header defines global metadata and appears at the top of the file using Markdown-style syntax:

# Level: Skull Canyon Bridge
Size: 8x6
Layers:
  - terrain
  - collision
  - units
  - loot
Header Fields:

# Level: <Name> — Required; name of the level.
Size: <width>x<height> — Required; dimensions of each layer.
Layers: — Required; ordered list of layer names. Determines render/composition order (bottom to top).
2. Legends (Optional but Recommended)
Used to describe tile or character mappings for each layer. Markdown-style sections with [legend: <layer>] syntax:

[legend: terrain]
G = Grass
M = Mountain
W = Water
B = Bridge
Keys must be single visible ASCII characters.
Descriptions are freeform but should be one line.
Multiple [legend: <layer>] sections allowed.
3. Layer Blocks
Each layer starts with [layer: <name>] followed by a tile grid delimited by ~~~~~~~~.

[layer: terrain]
~~~~~~~~
GGGGGGGG
GGMMMMGG
GGMBMMGG
WWBBBBWW
WWGGGGWW
GGGGGGGG
~~~~~~~~
Layer Rules:

The grid must exactly match the size defined in the header.
Characters are single-width ASCII glyphs.
Use . or a consistent null character for empty tiles.
Layers are composed in order, with later layers overlaying earlier ones.
Any unknown [layer] name not listed in the header Layers: will be ignored or warned.
🧠 Implementation Notes
Parsers should extract blocks using regex or line scanning:
^\[layer: (\w+)\] to find layers
^\[legend: (\w+)\] for legend blocks
^~~~~~~~~$ for layer delimiters
Treat whitespace strictly inside grids—spaces are valid characters.
Layer data should be stored as 2D lists/arrays indexed [y][x].
🧪 Example Snippet
[layer: loot]
~~~~~~~~
........
........
...$....
........
.....P..
........
~~~~~~~~
Means:

A gold coin ($) is at (3,2)
A potion (P) is at (5,4)
All other tiles are empty
🚫 Limitations
No support for multi-character tiles or tile metadata (yet).
No file inclusion or template support.
Comments in layer data not allowed (keep them in the legends).