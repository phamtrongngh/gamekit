---
name: godot-level-collision-navigation
description: >
  Add or verify collision, physics boundaries, walkable areas, navigation, spawn safety, and pathing in Godot levels. Use this skill for any playable 2D or 3D scene built from a screenshot/mockup/reference where the player, enemies, objects, hazards, platforms, terrain, walls, floors, or AI movement must work. It covers CollisionShape2D/3D, StaticBody, Area triggers, TileMap collision, NavigationRegion2D/3D, and gameplay bounds.
---

# Godot Level Collision Navigation

Make the scene playable, not just visible. Collision and navigation should be derived from gameplay roles, not from every decorative pixel.

## Collision Map

Create:

```markdown
## Collision And Navigation Plan

Player body:
World blockers:
Walkable areas:
Platforms:
Hazards:
Triggers:
Enemy navigation:
Camera/scene bounds:
Spawn safety:
```

## 2D Collision Patterns

| Need | Node/resource |
|---|---|
| static ground/wall/platform | `StaticBody2D` + `CollisionShape2D` |
| tile-based terrain | `TileMapLayer` with TileSet physics |
| one-way platform | platform collision layer/mask and one-way settings |
| pickup/hazard/trigger | `Area2D` + `CollisionShape2D` |
| player/enemy body | `CharacterBody2D` + `CollisionShape2D` |
| room/camera bounds | `ReferenceRect`, `Marker2D`, or exported Rect2 |
| AI pathfinding | `NavigationRegion2D` |

## 3D Collision Patterns

| Need | Node/resource |
|---|---|
| floor/wall/blocker | `StaticBody3D` + `CollisionShape3D` |
| pickup/hazard/trigger | `Area3D` + `CollisionShape3D` |
| player/enemy body | `CharacterBody3D` + `CollisionShape3D` |
| AI pathfinding | `NavigationRegion3D` |
| simple blockout mesh collision | box/capsule/sphere shapes matching primitive meshes |

## Collision Layer Policy

If the project already has layer names, use them. Otherwise document a simple scheme:

```text
1 World
2 Player
3 Enemies
4 PlayerHitBox
5 EnemyHitBox
6 Pickups
7 Interactables
8 Hazards
```

Keep masks narrow. For example, collectibles detect the player, not every body.

## From Reference To Collision

Translate visible forms into gameplay shapes:
- Ground/platforms: use simple rectangles/polygons along the walkable surface.
- Walls/rocks/trees/props: block only the solid body, not shadows/leaves unless needed.
- Hazards: make trigger areas slightly smaller than the visual danger effect.
- Doors/switches/chests: use interaction areas larger than exact sprite bounds.
- Enemy detection: use radius/area based on gameplay, not screenshot size alone.

Do not trace every visual contour if a simple shape would feel better in play.

## Navigation Rules

Add navigation when:
- Enemies chase or patrol around obstacles.
- NPCs walk to targets.
- Top-down/3D scenes have blockers and moving AI.

Skip navigation when:
- Enemies are stationary.
- Patrol is a simple line between markers.
- The scene is a static menu/cutscene.

## Spawn Safety

Verify:
- Player does not spawn inside collision.
- Player starts on walkable ground or valid floor.
- Enemies do not spawn inside walls/props.
- Collectibles are reachable unless intentionally gated.
- Hazards are not unavoidable at spawn.

## Checklist

```markdown
[ ] Collision exists for all gameplay blockers
[ ] Trigger areas exist for pickups/hazards/interactables
[ ] Collision layers/masks are documented or follow project naming
[ ] Spawn points are safe
[ ] Navigation exists if AI needs pathfinding
[ ] Camera/level bounds prevent obvious out-of-world issues
[ ] Debug collision can be visually inspected
```
