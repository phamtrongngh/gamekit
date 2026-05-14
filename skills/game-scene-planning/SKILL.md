---
name: game-scene-planning
description: >
  Convert a game reference brief or user feature request into a concrete Godot scene plan. Use this skill after analyzing a screenshot/mockup/concept image, or whenever the user wants to build a level, gameplay scene, combat arena, cutscene, UI screen, or hybrid scene in Godot. It chooses 2D vs 3D, node architecture, reusable scene boundaries, asset strategy, gameplay assumptions, and implementation order.
---

# Game Scene Planning

Create the implementation blueprint before editing a Godot project. This skill turns visual analysis and user intent into scene structure, responsibilities, and build order.

## Required Inputs

Use `game-reference-analysis` first when an image is involved. If no image exists, infer from the user's request and existing project structure.

Before planning, determine:
- Target project path and Godot version if available.
- Scene type: UI, 2D world, 3D world, hybrid, cutscene, arena, level.
- Deliverable: visual blockout, playable prototype, production scene, or scene refactor.
- Existing scenes/scripts/assets that should be reused.

## Planning Output

Always output:

```markdown
## Scene Plan

Goal:
Scene type:
Primary Godot root:
Target scene path:

Scene tree:
```text
...
```

Reusable sub-scenes:
| scene | root node | responsibility |

Scripts:
| script | owner node | responsibility |

Assets:
| asset need | source | fallback |

Interactions:
| actor | behavior | signals/events |

Assumptions:
Build order:
Verification plan:
```

## Root Node Decision

| Scene need | Root node |
|---|---|
| Menu, shop, settings, inventory, HUD-only | `Control` |
| 2D gameplay level | `Node2D` |
| Reusable 2D player/enemy/object | `CharacterBody2D`, `Area2D`, `RigidBody2D`, or `Node2D` |
| 3D gameplay level | `Node3D` |
| Reusable 3D character/enemy/object | `CharacterBody3D`, `Area3D`, `RigidBody3D`, or `Node3D` |
| Overlay on gameplay | `CanvasLayer` with `Control` children |

Prefer the simplest root that matches the scene's responsibility.

## Scene Boundary Rules

Create separate reusable scenes for:
- Player characters.
- Enemy types.
- Collectibles.
- Interactables.
- Projectiles.
- HUD overlays.
- Complex props with collision or behavior.

Keep level scenes responsible for composition and spawning, not detailed actor behavior.

## 2D Scene Template

```text
LevelName (Node2D)
├── World
│   ├── Background
│   ├── Terrain
│   ├── Props
│   ├── Interactables
│   ├── Hazards
│   └── SpawnPoints
├── Player
├── Enemies
├── Camera2D
├── Navigation
└── HUDLayer (CanvasLayer)
```

Use `TileMapLayer` when the project already uses tiles or the scene is tile-based. Use composed `StaticBody2D`/`Sprite2D` props for bespoke mockups and blockouts.

## 3D Scene Template

```text
LevelName (Node3D)
├── World
│   ├── BlockoutGeometry
│   ├── Props
│   ├── Interactables
│   ├── Hazards
│   └── SpawnPoints
├── Player
├── Enemies
├── CameraRig
├── Navigation
├── Lighting
└── HUDLayer (CanvasLayer)
```

Use primitive meshes for blockout first unless the user supplied production assets.

## Architecture Decisions

### Player

Use `godot-character-setup` when the scene includes a controllable actor or player spawn.

### Enemies

Use `godot-enemy-setup` when the image or request includes hostile actors, combat, patrol, chasing, or spawn waves.

### Objects

Use `godot-object-interactions` for collectibles, doors, switches, pickups, chests, portals, triggers, hazards, breakables, or scripted props.

### Collision And Navigation

Use `godot-level-collision-navigation` before final testing for any playable world scene.

### UI/HUD

Use `godot-ui-hud-overlay` when a gameplay scene has health, score, minimap, inventory buttons, mobile controls, pause, dialogue, or prompts.

### Camera/Lighting/VFX

Use `godot-camera-lighting-vfx` for scene mood, framing, parallax, camera follow, lighting, particles, and visual effects.

## Build Order

1. Inspect existing project scenes, scripts, assets, and input actions.
2. Create or update reusable actor/object scenes.
3. Compose the level/world scene.
4. Add collision/navigation.
5. Add HUD overlay.
6. Add camera, lighting, and VFX.
7. Wire signals and scene transitions.
8. Run verification.

Use `godot-engine-tools` for scene/node automation and `godot-2d-expert` for GDScript patterns.
