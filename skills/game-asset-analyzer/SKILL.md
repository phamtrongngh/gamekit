---
name: game-asset-analyzer
description: >
  Analyzes game asset images (PNG/JPG) with vision to auto-generate structured YAML metadata sidecar files (.meta.yaml) containing pixel dimensions, key feature offsets, collision radii, anchor points, and Godot-ready placement hints — so no manual measurement is needed. Trigger this skill whenever the user wants to: "generate metadata for [asset]", "analyze this asset", "what are the coordinates of X in this image", "I need the pixel offset for [feature]", "document this asset", or wants to precisely position one element insid another (e.g., placing a gem inside a cannon barrel). Also trigger when the user references any PNG/JPG asset and asks how to place scale, or use it inside a Godot scene. When in doubt, trigger this skill.
---

# Game Asset Analyzer

Generate `.meta.yaml` sidecar files for game assets through vision analysis. These files
give any AI agent or developer precise, measurement-backed data to implement Godot node
placement without guessing or manual pixel-counting.

The `.meta.yaml` is a **single source of truth** — it lives next to the asset and should
be read by any agent before setting positions, scales, or collision shapes in Godot.

---

## Workflow

### Step 1 — Get image dimensions

Run for each asset (macOS built-in, zero dependencies):

```bash
sips -g pixelWidth -g pixelHeight "/path/to/asset.png"
```

Note `pixelWidth` as **W** and `pixelHeight` as **H**.

### Step 2 — Examine the image visually

Use `view_file` on the image path. Approach it the way a game artist would when handing
an asset to a programmer: ask yourself what a Godot developer *needs to know* to place
and use this asset correctly in a scene.

Look for:
- **What role does this asset play** in a game? (something that shoots, gets collected,
  decorates the UI, forms the terrain, represents a character…)
- **Are there any "active" regions** — openings, slots, attachment points, contact edges,
  clickable zones, or places where another asset will be layered on top?
- **Where is the visual center** — does it match the geometric center, or is it shifted
  by shadows, glows, or asymmetric decoration?
- **What shape best describes the collidable area** — circle, rectangle, or polygon?

### Step 3 — Choose a type label

Infer the type from the asset's visual role, not its filename. Use a short, lowercase
label that a developer reading the YAML will immediately understand — e.g. `projectile`,
`launcher`, `ui_button`, `pickup`, `terrain_tile`, `character`, `background`,
`ui_frame`, `indicator`, `vfx_particle`, `ui_slot`, `icon`.

Don't be constrained by a fixed list. If none of the common labels fits, invent a clear
one (e.g. `gate`, `rope_segment`, `score_popup`). The goal is clarity, not conformity.

### Step 4 — Calculate feature offsets

Godot `Sprite2D` defaults to **center-origin**: position `(0, 0)` = the center of the
image. All offsets in the YAML are measured **from the image center**:

```
offset_x = round((visual_x_fraction - 0.5) * W)   # negative=left, positive=right
offset_y = round((visual_y_fraction - 0.5) * H)   # negative=up,   positive=down
```

Estimate `visual_x_fraction` / `visual_y_fraction` by careful visual inspection.
Round to the nearest integer pixel. Mark estimates with a `# ~` comment.

**Example:** A feature visually centered at 50% horizontal and 58% from the top of a
400×400 image:
- `offset_x = (0.50 − 0.5) × 400 = 0`
- `offset_y = (0.58 − 0.5) × 400 = 32`

### Step 5 — Extract meaningful features

There is no fixed feature list — let the visual content drive what you document.
The guiding question is: *what does an agent need in order to use this asset correctly?*

Common feature categories (apply whichever are relevant):

| Category | What to measure |
|---|---|
| **Opening / slot** | Center offset + inner diameter or bounds — any hole or recess where another asset will be placed |
| **Anchor / contact** | Offset of the edge or point where this asset connects to the world (feet, base, hinge) |
| **Collision shape** | Radius for circles; `{w, h}` for rectangles; note if the shape is irregular |
| **Active zone** | Clickable/tappable area, attack hitbox, detection range |
| **Visual center** | Offset if the perceived center differs from the geometric center due to asymmetry, glow, or shadow |
| **Child placement** | Where a child node (label, icon, badge, overlay) should be positioned |
| **Seam / tiling** | Whether left/right/top/bottom edges are seamless for tiling |
| **Surface edge** | Top walkable edge y-offset for platforms; ledge corners for jump detection |
| **Dominant color** | One-word label — useful for runtime color-keyed logic |

Document only what is genuinely present and useful. An `icon` asset may only need
`collision_radius`. A `launcher` may need an `opening` offset and a `base_anchor`.
A `ui_frame` may only need `inner_bounds`. Omit anything that would be a guess.

### Step 6 — Write the `.meta.yaml` file

Save as `<asset_stem>.meta.yaml` in **the same directory** as the asset.

Use compact inline YAML (`{key: val}`) for small coordinate objects to minimize tokens.
Omit any section that doesn't apply. Keep `desc` strings under 60 characters.

**Template:**

```yaml
asset: <filename.png>
dimensions: {w: <W>, h: <H>}
type: <type_label>
anchor: center
analyzed: <YYYY-MM-DD>
features:
  <feature_name>:
    offset: {x: <int>, y: <int>}  # from sprite center; omit key if both are zero
    <other_keys>: <values>        # e.g. diameter, radius, color, bounds...
    desc: "<brief human note, ≤60 chars>"
godot_hints:
  # Practical copy-paste values for Godot Inspector / GDScript
  # e.g. child_node_position: {x: 0, y: 24}
notes: "<caveats: shadows, alpha padding, import scale, estimation uncertainty, etc.>"
```

---

## Examples

These show the format for different asset roles. The specific feature names are invented
from the asset's visual content — not taken from a fixed list.

### A launcher-type asset (400×390)

```yaml
asset: tank_turret.png
dimensions: {w: 400, h: 390}
type: launcher
anchor: center
analyzed: 2026-05-08
features:
  barrel_tip:
    offset: {x: 142, y: -8}   # ~
    desc: "End of barrel — projectile spawn point"
  pivot_base:
    offset: {x: -10, y: 60}   # ~
    desc: "Rotation pivot, sits on tank body"
godot_hints:
  muzzle_position: {x: 142, y: -8}
  rotation_pivot_offset: {x: -10, y: 60}
notes: "Barrel glow adds ~6px visual overshoot; use inner-edge measurement"
```

### A collectible/projectile-type asset (96×96)

```yaml
asset: fire_orb.png
dimensions: {w: 96, h: 96}
type: projectile
anchor: center
analyzed: 2026-05-08
features:
  collision_radius: {px: 38, desc: "Inner flame body, excluding glow"}  # ~
  visual_center: {offset: {x: 0, y: -4}, desc: "Flame skews slightly upward"}
  dominant_color: orange
godot_hints:
  collision_shape: "CircleShape2D radius: 38"
notes: "Outer glow extends ~10px beyond collision edge; don't use full image half-width"
```

### A UI frame / slot asset (160×180)

```yaml
asset: inventory_slot.png
dimensions: {w: 160, h: 180}
type: ui_slot
anchor: center
analyzed: 2026-05-08
features:
  inner_bounds: {w: 128, h: 148, desc: "Usable area inside decorative border"}
  inner_center: {offset: {x: 0, y: 4}, desc: "Inner area is slightly below center"}
godot_hints:
  child_item_position: {x: 0, y: 4}
  child_item_max_size: {w: 128, h: 148}
```

### A terrain tile (64×64)

```yaml
asset: grass_tile.png
dimensions: {w: 64, h: 64}
type: terrain_tile
anchor: center
analyzed: 2026-05-08
features:
  surface_top_y: -28          # y-offset of walkable top edge from center
  tileable: {x: true, y: false}
godot_hints:
  collision_rect_offset_y: -28
  tile_size: {w: 64, h: 64}
```

---

## Batch processing

When the user supplies multiple assets, process them **sequentially** (one `view_file`
+ one `sips` call per asset). Write all `.meta.yaml` files, then report a summary table:

```
| Asset              | Type        | Key feature           | Value         |
|--------------------|-------------|-----------------------|---------------|
| tank_turret.png    | launcher    | barrel_tip offset     | x:142 y:-8   |
| fire_orb.png       | projectile  | collision_radius      | ~38 px        |
| inventory_slot.png | ui_slot     | inner_bounds          | 128×148       |
```

Flag any measurement requiring significant estimation with ⚠️ and a brief reason.

---

## Accuracy tips

- **Glows and drop shadows** are visual, not physical — measure to the hard inner edge
  of the feature, not the soft outer boundary.
- **Asymmetric assets**: if the visual center of mass differs from the geometric center,
  document it in `visual_center` so child nodes can be offset correctly.
- **Alpha padding**: images often have transparent padding that inflates reported
  dimensions. Subtract padding from dimension-based calculations where it matters.
- **When uncertain between two values**, use the tighter/smaller one and flag with `# ~`.
- **`sips` returns true pixel dimensions**, not display-scaled ones. Mention any Godot
  `import_scale` or texture compression that would affect runtime size in `notes`.
