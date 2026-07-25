# Cutting and overlap rules

## Contents

- [Cut contract](#cut-contract)
- [Joint-specific cuts](#joint-specific-cuts)
- [Place cuts behind occluders](#place-cuts-behind-occluders)
- [Size overlap from motion and thickness](#size-overlap-from-motion-and-thickness)
- [Build evidence masks](#build-evidence-masks)
- [Complete hidden geometry](#complete-hidden-geometry)
- [Composite and crop](#composite-and-crop)
- [Common observed failures](#common-observed-failures)
- [Review checklist](#review-checklist)

## Cut contract

Cut parts according to motion topology and declared articulation, not merely
along visible color islands. Keep every source-visible pixel immutable. Copy it
from `source/normalized.png` through a binary mask; never redraw, heal, mirror,
color-match, or synthesize it.

Work on full-canvas RGBA layers until reconstruction is correct. Crop only after
completion and mask evidence are final.

## Joint-specific cuts

| Joint type | Observable motion | Cut and overlap rule |
| --- | --- | --- |
| `hinge` | Rotation primarily around one pivot and one plane. | Hide a curved cut under the occluding part. Complete a rounded underlay around the pivot that covers the full declared angle range. |
| `ball` | Rotation may fan in multiple directions. | Use a rounded or socket-like concealed boundary. Provide coverage around the pivot in every tested direction rather than only along one axis. |
| `flex` | A soft or serial region bends without one rigid pivot. | Split only at a stable fold or concealed transition. Provide a tapered overlap and declare a conservative preview range. |
| `slide` | One part translates across another. | Keep `slide` in anatomy metadata, set its runtime rotation range to `[0, 0]`, and record the intended translation in the plan and warnings. Prepare a concealed rail or sleeve for external review; the runtime cannot apply or test translation, so the pack remains `NEEDS_REVIEW`. |
| `fixed` | The child follows the parent without independent articulation. | Keep a separate part only when z-order or downstream control requires it. Place the seam under an existing edge and require neutral coverage. |
| `unknown` | The source does not establish a reliable mechanism. | Mark the joint low confidence when the uncertainty changes topology or attachment. Stop at plan review instead of choosing a convenient cut. |

## Place cuts behind occluders

1. Identify which form visibly occludes the attachment in the neutral pose.
2. Move the cut inward beneath that form, beyond the antialiased visible edge.
3. Preserve the full visible contour on the foreground part.
4. Extend the concealed part under the occluder far enough for every declared
   test angle.
5. Keep cut-edge and generated pixels out of the neutral silhouette.
6. Split the part when a single layer cannot preserve the observed front/back
   order.

Do not cut exactly along the exposed joint boundary. That exposes transparent,
black, or generated seams as soon as the child rotates.

## Size overlap from motion and thickness

Measure local thickness `t` across the narrowest joint cross-section in source
pixels. Let `a` be the larger absolute value of the declared minimum and maximum
safe rotation, in radians. Let `p` be the crop safety padding:

```text
p = max(2 px, ceil(0.005 × longest canvas side))
d = ceil(t / 2 + t × sin(min(a, π/2))) + p
```

Use `d` as the initial concealed overlap depth from the visible joint boundary.
For a hinge or ball joint, shape the joint end around the pivot with radius at
least `ceil(t / 2) + p` and extend it through the angular sweep.

Treat this calculation as the starting geometry, not proof of coverage. Render
the minimum, neutral, and maximum declared rotation poses. Expand the
completion mask and concealed artwork until the required coverage mask remains
nontransparent at every rendered rotation. Narrow the declared safe-angle range
when the source design cannot support a larger overlap without visible
alteration.

Do not use this angular calculation as slide-translation evidence. Size a slide
overlap from the intended external translation range and local thickness, then
hand it off for external translation review. The runtime renderer and validator
cannot prove slide coverage or return validator `PASS` for a pack containing a
slide joint.

## Build evidence masks

Use binary masks with alpha values `0` and `255`. Keep every artwork mask in the
same local dimensions and offset as its corresponding part.

| Mask | Construct it from | Required meaning |
| --- | --- | --- |
| Visible-source mask | Select only pixels visibly owned by one planned part in `source/normalized.png`. | Define the exact normalized source pixels to extract for that part. Avoid duplicate ownership among parts drawn together in neutral pose. |
| Provenance mask | Emit it with deterministic source extraction. | Mark every final part pixel copied exactly from the normalized source. A marked pixel must match source RGBA at its recorded canvas coordinate. |
| Completion mask | Paint only hidden surfaces, joint faces, and overlap needed for articulation, then subtract the provenance mask. | Bound every generated pixel that may enter the final part. Keep source-visible regions outside this mask. |
| Joint-coverage mask | Mark the source-canvas region around a joint that must stay covered throughout the declared motion range. | Require composite alpha greater than zero at each marked pixel in every tested pose. |

Store one provenance and one completion mask per part. Store one required
coverage mask per articulated joint. Preserve empty completion masks as explicit
evidence when a part needs no generated pixels.

Enforce both package-wide invariants: every opaque layer pixel belongs to
exactly one of its provenance or completion masks, and every opaque normalized
source pixel has exactly one provenance owner across all parts. Treat zero
owners, multiple owners, mask overlap, and unclassified opaque layer pixels as
`FAIL`.

## Complete hidden geometry

Generate only inside the completion mask. Supply enough context to match the
local contour, material, line weight, color, and lighting without exposing the
source-visible region to replacement.

Keep asymmetric structures independent. Do not mirror missing material unless
the source, approved plan, or reviewer establishes symmetry. Limit completion
to two attempts. If the second attempt still changes design, mismatches local
material, or cannot cover the declared motion, preserve the best review
artifact, set `NEEDS_REVIEW`, and report an artist handoff.

If no image-editing capability is available, keep the source extraction, plan,
and masks; deliver a plan-only `NEEDS_REVIEW` result. Do not fabricate
completion or call the pack rig-ready.

## Composite and crop

Use this deterministic order exactly:

```text
generated completion inside completion mask
→ exact source pixels inside provenance mask
→ crop with transparent padding
```

Discard every generated pixel outside the completion mask. Overlay exact source
pixels last so completion cannot modify visible art. Crop the resulting part to
its alpha bounds with at least
`max(2 px, ceil(0.5% × longest canvas side))` transparent padding, except at a
documented source-canvas limit. Record the crop offset; do not rescale artwork
or masks independently.

## Common observed failures

| Failure | Cause | Required correction |
| --- | --- | --- |
| Black joint holes | A cut exposes an opaque fill or missing alpha instead of concealed artwork. | Remove the fill, complete a proper underlay, and rerun joint coverage. |
| Cut-off hidden geometry | The layer contains only the visible island. | Extend the concealed form inside a completion mask and verify the articulated poses. |
| Insufficient overlap | The cut and underlay were sized for neutral pose only. | Recalculate from local thickness and declared safe angles; expand and rerender. |
| Altered visible detail | Visible art was generated, repainted, or composited below an edited region. | Discard that result and restore exact normalized pixels through the provenance mask. |
| Sheet-only output | Parts were arranged on one sprite sheet without independent files and offsets. | Emit one transparent cropped PNG per part and preserve reconstruction metadata. |

## Review checklist

- Confirm that every visible source pixel has one auditable owner.
- Confirm that every generated pixel lies inside a completion mask.
- Confirm that every cut remains behind an occluding form throughout the safe
  rotation range.
- Confirm that source pixels overlay completion pixels in the final composite.
- Confirm that every joint coverage mask stays opaque at all rendered angles.
- Confirm that every slide joint has separate external translation-review
  evidence and remains `NEEDS_REVIEW`.
- Confirm that every cropped file retains transparent padding and a recorded
  offset.
