---
name: godot-scene-from-reference
description: >
  Master orchestrator for turning any screenshot, mockup, sketch, concept art, or gameplay reference image into a Godot scene. Use this skill whenever the user provides an image and asks to build, recreate, prototype, or implement it in Godot, whether it is a main menu, HUD, in-game level, 2D platformer scene, top-down RPG scene, 3D scene, combat arena, cutscene, room, character/enemy/object setup, or hybrid gameplay plus UI. This skill coordinates the smaller reference-analysis, planning, asset, composition, character, enemy, object, collision, HUD, camera/VFX, and verification skills.
---

# Godot Scene From Reference

Transform a visual reference into a working Godot scene. This is an orchestrator skill: it decides which specialized skills to use and in what order.

Use it for any image-driven Godot scene, not only UI.

## Core Pipeline

```text
REFERENCE
  -> ANALYZE
  -> PLAN
  -> PREPARE ASSETS
  -> COMPOSE SCENE
  -> ADD ACTORS/OBJECTS
  -> ADD COLLISION/NAVIGATION
  -> ADD HUD/CAMERA/VFX
  -> VERIFY
```

Do not skip analysis and verification. They prevent visual guesses from becoming broken scene architecture.

## Skill Routing

| Need                                      | Use skill                                    |
| ----------------------------------------- | -------------------------------------------- |
| Understand screenshot/mockup/concept art  | `game-reference-analysis`                    |
| Choose scene architecture and build order | `game-scene-planning`                        |
| Reuse/crop/placeholder/generate assets    | `game-reference-asset-preparation`           |
| Build 2D world scene                      | `godot-scene-composition-2d`                 |
| Build 3D world scene                      | `godot-scene-composition-3d`                 |
| Build player/controller                   | `godot-character-setup`                      |
| Build enemies/AI/spawns                   | `godot-enemy-setup`                          |
| Build collectibles/interactables/hazards  | `godot-object-interactions`                  |
| Add collision/navigation/bounds           | `godot-level-collision-navigation`           |
| Add HUD/gameplay overlay                  | `godot-ui-hud-overlay`                       |
| Add camera/lighting/parallax/VFX          | `godot-camera-lighting-vfx`                  |
| Verify implementation                     | `godot-scene-verification`                   |
| Create/modify/run Godot projects          | Godot MCP tools from `Coding-Solo/godot-mcp` |
| Analyze individual image assets           | `game-asset-analyzer`                        |
| Generate or edit missing bitmap assets    | `imagegen`                                   |

## Tooling Backends

Use the project-configured Godot MCP tools from `Coding-Solo/godot-mcp` for:

- getting the Godot version and project info
- listing/discovering projects
- creating scenes
- adding nodes
- loading sprites/textures
- saving scenes
- running the project
- capturing debug output
- stopping the project
- updating UIDs for Godot 4.4+ projects

Use ordinary shell/Godot CLI commands only for operations outside the MCP tool surface.

When a missing visual asset should be created as a bitmap, use the `imagegen` skill. It is appropriate for sprites, textures, background plates, props, concept variants, transparent cutouts, and UI mockups. Do not use image generation for simple Godot-native shapes, deterministic UI controls, vector/SVG assets, or placeholders that are better built directly in code.

## Phase 1: Analyze

Use `game-reference-analysis` and produce a reference brief with:

- Scene category.
- Camera/view.
- Visible entities.
- Terrain/objects/props.
- HUD/UI elements.
- Collision candidates.
- Style, color, lighting.
- Gameplay assumptions and open questions.

Ask only questions that affect architecture. Otherwise proceed with documented assumptions.

## Phase 2: Plan

Use `game-scene-planning` to decide:

- 2D or 3D.
- Root node and target scene path.
- Reusable sub-scenes.
- Scripts and signals.
- Asset strategy.
- Build order.
- Verification plan.

Inspect the existing Godot project before editing. Reuse existing architecture whenever reasonable.

## Phase 3: Prepare Assets

Use `game-reference-asset-preparation`.

Rules:

- Search existing assets first.
- Use placeholders for playable prototypes.
- Crop only clean static elements.
- Generate raster assets only when they materially improve the scene.
- Use `imagegen` for generated raster assets, then save the final selected asset inside the Godot project before referencing it.
- Use `game-asset-analyzer` for any asset needing precise offsets, collision, or attachment points.

## Phase 4: Compose Scene

Route by scene type:

| Reference type                                       | Composition skill                          |
| ---------------------------------------------------- | ------------------------------------------ |
| 2D side-scroller/platformer/top-down/isometric/arena | `godot-scene-composition-2d`               |
| 3D first-person/third-person/isometric/room/arena    | `godot-scene-composition-3d`               |
| Gameplay plus HUD                                    | 2D/3D composition + `godot-ui-hud-overlay` |

Use Godot MCP tools for scene and node operations instead of manually writing `.tscn` files.

## Phase 5: Add Gameplay Elements

Use specialized skills based on the reference:

- Player visible or required: `godot-character-setup`.
- Hostiles visible or required: `godot-enemy-setup`.
- Collectibles, hazards, doors, switches, triggers: `godot-object-interactions`.
- Walkable/blocking spaces, AI paths, spawn safety: `godot-level-collision-navigation`.

Keep reusable actor/object behavior in separate scenes/scripts.

## Phase 6: Add Presentation Layer

Use:

- `godot-ui-hud-overlay` for health, score, prompts, inventory, dialogue, mobile controls.
- `godot-camera-lighting-vfx` for framing, camera follow, parallax, lighting, particles, and visual mood.

Presentation should support gameplay readability.

## Phase 7: Verify

Use `godot-scene-verification`.

At minimum:

- Run or load the target scene.
- Capture errors/warnings.
- Check missing resources and node paths.
- Check player spawn/collision if playable.
- Check visible match against the reference.
- Report assumptions and remaining gaps.

## Default Assumptions

Use these only when the user has not specified otherwise:

| Ambiguity                     | Default                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| deliverable unclear           | playable prototype with clear placeholders                     |
| screenshot is side-view       | 2D `Node2D` scene                                              |
| screenshot is top-down        | 2D `Node2D` scene                                              |
| screenshot has perspective 3D | 3D `Node3D` blockout                                           |
| player controls unclear       | genre-standard movement                                        |
| target scene path unclear     | `res://scenes/[scene_name].tscn` following project conventions |
| source assets missing         | use placeholders and document gaps                             |

## Final Response Shape

Keep the final concise:

```markdown
Built:
Verified:
Assumptions:
Files changed:
Remaining gaps:
```

Mention any scene URL/path or run command the user needs to try it locally.
