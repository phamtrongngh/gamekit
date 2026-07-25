#!/usr/bin/env python3
"""Validate the structural and pixel invariants of a rig-ready asset pack."""

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

from PIL import Image

from build_reconstruction import _path_in_pack, reconstruct
from render_articulation_check import render_joint_pose


TOP_LEVEL_FIELDS = {
    "schema_version",
    "character_id",
    "status",
    "source_sha256",
    "canvas",
    "coordinate_system",
    "parts",
    "joints",
    "neutral_pose",
    "qa_report",
    "preview_files",
}
PART_FIELDS = {
    "id",
    "name",
    "file",
    "semantic_role",
    "parent_id",
    "chain_id",
    "chain_index",
    "side",
    "instance_index",
    "z_index",
    "bbox",
    "offset",
    "pivot_local",
    "pivot_canvas",
    "attachment_to_parent",
    "deform_safe_region",
    "provenance_mask",
    "completion_mask",
    "confidence",
    "warnings",
}
JOINT_FIELDS = {
    "id",
    "parent_part_id",
    "child_part_id",
    "type",
    "pivot_canvas",
    "safe_rotation_degrees",
    "required_coverage_mask",
    "confidence",
    "warnings",
}
CONFIDENCE = {"high", "medium", "low"}
JOINT_TYPES = {"hinge", "ball", "flex", "slide", "fixed", "unknown"}
MANIFEST_STATUS = {"PASS", "NEEDS_REVIEW", "FAIL"}


def _add(checks: list[dict], check_id: str, status: str, message: str) -> None:
    checks.append({"id": check_id, "status": status, "message": message})


def _fail(checks: list[dict], check_id: str, message: str) -> None:
    _add(checks, check_id, "FAIL", message)


def _pass(checks: list[dict], check_id: str, message: str) -> None:
    _add(checks, check_id, "PASS", message)


def _warn(checks: list[dict], check_id: str, message: str) -> None:
    _add(checks, check_id, "WARN", message)


def _report(checks: list[dict]) -> dict:
    if any(check["status"] == "FAIL" for check in checks):
        status = "FAIL"
    elif any(check["status"] == "WARN" for check in checks):
        status = "NEEDS_REVIEW"
    else:
        status = "PASS"
    return {"status": status, "checks": checks}


def _report_with_manifest_status(checks: list[dict], declared_status) -> dict:
    if not isinstance(declared_status, str) or declared_status not in MANIFEST_STATUS:
        return _report(checks)
    provisional = _report(checks)["status"]
    if declared_status == "FAIL":
        _fail(checks, "manifest-status", "Manifest declares FAIL")
    elif declared_status == "NEEDS_REVIEW" and provisional == "PASS":
        _warn(
            checks,
            "manifest-status",
            "Manifest declares NEEDS_REVIEW although all other checks pass",
        )
    elif declared_status == provisional:
        _pass(checks, "manifest-status", "Manifest status agrees with validation checks")
    elif provisional == "NEEDS_REVIEW":
        _warn(
            checks,
            "manifest-status",
            f"Manifest declares {declared_status} but validation requires NEEDS_REVIEW",
        )
    else:
        _fail(
            checks,
            "manifest-status",
            f"Manifest declares {declared_status} but validation checks fail",
        )
    return _report(checks)


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _is_vector(value, length: int, integers: bool = False) -> bool:
    item_check = _is_int if integers else _is_number
    return isinstance(value, list) and len(value) == length and all(item_check(item) for item in value)


def _is_relative_path(value) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _point_in_canvas(point, width: int, height: int) -> bool:
    return _is_vector(point, 2) and 0 <= point[0] < width and 0 <= point[1] < height


def _bbox_in_canvas(bbox, width: int, height: int) -> bool:
    return (
        _is_vector(bbox, 4, integers=True)
        and bbox[2] >= 0
        and bbox[3] >= 0
        and 0 <= bbox[0] <= width
        and 0 <= bbox[1] <= height
        and bbox[0] + bbox[2] <= width
        and bbox[1] + bbox[3] <= height
    )


def _ids(items: list, item_kind: str) -> tuple[set[str], str | None]:
    values = set()
    duplicates = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            return set(), f"Every {item_kind} requires a non-empty string id"
        if item["id"] in values:
            duplicates.add(item["id"])
        values.add(item["id"])
    if duplicates:
        return values, f"Duplicate {item_kind} id: {sorted(duplicates)[0]}"
    return values, None


def _part_field_error(part: dict) -> str | None:
    missing = sorted(PART_FIELDS - set(part))
    if missing:
        return f"Part {part.get('id', '<unknown>')} is missing {missing[0]}"
    string_fields = ("id", "name", "semantic_role", "chain_id", "side")
    if any(not isinstance(part[field], str) or not part[field] for field in string_fields):
        return f"Part {part.get('id', '<unknown>')} has an invalid string field"
    if not _is_relative_path(part["file"]):
        return f"Part {part['id']} has an invalid file path"
    if not _is_relative_path(part["provenance_mask"]):
        return f"Part {part['id']} has an invalid provenance mask path"
    if not _is_relative_path(part["completion_mask"]):
        return f"Part {part['id']} has an invalid completion mask path"
    if part["parent_id"] is not None and (
        not isinstance(part["parent_id"], str) or not part["parent_id"]
    ):
        return f"Part {part['id']} has an invalid parent id"
    if not all(_is_int(part[field]) and part[field] >= 0 for field in ("chain_index", "instance_index")):
        return f"Part {part['id']} has an invalid chain or instance index"
    if not _is_int(part["z_index"]):
        return f"Part {part['id']} has an invalid z index"
    if not _is_vector(part["bbox"], 4, integers=True):
        return f"Part {part['id']} has an invalid bbox"
    if not _is_vector(part["offset"], 2, integers=True):
        return f"Part {part['id']} has an invalid offset"
    if not _is_vector(part["pivot_local"], 2):
        return f"Part {part['id']} has an invalid local pivot"
    if not _is_vector(part["pivot_canvas"], 2):
        return f"Part {part['id']} has an invalid canvas pivot"
    if part["attachment_to_parent"] is not None and not _is_vector(part["attachment_to_parent"], 2):
        return f"Part {part['id']} has an invalid attachment point"
    if not isinstance(part["deform_safe_region"], list):
        return f"Part {part['id']} has an invalid deform-safe region"
    if not isinstance(part["confidence"], str) or part["confidence"] not in CONFIDENCE:
        return f"Part {part['id']} has an invalid confidence value"
    if not isinstance(part["warnings"], list) or not all(isinstance(item, str) for item in part["warnings"]):
        return f"Part {part['id']} has invalid warnings"
    return None


def _joint_field_error(joint: dict) -> str | None:
    missing = sorted(JOINT_FIELDS - set(joint))
    if missing:
        return f"Joint {joint.get('id', '<unknown>')} is missing {missing[0]}"
    string_fields = ("id", "parent_part_id", "child_part_id", "type")
    if any(not isinstance(joint[field], str) or not joint[field] for field in string_fields):
        return f"Joint {joint.get('id', '<unknown>')} has an invalid string field"
    if joint["type"] not in JOINT_TYPES:
        return f"Joint {joint['id']} has an invalid type"
    if not _is_relative_path(joint["required_coverage_mask"]):
        return f"Joint {joint['id']} has an invalid coverage mask path"
    if not _is_vector(joint["pivot_canvas"], 2):
        return f"Joint {joint['id']} has an invalid canvas pivot"
    if not _is_vector(joint["safe_rotation_degrees"], 2) or joint["safe_rotation_degrees"][0] > joint["safe_rotation_degrees"][1]:
        return f"Joint {joint['id']} has an invalid rotation range"
    if not isinstance(joint["confidence"], str) or joint["confidence"] not in CONFIDENCE:
        return f"Joint {joint['id']} has an invalid confidence value"
    if not isinstance(joint["warnings"], list) or not all(isinstance(item, str) for item in joint["warnings"]):
        return f"Joint {joint['id']} has invalid warnings"
    return None


def _parent_graph_error(parts: list[dict]) -> str | None:
    parents = {part["id"]: part["parent_id"] for part in parts}
    state = {part_id: 0 for part_id in parents}
    for part_id in parents:
        if state[part_id] != 0:
            continue
        stack = [(part_id, False)]
        while stack:
            current_id, exiting = stack.pop()
            if exiting:
                state[current_id] = 2
                continue
            if state[current_id] == 2:
                continue
            if state[current_id] == 1:
                return f"Parent graph contains a cycle at {current_id}"
            state[current_id] = 1
            stack.append((current_id, True))
            parent_id = parents[current_id]
            if parent_id is None:
                continue
            if state[parent_id] == 1:
                return f"Parent graph contains a cycle at {parent_id}"
            if state[parent_id] == 0:
                stack.append((parent_id, False))
    return None


def _open_rgba(path: Path) -> tuple[Image.Image | None, str | None]:
    try:
        with Image.open(path) as opened:
            if opened.mode != "RGBA":
                return None, "must be RGBA"
            return opened.copy(), None
    except (OSError, ValueError) as error:
        return None, str(error)


def _open_binary_mask(path: Path) -> tuple[Image.Image | None, str | None]:
    try:
        with Image.open(path) as opened:
            if opened.mode not in {"1", "L"}:
                return None, "must use 1-bit or L mode"
            mask = opened.convert("L")
    except (OSError, ValueError) as error:
        return None, str(error)
    if any(value not in (0, 255) for value in mask.get_flattened_data()):
        return None, "must be binary (0 or 255)"
    return mask, None


def _image_equal(left: Image.Image, right: Image.Image) -> bool:
    return (
        left.mode == right.mode
        and left.size == right.size
        and list(left.get_flattened_data()) == list(right.get_flattened_data())
    )


def _local_padding(layer: Image.Image) -> tuple[int, int, int, int] | None:
    bbox = layer.getchannel("A").getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    return left, top, layer.width - right, layer.height - bottom


def _valid_top_level(manifest: dict, checks: list[dict]) -> bool:
    missing = sorted(TOP_LEVEL_FIELDS - set(manifest))
    if missing:
        _fail(checks, "top-level-fields", f"Manifest is missing {missing[0]}")
        return False
    if not isinstance(manifest["schema_version"], str) or not manifest["schema_version"]:
        _fail(checks, "top-level-fields", "schema_version must be a non-empty string")
        return False
    if not isinstance(manifest["character_id"], str) or not manifest["character_id"]:
        _fail(checks, "top-level-fields", "character_id must be a non-empty string")
        return False
    if not isinstance(manifest["status"], str) or manifest["status"] not in MANIFEST_STATUS:
        _fail(checks, "top-level-fields", "status must be PASS, NEEDS_REVIEW, or FAIL")
        return False
    if not isinstance(manifest["source_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", manifest["source_sha256"]):
        _fail(checks, "top-level-fields", "source_sha256 must be a lowercase SHA-256 hex digest")
        return False
    canvas = manifest["canvas"]
    if not isinstance(canvas, dict) or not _is_int(canvas.get("width")) or not _is_int(canvas.get("height")) or canvas["width"] <= 0 or canvas["height"] <= 0:
        _fail(checks, "top-level-fields", "canvas width and height must be positive integers")
        return False
    coordinate_system = manifest["coordinate_system"]
    if coordinate_system != {"unit": "pixel", "origin": "top_left", "x_axis": "right", "y_axis": "down"}:
        _fail(checks, "top-level-fields", "coordinate_system must use top-left pixel coordinates")
        return False
    if not isinstance(manifest["parts"], list) or not isinstance(manifest["joints"], list):
        _fail(checks, "top-level-fields", "parts and joints must be arrays")
        return False
    if not isinstance(manifest["neutral_pose"], dict):
        _fail(checks, "top-level-fields", "neutral_pose must be an object")
        return False
    if not _is_relative_path(manifest["qa_report"]):
        _fail(checks, "top-level-fields", "qa_report must be a relative path")
        return False
    previews = manifest["preview_files"]
    if not isinstance(previews, dict) or not _is_relative_path(previews.get("neutral")) or not _is_relative_path(previews.get("articulation")):
        _fail(checks, "top-level-fields", "preview file paths must be relative")
        return False
    _pass(checks, "top-level-fields", "Required manifest fields and enums are valid")
    return True


def _validate_structure(manifest: dict, checks: list[dict]) -> bool:
    if not _valid_top_level(manifest, checks):
        return False
    if not manifest["parts"]:
        _fail(checks, "part-fields", "At least one part is required")
        return False
    part_ids, part_id_error = _ids(manifest["parts"], "part")
    if part_id_error:
        _fail(checks, "part-ids", part_id_error)
        return False
    _pass(checks, "part-ids", "Part ids are unique")
    for part in manifest["parts"]:
        error = _part_field_error(part)
        if error:
            _fail(checks, "part-fields", error)
            return False
    _pass(checks, "part-fields", "Part fields and enums are valid")

    joint_ids, joint_id_error = _ids(manifest["joints"], "joint")
    if joint_id_error:
        _fail(checks, "joint-ids", joint_id_error)
        return False
    _pass(checks, "joint-ids", "Joint ids are unique")
    for joint in manifest["joints"]:
        error = _joint_field_error(joint)
        if error:
            _fail(checks, "joint-fields", error)
            return False
    _pass(checks, "joint-fields", "Joint fields and enums are valid")

    missing_parent = next(
        (part["parent_id"] for part in manifest["parts"] if part["parent_id"] is not None and part["parent_id"] not in part_ids),
        None,
    )
    if missing_parent:
        _fail(checks, "parent-references", f"Unknown parent part id: {missing_parent}")
        return False
    _pass(checks, "parent-references", "Parent references are valid")
    graph_error = _parent_graph_error(manifest["parts"])
    if graph_error:
        _fail(checks, "parent-graph", graph_error)
        return False
    _pass(checks, "parent-graph", "Parent graph is acyclic")

    for joint in manifest["joints"]:
        if joint["parent_part_id"] not in part_ids or joint["child_part_id"] not in part_ids:
            _fail(checks, "joint-references", f"Joint {joint['id']} references an unknown part")
            return False
        if joint["parent_part_id"] == joint["child_part_id"]:
            _fail(checks, "joint-references", f"Joint {joint['id']} cannot join a part to itself")
            return False
        child = next(part for part in manifest["parts"] if part["id"] == joint["child_part_id"])
        if child["parent_id"] != joint["parent_part_id"]:
            _fail(checks, "joint-references", f"Joint {joint['id']} disagrees with child parent_id")
            return False
        if child["attachment_to_parent"] != joint["pivot_canvas"] or child["pivot_canvas"] != joint["pivot_canvas"]:
            _fail(checks, "joint-references", f"Joint {joint['id']} pivot disagrees with child attachment or pivot")
            return False
    _pass(checks, "joint-references", "Joint part references are valid")

    neutral_pose = manifest["neutral_pose"]
    draw_order = neutral_pose.get("draw_order")
    if not isinstance(draw_order, list) or not all(isinstance(part_id, str) for part_id in draw_order):
        _fail(checks, "draw-order", "neutral_pose.draw_order must contain part ids")
        return False
    if set(draw_order) != part_ids or len(draw_order) != len(part_ids):
        _fail(checks, "draw-order", "neutral_pose.draw_order must list every part exactly once")
        return False
    transforms = neutral_pose.get("transforms")
    if not isinstance(transforms, dict) or set(transforms) != part_ids:
        _fail(checks, "neutral-transforms", "neutral_pose.transforms must define every part")
        return False
    for part_id in part_ids:
        transform = transforms[part_id]
        if not isinstance(transform, dict) or set(transform) != {"translation", "rotation_degrees", "scale"}:
            _fail(checks, "neutral-transforms", f"Part {part_id} has an invalid neutral transform")
            return False
        if not _is_vector(transform["translation"], 2) or not _is_number(transform["rotation_degrees"]) or not _is_vector(transform["scale"], 2):
            _fail(checks, "neutral-transforms", f"Part {part_id} has an invalid neutral transform value")
            return False
        if (
            transform["translation"] != [0, 0]
            or transform["rotation_degrees"] != 0
            or transform["scale"] != [1, 1]
        ):
            _fail(
                checks,
                "neutral-transforms",
                f"Part {part_id} has an unsupported non-identity neutral transform",
            )
            return False
    _pass(checks, "draw-order", "Neutral draw order references every part once")
    _pass(checks, "neutral-transforms", "Neutral transforms are complete")
    return True


def _validate_declared_canvas_bounds(manifest: dict, checks: list[dict]) -> bool:
    width = manifest["canvas"]["width"]
    height = manifest["canvas"]["height"]
    for part in manifest["parts"]:
        if not _bbox_in_canvas(part["bbox"], width, height):
            _fail(checks, "canvas-bounds", f"Part {part['id']} bbox is outside the canvas")
            return False
        if not _point_in_canvas(part["pivot_canvas"], width, height):
            _fail(checks, "canvas-bounds", f"Part {part['id']} pivot is outside the canvas")
            return False
        if part["attachment_to_parent"] is not None and not _point_in_canvas(part["attachment_to_parent"], width, height):
            _fail(checks, "canvas-bounds", f"Part {part['id']} attachment is outside the canvas")
            return False
    for joint in manifest["joints"]:
        if not _point_in_canvas(joint["pivot_canvas"], width, height):
            _fail(checks, "canvas-bounds", f"Joint {joint['id']} pivot is outside the canvas")
            return False
    return True


def _validate_asset_files(pack: Path, manifest: dict, checks: list[dict]) -> bool:
    paths = [
        pack / "source" / "original.png", pack / "source" / "normalized.png",
        pack / "plan" / "source-inspection.json", pack / "plan" / "separation-plan.json", pack / "plan" / "separation-plan.png",
        pack / manifest["preview_files"]["neutral"], pack / manifest["preview_files"]["articulation"],
    ]
    for part in manifest["parts"]:
        paths.extend(pack / part[field] for field in ("file", "provenance_mask", "completion_mask"))
    for joint in manifest["joints"]:
        paths.append(pack / joint["required_coverage_mask"])
    missing = next((path for path in paths if not path.is_file()), None)
    if missing is not None:
        _fail(checks, "asset-files", f"Required asset is missing: {missing.relative_to(pack)}")
        return False
    _pass(checks, "asset-files", "All required source, plan, layer, mask, and preview artifacts exist")
    return True


def _validate_source_and_plan(pack: Path, manifest: dict, checks: list[dict]) -> bool:
    original_path = pack / "source" / "original.png"
    if hashlib.sha256(original_path.read_bytes()).hexdigest() != manifest["source_sha256"]:
        _fail(checks, "source-integrity", "source_sha256 does not match source/original.png")
        return False
    original, error = _open_rgba(original_path)
    normalized, normalized_error = _open_rgba(pack / "source" / "normalized.png")
    if error or normalized_error or not _image_equal(original, normalized):
        _fail(checks, "source-integrity", "normalized source must be the exact RGBA conversion of original source")
        return False
    try:
        plan = json.loads((pack / "plan" / "separation-plan.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(checks, "plan-review", f"Could not read separation plan: {error}")
        return False
    review_gate = plan.get("review_gate", {})
    if review_gate.get("status") not in {"APPROVED", "APPROVED_WITH_LIMITATIONS"} or review_gate.get("evaluated_before_extraction") is not True:
        _fail(checks, "plan-review", "Plan review must be approved and evaluated before extraction")
        return False
    _pass(checks, "source-integrity", "Original checksum and normalized RGBA source match")
    _pass(checks, "plan-review", "Approved separation plan records pre-extraction review")
    return True


def _load_images(pack: Path, manifest: dict, checks: list[dict]) -> tuple[Image.Image | None, dict[str, Image.Image], dict[str, Image.Image], dict[str, Image.Image]]:
    source, error = _open_rgba(pack / "source" / "normalized.png")
    if error:
        _fail(checks, "source-image", f"source/normalized.png {error}")
        return None, {}, {}, {}
    width = manifest["canvas"]["width"]
    height = manifest["canvas"]["height"]
    if source.size != (width, height):
        _fail(checks, "source-image", "source/normalized.png dimensions do not match the canvas")
        return None, {}, {}, {}
    _pass(checks, "source-image", "Normalized source is RGBA and matches the canvas")

    layers: dict[str, Image.Image] = {}
    provenance: dict[str, Image.Image] = {}
    completion: dict[str, Image.Image] = {}
    for part in manifest["parts"]:
        part_id = part["id"]
        layer, layer_error = _open_rgba(pack / part["file"])
        if layer_error:
            _fail(checks, "part-images", f"Part {part_id} image {layer_error}")
            return None, {}, {}, {}
        provenance_mask, provenance_error = _open_binary_mask(pack / part["provenance_mask"])
        if provenance_error:
            _fail(checks, "part-masks", f"Part {part_id} provenance mask {provenance_error}")
            return None, {}, {}, {}
        completion_mask, completion_error = _open_binary_mask(pack / part["completion_mask"])
        if completion_error:
            _fail(checks, "part-masks", f"Part {part_id} completion mask {completion_error}")
            return None, {}, {}, {}
        if provenance_mask.size != layer.size or completion_mask.size != layer.size:
            _fail(checks, "part-masks", f"Part {part_id} masks must match its cropped layer size")
            return None, {}, {}, {}
        layers[part_id] = layer
        provenance[part_id] = provenance_mask
        completion[part_id] = completion_mask
    _pass(checks, "part-images", "All part images are RGBA")
    _pass(checks, "part-masks", "Part masks are binary and match their cropped layer sizes")
    return source, layers, provenance, completion


def _validate_actual_canvas_bounds(manifest: dict, layers: dict[str, Image.Image], checks: list[dict]) -> bool:
    width = manifest["canvas"]["width"]
    height = manifest["canvas"]["height"]
    for part in manifest["parts"]:
        layer = layers[part["id"]]
        offset_x, offset_y = part["offset"]
        if offset_x < 0 or offset_y < 0 or offset_x + layer.width > width or offset_y + layer.height > height:
            _fail(checks, "canvas-bounds", f"Part {part['id']} cropped layer is outside the canvas")
            return False
        pivot_x, pivot_y = part["pivot_local"]
        if not (0 <= pivot_x < layer.width and 0 <= pivot_y < layer.height):
            _fail(checks, "canvas-bounds", f"Part {part['id']} local pivot is outside its cropped layer")
            return False
        if part["pivot_canvas"] != [offset_x + pivot_x, offset_y + pivot_y]:
            _fail(checks, "canvas-bounds", f"Part {part['id']} local and canvas pivots disagree")
            return False
    _pass(checks, "canvas-bounds", "Declared geometry and cropped layers are within canvas bounds")
    return True


def _validate_masks_and_provenance(source: Image.Image, manifest: dict, layers: dict[str, Image.Image], provenance: dict[str, Image.Image], completion: dict[str, Image.Image], checks: list[dict]) -> None:
    overlap_error = None
    completeness_error = None
    provenance_error = None
    ownership_counts = [0] * (source.width * source.height)
    for part in manifest["parts"]:
        part_id = part["id"]
        provenance_values = list(provenance[part_id].get_flattened_data())
        completion_values = list(completion[part_id].get_flattened_data())
        layer_values = list(layers[part_id].get_flattened_data())
        if overlap_error is None and any(left and right for left, right in zip(provenance_values, completion_values)):
            overlap_error = f"Part {part_id} provenance and completion masks overlap"
        offset_x, offset_y = part["offset"]
        for index, (source_selected, completion_selected) in enumerate(
            zip(provenance_values, completion_values)
        ):
            local_x = index % layers[part_id].width
            local_y = index // layers[part_id].width
            classified_once = (source_selected == 255) + (completion_selected == 255) == 1
            opaque = layer_values[index][3] > 0
            if completeness_error is None and opaque != classified_once:
                completeness_error = (
                    f"Part {part_id} layer alpha and masks disagree at local "
                    f"[{local_x}, {local_y}]"
                )
            if not source_selected:
                continue
            canvas_x = offset_x + local_x
            canvas_y = offset_y + local_y
            ownership_counts[canvas_y * source.width + canvas_x] += 1
            source_pixel = source.getpixel((canvas_x, canvas_y))
            if provenance_error is None and layer_values[index] != source_pixel:
                provenance_error = f"Part {part_id} provenance pixel differs from source at local [{local_x}, {local_y}]"
    if overlap_error:
        _fail(checks, "mask-overlap", overlap_error)
    else:
        _pass(checks, "mask-overlap", "Provenance and completion masks do not overlap")
    if completeness_error:
        _fail(checks, "layer-mask-completeness", completeness_error)
    else:
        _pass(
            checks,
            "layer-mask-completeness",
            "Every opaque layer pixel is classified by exactly one part mask",
        )
    if provenance_error:
        _fail(checks, "provenance-source", provenance_error)
    else:
        _pass(checks, "provenance-source", "Provenance pixels exactly match the normalized source")
    ownership_error = None
    for index, source_pixel in enumerate(source.get_flattened_data()):
        if source_pixel[3] > 0 and ownership_counts[index] != 1:
            canvas_x = index % source.width
            canvas_y = index // source.width
            ownership_error = (
                f"Normalized source pixel [{canvas_x}, {canvas_y}] has "
                f"{ownership_counts[index]} provenance owners"
            )
            break
    if ownership_error:
        _fail(checks, "provenance-ownership", ownership_error)
    else:
        _pass(
            checks,
            "provenance-ownership",
            "Every opaque normalized-source pixel has exactly one provenance owner",
        )


def _validate_padding(manifest: dict, layers: dict[str, Image.Image], checks: list[dict]) -> None:
    canvas = manifest["canvas"]
    required_padding = max(2, math.ceil(0.005 * max(canvas["width"], canvas["height"])))
    inadequate = []
    for part in manifest["parts"]:
        padding = _local_padding(layers[part["id"]])
        if padding is not None and min(padding) < required_padding:
            inadequate.append(part["id"])
    if inadequate:
        _warn(checks, "crop-padding", f"Insufficient transparent padding ({required_padding}px) on: {', '.join(inadequate)}")
    else:
        _pass(checks, "crop-padding", f"All visible crops have at least {required_padding}px transparent padding")


def _validate_reconstruction(pack: Path, manifest: dict, source: Image.Image, checks: list[dict]) -> None:
    try:
        reconstructed = reconstruct(pack, manifest)
    except (OSError, ValueError, KeyError) as error:
        _fail(checks, "neutral-reconstruction", str(error))
        return
    if _image_equal(reconstructed, source):
        _pass(checks, "neutral-reconstruction", "Neutral reconstruction exactly matches source/normalized.png")
    else:
        _fail(checks, "neutral-reconstruction", "Neutral reconstruction differs from source/normalized.png")


def _validate_confidence(manifest: dict, checks: list[dict]) -> None:
    low_confidence = [part["id"] for part in manifest["parts"] if part["confidence"] == "low"]
    low_confidence.extend(joint["id"] for joint in manifest["joints"] if joint["confidence"] == "low")
    if low_confidence:
        _warn(checks, "confidence", f"Low-confidence topology requires review: {', '.join(low_confidence)}")
    else:
        _pass(checks, "confidence", "No topology decisions have low confidence")


def _validate_slide_joints(manifest: dict, checks: list[dict]) -> None:
    slide_ids = [joint["id"] for joint in manifest["joints"] if joint["type"] == "slide"]
    if slide_ids:
        _warn(
            checks,
            "slide-joints",
            "Slide joints require external translation review: " + ", ".join(slide_ids),
        )
    else:
        _pass(checks, "slide-joints", "No slide joints require external translation review")


def _validate_joint_coverage(pack: Path, manifest: dict, checks: list[dict]) -> None:
    width = manifest["canvas"]["width"]
    height = manifest["canvas"]["height"]
    coverage_masks: dict[str, Image.Image] = {}
    for joint in manifest["joints"]:
        mask, error = _open_binary_mask(pack / joint["required_coverage_mask"])
        if error:
            _fail(checks, "joint-coverage-mask", f"Joint {joint['id']} coverage mask {error}")
            return
        if mask.size != (width, height):
            _fail(checks, "joint-coverage-mask", f"Joint {joint['id']} coverage mask must use full canvas dimensions")
            return
        coverage_masks[joint["id"]] = mask
    _pass(checks, "joint-coverage-mask", "Joint coverage masks are binary and full canvas")

    missing_coverage = None
    for joint in manifest["joints"]:
        mask_values = list(coverage_masks[joint["id"]].get_flattened_data())
        if not any(mask_values):
            _warn(checks, "joint-coverage", f"Joint {joint['id']} coverage mask is empty")
            return
        pivot_x, pivot_y = joint["pivot_canvas"]
        if not any(
            selected and abs(index % width - pivot_x) <= 16 and abs(index // width - pivot_y) <= 16
            for index, selected in enumerate(mask_values)
        ):
            _warn(checks, "joint-coverage", f"Joint {joint['id']} coverage mask is not localized near its pivot")
            return
        minimum, maximum = joint["safe_rotation_degrees"]
        for angle in (minimum, maximum):
            try:
                posed = render_joint_pose(pack, manifest, joint["id"], angle)
            except (OSError, ValueError, KeyError) as error:
                _fail(checks, "joint-coverage", str(error))
                return
            if missing_coverage is not None:
                continue
            for index, selected in enumerate(mask_values):
                if selected and posed.getpixel((index % width, index // width))[3] == 0:
                    missing_coverage = f"Joint {joint['id']} leaves required coverage empty at {angle:g} degrees"
                    break
    if missing_coverage:
        _warn(checks, "joint-coverage", missing_coverage)
    else:
        _pass(checks, "joint-coverage", "Required coverage remains opaque at every declared angle")


def validate_pack(pack: Path, manifest_path: Path) -> dict:
    """Return a structured PASS, NEEDS_REVIEW, or FAIL report for *pack*."""
    pack = Path(pack)
    manifest_path = _path_in_pack(pack, Path(manifest_path))
    checks: list[dict] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail(checks, "manifest", f"Could not read manifest: {error}")
        return _report(checks)
    if not isinstance(manifest, dict):
        _fail(checks, "manifest", "Manifest root must be an object")
        return _report(checks)
    if not _validate_structure(manifest, checks):
        return _report_with_manifest_status(checks, manifest.get("status"))
    if not _validate_declared_canvas_bounds(manifest, checks):
        return _report_with_manifest_status(checks, manifest.get("status"))
    if not _validate_asset_files(pack, manifest, checks):
        return _report_with_manifest_status(checks, manifest.get("status"))
    if not _validate_source_and_plan(pack, manifest, checks):
        return _report_with_manifest_status(checks, manifest.get("status"))
    source, layers, provenance, completion = _load_images(pack, manifest, checks)
    if source is None:
        return _report_with_manifest_status(checks, manifest.get("status"))
    if not _validate_actual_canvas_bounds(manifest, layers, checks):
        return _report_with_manifest_status(checks, manifest.get("status"))
    _validate_masks_and_provenance(source, manifest, layers, provenance, completion, checks)
    _validate_padding(manifest, layers, checks)
    _validate_reconstruction(pack, manifest, source, checks)
    _validate_confidence(manifest, checks)
    _validate_slide_joints(manifest, checks)
    _validate_joint_coverage(pack, manifest, checks)
    return _report_with_manifest_status(checks, manifest.get("status"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a rig-ready asset pack.")
    parser.add_argument("pack", type=Path, metavar="PACK")
    parser.add_argument("--manifest", type=Path, required=True, metavar="PATH")
    parser.add_argument("--report", type=Path, required=True, metavar="PATH")
    args = parser.parse_args()

    report = validate_pack(args.pack, args.manifest)
    report_path = _path_in_pack(args.pack, args.report)
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        print(f"Could not write report: {error}", file=sys.stderr)
        sys.exit(1)
    sys.exit({"PASS": 0, "NEEDS_REVIEW": 2, "FAIL": 1}[report["status"]])


if __name__ == "__main__":
    main()
