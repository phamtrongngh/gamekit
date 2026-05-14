---
name: godot-object-interactions
description: >
  Implement interactive, collectible, hazardous, or scripted objects in Godot scenes. Use this skill when a reference image or game request includes coins, gems, keys, pickups, doors, switches, chests, portals, signs, NPC triggers, breakables, hazards, traps, buttons, pressure plates, checkpoints, spawn triggers, or scene transition objects. Supports 2D and 3D Godot patterns.
---

# Godot Object Interactions

Objects should advertise what happened through signals. Keep object scenes reusable and keep level-specific outcomes in the level or scene manager.

## Object Classification

Classify each object:

| Object type | Typical root | Behavior |
|---|---|---|
| collectible | `Area2D` / `Area3D` | collected by player, emits signal, hides/frees |
| hazard | `Area2D` / `Area3D` | damages or kills on overlap |
| door/portal | `Area2D` / `Area3D` or `Node` | changes scene or moves player |
| switch/lever/button | `Area2D` / `Area3D` | toggles state, emits changed signal |
| chest/container | `Area2D` / `Area3D` | opens, grants item, persists state |
| breakable | `StaticBody` + damage area | health, destroyed signal |
| checkpoint | `Area2D` / `Area3D` | records respawn point |
| prop | `StaticBody` or visual node | decoration, maybe collision |

## Standard Object Scene

2D:

```text
ObjectName (Area2D/StaticBody2D/Node2D)
├── Sprite2D
├── CollisionShape2D
├── PromptMarker (optional)
└── AnimationPlayer
```

3D:

```text
ObjectName (Area3D/StaticBody3D/Node3D)
├── Visuals
├── CollisionShape3D
├── PromptMarker (optional)
└── AnimationPlayer
```

## Signals

Prefer clear signals:

```gdscript
signal collected(by: Node)
signal activated(by: Node)
signal deactivated(by: Node)
signal opened(by: Node)
signal triggered(by: Node)
signal destroyed
```

The object emits; the level decides what to do if the result is level-specific.

## Interaction Prompts

For objects requiring an action:
- Add an interaction area.
- Show prompt only when player enters range.
- Use an `interact` input action.
- Let the player or interaction manager call `interact(player)`.

Do not make every overlap immediately activate unless that is the expected genre convention.

## Scene Transition Objects

For doors/portals:

```markdown
target_scene:
target_spawn_id:
requires_key:
transition_effect:
```

If the target scene does not exist, create a placeholder only when the user's task requires a working button/door path.

## Reference-Based Placement

From screenshots:
- Place collectibles and hazards where visible.
- Treat unknown decorative items as props until gameplay need is clear.
- Use visible affordances: glow means collectible/interactive; spikes/fire means hazard; door/portal means transition.
- Avoid inventing inventory systems unless the object requires persistence.

## Checklist

```markdown
[ ] Object type and root node match behavior
[ ] Collision/trigger area exists
[ ] Signals are exposed for important events
[ ] Level-specific outcomes are not buried inside generic objects
[ ] Prompt exists for explicit interactions
[ ] Transition target is real or intentionally placeholder
[ ] Object works with player groups or interaction interface
```
