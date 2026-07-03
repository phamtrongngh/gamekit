---
name: game-environment-builder
description: Build or improve 3D game environments and scenes from reference images while matching composition, camera view, object placement, mood, and available assets. Use this skill whenever the user asks to recreate a game scene/environment from images, make a Godot scene look like references, achieve high visual similarity. This skill is especially important for scene construction with provided 3D assets, world materials (terrain, interiors, water when present), camera POV, and iterative visual QA.
---

# Game Environment Builder

Use this skill when the goal is not merely to place assets, but to make a playable/editor scene visually match reference images. Treat the reference as a target composition with foreground, midground, background, lighting, atmosphere, and camera constraints.

The main failure mode to avoid is "asset dumping": placing the right models without matching scale, camera, density, silhouette, color, and spatial relationships. The successful workflow is iterative: inspect assets, build a camera-anchored layout, screenshot it, compare against the reference, and make targeted fixes until the major visual anchors line up.

## Operating Principle

Work from the camera outward.

For a reference-matched scene, the player's or screenshot camera is the truth. Aerial organization matters, but only after the target view reads correctly. Always identify what the user will see in the first frame: object sizes in screen space, horizon or ceiling line height, near-camera props, left/right framing (banks, walls, streets, cliffs), focal object distance, and atmospheric depth.

## Workflow

### 1. Extract A Visual Brief From The References

Before editing, write a compact visual brief for yourself:

- Target camera: first-person, third-person, top-down, side view, cinematic, editor view, or multiple required views.
- Foreground anchors: objects touching the bottom/edges of the frame, cockpit/vehicle parts, hands/tools, nearby props, vegetation, railings, door frames, shoreline or street curb when visible.
- Midground anchors: hero structure/vehicle/enemy/NPC, crossing object, intersection, archway, platform, crowd, signs, focal furniture.
- Background anchors: skyline, tree line, mountains, interior depth, fog, far buildings, clouds, vanishing corridor or road direction.
- Scene density: approximate counts and clusters, not just asset categories.
- Palette and material read: dominant surface tones (floor, walls, ground, water if any), sky or ambient fill, fog color, contrast, saturation.
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

For GLB/GLTF assets, measure bounding boxes rather than guessing. Use the project's engine (Godot): a headless script, editor preview scene, or import preview can report AABBs and child mesh names. In Godot, a small inspection script or preview scene is a common approach. Convert normalized asset dimensions into plausible world scales.

Use universal anchors first, then genre-specific sizes only when the reference and assets call for them:

- Human-scale: standing character ~1.6-1.9 m; eye height ~1.5-1.7 m for first-person.
- Architecture: door ~2-2.2 m tall; single-story wall ~2.5-3.5 m; typical room depth often 3-8 m depending on type.
- Vehicles: compact car ~4 m long; truck/bus proportionally larger; player vehicle sized to reference screen footprint.

When the reference shows waterways, villages, or tropical outdoor scenes, examples include: small boat/canoe ~4-8 m; ferry/large boat ~15-30 m; stilt house or shop ~6-12 m wide/deep; palm or tall street tree ~10-18 m. Do not apply these defaults to sci-fi interiors, dungeons, or arenas unless the reference matches.

Also inspect orientation. Do not assume the model's "front" points along the engine's conventional forward axis. Take preview screenshots from known azimuths when facing direction (vehicle bow, door, sign, weapon barrel) matters.

### 3. Plan The Layout In Camera Coordinates

Define a simple world model:

- Choose the main axis of travel or depth (corridor, road, river, runway) along a consistent world axis such as `Z`.
- Place the player or target camera first.
- Place the hero foreground object second, so it occupies the same screen area as the reference.
- Place the main midground object next at an approximate distance and lateral offset.
- Place framing edges: banks, terrain strips, walls, aisles, or path borders that match the reference silhouette.
- Place repeated background objects in rows or clusters that recede into fog or perspective.

Use a spatial plan with approximate coordinates before authoring dozens of nodes. Include scale, rotation, and why each key object sits there.

Example planning notes (pick the shape that matches the reference; do not default to outdoor water scenes):

```text
Outdoor / travel corridor:
Camera: [POV type], y=[eye height]m, looking along [axis], pitch [degrees].
Foreground: [player vehicle or hands/props] fill lower [~]% of frame.
Midground: [hero object] [distance]m ahead-[left/right], yaw [degrees].
Left frame: [nearest landmark] at screen-left; [cluster] behind.
Right frame: [farther cluster], lower contrast through fog if reference shows depth haze.
Ground/sky read: [corridor width, material identity — river, road, plaza, etc.].
```

```text
Interior / structured space:
Camera: third-person behind player, y=1.6m, looking down main aisle along +Z.
Foreground: player shoulders and weapon occupy lower-center ~20% of frame.
Midground: enemy or desk cluster 8-12m ahead, slightly right.
Left frame: wall modules, windows, or shelves to match reference vertical rhythm.
Right frame: doorway or lit alcove for contrast.
Materials: floor and wall tones match reference screenshot, not engine defaults.
```

### 4. Build Missing Recognition Details

Do not stop because a perfect asset is missing. A scene often becomes recognizable through cheap, genre-dependent high-signal details. Prefer primitives, labels, decals, and simple meshes that read at screenshot scale.

Generic (most scenes):

- Signs and text: engine text labels (e.g. Godot `Label3D`), textured quads, emissive panels.
- Crowds at distance: capsules/spheres with simple color blocks for clothing or uniforms.
- Railings, pipes, cables: thin cylinders/boxes between posts or along walls.
- Lights: emissive quads, point/spot placeholders, neon strips.
- Crates, tires, ropes, handles: boxes, torus, cylinders.
- Atmosphere: fog, procedural sky, particle haze when no sky texture exists.

Optional when the reference shows outdoor village or water travel:

- Regional costume silhouettes only if visible in the reference (hats, umbrellas, etc.).
- Boat engines, docks, paddles: boxes, cylinders, planks, posts.
- Overhead power lines between poles.

Kitbash these details where they appear in the camera, especially foreground and midground. Far objects need silhouette and color more than mesh fidelity.

### 5. Author Efficiently And Deterministically

For scenes with many repeated objects, prefer a deterministic generator script or structured scene authoring over dozens of manual editor calls. A generator is useful when it:

- Computes transforms for repeated instances (props, trees, modules, NPC placeholders, vehicles).
- Uses a fixed seed for natural variation.
- Keeps constants near the top for fast iteration.
- Groups objects into meaningful nodes named by scene semantics (e.g. `Terrain`, `Props`, `Lighting`, `HeroVehicle`, or for a river scene `River`, `Banks`, `Village`).
- Produces final authored nodes that remain inspectable in the editor.

Keep the generator temporary unless the project convention says otherwise. If you remove it at the end, make sure the final scene file contains the complete authored result.

When editing scene files on disk (e.g. Godot `.tscn`), verify the scene reloads in the editor and through the engine's headless or batch load path. Be alert for stale in-memory editor state: an editor can show or autosave an older scene after disk edits. If screenshots show old node paths or old content, force a reload or restart the editor before running more visual QA.

### 6. Treat Atmosphere And Materials As Core Scene Objects

Reference similarity often depends as much on color and atmosphere as geometry. Tune these deliberately:

- Dominant surfaces: floors, walls, ground, and water (if present) should match the reference hue, roughness, and reflectivity — avoid engine defaults that fight the screenshot.
- Fog density/color: use enough to create depth, not enough to wash out all assets.
- Sky or ambient fill: overcast, interior bounce, tropical haze, sunset, noon, night, studio rim light — match what the reference shows.
- Ambient and directional light: reduce washed-out scenes by lowering ambient energy or changing tonemap/exposure before adding more geometry.
- Framing terrain or architecture: edge materials (banks, curbs, baseboards, trim) should support the palette and not read as unrelated slabs.

Iterate material values from screenshots, not from numeric preference. If a surface reads wrong (e.g. sand instead of water, plastic instead of concrete), adjust albedo, roughness, and reflections, then retest from the target camera.

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

For a high-similarity request such as "1:1" or ">=80%", expect several visual loops. It is normal to fix camera height, object yaw, key surface materials, fog, foreground prop size, and hero-object position after seeing screenshots.

### 8. Validate And Clean Up

Before reporting completion:

- Run the project's normal load/lint/headless validation when available.
- Confirm there are no runtime errors in recent logs.
- Confirm the scene on disk matches what the editor/game is showing.
- Remove temporary preview scenes, inspection scripts, and generator scripts if they are not intended artifacts.
- Leave useful generated materials, shaders, scripts, and final scenes.
- Summarize what was changed in concrete counts and named nodes.

Use whatever headless load or play-mode smoke test the project already supports. For Godot projects, useful checks include:

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
- Scene density is comparable: not a single instance where the reference shows many (trees, crates, NPCs, modules, etc.).
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
- Skipping cheap high-signal kitbash (signs, lights, crowds, cables, handles) because no exact model exists.
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
