#!/usr/bin/env python3
"""Render joint rotations and an articulation contact sheet for a rig pack."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from build_reconstruction import _load_part_layers, _path_in_pack, load_manifest, reconstruct


def _draw_order(manifest: dict) -> list[str]:
    draw_order = manifest.get("neutral_pose", {}).get("draw_order")
    if draw_order is not None:
        return draw_order
    return [
        part["id"]
        for part in sorted(manifest["parts"], key=lambda part: part["z_index"])
    ]


def _descendant_ids(parts: dict[str, dict], root_id: str) -> set[str]:
    """Return *root_id* and every descendant in the manifest parent graph."""
    descendants = {root_id}
    changed = True
    while changed:
        changed = False
        for part_id, part in parts.items():
            if part.get("parent_id") in descendants and part_id not in descendants:
                descendants.add(part_id)
                changed = True
    return descendants


def render_joint_pose(pack: Path, manifest: dict, joint_id: str, angle: float) -> Image.Image:
    """Render one joint's child part rotated by *angle* about its canvas pivot."""
    joint = next((item for item in manifest["joints"] if item["id"] == joint_id), None)
    if joint is None:
        raise ValueError("Unknown joint")
    if angle == 0:
        return reconstruct(pack, manifest)

    pack = Path(pack)
    canvas = manifest["canvas"]
    canvas_size = (canvas["width"], canvas["height"])
    parts = {part["id"]: part for part in manifest["parts"]}
    child_id = joint["child_part_id"]
    if child_id not in parts:
        raise ValueError("Unknown child part")
    layers = _load_part_layers(pack, manifest)
    descendant_ids = _descendant_ids(parts, child_id)
    subtree_canvas = Image.new("RGBA", canvas_size)
    for part_id in _draw_order(manifest):
        if part_id in descendant_ids:
            subtree_canvas.alpha_composite(layers[part_id], tuple(parts[part_id]["offset"]))
    rotated_subtree = subtree_canvas.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        center=tuple(joint["pivot_canvas"]),
        expand=False,
    )

    posed = Image.new("RGBA", canvas_size)
    for part_id in _draw_order(manifest):
        if part_id not in parts:
            raise ValueError("Unknown part in draw order")
        if part_id == child_id:
            posed.alpha_composite(rotated_subtree)
        elif part_id not in descendant_ids:
            posed.alpha_composite(layers[part_id], tuple(parts[part_id]["offset"]))
    return posed


def _label_tile(tile: Image.Image, joint_id: str, angle: float) -> Image.Image:
    labeled = tile.copy()
    label = f"{joint_id}: {angle:g}\N{DEGREE SIGN}"
    draw = ImageDraw.Draw(labeled)
    left, top, right, bottom = draw.textbbox((2, 2), label)
    draw.rectangle((left - 1, top - 1, right + 1, bottom + 1), fill=(0, 0, 0, 192))
    draw.text((2, 2), label, fill=(255, 255, 255, 255))
    return labeled


def render_contact_sheet(pack: Path, manifest: dict) -> Image.Image:
    """Return a three-column min/neutral/max articulation row for each joint."""
    canvas = manifest["canvas"]
    width, height = canvas["width"], canvas["height"]
    joints = manifest["joints"]
    sheet = Image.new("RGBA", (width * 3, height * len(joints)))
    for row, joint in enumerate(joints):
        minimum, maximum = joint["safe_rotation_degrees"]
        for column, angle in enumerate((minimum, 0, maximum)):
            tile = render_joint_pose(pack, manifest, joint["id"], angle)
            sheet.alpha_composite(
                _label_tile(tile, joint["id"], angle), (column * width, row * height)
            )
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render min, neutral, and max articulation checks for a rig pack."
    )
    parser.add_argument("pack", type=Path, metavar="PACK")
    parser.add_argument("--manifest", type=Path, required=True, metavar="PATH")
    parser.add_argument("--output", type=Path, required=True, metavar="PATH")
    args = parser.parse_args()

    try:
        manifest = load_manifest(_path_in_pack(args.pack, args.manifest))
        output = _path_in_pack(args.pack, args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        render_contact_sheet(args.pack, manifest).save(output, format="PNG")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
