---
name: preparing-2d-rig-assets
description: Use when a single character concept image must become separate transparent 2D parts for skeletal animation in Spine, DragonBones, or similar tools, including humanoids, quadrupeds, multi-limbed creatures, or non-humanoid anatomy.
---

# Preparing 2D rig assets

## Core principle

Treat source-visible pixels as immutable. Copy visible RGBA exactly from the
normalized source through binary masks. Generate only hidden surfaces, joint
faces, and overlap needed for declared articulation.

Use a generic anatomy graph and indexed chains. Do not impose a humanoid
skeleton or naming scheme on non-humanoid topology.

## Read the resources

- Always read [anatomy-graphs.md](references/anatomy-graphs.md) before planning
  parts or topology.
- Always read
  [cutting-and-overlap-rules.md](references/cutting-and-overlap-rules.md) before
  cutting, masking, completing, or cropping parts.
- Read [manifest-schema.md](references/manifest-schema.md) before authoring
  metadata.
- Read [quality-gates.md](references/quality-gates.md) before validation and
  final reporting.

Keep reference routing one level deep. Load each detailed field list from its
reference instead of reconstructing it from this overview.

## Required workflow

1. **Inspect and normalize.** Preserve the original and checksum. Create an
   RGBA8 normalized source, inspect canvas contact, alpha, islands, scale, and
   crop risk, and resolve background ownership.
2. **Build the anatomy graph.** Identify core masses, generic indexed chains,
   parents, joint types, pivots, attachments, neutral z-order, safe motion
   ranges, and confidence before creating layers.
3. **Emit the separation plan.** Write the plan JSON and overlay with part IDs,
   cut boundaries, visible-source regions, completion regions, pivots,
   attachments, z-order, and explicit ambiguities. Save both
   `plan/separation-plan.json` and `plan/separation-plan.png`, then evaluate the
   review gate before any extraction, completion, part PNG, rig manifest,
   reconstruction, articulation, or QA generation. Writing either plan file
   retrospectively after downstream work is a workflow violation.
4. **Stop on low-confidence topology.** Return the plan as `NEEDS_REVIEW` when
   parentage, chain structure, attachment, joint relationship, or segment count
   has multiple plausible interpretations. Stop immediately after saving both
   plan files. Continue only after plan approval resolves or explicitly accepts
   the topology.
5. **Extract original pixels through binary masks.** Create one visible-source
   mask per part. Use the extraction script to copy exact normalized RGBA and
   emit the matching provenance mask. Keep full-canvas coordinates during
   assembly.
6. **Generate only completion regions.** Create a separate completion mask for
   hidden geometry and overlap. Accept generated pixels only inside that mask,
   then composite immutable source pixels above them. Limit completion to two
   attempts; use the plan-only fallback when image editing is unavailable.
7. **Populate metadata.** Author the manifest from the approved graph, cropped
   part offsets, pivots, attachments, declared safe ranges, mask paths, warnings,
   identity neutral transforms, previews, and QA path. Set every neutral
   transform exactly to translation `[0, 0]`, rotation `0`, and scale `[1, 1]`;
   the runtime reconstructs from offsets and draw order only.
8. **Reconstruct and render articulation.** Build the neutral pose from separate
   part files and manifest metadata. Render minimum, neutral, and maximum
   declared rotation angles against required coverage masks. Keep slide joints
   in anatomy metadata, but require external translation review and keep the
   pack `NEEDS_REVIEW`; the runtime cannot apply or test translation.
9. **Validate and report evidence.** Run deterministic validation, reduce all
   gate results to one status, and report the manifest, reconstruction,
   articulation, masks, coverage evidence, warnings, and QA report. Use
   `rig-ready` only when the manifest and fresh validator report both say
   `PASS` and the validator exits `0`.

## Output contract

Deliver a character pack containing the preserved original and normalized
source, separation-plan JSON and overlay, separate cropped RGBA PNGs for every
part, per-part provenance and completion masks, per-joint coverage masks,
neutral and articulation previews, a neutral manifest, and a structured QA
report.

Use `lower_snake_case` filenames, source-canvas pixel coordinates with a
top-left origin, and recorded crop offsets. Do not pack an atlas or substitute
a sprite sheet for the independent PNG files. Require every opaque layer pixel
to belong to exactly one provenance/completion mask and every opaque normalized
source pixel to have exactly one provenance owner.

## Red flags

Stop and correct the workflow when any of these appears:

- Extraction or any downstream artifact is created before both separation-plan
  files are saved and the review gate is evaluated; a retrospective plan does
  not satisfy graph-first workflow.
- One sprite sheet exists instead of separate PNGs.
- A joint exposes a black or empty hole.
- A model generates or repaints visible source regions.
- A part lacks a provenance mask or completion mask.
- The graph uses forced humanoid identifiers instead of generic indexed chains.
- Attachments or safe-angle ranges are absent.
- Neutral reconstruction or joint-coverage evidence is absent.
- A neutral transform is not identity even though the runtime ignores it.
- A slide joint is presented as runtime-tested translation or validator `PASS`.
- A report claims rig-ready without manifest `PASS`, validator report `PASS`,
  and validator exit `0`.

## Quick commands

Run from the skill directory. Read
[quality-gates.md](references/quality-gates.md) for the exact invocations and
recovery rules.

| Script | Use |
| --- | --- |
| `scripts/inspect_source.py` | Normalize the source and record preflight evidence. |
| `scripts/extract_original_pixels.py` | Copy exact source RGBA and emit provenance. |
| `scripts/build_reconstruction.py` | Rebuild the neutral pose from cropped parts. |
| `scripts/render_articulation_check.py` | Render declared rotation-angle checks; do not use it as slide-translation evidence. |
| `scripts/validate_asset_pack.py` | Validate structure, pixels, graph, masks, and coverage; write the QA report. |

Run any script with `--help` for its interface. Treat any nonzero exit from
inspection, extraction, reconstruction, or articulation as `FAIL`. Interpret
validator exit `0` as `PASS`, exit `2` as `NEEDS_REVIEW`, and exit `1` as
`FAIL`. A clean pack declared `NEEDS_REVIEW` remains `NEEDS_REVIEW`; after human
review, set the manifest to `PASS` and rerun. A declared `FAIL` remains `FAIL`.
