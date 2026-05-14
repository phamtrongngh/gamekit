---
name: godot-enemy-setup
description: >
  Create or adapt enemies for Godot scenes from screenshots, mockups, reference briefs, or gameplay requests. Use this skill whenever a scene includes hostile actors, monsters, patrol units, turrets, bosses, waves, enemy spawn points, chase behavior, attacks, hitboxes, hurtboxes, health, drops, or basic AI. Supports 2D and 3D enemy scene patterns.
---

# Godot Enemy Setup

Enemies should be reusable scenes with small, readable behavior. Start with the simplest AI that makes the reference playable.

## Enemy Brief

Create:

```markdown
## Enemy Setup
Enemy types:
Dimension: 2D / 3D
Root node:
Scene path:
Movement:
Detection:
Attack:
Health:
Drops/rewards:
Spawn placement:
```

## Root Node Choices

| Enemy behavior | 2D root | 3D root |
|---|---|---|
| Walking/chasing actor | `CharacterBody2D` | `CharacterBody3D` |
| Stationary hazard/turret | `Area2D` or `Node2D` | `Area3D` or `Node3D` |
| Projectile | `Area2D` | `Area3D` |
| Physics object enemy | `RigidBody2D` when required | `RigidBody3D` when required |

## Standard 2D Enemy Tree

```text
EnemyName (CharacterBody2D)
├── Sprite2D / AnimatedSprite2D
├── CollisionShape2D
├── HurtBox (Area2D)
│   └── CollisionShape2D
├── HitBox (Area2D)
│   └── CollisionShape2D
├── DetectionArea (Area2D)
│   └── CollisionShape2D
└── AnimationPlayer
```

## Standard 3D Enemy Tree

```text
EnemyName (CharacterBody3D)
├── Visuals
├── CollisionShape3D
├── HurtBox (Area3D)
├── HitBox (Area3D)
├── DetectionArea (Area3D)
└── AnimationPlayer
```

## AI Defaults By Scene Type

| Scene type | Default enemy behavior |
|---|---|
| Platformer | patrol between markers, turn at edges/walls |
| Top-down RPG | idle until player enters detection radius, then chase |
| Arena action | move toward player, attack on cooldown |
| Shooter | maintain distance, fire projectiles |
| Tower defense | follow path markers |
| Boss/cutscene | staged phases only if user asks |

Avoid overbuilding AI. Implement the behavior needed for the current scene.

## Spawn And Placement

In level scenes:

```text
Enemies
├── EnemySpawn_A (Marker2D/Marker3D)
├── EnemySpawn_B
└── Enemy instances
```

Use spawn markers when enemies may respawn, wave-spawn, or be moved during iteration. Directly instance enemies only for fixed scene dressing.

## Combat Signals

Use signals to keep enemies decoupled:

```gdscript
signal died(enemy: Node)
signal damaged(amount: int)
signal attack_started
signal attack_finished
```

Hitboxes should emit or call damage on hurtboxes through groups or a small damage interface. Avoid hardcoded deep node paths to the player.

## Reference-Based Rules

When enemies come from a screenshot:
- Count visible enemies and classify types.
- Place enemies at visible positions first.
- Infer patrol/chase only from genre and layout.
- If the image shows a boss or unique enemy, make it a separate scene.
- If art is unavailable, use placeholders with distinct color/shape per enemy type.

## Checklist

```markdown
[ ] Each enemy type is a reusable scene
[ ] Collision, hurtbox, and hitbox are separate when combat exists
[ ] Detection radius/path markers exist when AI needs them
[ ] Enemy uses exported tuning values
[ ] Enemy death/damage signals exist
[ ] Level owns spawn placement
[ ] Placeholder art is clearly named
```
