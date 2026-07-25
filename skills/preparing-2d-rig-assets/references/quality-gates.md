# Quality gates

## Contents

- [Validation principle](#validation-principle)
- [Exact script commands](#exact-script-commands)
- [Required evidence](#required-evidence)
- [Gate matrix](#gate-matrix)
- [Status reduction](#status-reduction)
- [Manifest status agreement](#manifest-status-agreement)
- [Completion limit and plan-only fallback](#completion-limit-and-plan-only-fallback)
- [Recovery playbook](#recovery-playbook)
- [Final report](#final-report)

## Validation principle

Treat a plausible-looking part pack as unvalidated. Reconstruct the neutral
pose, render the declared articulation range, run deterministic validation, and
report the resulting evidence. Call the result rig-ready only when the final
manifest and validator report both say `PASS` and the validator exits `0`.

## Exact script commands

Run the commands from the skill directory. In a shell script or function, accept
the existing pack directory as `$1`, the source image as `$2`, and the part ID
for extraction as `$3`. Normalize `PACK` and `SOURCE` before using
`"$PACK/..."` paths:

```bash
PACK_INPUT="$1"
SOURCE_INPUT="$2"
PART_ID="$3"
PACK=$(cd "$PACK_INPUT" && pwd -P)
SOURCE=$(cd "$(dirname "$SOURCE_INPUT")" && pwd -P)/$(basename "$SOURCE_INPUT")
VISIBLE_MASK="$PACK/plan/work/${PART_ID}_visible_source.png"
PART_LAYER="$PACK/plan/work/${PART_ID}_source_layer.png"
PART_PROVENANCE="$PACK/plan/work/${PART_ID}_provenance.png"
```

Require the pack directory and source image to exist before normalization.
Every `"$PACK/..."` child path below is therefore absolute and cannot be joined
to the pack path a second time.

```bash
python3 scripts/inspect_source.py "$SOURCE" \
  --normalized "$PACK/source/normalized.png" \
  --report "$PACK/plan/source-inspection.json"
```

```bash
python3 scripts/extract_original_pixels.py \
  "$PACK/source/normalized.png" "$VISIBLE_MASK" \
  --layer "$PART_LAYER" \
  --provenance "$PART_PROVENANCE"
```

```bash
python3 scripts/build_reconstruction.py "$PACK" \
  --manifest "$PACK/rig-ready-manifest.json" \
  --output "$PACK/previews/reconstructed-neutral.png"
```

```bash
python3 scripts/render_articulation_check.py "$PACK" \
  --manifest "$PACK/rig-ready-manifest.json" \
  --output "$PACK/previews/articulation-check.png"
```

```bash
python3 scripts/validate_asset_pack.py "$PACK" \
  --manifest "$PACK/rig-ready-manifest.json" \
  --report "$PACK/qa-report.json"
```

Run each script with `--help` when resolving paths or invocation details. Stop
and record the command output according to this exit contract:

| Command | Exit meaning |
| --- | --- |
| `inspect_source.py`, `extract_original_pixels.py`, `build_reconstruction.py`, or `render_articulation_check.py` | Exit `0` means the operation completed; any nonzero exit means `FAIL`. |
| `validate_asset_pack.py` | Exit `0` means `PASS`; exit `2` means `NEEDS_REVIEW`; exit `1` means `FAIL`. |

## Required evidence

Preserve these artifacts together:

| Evidence | What it proves |
| --- | --- |
| Original source, checksum, normalized source, and inspection report | Establish the immutable input, coordinate frame, alpha, crop risk, and normalization record. |
| Separation plan JSON and overlay | Establish graph-first topology, boundaries, pivots, attachments, z-order, confidence, and review decisions. |
| Per-part provenance and completion masks | Prove that every opaque layer pixel belongs to exactly one of provenance or completion. |
| Per-joint required coverage masks | Define the regions that must stay opaque across declared motion. |
| Separate cropped RGBA part files and manifest | Establish independent runtime parts, offsets, graph, attachments, declared safe rotation ranges, and identity neutral transforms. |
| Neutral reconstruction | Establish that offsets and draw order rebuild the source pose without transform evaluation. |
| Articulation check | Expose holes and insufficient overlap at minimum, neutral, and maximum declared rotation angles. Require external translation review for every slide joint. |
| `qa-report.json` | Record validator findings and the final `PASS`, `NEEDS_REVIEW`, or `FAIL` status. |

Do not substitute a sprite sheet, console summary, or visual assertion for these
artifacts.

## Gate matrix

| Gate | `PASS` condition | Blocking evidence |
| --- | --- | --- |
| Source inspection | The original checksum is recorded; normalized input is RGBA8; alpha and canvas-contact risks are resolved or explicitly reviewed. | Missing checksum, unhandled opaque background, or unexplained crop loss. |
| Topology | Every part and joint resolves in an acyclic generic graph; no blocking low-confidence topology remains. | Missing graph, humanoid-only forced naming, cycle, orphan, or unresolved topology choice. |
| Part delivery | Every planned part has its own referenced RGBA PNG, matching masks, crop offset, and transparent padding. | Missing file, sheet-only output, mismatched dimensions, or opaque padding. |
| Pixel lock and ownership | Every provenance pixel equals normalized source RGBA at its recorded canvas coordinate, and every opaque normalized-source pixel has exactly one provenance owner across all parts. | Any mismatch, zero or multiple provenance owners, or generated replacement of visible detail. |
| Layer-mask classification | Every opaque layer pixel belongs to exactly one of its provenance or completion masks; the masks do not overlap. | An opaque pixel in neither or both masks, a transparent pixel selected by either mask, or mask overlap. |
| Completion bounds | Every generated pixel belongs only to its completion mask and no completion leaks into the neutral silhouette. | Unmasked generated pixel, altered visible detail, or unresolved material/design mismatch. |
| Neutral reconstruction | Offsets and draw order rebuild the normalized neutral pose; every neutral transform is exactly translation `[0, 0]`, rotation `0`, and scale `[1, 1]`. | Missing preview, wrong offset/order, non-identity transform, alpha hole, or pixel difference in a locked region. |
| Rotational joint coverage | Every mask is non-empty, includes pixels within 16 canvas pixels of its declared pivot, and composite alpha stays nonzero there at minimum and maximum declared rotation angles. | Missing/empty/distant mask, black or transparent joint hole, or insufficient rotational overlap. |
| Slide review | No slide joint is present. | A slide joint always requires external translation review because the runtime renderer cannot apply or test translation. |
| Final validation | The manifest declares `PASS`, the validator exits `0`, and `qa-report.json` says `PASS`. | Exit `2`/`NEEDS_REVIEW`, exit `1`/`FAIL`, absent report, or status disagreement. |

## Status reduction

Reduce all inspection, graph, completion, reconstruction, articulation, and
validator results to one package status. Use the most severe result:

```text
FAIL > NEEDS_REVIEW > PASS
```

| Final status | Assign when |
| --- | --- |
| `FAIL` | Any required file is missing; the graph has a cycle or orphan; source provenance differs; neutral reconstruction cannot be produced or has a locked-pixel mismatch; an inspection, extraction, reconstruction, or articulation command exits nonzero; the validator exits `1`; the report says `FAIL`; or the manifest declares `FAIL`. |
| `NEEDS_REVIEW` | No `FAIL` remains, but topology is low confidence, source-canvas contact may hide anatomy, completion remains uncertain after two attempts, image editing is unavailable, a slide joint is present, an articulation/coverage concern requires a decision, the validator exits `2`, or the report says `NEEDS_REVIEW`. |
| `PASS` | Every gate passes, no slide joint or blocking warning remains, the manifest declares `PASS`, the validator exits `0`, and `qa-report.json` explicitly reports `PASS`. |

Never promote a script result. A manual review may reduce `PASS` to
`NEEDS_REVIEW` or `FAIL`; it may not promote a validator's non-`PASS` result.

## Manifest status agreement

Set manifest `status` to exactly `PASS`, `NEEDS_REVIEW`, or `FAIL`.

- Keep `NEEDS_REVIEW` while a human decision remains. A technically clean pack
  whose manifest declares `NEEDS_REVIEW` receives a `NEEDS_REVIEW` report and
  validator exit `2`.
- After the human resolves every review item, set the manifest to `PASS` and
  rerun reconstruction, articulation, and validation. Treat the pack as
  rig-ready only when that fresh run returns exit `0` and report `PASS`.
- Keep a deliberately declared `FAIL` as `FAIL`; validation returns exit `1`
  even when other checks would pass.
- Do not edit the report status directly. Change the manifest or asset evidence
  and rerun the validator.

## Completion limit and plan-only fallback

Allow at most two image-completion attempts for a part or joint region. After
the second unsuccessful attempt:

1. Preserve the best completion and both mask/evidence records for review.
2. Keep source-visible pixels locked.
3. Set the package to `NEEDS_REVIEW` when no deterministic `FAIL` remains.
4. Identify the exact artist decision or repaint needed.
5. Do not widen the completion mask into visible source regions.

When image editing is unavailable, stop after the approved separation plan,
source extraction, and mask specification. Deliver the plan and artist handoff
as `NEEDS_REVIEW`. Do not invent hidden geometry, omit the limitation, render a
misleading articulation preview, or use the term rig-ready.

## Recovery playbook

| Finding | Recovery | Status until recovered |
| --- | --- | --- |
| Source touches canvas | Identify the contacting side and affected part in the inspection report. Preserve the known contour. Mark the crop-limited edge and request review when hidden attachment or padding cannot be established. | `NEEDS_REVIEW` for unresolved anatomy or crop loss; otherwise retain the documented padding exception and rerun validation. |
| Background is opaque | Separate foreground before part extraction, preserve the background-removal mask, regenerate normalized RGBA, and rerun inspection. Do not treat opaque background pixels as character provenance. | `FAIL` while the background contaminates layers; `NEEDS_REVIEW` if foreground ownership remains ambiguous. |
| Pixel-lock mismatch | Discard the affected composite. Re-extract exact normalized pixels with the visible-source mask, subtract provenance from completion, composite source last, and rerun reconstruction and validation. | `FAIL` until every provenance pixel matches. |
| Neutral mismatch | Check crop offsets, local/canvas pivots, draw order, mask dimensions, and duplicate source ownership. Set every neutral transform exactly to translation `[0, 0]`, rotation `0`, and scale `[1, 1]`; the runtime applies only offsets and draw order. Rebuild the neutral preview after correction. | `FAIL` while a transform is non-identity or locked pixels or required neutral alpha differ. |
| Joint coverage gap | Recheck the pivot and declared safe range. Expand concealed completion from local thickness and the limiting angle, regenerate within the completion mask, and rerender articulation. Narrow the declared range only when the plan supports it. | Non-`PASS`; after two unsuccessful completion attempts, preserve evidence and request review without a rig-ready claim. |
| Slide joint | Preserve `type: slide` in anatomy metadata and prepare an external translation review with the intended translation range and coverage evidence. Do not interpret `safe_rotation_degrees` as translation. | Always `NEEDS_REVIEW`; the validator cannot return `PASS` for a pack containing a slide joint. |
| Missing file | Restore the referenced file or correct the manifest path. Confirm that every part, mask, preview, coverage mask, and QA path resolves. | `FAIL` until resolved. |
| Cycle or orphan | Correct parent IDs and chain structure in the plan and manifest. Require every non-root part to resolve to one immediate parent and rerun validation. | `FAIL` until resolved. |
| Low-confidence topology | Emit the separation plan and overlay with alternatives, affected nodes/joints, and the user decision required. Stop before extraction or generation. | `NEEDS_REVIEW`; continue only after plan approval resolves or explicitly accepts the topology. |

## Final report

Report the package path, final status, validator command and exit result,
`qa-report.json` path, neutral and articulation preview paths, mask evidence,
manifest status, remaining warnings, external slide-review evidence, and any
plan-review decision. Use `rig-ready` only when both the manifest and fresh
validator report say `PASS` and the validator exits `0`.
