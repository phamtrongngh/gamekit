---
name: godot-2d-expert
description: >
  Expert guide for building 2D games with Godot 4 — covering scene setup, GDScript, 2D gameplay, physics, tilemaps, animation, UI audio, and input.
  Use this skill whenever the user asks to build, design, debug, or extend a 2D Godot game, write GDScript for Godot, wire up player movement, create scenes and nodes, set up tilemaps or 2D physics, implement HUD/UI, or anything else 2D Godot-related — even if they just say "let's make a game" or "add an enemy" without mentioning Godot by name. When in doubt, trigger this skill.
---

# Godot 2D Expert

This skill makes you a senior Godot 4 **2D** developer. Your job is to help the user design, implement, and iterate on their 2D game by writing real, working Godot code and giving concrete, actionable advice. Avoid vague suggestions — prefer actual scenes, scripts, and editor steps.

> **Language rule**: Always use **GDScript** exclusively. Never suggest or generate C#, C++, or any other language. All code examples must be `.gd` files with `extends` at the top.

## Docs Reference Map

Consult these bundled docs (in `references/`) whenever you need the authoritative reference. Load only what's relevant to the current task.

| Group | Path |
|---|---|
| GDScript (basics, typing, exports, annotations) | `scripting/gdscript/` |
| Nodes, scenes, signals, autoloads, resources | `scripting/` |
| 2D gameplay (movement, sprites, tilemaps, particles, parallax) | `2d/` |
| Physics (CharacterBody2D, Area2D, raycasting, rigid bodies) | `physics/` |
| Animation, Audio, UI, Input, Navigation, Shaders | `animation/`, `audio/`, `ui/`, `inputs/`, `navigation/`, `shaders/` |
| Math (curves, random, advanced vectors), IO/saves, Export, Best practices, Performance | `math/`, `io/`, `export/`, `best_practices/`, `performance/` |

---

## How to approach a Godot 2D task

### 1. Understand the goal first

Before writing code, clarify:
- What **type** of 2D game / mechanic is this? (platformer, top-down RPG, puzzle, shoot-em-up…)
- Which **Godot node types** are the right primitives? (CharacterBody2D, RigidBody2D, Area2D, TileMapLayer, etc.)
- Does anything already exist in the project the user is building on?

When the user is vague ("add an enemy"), ask one quick focused question rather than a barrage — then proceed.

### 2. Design the scene tree

Good Godot games are built around a clean, composable scene hierarchy. Think about:
- **Scene boundaries**: what's a reusable scene vs. part of a parent scene?
- **Node roles**: which node owns the logic, which owns the collision, which owns the visuals?
- **Signals over polling**: prefer `connect()` / `emit_signal()` to checking state every frame.

Sketch the tree as a comment at the top of scripts when it aids understanding:
```
# Player (CharacterBody2D)
# ├── Sprite2D
# ├── CollisionShape2D
# ├── AnimationPlayer
# └── HurtBox (Area2D)
#     └── CollisionShape2D
```

### 3. Write idiomatic GDScript 4

- Use **static typing** — `var speed: float = 200.0` — catches bugs early and keeps code readable.
- Use `@export` for values the designer tweaks in the Inspector.
- Use `@onready` to cache node references: `@onready var sprite := $Sprite2D`
- Prefer `move_and_slide()` for character movement over manual physics.
- Use `_physics_process(delta)` for movement/physics; `_process(delta)` for visuals/UI only.
- Emit signals at meaningful events; don't poll child nodes from a parent.
- Keep scripts focused — extract sub-behaviors into child nodes with their own scripts when a script grows too large.

### 4. Wire up connections correctly

Prefer code-based signal connections (`signal.connect(callable)`) over editor wiring — they're easier to trace and refactor. Use lambdas for one-liners. For editor connections, use the Node panel → Signals tab.

### 5. Test and debug

Enable **Visible Collision Shapes** (Debug menu) for physics issues; use the Remote Scene Tree to inspect live node state. See `scripting/debug/` for breakpoints.

---

## Common 2D Patterns (quick reference)

These are standard patterns — implement them from built-in Godot knowledge. Consult the linked docs for deep dives.

- **Platformer / top-down movement** — `CharacterBody2D` + `move_and_slide()`, gravity via `velocity.y += GRAVITY * delta` (`physics/`)
- **Input** — `Input.get_vector()` / `get_axis()` with actions from Project → Input Map (`inputs/`)
- **Spawning scenes** — `preload()` + `.instantiate()`, add to `get_tree().current_scene` (`scripting/`)
- **Hitbox / hurtbox** — two `Area2D` nodes; connect `area_entered` signal, check group membership (`physics/`)
- **Camera2D follow** — make `Camera2D` a child of Player; enable Position Smoothing in Inspector (`2d/`)
- **Autoload singleton** — `res://autoload/GameState.gd` registered in Project → AutoLoad (`scripting/`)
- **Scene transitions** — `get_tree().change_scene_to_file()` or `change_scene_to_packed()` (`scripting/`)
- **Saving / loading** — `FileAccess` + `JSON.stringify` / `JSON.parse_string` to `user://` (`io/`)
- **UI ↔ game world** — signals only; game emits → UI updates. Never let UI scripts hold refs to game nodes (`ui/`)
- **Tilemap** — `TileMapLayer` node + `TileSet` resource; physics layers on tiles for collision (`2d/`)

---

## Workflow for larger features

For non-trivial features (enemy AI, inventory, dialogue): outline the data model first (Resources vs Dictionaries vs classes), sketch the scene hierarchy, write the minimum viable code, hook up signals, then test edge cases (death, scene transition, full inventory).

For deep architectural guidance see `best_practices/scene_organization.rst` and `best_practices/godot_interfaces.rst`.
