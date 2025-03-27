# Isoline Tile Rendering Pipeline

This document describes the high-level steps in the Isoline tile rendering pipeline, from map loading to screen rendering.

## 1. Map Loading

- **Map Parsing**: The `.mdmap` file is parsed by the `parse_mdmap` function, which creates an `MDMap` object containing map header and layer data.
- **Tile Initialization**: Upon loading a map, the `_init_tiles` method identifies all unique tile types in the map and creates corresponding `VectorTile` objects (such as `GrassTile`). These are stored in the `tile_cache` dictionary.

## 2. Camera and Viewport Management

- **Offset Handling**: Camera position is managed through the `x_offset` and `y_offset` variables in the `IsometricRenderer`.
- **User Input**: The application responds to arrow key inputs by updating these offsets via the `set_offset` method, which flags the need for a batch rebuild.
- **Centering**: The spacebar resets the view to center the map on the screen.

## 3. Batch Creation and Management

- **Batch Initialization**: When a map is loaded or the camera position changes, a new `pyglet.graphics.Batch` is created.
- **Layer Processing**: Each layer from the map is processed in order, with tiles from each layer added to the batch.
- **Isometric Projection**: For each tile, its isometric screen position is calculated based on:
  - The renderer's current offset
  - The tile's grid position (x, y)
  - The isometric projection formula:
    - `x_screen = x_offset + (x * tile_width/2) - (y * tile_width/2)`
    - `y_screen = y_offset + (x * tile_height/2) + (y * tile_height/2)`

## 4. Vector Shape Generation

- **Shape Creation**: Each `VectorTile` instance creates vector shapes (lines, polygons) for its visual representation.
- **Outlining**: Tiles have outline points that form their diamond shape.
- **Content Rendering**: Each tile type implements its own `_create_content_shapes` method to draw its specific graphics (e.g., grass blades).
- **Shape Tracking**: Generated shapes are stored in `shapes_by_position` to manage them during updates and cleanup.

## 5. OpenGL Rendering

- **State Setup**: Before rendering, OpenGL state is configured (blending, line width, etc.).
- **Batch Drawing**: The entire batch is rendered with a single `batch.draw()` call, which is highly efficient.
- **State Cleanup**: After rendering, OpenGL state is restored.

## 6. Memory and Resource Management

- **Cleanup**: The `cleanup` method ensures all OpenGL resources are properly released when tiles are no longer needed.
- **Position-based Caching**: Shapes are cached by their screen position, but are always recreated when the position changes to ensure proper camera movement.

## Performance Considerations

- **Batch Rendering**: Using batched rendering significantly improves performance (from ~4 FPS to ~35-40 FPS).
- **Rebuild Triggers**: The batch is only rebuilt when necessary (camera movement, map loading), not on every frame.
- **Shape Management**: When adding tiles to a batch at a position, existing shapes at that position are deleted before creating new ones to prevent memory leaks.

## Key Components

- **IsometricRenderer**: Manages the overall rendering process and map data.
- **VectorTile**: Base class for all tile types, handling common rendering operations.
- **Specific Tile Types**: Extend the base `VectorTile` class to implement unique visuals (e.g., `GrassTile`).

## Update Cycle

1. Input handling updates camera offsets
2. When offsets change, the `needs_rebuild` flag is set
3. During the next render call, if `needs_rebuild` is true, the batch is completely rebuilt
4. The rebuilt batch contains all tiles at their new screen positions
5. The batch is rendered with a single OpenGL call
