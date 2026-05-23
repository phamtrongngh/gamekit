---
name: mockup-to-game-assets
description: Turn one or more game mockups, UI screenshots, in-game screenshots, sprite sheets, or concept frames into production-ready game asset layers. Use this skill whenever the user asks to extract, split, recreate, slice, or prepare game assets from images. It is especially relevant for Godot-ready PNG assets, UI buttons/icons, gems/items, parallax backgrounds, foreground occluders, characters, and animated object sheets. Prefer this skill even when the user only provides a single flattened screenshot.
---

# Mockup To Game Assets

Use this skill to convert reference images into usable game assets. The default approach is hybrid:

- Crop or slice from the source when an asset is already clean, high resolution, unoccluded, and separable.
- Recreate with the `game_asset_imagegen` skill when the source is flattened, text-baked, occluded, too low quality, missing alpha, or when a cleaner reusable asset is needed.

Do not promise pixel-perfect extraction from a single flattened screenshot. A screenshot does not contain original layers, hidden pixels, exact fonts, animation frames, or alpha. Produce a practical asset pack with confidence notes and review artifacts.

## Required Workflow

1. Inspect the inputs.
   - View every provided image before deciding layers.
   - Record image dimensions and aspect ratio.
   - If working in this Godot project, note the viewport from `project.godot` and the existing asset folders.
   - Treat attached screenshots as references unless the user explicitly says to crop directly from them.

2. Propose the layer breakdown.
   - List each likely layer with `role`, intended use, expected transparency, and whether it should be source-cropped or recreated.
   - Use depth/parallax grouping for side-scrollers and large environment art.
   - Separate text from UI frames by default. Text is usually better rendered by the engine unless the user explicitly wants baked text.
   - Ask the user before generation when confidence is low: ambiguous boundaries, text may need to be baked, heavy occlusion, unclear alpha, unknown animation frames, or unclear parallax depth.

3. Choose an asset strategy per layer.
   - `source_crop`: clean asset can be cropped directly from the source.
   - `source_crop_alpha`: source crop can be made usable with local alpha cleanup.
   - `imagegen_single`: recreate one standalone asset.
   - `imagegen_sprite_sheet`: recreate many small related assets in one non-overlapping sheet.
   - `imagegen_large_layer`: generate a large full-frame or parallax layer separately.
   - `engine_text_or_shape`: use engine-rendered text or simple code-native shapes instead of bitmap text.

4. Generate or extract.
   - If using image generation, load and follow the `game_asset_imagegen` skill. Use built-in `image_gen` first.
   - For transparent assets, follow the `game_asset_imagegen` skill's chroma-key plus local alpha-removal workflow. Do not switch to true/native transparency CLI fallback unless the user explicitly confirms it.
   - Use sprite sheets for small related assets with shared style and enough spacing: gems, item icons, button frames, small characters, animation frames.
   - Generate large layers separately: full backgrounds, parallax buildings, platforms, fog, light shafts, foreground occluders.
   - For generated sprite sheets, require flat background or transparent-ready output, explicit cell layout, no overlap, generous gutters, and no labels/text inside cells unless intentionally baked.

5. Slice sprite sheets or source sheets when needed.
   - Use `scripts/slice_sprite_sheet.py` with a JSON manifest containing pixel bboxes.
   - Keep crop boxes tight enough to avoid neighboring assets, but preserve enough padding for animation frames and glow.
   - Use `--trim-alpha` for transparent/generated sheets when the bbox includes empty gutters.
   - Review the generated `asset_review_sheet.png` before calling the pack final.

6. Validate and report.
   - Confirm every requested asset exists, has the expected dimensions, and has alpha when expected.
   - Check for clipped glow, missing animation padding, unwanted text, source-background contamination, and accidental overlap.
   - Save project-bound outputs under the workspace, not only under `$CODEX_HOME/generated_images`.
   - Report final paths, strategies used, confidence notes, and any assets requiring user review.

## Default Output Layout

For this repository, put new asset packs here unless the user asks for integration or replacement:

```text
assets/generated/<pack_slug>/
├── asset_manifest.json
├── asset_review_sheet.png
└── assets/
    ├── <asset_name>.png
    └── ...
```

Only write into established folders such as `assets/menu/assets`, `assets/gems`, or `assets/items` when the user explicitly asks to integrate or replace those assets.

## Manifest Format

Use this compact manifest for planning and slicing. `bbox_px` is `[x, y, width, height]` in the sheet/source coordinate space. Include `bbox_norm` for analysis when useful, but the slicer requires `bbox_px`.

```json
{
  "source_images": [
    {
      "path": "/absolute/path/or/thread-image-label.png",
      "role": "reference",
      "width": 1080,
      "height": 1920
    }
  ],
  "assets": [
    {
      "name": "play_button_frame",
      "role": "empty primary menu button frame",
      "strategy": "imagegen_sprite_sheet",
      "bbox_px": [64, 96, 420, 144],
      "bbox_norm": [0.125, 0.1875, 0.8203, 0.2813],
      "target_size": [512, 192],
      "alpha_policy": "transparent_png",
      "output_path": "assets/play_button_frame.png",
      "confidence": "medium",
      "review_notes": "No baked PLAY text; preserve gold trim and purple fill."
    }
  ]
}
```

## Layering Heuristics

Menu UI:
- Logo or title mark.
- Empty button frames, not baked button text, unless requested.
- Icon buttons.
- Background and foreground decoration either combined or split based on reuse.
- Engine-rendered labels and button text.

Match-3 or bubble-shooter gameplay:
- Gem colors as reusable sprites, one asset per gem color.
- Special items and powerups as separate sprites.
- Cannon/launcher as its own sprite or small state sheet.
- Slots, panels, counters, and buttons as UI assets.
- Background separated from gameplay objects.

Side-scroller or cinematic scene:
- Sky/fog background as the farthest layer.
- Far, mid, and foreground structures separated by depth.
- Light shafts, haze, smoke, and atmosphere as alpha overlay PNGs.
- Main gameplay platform/walkway as a collision-aligned visual layer.
- Foreground occluders as separate layers.
- Characters, birds, crowds, and repeatable details as separate sprites or small animation sheets.

## Sprite Sheet Prompt Guidance

When using `imagegen_sprite_sheet`, specify:

- One plain background color suitable for removal, or transparent-ready composition if supported by the chosen workflow.
- A fixed grid with named cells.
- Large gutters between cells.
- No drop shadows crossing cell boundaries.
- No labels, captions, watermarks, or decorative borders around the sheet.
- Each asset centered in its cell with enough padding for glow and antialiasing.

Example prompt fragment:

```text
Create a clean game asset sprite sheet on a perfectly flat #00ff00 chroma-key background.
Grid: 4 columns x 2 rows, each cell 256x256 px with at least 32 px empty gutter.
Assets: red gem, blue gem, yellow gem, green gem, purple gem, bomb item, fireball item, lightning item.
Each asset must be isolated, fully visible, centered, and not touching any other asset.
No text, no labels, no watermark, no cast shadow outside the object.
```

## Slicing Script

Use the bundled slicer for generated sheets and any source screenshot/sheet with known bboxes:

```bash
python .agents/skills/mockup-to-game-assets/scripts/slice_sprite_sheet.py \
  --sheet <sprite_sheet.png> \
  --manifest <slice_manifest.json> \
  --out-dir <output_dir> \
  --trim-alpha \
  --padding 8
```

The slicer:

- Reads `assets[].bbox_px` as `[x, y, width, height]`.
- Rejects overlapping final crop regions after padding.
- Preserves alpha by writing PNG files from RGBA crops.
- Optionally trims to non-transparent bounds before adding padding.
- Writes `asset_review_sheet.png` and `slice_manifest.resolved.json`.

## Review Checklist

Before finishing, check:

- Asset names are stable, lowercase snake_case, and engine-friendly.
- PNG alpha exists for sprites, icons, overlays, and UI frames that need transparency.
- Backgrounds and large parallax layers keep the target aspect ratio or documented alignment.
- Button frames do not include baked text unless requested.
- Animated sprites have consistent frame size and enough padding.
- Glow, wings, shadows, and translucent edges are not clipped.
- The manifest records low-confidence areas honestly.
