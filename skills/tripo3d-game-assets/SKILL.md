---
name: tripo3d-game-assets
description: "Generate, texture, edit, optimize, rig, animate, and export 3D game models with the Tripo3D OpenAPI. Use this skill whenever the user mentions Tripo, Smart Mesh, P1, text-to-3D, image-to-3D, multiview-to-3D, game-ready 3D assets, low poly or retopology, mesh segmentation or completion, PBR texturing, rigging, animation retargeting, FBX/GLB/GLTF/USDZ/OBJ/STL export, or asks an agent to create usable 3D models for games. Prefer this over bitmap image skills when the desired final output is a 3D model file, animated rig, mesh, texture pass, or engine import asset; when a raster reference image must be created or edited first, use the game-asset-imagegen skill instead of Tripo image-generation APIs."
---

# Tripo3D Game Assets

Use this skill to turn text, reference images, multiview images, or existing 3D files into game-ready 3D model assets through Tripo3D. The skill is a production workflow, not just an API wrapper: plan the asset for its target engine, choose the Tripo task/version, run generation or post-processing, download expiring outputs, verify basic asset quality, and save a traceable manifest.

## Requirements

- Live generation requires `TRIPO_API_KEY` in the environment. Never paste or commit the key.
- The API base URL is `https://api.tripo3d.ai/v2/openapi`.
- Most work submits `POST /task`, receives `task_id`, then polls `GET /task/{task_id}` until a finalized status.
- Download output URLs immediately; Tripo documents model and preview result URLs as short-lived.
- Prefer the official `tripo3d` Python SDK when it is already installed or the user approves installing it. Otherwise use raw HTTP and the helper script in `scripts/tripo_task.py`.
- If Tripo rejects a model version or task type, check the current docs before guessing. Tripo versions move quickly.

## Image Preparation Policy

Do not use Tripo image-generation or image-editing tasks in this gamekit workflow. If a reference image, T-pose sheet, cleaner concept, texture reference, or multiview image set must be created or edited, load and follow `skills/game-asset-imagegen/SKILL.md` first, save the raster output into the workspace, then upload or reference that image for Tripo 3D model tasks.

This policy covers Tripo task types such as `text_to_image`, `generate_image`, `generate_multiview_image`, and `edit_multiview_image`. Use Tripo for 3D tasks: model generation, import, texturing, mesh editing, low-poly conversion, rigging, retargeting, and format conversion.

## Default Output Layout

For this repository, save project-bound 3D asset packs under:

```text
assets/generated/<pack_slug>/
+-- tripo_manifest.json
+-- source_refs/
+-- prompts/
+-- models/
    +-- <asset_slug>/
        +-- raw/
        +-- final/
        +-- previews/
        +-- reports/
```

Use stable lowercase snake_case filenames. Do not overwrite existing project assets unless the user explicitly requests replacement.

## Choose The Route

- Smart Mesh request: use Tripo P1.0 via `model_version="P1-20260311"` on `text_to_model`, `image_to_model`, or `multiview_to_model`. This is the API-backed Smart Mesh route for clean structured low-poly topology and real-time game assets.
- Prompt-only concept prop: use `text_to_model`. Choose Smart Mesh P1 (`P1-20260311`) for low-poly topology and cleaner structured mesh; choose H3 (`v3.1-20260211` or `v3.0-20250812`) for better prompt fidelity and advanced controls.
- One reference image: use `image_to_model`. Use H3 for high fidelity, Smart Mesh P1 when low-poly output is the priority.
- Four directional references or higher geometry consistency: use `multiview_to_model` with user-provided images or images prepared by `game-asset-imagegen`. Use Smart Mesh P1 for cleaner low-poly topology. The files order is `[front, left, back, right]`; front is required and at least two images are needed.
- Weak concept art, missing character parts, or non-rig pose: first use `game-asset-imagegen` to create or edit a clean reference, such as a T-pose/A-pose sheet, complete character view, head/body reference, style-consistent variant, or four-view turnaround. Then upload or reference that image in `image_to_model` or `multiview_to_model`.
- Existing 3D model: use `import_model`, then texture, segment, low-poly, rig, retarget, or convert.
- Re-texture or add PBR: use `texture_model` (`v3.0-20250812` preferred) with a text, image, or multi-image texture prompt. Use `part_names` after segmentation for selective retexture.
- Editable parts: use generation with `generate_parts=true` when supported, or run `mesh_segmentation`. Segment before selective texturing or completion.
- Lower poly game mesh: prefer Smart Mesh P1 direct generation when creating a new asset. Use H3 with `smart_low_poly=true` when you need H3 fidelity/controls but want hand-crafted low-poly topology. Use post-process `highpoly_to_lowpoly` (`P-v2.0-20251225`) with an explicit `face_limit` for existing or already-generated high-poly models.
- Rigging and animation: run `animate_prerigcheck`, then `animate_rig` (`v2.5-20260210`), then `animate_retarget` with preset motions.
- Engine/export format: use `convert_model`. Prefer GLB/GLTF for Godot/web previews, FBX for Unity/Unreal/Mixamo workflows, USDZ for Apple AR, OBJ for static textured assets, STL/3MF only for geometry/printing.

## Core Workflow

1. Capture the game asset spec: target engine, scale, camera use, silhouette priority, poly budget, texture/PBR needs, rig/animation needs, desired formats, and reference images.
2. Pick the minimal Tripo pipeline from the route map. Avoid spending credits on high fidelity, PBR, rigging, or multiple animations unless the output needs them.
3. Build a payload and save it under `prompts/<asset_slug>.<stage>.json`.
4. Submit the task with `TRIPO_API_KEY`. Poll with exponential backoff or the helper script. Respect `Retry-After` on 429/2000 responses.
5. On success, save the full task JSON, `task_id`, input parameters, seed values, `consumed_credit`, and any `X-Tripo-Trace-ID` values into `tripo_manifest.json`.
6. Download `output.model`, `output.base_model`, `output.pbr_model`, `output.rendered_image`, and any other model/preview URLs immediately when present.
7. Run needed post-process tasks in sequence: texture, segment, low-poly, rig, retarget, convert.
8. Verify the final files before reporting: file exists, format matches request, rough size is plausible, preview image exists when available, and the manifest identifies exactly which task produced each final file.

## Game-Ready Defaults

- Static prop or collectible: Smart Mesh P1 `P1-20260311`, `texture=true`, `pbr=true`, `face_limit` around `2000-8000`, final GLB/GLTF.
- Hero prop or environment piece: H3 `v3.1-20260211`, `geometry_quality=standard` first, `texture_quality=standard` first, then selectively upgrade.
- Mobile/low-end game asset: P1 or `highpoly_to_lowpoly`, explicit `face_limit`, `texture_size` reduced during conversion, `pivot_to_center_bottom=true` when useful.
- Rigged humanoid/creature: make or edit the reference into a clean T-pose/A-pose, generate textured model, run pre-rig check, rig with the reported `rig_type`, then retarget up to five preset animations.
- Deterministic variants: reuse `model_seed` for geometry; change `texture_seed` for texture variants.
- Part-level edits: segment first, inspect/record part names from the task output, then pass `part_names` to texture, completion, low-poly, or conversion tasks.

## Constraints To Remember

- Prompt max is 1024 characters; negative prompt max is 255 characters. Avoid emojis and unusual Unicode in API prompts.
- For image inputs, direct URL supports JPEG/PNG up to 20 MB. Direct quick upload only supports images; do not use it for 3D model files.
- `pbr=true` implies texturing even when `texture=false`.
- `generate_parts=true` is incompatible with `texture=true`, `pbr=true`, and `quad=true`; use an untextured non-quad generation for part editing.
- H3 quad output forces FBX. Quad face limits are much lower than triangle outputs.
- Smart Mesh P1 supports selected generation parameters; unsupported H3-only parameters can return an API error. Keep P1 payloads lean and check the P1 docs before adding advanced controls.
- `texture_quality=standard` with both `texture=false` and `pbr=false` is invalid.
- 1.x generation tasks are not supported by current texture, mesh editing, animation, and conversion tasks.
- OBJ, STL, and 3MF conversion are not supported for rigged models; STL drops textures.
- `animate_retarget` needs either `animation` or `animations`, and `animations` length cannot exceed five.

## Helper Script

Use the bundled script for raw HTTP task submission, polling, and output downloads:

```bash
TRIPO_API_KEY=tsk_... python skills/tripo3d-game-assets/scripts/tripo_task.py run \
  --payload assets/generated/<pack_slug>/prompts/<asset_slug>.text_to_model.json \
  --out-dir assets/generated/<pack_slug>/models/<asset_slug>/raw \
  --download
```

The script intentionally does not implement STS upload. For local image/model uploads, prefer the official SDK or follow Tripo's upload docs, then place the returned `file_token` or `{bucket, key}` object in the task payload.

## Reference Map

- `references/payload-recipes.md`: copyable payloads for generation, texturing, mesh editing, rigging, retargeting, and export.
- `references/api-notes.md`: concise Tripo API facts, task/version map, statuses, error handling, and rate-limit notes.
- `scripts/tripo_task.py`: dependency-free HTTP helper for JSON task workflows.
- Official docs: start at `https://docs.tripo3d.ai/get-started/introduction.html` when behavior changes.
