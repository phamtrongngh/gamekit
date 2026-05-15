---
name: game-reference-analysis
description: >
  Analyze any game reference image, screenshot, mockup, sketch, concept art, or in-game frame before implementation. Use this skill whenever the user provides a visual reference and wants a Godot scene, level, gameplay screen, UI, character setup, enemy placement, objects, HUD, or scene recreation. This skill extracts scene type, camera/view, entities, objects, layout, colors, proportions, inferred gameplay affordances, and uncertainty. Use it even when the user only says "make this in Godot" with an image.
---

# Game Reference Analysis

Turn a visual reference into a structured implementation brief. This skill is engine-agnostic, but its output is designed to feed Godot scene-building skills.

Use this before building anything from an image. A screenshot contains visible facts and hidden assumptions; separate them clearly so later implementation does not invent architecture accidentally.

## Output Contract

Always produce this brief before implementation:

```markdown
## Reference Brief

Scene category:
Camera/view:
Target orientation/aspect:
Core gameplay genre:

Visible entities:
| id | kind | approximate position | size/scale | visible details |

World objects and props:
| id | kind | static/interactable | approximate position | notes |

Terrain and collision candidates:
| area | likely collision type | notes |

UI/HUD overlay:
| element | position | content | notes |

Color and lighting:
Typography:
Motion implied by image:
Gameplay assumptions:
Open questions:
Implementation risks:
```

Keep positions relative to the image: `top-left`, `center`, `bottom-right`, or percentages such as `x 42%, y 68%`. Use approximate values when exact pixel data is unavailable.

## Analysis Steps

### 1. Classify The Scene

Pick the primary category:

| Category           | Trigger signs                                                      |
| ------------------ | ------------------------------------------------------------------ |
| UI screen          | menu, buttons, panels, inventory, shop, settings, HUD-heavy screen |
| 2D side-view level | ground/platforms, horizon, side-facing characters                  |
| 2D top-down level  | floor plan, rooms, paths, overhead characters                      |
| 2D isometric scene | diamond tiles, angled top-down view                                |
| 3D gameplay scene  | perspective depth, 3D camera, volumetric objects                   |
| Combat arena       | centered play space, enemies, hazards, player/enemy confrontation  |
| Dialogue/cutscene  | characters staged for conversation, text box, cinematic framing    |
| Hybrid             | gameplay plus HUD, level plus menu overlay, or mixed scene         |

If the image is hybrid, name both the world layer and the UI layer.

### 2. Identify The Camera

Record:

- View type: side, top-down, isometric, first-person, third-person, fixed cinematic, orthographic 3D, perspective 3D.
- Camera behavior inferred: fixed, follows player, room-based, side-scroll, arena-centered.
- Framing: where the player/action is meant to sit in the viewport.
- Important negative space: sky, floor, UI-safe margins, offscreen spawn space.

### 3. Inventory Entities

Separate visible things into stable implementation categories:

| Visual thing                         | Implementation category |
| ------------------------------------ | ----------------------- |
| Main controllable character          | player                  |
| Hostile creature/robot/NPC attacking | enemy                   |
| Neutral character                    | npc                     |
| Coin, gem, key, heart, ammo          | collectible             |
| Door, chest, lever, switch, portal   | interactable            |
| Spikes, lava, projectile, trap       | hazard                  |
| Crate, rock, tree, furniture         | prop                    |
| Ground, wall, platform, water edge   | terrain                 |
| Health bar, score, minimap, buttons  | hud_ui                  |

For each entity, include count, placement, approximate size, and likely role.

### 4. Infer Gameplay Affordances

Only infer behavior that common genre conventions strongly support.

Examples:

- Side-view platformer: ground collision, jumpable platforms, pits/hazards, player gravity.
- Top-down RPG: walkable floor, blocked walls/props, interactable NPCs, camera follow.
- Arena action: bounded play area, enemy spawn points, player movement, hitboxes.
- Tower defense: path, spawn entrance, exit, build slots, wave UI.

Mark uncertain behavior as `assumption`, not fact.

### 5. Extract Visual Style

Capture:

- Dominant palette and contrast.
- Lighting direction and mood.
- Sprite style: pixel art, hand-painted, vector, low-poly, realistic, cel-shaded.
- Scale convention: character height relative to tiles/platforms/doors.
- UI style if present: flat, skeuomorphic, fantasy, sci-fi, pixel, minimal.

### 6. Decide What Needs Assets

Flag each visual component:

| Status                 | Meaning                                                  |
| ---------------------- | -------------------------------------------------------- |
| existing asset         | search repo and reuse                                    |
| extract from reference | crop/background/icon possible                            |
| placeholder            | shape or simple sprite is enough for gameplay            |
| generated asset        | needs new raster asset                                   |
| code-native            | can be built with Godot nodes, materials, shapes, labels |

Do not recommend extracting stylized text as a raster logo unless the user explicitly requires pixel-perfect reproduction.

When marking an item as `generated asset`, note whether it should use `imagegen` and whether it needs transparency, animation frames, tiling, or later `game-asset-analyzer` metadata.

## Questions Policy

Ask only when the answer changes architecture:

- 2D or 3D when the image is ambiguous.
- Player controller type when multiple are plausible.
- Whether the goal is visual blockout, playable prototype, or close visual recreation.
- Which existing Godot project/scene path to integrate into if not discoverable.

If nothing blocks architecture, proceed with reasonable conventions and list assumptions.
