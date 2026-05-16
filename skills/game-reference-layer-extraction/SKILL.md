---
name: game-reference-layer-extraction
description: >
  Use this skill whenever a user provides a game screenshot/mockup/reference image and wants to split it into reusable Godot assets such as background plates, logos, empty UI buttons, icon buttons, decorations, props, or reviewable crop candidates. It creates an explicit asset decomposition plan, asks the user to approve uncertain layer choices before extraction, uses bundled Pillow scripts to crop/erase/review assets, and requires user confirmation before those assets are used to build a scene.
---

# Game Reference Layer Extraction

Turn a flat reference image into a reviewable set of asset candidates. This skill is for screenshot-to-assets work where source layers are not available.

The goal is not to pretend a flattened screenshot contains real layers. The goal is to make the best possible decomposition, label uncertainty, produce inspectable assets, and stop for user approval at the points where visual judgement matters.

## Required Human Approval Gates

Do not run the whole workflow end-to-end unless the user explicitly says to skip approvals.

1. **Decomposition approval:** After analyzing the image, show the proposed asset list, crop boxes, and strategy for each asset. Ask the user to confirm or revise before running extraction.
2. **Asset approval:** After extraction/generation, show the contact sheet and list known defects. Ask whether the assets are acceptable, need recrop/regeneration, or should be merged into the background.
3. **Scene-build approval:** Before building the Godot scene from extracted assets, confirm which approved assets to use and which items should remain baked into the background.

If the user has already given explicit permission for a specific gate, continue through only that gate and still stop at the next one.

## Output Contract

Produce this before extraction:

```markdown
## Asset Decomposition Plan

Reference:
Target scene:
Layering approach:

| asset | role | strategy | crop/region | empty/text-free? | confidence | notes |
| ----- | ---- | -------- | ----------- | ---------------- | ---------- | ----- |

Approval needed:
```

Use confidence labels:

| Confidence | Meaning                                                                    |
| ---------- | -------------------------------------------------------------------------- |
| high       | Clean rectangular crop or already isolated asset                           |
| medium     | Usable with minor background/glow contamination                            |
| low        | Needs user judgement, generated replacement, source art, or manual cleanup |

## Strategy Choices

| Strategy                     | Use when                                                                                             |
| ---------------------------- | ---------------------------------------------------------------------------------------------------- |
| `full_reference_plate`       | The fastest visually faithful result is to keep the screenshot baked as a background/reference plate |
| `background_clean_candidate` | UI regions can be blurred/filled as a temporary background, but this is not production-clean         |
| `crop_reference`             | The element can be cropped as a rectangular asset                                                    |
| `crop_with_alpha_candidate`  | A crop can be made transparent approximately; edge quality must be reviewed                          |
| `empty_ui_candidate`         | A button/panel crop can have text removed with a rough patch/blur pass                               |
| `code_native`                | The element should be rebuilt with Godot controls, labels, shapes, or theme resources                |
| `generate_raster`            | A clean replacement asset should be generated because screenshot extraction is not clean enough      |
| `request_source`             | Pixel-perfect layer extraction requires PSD/Figma/source art                                         |

## Main Menu Asset Defaults

For fantasy mobile menu screenshots like the Gemonite reference, start with this decomposition, then adapt by vision:

| asset                      | default role                                                     | preferred strategy                                                               |
| -------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `background.png`           | cave/crystal environment, optionally bottom decorations baked in | `background_clean_candidate` or `generate_raster`                                |
| `logo.png`                 | game title/logo                                                  | `crop_with_alpha_candidate` if exact logo is wanted; otherwise `generate_raster` |
| `primary_button.png`       | empty Play-style button frame                                    | `empty_ui_candidate`                                                             |
| `secondary_button.png`     | empty smaller/menu button frame                                  | `empty_ui_candidate`                                                             |
| `settings_icon_button.png` | top-right settings button                                        | `crop_with_alpha_candidate`                                                      |
| `score_panel.png`          | top-left best score panel                                        | `crop_reference` or `code_native`                                                |
| `bottom_decoration.png`    | cannon/gems/bomb foreground props                                | `crop_reference` or bake into `background.png`                                   |

Prefer fewer, cleaner assets over many contaminated fragments. It is acceptable to keep complex decorations baked into the background when they are not interactive.

## Bundled Script

Use `scripts/reference_layer_tool.py` for deterministic asset extraction and review.

Common commands:

```bash
python3 skills/game-reference-layer-extraction/scripts/reference_layer_tool.py init-main-menu \
  --image /path/to/reference.png \
  --out-dir /path/to/output_dir

python3 skills/game-reference-layer-extraction/scripts/reference_layer_tool.py extract \
  --image /path/to/reference.png \
  --manifest /path/to/output_dir/asset_manifest.json \
  --out-dir /path/to/output_dir/assets

python3 skills/game-reference-layer-extraction/scripts/reference_layer_tool.py review \
  --assets-dir /path/to/output_dir/assets \
  --out /path/to/output_dir/asset_review_sheet.png
```

The `init-main-menu` command creates a starter manifest with normalized boxes for a portrait fantasy menu. Treat it as a draft. Review and edit `asset_manifest.json` before extraction.

## Manifest Rules

The manifest is JSON:

```json
{
  "source_image": "reference.png",
  "coordinate_space": "normalized",
  "requires_user_approval": true,
  "assets": [
    {
      "name": "primary_button.png",
      "role": "empty Play-style button",
      "strategy": "empty_ui_candidate",
      "bbox": [0.24, 0.335, 0.76, 0.432],
      "erase_regions": [[0.3, 0.28, 0.7, 0.72]],
      "alpha": "rounded_rect",
      "confidence": "medium",
      "notes": "Text removal is approximate; ask user to approve."
    }
  ]
}
```

`bbox` is `[left, top, right, bottom]`. If `coordinate_space` is `normalized`, values are 0..1 relative to the source image. `erase_regions` are normalized inside the crop.

## Quality Rules

- Do not claim extracted assets are clean if they contain baked text, glow halos, background fragments, or distorted fill.
- Empty buttons extracted from screenshots are usually candidates, not final production assets.
- For logo crops, preserve enough glow/shadow padding for visual match, but flag background contamination.
- For background cleanup from one screenshot, use `background_clean_candidate` language. Recommend source art or generated replacement for production.
- If an asset is low-confidence, ask whether to regenerate it, recrop it, keep it baked into background, or request source art.

## Handoff To Godot Scene Build

After the user approves assets, provide a Godot-ready asset map:

```markdown
## Approved Asset Map

| asset | Godot path | intended node | placement | scale mode |
| ----- | ---------- | ------------- | --------- | ---------- |
```

Then `godot-scene-from-reference` can build the scene using approved assets. Do not build from unapproved extraction candidates unless the user explicitly permits it.
