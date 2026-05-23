---
name: "game-asset-imagegen"
description: "Generate or edit raster images for game production workflows, especially sprites, UI icons, item art, character or environment concepts, parallax layers, sprite sheets, tileable textures, mockup-derived replacements, and transparent-background cutouts. Use this skill whenever a game asset needs to be created, cleaned up, restyled, or regenerated as bitmap output. Prefer it as the image-generation utility underneath game-asset workflows such as mockup-to-game-assets. Do not use it for deterministic Godot scenes, collision, import settings, vector/SVG-only work, or simple engine-rendered text/shapes."
---

# Imagegen For Game Assets

Use this skill to generate or edit images that will become game assets. It is intentionally an image utility, not a full Godot integration workflow. Use `mockup-to-game-assets` as the higher-level workflow when the task starts from a mockup, screenshot, sprite sheet, or layered asset pack request.

## Operating modes

Default to the built-in `image_gen` tool.

- Built-in mode is preferred for normal generation, editing, variants, sprite sheets, and simple transparent asset requests. It does not require `OPENAI_API_KEY`.
- CLI fallback uses `scripts/image_gen.py` only when the user explicitly asks for CLI/API/model controls, or when the user explicitly confirms true model-native transparency with `gpt-image-1.5`.
- Do not switch to CLI fallback for ordinary size, quality, filename, or batch requests. Generate first, then copy or move selected outputs into the workspace.
- Do not silently downgrade from built-in `image_gen` or CLI `gpt-image-2` to CLI `gpt-image-1.5`. Ask first unless the user already requested that model/path.
- Never modify `scripts/image_gen.py`; it is a bundled fallback implementation.

CLI fallback subcommands:

- `generate`
- `edit`
- `generate-batch`

Read `references/cli.md`, `references/image-api.md`, and `references/codex-network.md` only when CLI fallback is actually needed.

## Good uses

- Standalone sprites, props, pickups, gems, powerups, weapons, cards, badges, and UI icons.
- Character, creature, vehicle, environment, and set-dressing concept art.
- Parallax background layers, foreground occluders, fog/light overlays, and large scene plates.
- Game UI panels, empty button frames, inventory slots, HUD ornaments, and menu decoration.
- Sprite sheets for small related assets or animation frames with fixed cell layout.
- Tileable textures when the prompt explicitly requests seamless edges.
- Transparent PNG/WebP cutouts for Godot `Sprite2D`, `TextureRect`, particles, overlays, and UI.
- Reference-guided edits, style transfer, compositing, background replacement, and cleanup.

## Bad uses

- Godot scene/resource generation, import presets, collision shapes, tile maps, animation players, or `.tscn`/`.tres` work.
- Simple labels, numbers, button text, geometric UI shapes, and layout primitives that should be rendered by the engine.
- Vector-only output, SVG icon systems, or code-native canvas/HTML drawings.
- Pixel-perfect extraction from a flattened screenshot. Use `mockup-to-game-assets` for inspection, layer strategy, slicing, and confidence notes.

## Output policy

For this repository, save project-bound final assets under:

```text
assets/generated/<pack_slug>/
├── asset_manifest.json
├── asset_review_sheet.png        # when useful for multi-asset packs
└── assets/
    ├── <asset_name>.png
    └── ...
```

Built-in `image_gen` normally saves under `$CODEX_HOME/*`. Do not leave any project-referenced asset only there. Copy or move selected finals into the workspace before finishing.

Use stable, engine-friendly filenames:

- lowercase snake_case
- semantic names such as `red_gem.png`, `play_button_frame.png`, `forest_far_layer.png`
- versioned siblings when not replacing, such as `red_gem_v2.png`

Do not overwrite existing assets unless the user explicitly requested replacement.

## Core workflow

1. Classify the request: new generation, edit, reference-guided generation, sprite sheet, transparent cutout, or asset-pack support for `mockup-to-game-assets`.
2. Decide whether the output is preview-only or project-bound. Project-bound work must end in `assets/generated/<pack_slug>/` unless the user names another path.
3. Label every input image by role: edit target, style reference, composition reference, source screenshot, or compositing input.
4. Prefer built-in `image_gen`.
5. Shape the prompt into a short production spec. Preserve user requirements; add only details that materially improve game-asset usability.
6. Generate one distinct asset per prompt unless a sprite sheet is intentionally better.
7. Inspect the output for usability: alpha, clipping, readable silhouette, consistent style, no watermark, no unwanted text, no background contamination.
8. Iterate with one targeted correction when needed.
9. Save finals into the workspace and report final paths, prompts used, mode used, and any confidence notes.

## Game prompt schema

Use only the fields that help. Keep prompts concise.

```text
Use case: stylized-concept | background-extraction | style-transfer | compositing | sketch-to-render
Asset type: <sprite / UI icon / item / character concept / parallax layer / sprite sheet / tileable texture>
Primary request: <user goal>
Input images: <Image 1: role; Image 2: role> (optional)
Style/medium: <pixel art / painted UI / stylized 3D / hand-painted / photoreal / etc>
Composition/framing: <centered icon / side-view sprite / top-down / fixed grid / wide layer>
Size/layout intent: <single asset / 4x2 sheet / 16:9 background / 256x256 icon>
Transparency/background: <transparent cutout intent or chroma-key plan>
Constraints: <must keep, must avoid, no text, no watermark, no logos>
Avoid: <unwanted elements, baked labels, shadows crossing cell boundaries>
```

For edits, repeat invariants:

```text
Change only <target change>. Keep <identity/pose/framing/style/edges> unchanged.
```

## Sprite sheets

Use a sprite sheet when several related small assets share style and can be cleanly separated.

Prompt requirements:

- fixed rows and columns
- cell size or target dimensions when known
- generous gutters between cells
- each asset centered and fully visible
- no overlap, labels, captions, watermarks, or decorative borders
- no shadows/glows crossing cell boundaries unless intentionally part of a single cell
- flat chroma-key background if the sheet needs alpha extraction

Example fragment:

```text
Create a clean game asset sprite sheet on a perfectly flat #00ff00 chroma-key background.
Grid: 4 columns x 2 rows, each cell 256x256 px with at least 32 px empty gutter.
Assets: red gem, blue gem, yellow gem, green gem, purple gem, bomb item, fireball item, lightning item.
Each asset is isolated, fully visible, centered, and not touching any other asset.
No text, no labels, no watermark, no cast shadow outside each object.
```

After generation, use `skills/mockup-to-game-assets/scripts/slice_sprite_sheet.py` when slicing is needed. Preserve enough padding for glows and animation frames.

## Transparent assets

Use built-in `image_gen` first for transparent requests. Because built-in mode does not expose true native transparency controls, generate on a flat chroma-key background and remove the key locally.

Default sequence:

1. Prompt for a perfectly flat solid key background. Use `#00ff00` by default, or `#ff00ff` when the subject is green.
2. Require no shadows, gradients, floor plane, texture, reflection, watermark, or text unless explicitly requested.
3. Copy the selected source image from `$CODEX_HOME/generated_images/...` into the workspace or `tmp/imagegen/`.
4. Run the installed helper:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input <source> \
  --out <final.png> \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

5. Validate that the output has alpha, transparent corners, plausible subject coverage, and no obvious key-color fringe.
6. If a thin fringe remains, retry once with `--edge-contract 1`. Use `--edge-feather 0.25` only for visibly stair-stepped edges on non-reflective subjects.
7. Save the final PNG/WebP into the project asset pack.

Ask before using true CLI transparency when the user asks for native transparency, chroma-key cleanup fails, or the subject is complex: hair, fur, feathers, smoke, glass, liquids, translucent material, reflective material, soft shadows, or colors that conflict with practical key colors.

Confirmation wording:

```text
This likely needs true native transparency. The default path uses a chroma-key background plus local removal, but true transparency requires CLI fallback with gpt-image-1.5 because gpt-image-2 does not support background=transparent. It also requires OPENAI_API_KEY. Should I proceed with that CLI fallback?
```

## Asset quality checklist

Before finishing, check:

- Final files exist in the workspace, not only under `$CODEX_HOME`.
- PNG/WebP assets that need transparency actually have an alpha channel.
- Sprite or icon silhouettes are readable at intended in-game size.
- No unwanted text, watermark, logo, baked label, or decorative border appears.
- Sprite sheet cells are non-overlapping and leave enough padding.
- Animation frames have consistent framing and size when requested.
- Parallax/background layers match the target aspect ratio or document the intended crop.
- UI frames avoid baked button text unless the user requested it.
- Asset manifest or notes include low-confidence areas for user review.

## CLI fallback notes

Use CLI fallback only after explicit opt-in or confirmed true-transparency fallback.

- Default model: `gpt-image-2`.
- `gpt-image-2` supports `quality`: `low`, `medium`, `high`, `auto`.
- Use `quality low` for drafts and thumbnails; use `medium` or `high` for finals, dense text, identity-sensitive edits, or high-resolution outputs.
- Do not pass `input_fidelity` with `gpt-image-2`; image inputs are already high fidelity.
- `gpt-image-2` does not support `background=transparent`.
- True transparent CLI output requires `gpt-image-1.5 --background transparent --output-format png` or WebP, after confirmation.
- Live CLI calls require `OPENAI_API_KEY`, the OpenAI SDK, and network access.

CLI command details live in `references/cli.md`; API options live in `references/image-api.md`.

## Reference map

- `references/prompting.md`: shared prompt principles.
- `references/sample-prompts.md`: copy/paste prompt recipes, including game asset examples.
- `references/cli.md`: fallback-only CLI usage.
- `references/image-api.md`: fallback-only API/model parameter reference.
- `references/codex-network.md`: fallback-only network and sandbox notes.
- `scripts/image_gen.py`: fallback-only CLI implementation; do not modify.
- `scripts/remove_chroma_key.py`: repo copy of the chroma-key helper; use the installed `$CODEX_HOME/...` helper when following the built-in transparent workflow.
