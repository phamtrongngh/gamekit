---
name: godot-scene-composition-3d
description: >
  Build or modify 3D Godot gameplay scenes from a reference brief, mockup, screenshot, blockout, or level plan. Use this skill for Node3D scenes, 3D arenas, third-person/first-person gameplay spaces, low-poly scenes, 3D platforming areas, rooms, dioramas, and perspective concept images. It covers blockout geometry, camera rigs, lighting, spawn points, props, collision, navigation, and HUD integration.
---

# Godot Scene Composition 3D

Create a practical 3D scene from a reference. Start with a readable blockout unless production models already exist.

Use the project-configured Godot MCP server from `Coding-Solo/godot-mcp` for scene/node automation, project runs, debug output, stopping execution, and MeshLibrary export. Use local Godot CLI/headless commands only for operations outside the MCP tool surface. Use Godot primitives and simple materials before custom meshes when the goal is prototype or structure.

## Standard Scene Tree

```text
LevelName (Node3D)
├── World (Node3D)
│   ├── BlockoutGeometry (Node3D)
│   ├── Terrain (Node3D)
│   ├── Props (Node3D)
│   ├── Interactables (Node3D)
│   ├── Hazards (Node3D)
│   └── SpawnPoints (Node3D)
├── PlayerSpawn (Marker3D)
├── Player (instance)
├── Enemies (Node3D)
├── Navigation (Node3D)
├── CameraRig (Node3D)
├── Lighting (Node3D)
├── WorldEnvironment
└── HUDLayer (CanvasLayer)
```

## Blockout First

Use primitive meshes:

| Visual role | Prototype node/resource |
|---|---|
| floor/platform | `MeshInstance3D` with `BoxMesh` |
| wall/barrier | `BoxMesh` |
| column/tree/trunk | `CylinderMesh` |
| boulder/orb | `SphereMesh` |
| character placeholder | `CapsuleMesh` plus label or color |
| trigger area | `Area3D` with debug material |

Add collision shapes matching the simple geometry. Do not rely on visuals alone.

## Camera Decision

Pick one:

| Reference view | Camera approach |
|---|---|
| first-person screenshot | `Camera3D` under player head/camera pivot |
| third-person character view | camera rig follows player with spring arm or offset pivot |
| top-down 3D/isometric | orthographic `Camera3D` angled downward |
| fixed room/cutscene | fixed `Camera3D` markers |
| arena | camera looks at arena center or follows player with bounds |

Use `godot-camera-lighting-vfx` for camera behavior and polish.

## Scale Conventions

Default human-scale blockout:
- Player capsule height: about 1.8 units.
- Door height: about 2.2 units.
- Waist-high prop: about 0.8-1.1 units.
- One tile/grid unit: 1.0 or 2.0 units depending level density.

If the project already has scale conventions, follow them.

## Navigation And Collision

For playable 3D scenes:
- Add floor collision.
- Add blocking wall/prop collisions.
- Add `NavigationRegion3D` when AI needs pathfinding.
- Add `Area3D` triggers for doors, pickups, hazards, and encounter volumes.
- Use spawn markers for player/enemies instead of hardcoded positions.

## 3D Asset Strategy

If no models exist:
- Use colored primitives for blockout.
- Use generated textures sparingly.
- Use `imagegen` only when a generated bitmap texture or concept plate materially improves the scene.
- Do not create complex mesh assets by hand in scene files.
- Ask for source models only when the requested quality depends on them.

If models exist:
- Inspect import paths and reuse them.
- Keep transforms and collision separate from visual mesh when possible.

## Composition Checklist

```markdown
[ ] Scene has floor/world geometry
[ ] Camera sees the intended action
[ ] Lighting makes objects readable
[ ] Player/enemy/object spawn markers exist
[ ] Collision exists for floors, blockers, and hazards
[ ] Navigation exists if moving AI needs it
[ ] Placeholder meshes are named clearly
[ ] HUD/overlay is in CanvasLayer
[ ] Scene runs without missing resource errors
```
