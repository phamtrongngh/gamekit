---
name: godot-character-setup
description: >
  Create or adapt a controllable character for a Godot scene. Use this skill whenever a reference image, mockup, or gameplay request includes a player character, avatar, controllable unit, spawn point, movement controller, camera follow target, animation placeholder, hitbox/hurtbox, health, or input setup. Supports both 2D and 3D Godot scenes, with GDScript and standard Godot node patterns.
---

# Godot Character Setup

Build the player character as a reusable scene with clear movement, collision, visuals, and signals. Keep the level scene responsible for placement; keep character behavior inside the character scene.

## Character Brief

Before implementation, write:

```markdown
## Character Setup
Dimension: 2D / 3D
View/controller type:
Root node:
Scene path:
Input actions needed:
Movement behavior:
Combat/interaction needs:
Health/damage needs:
Animation state needs:
Camera relationship:
```

## 2D Root Decisions

| Need | Root |
|---|---|
| Platformer or top-down movement | `CharacterBody2D` |
| Static selectable unit | `Area2D` or `Node2D` |
| Physics-driven character | `RigidBody2D` only when physics simulation is core |

Standard 2D tree:

```text
Player (CharacterBody2D)
├── Sprite2D / AnimatedSprite2D
├── CollisionShape2D
├── HurtBox (Area2D)
│   └── CollisionShape2D
├── InteractionArea (Area2D)
│   └── CollisionShape2D
├── AnimationPlayer
└── Camera2D (optional)
```

## 3D Root Decisions

| Need | Root |
|---|---|
| First/third-person controller | `CharacterBody3D` |
| Clickable static character | `Area3D` or `Node3D` |
| Physics-driven actor | `RigidBody3D` only when needed |

Standard 3D tree:

```text
Player (CharacterBody3D)
├── Visuals (Node3D)
│   └── MeshInstance3D / model instance
├── CollisionShape3D
├── HurtBox (Area3D)
├── InteractionArea (Area3D)
├── AnimationPlayer
└── CameraPivot / Camera3D (optional)
```

## Input Rules

Check existing input actions before adding new ones. Common actions:
- `move_left`, `move_right`, `move_up`, `move_down`
- `jump`
- `attack`
- `interact`
- `dash`
- `pause`

If actions are missing, add them consistently with project conventions or document that they must be added in Project Settings.

## Movement Defaults

| Scene type | Default movement |
|---|---|
| 2D platformer | horizontal movement, gravity, jump |
| 2D top-down | 8-direction movement with `Input.get_vector()` |
| 2D arena | top-down movement, optional dash/attack |
| 3D third-person | camera-relative movement |
| 3D first-person | mouse look + WASD movement |

Use exported speed/jump/gravity values so tuning does not require code changes.

## Signals

Expose meaningful signals:

```gdscript
signal health_changed(current: int, maximum: int)
signal died
signal interacted(target: Node)
signal attacked
```

Let HUD and level scripts connect to signals. Do not make UI scripts reach deeply into the player scene.

## Reference-Based Placement

When the player comes from a screenshot:
- Put `PlayerSpawn` at the visible player position.
- If the screenshot shows a character but not enough animation frames, create a static placeholder or single-sprite prototype.
- If using a cropped player image, run `game-asset-analyzer` to capture visual center, feet/contact point, and collision shape.
- Align collision to body/feet, not outer glow/shadow.

## Checklist

```markdown
[ ] Player is a reusable scene
[ ] Collision shape matches gameplay body
[ ] Movement script uses exported values
[ ] Input actions are known or documented
[ ] Health/damage signals exist if combat exists
[ ] Interaction area exists if interactables exist
[ ] Camera relationship is clear
[ ] Placeholder/temporary art is named clearly
```
