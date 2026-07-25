# Rig-ready manifest schema

`assets/rig-ready-manifest.template.json` is the neutral interchange contract
for rendering and validation scripts. It describes a character in its neutral
pose; it is not itself proof that the character has passed QA.

All paths are relative to the manifest's containing skill directory. All point
values use arrays in `[x, y]` order, all boxes use `[x, y, width, height]`, and
angle ranges use `[min, max]` degrees.

## Top-level fields

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Version of this manifest contract. The template uses `1.0.0`. |
| `character_id` | string | Stable identifier for the represented character. |
| `status` | enum | Declared deliverable state: `PASS`, `NEEDS_REVIEW`, or `FAIL`. |
| `source_sha256` | string | SHA-256 hash of the source artwork; empty only when not yet recorded. |
| `canvas` | object | Source canvas dimensions: `width` and `height`, in pixels. |
| `coordinate_system` | object | Coordinate units and axes used by every canvas-space value. |
| `parts` | array | Independently renderable rig parts. |
| `joints` | array | Parent-to-child articulation metadata. |
| `neutral_pose` | object | Draw order plus required identity transform records; runtime reconstruction uses part offsets and draw order only. |
| `qa_report` | string | Relative path to the structured QA report. |
| `preview_files` | object | Relative paths to review previews: `neutral` and `articulation`. |

`canvas.width` and `canvas.height` are non-negative pixel counts. A real
deliverable must replace template zeroes with its actual source dimensions.

## Coordinate convention

`coordinate_system.unit` is `pixel`; its origin is `top_left`, the x axis
points `right`, and the y axis points `down`. Coordinates reference the
uncropped source canvas unless a field explicitly says `local`.

Each cropped part file has an `offset`, the canvas coordinate of its local
`[0, 0]`. Therefore the required conversion invariant is:

```text
canvas_coordinate = offset + local_coordinate
```

Apply the equation component by component. `pivot_local` is a local point and
`pivot_canvas` is the same pivot in canvas coordinates. `bbox` is in canvas
coordinates. `attachment_to_parent`, when present, is a canvas-space point.

## Part fields

Every part object has these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique part identifier. |
| `name` | string | Readable part name. |
| `file` | string | Relative path to the cropped part image. |
| `semantic_role` | string | Functional label, such as `core` or `appendage`. |
| `parent_id` | string or `null` | Parent part ID; `null` for a root. |
| `chain_id` | string | Identifier shared by the part's rig chain. |
| `chain_index` | integer | Zero-based position in that chain. |
| `side` | string | Spatial grouping such as `center`, `left`, `right`, or `radial`. |
| `instance_index` | integer | Zero-based index distinguishing repeated instances. |
| `z_index` | integer | Neutral-pose layer order; higher values draw later. |
| `bbox` | `[x, y, width, height]` | Part bounds on the source canvas. |
| `offset` | `[x, y]` | Canvas position of the cropped image's local origin. |
| `pivot_local` | `[x, y]` | Rotation pivot in cropped-image coordinates. |
| `pivot_canvas` | `[x, y]` | Rotation pivot in source-canvas coordinates. |
| `attachment_to_parent` | `[x, y]` or `null` | Attachment location on the source canvas. |
| `deform_safe_region` | array | Canvas-space region(s) that are safe to deform; an empty list means none recorded. |
| `provenance_mask` | string | Relative path to the mask marking pixels sourced directly from original art. |
| `completion_mask` | string | Relative path to the mask marking pixels supplied or completed for articulation. |
| `confidence` | enum | Confidence in this part's segmentation and topology decision. |
| `warnings` | array of strings | Review notes that rendering scripts must preserve. |

## Joint fields

Each joint object contains:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Unique joint identifier. |
| `parent_part_id` | string | ID of the parent part. |
| `child_part_id` | string | ID of the articulated child part. |
| `type` | string | Joint classification; use `unknown` until established. |
| `pivot_canvas` | `[x, y]` | Joint pivot in source-canvas coordinates. |
| `safe_rotation_degrees` | `[min, max]` | Inclusive rotation range judged safe for runtime preview and validation; use `[0, 0]` for a slide joint. |
| `required_coverage_mask` | string | Relative full-canvas binary mask for non-empty pixels near the joint pivot that must remain covered during this joint's motion. |
| `confidence` | enum | Confidence in the joint type, pivot, and range. |
| `warnings` | array of strings | Joint-specific review notes. |

## Neutral pose, QA, and previews

`neutral_pose.draw_order` is an ordered list of part IDs from back to front.
`neutral_pose.transforms` maps every part ID to a transform object, but the
runtime does not evaluate those transforms. Require every entry to contain
exactly `translation: [0, 0]`, `rotation_degrees: 0`, and `scale: [1, 1]`.
Any non-identity neutral transform is unsupported and validator `FAIL`. Build
the neutral pose from each part's `offset` and the draw order only.

`qa_report` names the JSON report produced by validation. `preview_files.neutral`
names the neutral reconstruction preview and `preview_files.articulation` names
the articulated-motion preview.

Manifest status participates in validation. A clean pack declared
`NEEDS_REVIEW` returns report `NEEDS_REVIEW` and validator exit `2`. After human
review resolves every warning, set the manifest to `PASS` and rerun; only
manifest `PASS` plus report `PASS` and validator exit `0` is rig-ready. A
manifest declared `FAIL` remains report `FAIL` with validator exit `1`.

## Cropped-mask convention

Part image files and their provenance and completion masks share one cropped
local coordinate frame and pixel dimensions. A nontransparent pixel in a
provenance mask means that the corresponding part pixel came from the source;
a nontransparent pixel in a completion mask means that it was added, revealed,
or otherwise completed to support a usable rig. Joint `required_coverage_mask`
uses the source-canvas coordinate frame unless the producing tool explicitly
records a crop and offset alongside it. Masks must not be rescaled or shifted
independently of the artwork they describe.

## Enums and review rule

`confidence` is exactly one of `high`, `medium`, or `low`. A `low` confidence
value for any topology decision (a part's parentage, chain, semantic role, or a
joint's relationship/type) is a blocking review checkpoint. The manifest must
remain `NEEDS_REVIEW` until a reviewer resolves or explicitly accepts it.

Keep `slide` as a valid joint type for anatomy metadata. The runtime cannot
apply or test translation. Use `safe_rotation_degrees: [0, 0]` for a slide,
record its intended translation in `warnings` and the separation plan, and
require external translation review. Any slide joint forces validator
`NEEDS_REVIEW`; a pack containing one cannot receive validator `PASS`.
