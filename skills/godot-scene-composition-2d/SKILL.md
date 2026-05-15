---
name: godot-scene-composition-2d
description: >
  Build or modify 2D Godot gameplay scenes from a reference brief, mockup, screenshot, or level plan. Use this skill for side-scrollers, platformers, top-down RPG scenes, isometric-style 2D scenes, combat arenas, puzzle boards, tilemap levels, and any Godot scene rooted in Node2D. It covers scene tree structure, world layers, props, terrain, spawn points, camera placement, and integration with characters, enemies, objects, collision, HUD, and verification.
---

# Godot Scene Composition 2D

Compose a playable 2D Godot scene from a plan. This skill focuses on world assembly, not detailed actor scripts.

Use Godot MCP tools for creating scenes, adding nodes, loading sprites, saving scenes, and running the project when they are available. Fall back to `godot-engine-tools` or local Godot CLI helpers when MCP is unavailable. Use `godot-2d-expert` when writing GDScript if that skill is available.

## Standard Scene Tree

```text
LevelName (Node2D)
├── World (Node2D)
│   ├── Background (Node2D/ParallaxBackground/Sprite2D)
│   ├── Terrain (Node2D/TileMapLayer)
│   ├── Platforms (Node2D)
│   ├── Props (Node2D)
│   ├── Interactables (Node2D)
│   ├── Hazards (Node2D)
│   └── SpawnPoints (Node2D)
├── PlayerSpawn (Marker2D)
├── Player (instance)
├── Enemies (Node2D)
├── Navigation (Node2D)
├── Camera2D
└── HUDLayer (CanvasLayer)
```

Remove unused groups for tiny scenes, but keep names clear.

## Layering Order

Use increasing z-index/deeper tree order:

1. Far background.
2. Mid background/parallax.
3. Terrain behind actors.
4. Interactables and props.
5. Player/enemies/projectiles.
6. Foreground occluders.
7. HUD in `CanvasLayer`.

Set `z_index` only when needed. Prefer tree order and named layers for simple scenes.

## Scene Type Patterns

### Side-View Platformer

Required:
- Ground and platforms with collision.
- Player spawn above stable ground.
- Camera follow with horizontal margins.
- Kill zones for pits if visible or implied.
- Enemy patrol markers if enemies exist.

Use `CharacterBody2D` for player and most enemies.

### Top-Down Scene

Required:
- Walkable area and blocked props/walls.
- Camera follow or room camera.
- Navigation regions for AI if enemies/NPCs move.
- Interactable prompts near doors, NPCs, chests, or objects.

Use `CharacterBody2D` with `Input.get_vector()` for player movement.

### Combat Arena

Required:
- Arena boundaries.
- Player spawn.
- Enemy spawns.
- Hazard/object placement.
- Camera framing that keeps the arena readable.

Prefer spawn markers over hardcoded positions.

### Puzzle Board

Required:
- Board origin and cell size.
- Tile/container hierarchy.
- Interaction layer separate from visuals.
- Deterministic indexing by row/column.

## Working From A Screenshot

Map image coordinates to world coordinates:

```text
world_x = (image_x_percent - 0.5) * target_world_width
world_y = (image_y_percent - 0.5) * target_world_height
```

Choose a sensible scale:
- Platformer: player height usually 48-128 px depending art style.
- Top-down: one tile often 16, 32, 48, or 64 px.
- Mobile portrait scenes: keep controls/HUD in safe margins.

Document scale assumptions in the scene plan or script comments.

## Composition Checklist

Before moving to verification:

```markdown
[ ] Scene has a clear root and layer organization
[ ] Player spawn is on valid ground/walkable area
[ ] Enemies/objects are grouped under named parents
[ ] Collision/navigation nodes exist where gameplay needs them
[ ] Camera frames the intended play area
[ ] HUD is in CanvasLayer, not mixed into world nodes
[ ] Placeholder assets are named as placeholders
[ ] Reusable actors/objects are instanced, not rebuilt inline
```

## Integration Points

- Use `godot-character-setup` for player scenes.
- Use `godot-enemy-setup` for enemy scenes and AI markers.
- Use `godot-object-interactions` for collectibles/hazards/doors/triggers.
- Use `godot-level-collision-navigation` for world physics and AI paths.
- Use `godot-ui-hud-overlay` for gameplay UI.
- Use `godot-camera-lighting-vfx` for camera, parallax, particles, and mood.
