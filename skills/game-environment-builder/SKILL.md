---
name: game-environment-builder
description: Build or improve 3D game environments and scenes from reference images while matching composition, camera view, object placement, mood, and available assets. Use this skill whenever the user asks to recreate a game scene/environment from images, make a Godot/Unity/Unreal scene look like references, achieve high visual similarity. This skill is especially important for scene construction with provided 3D assets, water/terrain/materials, camera POV, and iterative visual QA.
---

# Game Environment Builder

Use this skill when the goal is not merely to place assets, but to make a playable/editor scene visually match reference images. Treat the reference as a target composition with foreground, midground, background, lighting, atmosphere, and camera constraints.

The main failure mode to avoid is "asset dumping": placing the right models without matching scale, camera, density, silhouette, color, and spatial relationships. The successful workflow is iterative: inspect assets, build a camera-anchored layout, screenshot it, compare against the reference, and make targeted fixes until the major visual anchors line up.

## Operating Principle

Work from the camera outward.

For a reference-matched scene, the player's or screenshot camera is the truth. Aerial organization matters, but only after the target view reads correctly. Always identify what the user will see in the first frame: object sizes in screen space, horizon height, near-camera props, left/right bank placement, focal object distance, and atmospheric depth.

## Workflow

### 1. Extract A Visual Brief From The References

Before editing, write a compact visual brief for yourself:

- Target camera: first-person, third-person, top-down, side view, cinematic, editor view, or multiple required views.
- Foreground anchors: objects touching the bottom/edges of the frame, cockpit/vehicle parts, hands/tools, nearby vegetation, shoreline, walls.
- Midground anchors: hero structure/vehicle/enemy, crossing object, bridge, road bend, dock, crowd, signs.
- Background anchors: skyline, tree line, mountains, fog, far buildings, clouds, river/road vanishing direction.
- Scene density: approximate counts and clusters, not just asset categories.
- Palette and material read: water color, mud/stone/grass tone, sky brightness, fog color, contrast, saturation.
- Missing details: details in the reference that are not in the asset pack and must be approximated with primitives, labels, decals, particles, or simple kitbash geometry.

If there are multiple references, assign each a purpose:

- Primary composition reference: the camera view to match first.
- Layout reference: aerial/top-down arrangement.
- Detail references: materials, props, signs, engine parts, vegetation, people, trim.

### 2. Inventory The Existing Project And Assets

Inspect before building:

- Current scene root, camera, world environment, terrain, water, lights, scripts.
- Available model files, textures, import metadata, materials, shaders.
- Existing gameplay controller and project main scene.
- Asset dimensions and orientation.

For GLB/GLTF assets, measure bounding boxes rather than guessing. If using Godot, a headless script or editor preview scene can report AABBs and child mesh names. Convert normalized asset dimensions into plausible world scales:

- Small boat/canoe: usually 4-8 meters long.
- Ferry/large boat: often 15-30 meters long.
- Stilt house/shop: usually 6-12 meters wide/deep.
- Palm/coconut tree: often 10-18 meters tall.

Also inspect orientation. Do not assume the model's "front" points along the engine's conventional forward axis. Take preview screenshots from known azimuths when the bow/front/sign direction matters.

### 3. Plan The Layout In Camera Coordinates

Define a simple world model:

- Choose the main axis of travel or depth, such as river/road along `Z`.
- Place the player or target camera first.
- Place the hero foreground object second, so it occupies the same screen area as the reference.
- Place the main midground object next at an approximate distance and lateral offset.
- Place banks, terrain strips, walls, or path edges to frame the scene.
- Place repeated background objects in rows or clusters that recede into fog or perspective.

Use a spatial plan with approximate coordinates before authoring dozens of nodes. Include scale, rotation, and why each key object sits there.

Example planning notes:

```text
Camera: stern POV, y=1.7m, looking down river along -Z, slight downward pitch.
Foreground: player boat hull and engine fill lower 25% of frame.
Midground: ferry 25-35m ahead-left, angled across river.
Left bank: nearest shop/stilt house visible at screen-left, trees behind.
Right bank: houses and palms farther back, lower contrast through fog.
Water: wide muddy river, but banks visible enough to define corridor.
```

### 4. Build Missing Recognition Details

Do not stop because a perfect asset is missing. A scene often becomes recognizable through cheap high-signal details:

- People at distance: capsules/spheres plus cone hats or simple colored bodies.
- Boat engines: boxes, cylinders, flywheels, exhaust pipes, rods, handles.
- Power lines: thin cylinders/boxes between poles.
- Docks: planks, posts, ramps.
- Shop signs: `Label3D`, textured quads, or simple panels.
- Tires, ropes, railings, paddles: torus/cylinders/boxes.
- Haze/clouds: environment fog and procedural sky if no sky texture exists.

Kitbash these details where they appear in the camera, especially foreground and midground. Far objects need silhouette and color more than mesh fidelity.

### 5. Author Efficiently And Deterministically

For scenes with many repeated objects, prefer a deterministic generator script or structured scene authoring over dozens of manual editor calls. A generator is useful when it:

- Computes transforms for repeated houses, trees, wires, passengers, boats, or props.
- Uses a fixed seed for natural variation.
- Keeps constants near the top for fast iteration.
- Groups objects into meaningful nodes such as `River`, `Banks`, `Village`, `Boats`, `PowerLines`, `PlayerBoat`.
- Produces final authored nodes that remain inspectable in the editor.

Keep the generator temporary unless the project convention says otherwise. If you remove it at the end, make sure the final scene file contains the complete authored result.

When editing Godot `.tscn` directly, verify the scene reloads in the editor and through headless Godot. Be alert for stale in-memory editor state: an editor can show or autosave an older scene after disk edits. If screenshots show old node paths or old content, force a reload or restart the editor before running more visual QA.

### 6. Treat Atmosphere And Materials As Core Scene Objects

Reference similarity often depends as much on color and atmosphere as geometry. Tune these deliberately:

- Water hue and roughness: avoid default blue or over-bright yellow if the reference shows muddy, reflective, or dark water.
- Fog density/color: use enough to create depth, not enough to wash out all assets.
- Sky/clouds: overcast, tropical haze, sunset, noon, night, etc.
- Ambient and directional light: reduce washed-out scenes by lowering ambient energy or changing tonemap before adding more geometry.
- Terrain/bank color: shore materials should support the scene palette and not read as unrelated slabs.

Iterate material values from screenshots, not from numeric preference. If a surface reads as sand when it should read as water, darken and desaturate the material, adjust reflections/roughness, and retest from the target camera.

### 7. Screenshot, Compare, Fix

Do not rely on reasoning alone. After the first pass:

1. Run or render from the target camera.
2. Capture a screenshot.
3. Compare against the primary reference by screen-space composition:
   - Is the camera too high, low, wide, or narrow?
   - Is the foreground object the right size?
   - Is the hero midground object at the right side and distance?
   - Are the banks/roads/walls framing the image at the right angles?
   - Are key object counts and density close enough?
   - Is color/lighting/fog close to the reference?
4. Make a targeted fix list. Avoid vague "improve scene" edits.
5. Regenerate/reload/rerun and screenshot again.

Use at least:

- One target camera/game screenshot.
- One editor/aerial or oblique screenshot to inspect layout, overlaps, and density.
- Another target screenshot after major material/camera/layout changes.

For a high-similarity request such as "1:1" or ">=80%", expect several visual loops. It is normal to fix camera height, object yaw, water color, fog, foreground prop size, and hero-object position after seeing screenshots.

### 8. Validate And Clean Up

Before reporting completion:

- Run the project's normal load/lint/headless validation when available.
- Confirm there are no runtime errors in recent logs.
- Confirm the scene on disk matches what the editor/game is showing.
- Remove temporary preview scenes, inspection scripts, and generator scripts if they are not intended artifacts.
- Leave useful generated materials, shaders, scripts, and final scenes.
- Summarize what was changed in concrete counts and named nodes.

For Godot, useful checks include:

```bash
godot --headless --path <project> --quit
godot --headless --path <project> res://scenes/Main.tscn --quit
```

## Similarity Checklist

Use this checklist before finalizing:

- Target camera matches the reference perspective and field of view.
- Foreground elements occupy similar screen area.
- Hero object position, scale, and yaw match the reference.
- Major left/right/background objects are in the same relative locations.
- Scene density is comparable: not just one house/tree/boat where the reference has many.
- Repeated objects have variation but preserve the overall pattern.
- Missing asset details are approximated with primitives or labels when visually important.
- Material palette matches the reference at screenshot level.
- Fog/lighting support depth without washing out the scene.
- Runtime and editor screenshots show the intended version, not stale editor state.

## Common Mistakes

- Starting with asset placement before deciding the camera.
- Using normalized GLB assets at raw scale.
- Assuming model orientation without checking.
- Treating material and fog as polish instead of identity.
- Adding many objects but missing the reference's foreground or focal object.
- Skipping cheap details such as passengers, wires, signs, docks, or handles because no exact model exists.
- Trusting the editor after direct file edits without forcing reload.
- Running once and stopping without screenshot-driven iteration.

## Response Style

Keep the user informed with short progress updates:

- What you inspected.
- What scale/orientation you learned.
- What visual mismatch the screenshot revealed.
- What you are changing next.

Final responses should include:

- The main scene/files changed.
- Concrete object counts or named groups when useful.
- How many visual checks were run.
- Any remaining fidelity limits caused by missing assets.
