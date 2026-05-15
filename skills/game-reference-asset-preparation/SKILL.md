---
name: game-reference-asset-preparation
description: >
  Prepare assets from a game screenshot, mockup, concept image, or existing repository assets for Godot scene building. Use this skill whenever a visual reference must become reusable backgrounds, sprites, icons, UI textures, placeholder shapes, generated asset requests, or asset metadata for a Godot scene. It generalizes screenshot asset extraction beyond UI into characters, enemies, props, terrain, objects, and HUD elements.
---

# Game Reference Asset Preparation

Decide how each visible reference element should become a Godot asset or placeholder. Use this after `game-reference-analysis` and before scene composition.

## Asset Strategy Table

Create this table:

```markdown
| element | role | strategy | output path | notes |
|---|---|---|---|---|
```

Strategies:

| Strategy | Use when |
|---|---|
| reuse_existing | Matching asset already exists in the project |
| crop_reference | Element can be cleanly cropped from a screenshot |
| extract_background | Whole image or layer can serve as temporary background |
| code_native | Shape, color panel, label, line, light, or primitive can be made in Godot |
| placeholder | Gameplay needs the role, but exact art is not required yet |
| generate_raster | A new bitmap asset is needed and no source exists |
| request_source | Pixel-perfect result needs original layered art or model |

## Image Generation Backend

When the strategy is `generate_raster`, use the `imagegen` skill to generate or edit bitmap assets. Good use cases:
- sprite placeholders that should look closer to the reference than simple shapes
- background plates
- terrain or prop textures
- icons and UI mockups
- transparent-background cutouts
- concept variants for characters, enemies, props, and VFX

Do not use `imagegen` when the asset is better handled as:
- a simple Godot-native primitive or UI control
- an SVG/vector asset
- a deterministic icon matching an existing vector/icon system
- an original source asset needed for pixel-perfect recreation

Generated assets are useful for prototypes and missing art, but they are not a substitute for original layered files, animation sheets, models, or source art when exact reproduction matters.

## Repository Search First

Before creating assets, search the project:

```bash
find . -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.webp" -o -name "*.svg"
find . -path "*/assets/*" -o -path "*/sprites/*" -o -path "*/art/*" -o -path "*/textures/*" -o -path "*/ui/*"
find . -name "*.tscn" -o -name "*.gd"
```

Reuse local assets when they reasonably match the reference. Do not create parallel duplicate assets unless the new scene needs a distinct variant.

## Output Organization

Use project conventions if they exist. Otherwise:

```text
res://assets/
├── backgrounds/
├── characters/
├── enemies/
├── props/
├── terrain/
├── objects/
├── ui/
└── vfx/
```

For scene-specific temporary assets:

```text
res://assets/reference_builds/[scene_name]/
```

## Cropping Guidelines

Crop when:
- The object has clear boundaries.
- Perspective and lighting match the target scene.
- The crop will not reveal missing background at runtime.
- The output can be used at intended resolution without visible artifacts.

Do not crop:
- Stylized text that should scale cleanly.
- Characters/enemies that require animation frames, unless it is a static prototype.
- Objects heavily occluded by other elements.
- Low-quality screenshot details that will become blurry.

When cropping from a screenshot, keep transparent padding minimal and document the intended origin.

## Asset Metadata

When an asset will be positioned, collided, animated, or used as a child attachment point, use `game-asset-analyzer` to create a `.meta.yaml` sidecar.

Metadata is especially important for:
- Player sprites.
- Enemies.
- Projectiles.
- Weapons.
- Collectibles.
- Doors/chests/switches.
- Platforms and terrain pieces.
- UI slots and buttons.

## Placeholder Rules

Use placeholders when implementation value matters more than exact art:

| Role | Placeholder |
|---|---|
| Player | colored capsule/rectangle with label |
| Enemy | contrasting capsule/shape with simple animation |
| Collectible | circle or icon-like sprite |
| Interactable | panel/box with prompt marker |
| Terrain | ColorRect, Polygon2D, TileMapLayer blockout, or primitive mesh |
| 3D prop | BoxMesh, SphereMesh, CapsuleMesh, CylinderMesh |

Name placeholders clearly, e.g. `PlayerPlaceholder`, `EnemyPlaceholder`, `DoorPlaceholder`.

## Generated Asset Brief

When using generated raster assets, write a compact brief:

```markdown
Asset:
Role in scene:
Style:
View angle:
Transparent background:
Approximate size:
Must match:
Avoid:
```

Generate only the assets needed to make the scene useful. Avoid generating an entire asset set when a blockout is enough.

After generation:
- Save the selected final asset inside the Godot project before referencing it.
- Use lowercase snake_case filenames.
- For transparent sprites/cutouts, prefer PNG.
- Run `game-asset-analyzer` when the generated asset needs collision, origin, attachment, or placement metadata.

## Import And Godot Notes

- Place files under the Godot project directory, not outside it.
- Keep filenames lowercase snake_case.
- Prefer PNG for sprites/UI with transparency.
- Use WebP/JPG only for opaque backgrounds when size matters.
- After adding many assets, open or run Godot once so imports are generated.
