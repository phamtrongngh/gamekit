# Anatomy graphs

## Contents

- [Graph contract](#graph-contract)
- [Profile selection](#profile-selection)
- [Node fields and naming](#node-fields-and-naming)
- [Repeated-chain rules](#repeated-chain-rules)
- [Parent and z-order rules](#parent-and-z-order-rules)
- [Joint records](#joint-records)
- [Confidence and the review checkpoint](#confidence-and-the-review-checkpoint)
- [Plan-review checklist](#plan-review-checklist)

## Graph contract

Build the anatomy graph before cutting or generating pixels. Represent the
character as a directed parent-to-child graph whose nodes are independently
movable parts and whose edges are joints.

Model the topology that the artwork supports. Do not force humanoid part names,
left/right pairs, or a fixed skeleton onto a robot, animal, radial creature, or
other non-humanoid form. Use indexed chains and instances so the same contract
supports any number of limbs, wings, tentacles, plates, or amorphous regions.

Store the proposed graph in `plan/separation-plan.json` and show the same IDs,
boundaries, pivots, attachments, and uncertain regions in
`plan/separation-plan.png`.

## Profile selection

Choose the profile from visible topology, not from character theme or species.
Combine profiles only when the character visibly combines structures.

| Profile | Select when | Core and chain model | Topology question to resolve |
| --- | --- | --- | --- |
| `biped` | One main core supports two primary locomotion chains and usually an upper pair of appendage chains. | Use one or more center core nodes; index each repeated chain independently. | Decide which visible masses move independently from the core. |
| `quadruped` | A trunk supports four weight-bearing chains. | Use an axial core chain plus four indexed limb chains; add head, tail, or other chains only when present. | Decide front/back and near/far attachment and occlusion without assuming a human hierarchy. |
| `winged` | One or more articulated wing chains attach to a core. | Use indexed wing chains; preserve any separate body, limb, or tail chains. | Decide whether membranes, feathers, and rigid struts require separate parts. |
| `serpentine` | Motion follows a long serial body without discrete limbs as the primary structure. | Use one ordered axial chain from root toward the terminal segment; attach secondary chains at their actual nodes. | Decide segment boundaries from bend behavior rather than color patches. |
| `tentacled` | Multiple flexible appendages attach to a core or mantle. | Give every tentacle its own indexed chain and order segments from attachment outward. | Decide attachment locations and which crossings establish front/back order. |
| `radial/multi-limbed` | Three or more comparable appendages repeat around a center or the limb count does not fit paired anatomy. | Use a center core with indexed radial or repeated chains; preserve visible angular order. | Decide whether repeated forms share a topology while retaining distinct instances. |
| `amorphous` | Motion is defined by deforming regions rather than stable rigid segments. | Use the smallest set of core and flex-region nodes supported by visible deformation boundaries. | Decide which regions can move independently without inventing hidden rigid anatomy. |

## Node fields and naming

Record every field in the following table for each planned node. Keep detailed
deliverable metadata in the manifest; use the graph to establish topology before
pixel work.

| Field | Required value and naming rule |
| --- | --- |
| `part_id` | Use a unique `lower_snake_case` identifier. Prefer role plus stable numeric indices, such as `core_00`, `appendage_03_segment_01`, or `plate_02`. Do not encode a humanoid label unless the visible anatomy supports it. |
| `parent_id` | Use the immediate supporting part's `part_id`; use `null` only for a graph root. |
| `semantic_role` | Describe function generically, such as `core`, `head`, `limb`, `wing`, `appendage`, `tail`, `plate`, or `flex_region`. |
| `chain_id` | Use one stable `lower_snake_case` ID per motion chain. Give repeated chains distinct numeric suffixes. |
| `chain_index` | Use a zero-based integer from the chain attachment outward. |
| `side` | Use exactly `left`, `right`, `center`, `radial`, or `unknown`. Use `unknown` when the artwork does not establish a side. |
| `instance_index` | Use a zero-based integer to distinguish repeated structures with the same role. |
| `z_index` | Use an integer neutral-pose draw rank; higher values draw later and therefore appear in front. |
| `confidence` | Use exactly `high`, `medium`, or `low` according to the rubric below. |

Keep IDs stable after plan approval. When a boundary changes without changing
topology, retain the ID. When a node splits, retire the old ambiguous ID and
assign explicit segment indices.

## Repeated-chain rules

| Situation | Rule |
| --- | --- |
| Comparable repeated limbs | Give each limb a distinct `chain_id` and `instance_index`; give corresponding segments the same `semantic_role` pattern. |
| Segments within a chain | Set `chain_index: 0` at the attachment or root segment and increment outward without gaps. |
| Radial appendages | Set `side: radial`; assign `instance_index` clockwise from the topmost attachment in source-canvas coordinates. Record another anchor in the plan when no topmost attachment is clear. |
| Paired structures | Use `left` and `right` only when character-local sides are supported. Otherwise use `unknown` with separate indices. |
| Unequal or asymmetric repeats | Preserve distinct geometry and warnings. Do not mirror one instance into another without evidence or approval. |
| Partially hidden chain | Record only the topology supported by attachment, symmetry, or clear continuation. Mark alternatives and lower confidence instead of silently adding segments. |
| Bent appendage without a segment boundary | If a visible bend suggests secondary motion but the artwork does not establish whether the form is one deforming part or multiple rigid segments, treat segment count as low-confidence topology and stop at plan review. Do not extract one piece and defer the unresolved bend to downstream mesh deformation. |
| Branching chain | Give every branch a new `chain_id`; parent the branch root to the visible branching part. |

Do not collapse several independently moving repeated appendages into one PNG or
one graph node. Do not create an expected counterpart merely because another
instance exists.

## Parent and z-order rules

| Decision | Rule |
| --- | --- |
| Root | Choose the stable core mass that carries the largest set of child chains. Use multiple roots only when the source depicts disconnected rig systems and record the reason. |
| Parent | Choose the part that mechanically carries the child at its attachment. Parent by motion dependency, not by visual containment or current front/back order. |
| Serial chain | Parent each segment to the immediately preceding segment, never directly to the core when an intervening articulated segment exists. |
| Fixed detail | Parent a fixed plate, decoration, or feature to the part whose motion it follows. |
| Cycle or orphan | Reject cycles. Reject every non-root node whose `parent_id` does not resolve. |
| Neutral z-order | Sort back to front with increasing `z_index`. Resolve ties before extraction. |
| Occlusion change | Split artwork into independently ordered parts when one part would need to be both in front of and behind the same neighbor during the neutral pose. |
| Crossing chains | Preserve the observed near/far order at each crossing in the plan. Do not infer parentage from a crossing. |

Keep parentage and z-order independent: a child may draw behind its parent, and
an unrelated part may draw between a parent and child.

## Joint records

Create one joint edge for each articulated parent-child relationship. Record a
stable joint ID, parent and child part IDs, joint type, canvas-space pivot,
declared safe-angle range, required coverage mask, confidence, and warnings.

Use the attachment shown or strongly implied by the source. Treat a visually
plausible pivot as a proposal until the separation-plan review establishes it.
Declare a narrow safe range when evidence supports only limited motion; never
inflate the range to make the asset appear more capable.

Keep `slide` as a valid anatomy classification, but do not encode translation
distance in the safe-angle field. Set its rotation range to `[0, 0]`, record the
intended translation range in the plan and joint warnings, and require external
translation review. The runtime renderer applies rotation only, so a pack with
any slide joint remains `NEEDS_REVIEW` and cannot receive validator `PASS`.

## Confidence and the review checkpoint

| Level | Rubric | Action |
| --- | --- | --- |
| `high` | Attachment and occlusion are directly visible. | Continue and preserve the supporting evidence in the plan. |
| `medium` | Topology is supported by symmetry or clear continuation. | Continue, record the inference, and expose it in the plan overlay. |
| `low` | Multiple plausible topologies remain. | Stop at plan review before extraction, completion, or a rig-ready claim. |

Apply confidence to every node and joint. A low-confidence color boundary that
does not affect topology may remain a segmentation warning. A low-confidence
parent, chain, attachment, joint relationship, or segment count is a
low-confidence topology decision and must stop at plan review.

## Plan-review checklist

Before approving extraction, verify that:

- Every independently movable form has one node and stable ID.
- Every non-root node resolves to one immediate parent.
- Every repeated limb or appendage uses a generic indexed chain.
- Every rotational joint has a pivot, type proposal, safe-angle range, and
  confidence.
- Every slide joint records its intended translation for external review and
  uses `[0, 0]` as its runtime rotation range.
- Every neutral-pose occlusion has an explicit z-order.
- Every ambiguity is visible in the JSON and overlay.
- No low-confidence topology decision remains unreviewed.
