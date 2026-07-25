#!/usr/bin/env python3
"""Reconstruct a rig pack's neutral pose from cropped RGBA layers."""

import argparse
import json
from pathlib import Path

from PIL import Image


def load_manifest(path: Path) -> dict:
    """Read a rig-ready manifest from *path*."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_part_layers(pack: Path, manifest: dict) -> dict[str, Image.Image]:
    layers: dict[str, Image.Image] = {}
    for part in manifest["parts"]:
        part_id = part["id"]
        with Image.open(pack / part["file"]) as source:
            if source.mode != "RGBA":
                raise ValueError(f"Part image must be RGBA: {part_id}")
            layers[part_id] = source.copy()
    return layers


def reconstruct(pack: Path, manifest: dict) -> Image.Image:
    """Return the neutral-pose composition on the manifest canvas."""
    pack = Path(pack)
    canvas = manifest["canvas"]
    image = Image.new("RGBA", (canvas["width"], canvas["height"]))
    parts = {part["id"]: part for part in manifest["parts"]}
    draw_order = manifest.get("neutral_pose", {}).get("draw_order")
    if draw_order is None:
        draw_order = [
            part["id"]
            for part in sorted(manifest["parts"], key=lambda part: part["z_index"])
        ]
    else:
        for part_id in draw_order:
            if part_id not in parts:
                raise ValueError("Unknown part in draw order")
    layers = _load_part_layers(pack, manifest)

    for part_id in draw_order:
        offset = tuple(parts[part_id]["offset"])
        image.alpha_composite(layers[part_id], offset)
    return image


def _path_in_pack(pack: Path, path: Path) -> Path:
    return path if path.is_absolute() else pack / path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconstruct a rig pack's neutral pose from cropped RGBA layers."
    )
    parser.add_argument("pack", type=Path, metavar="PACK")
    parser.add_argument("--manifest", type=Path, required=True, metavar="PATH")
    parser.add_argument("--output", type=Path, required=True, metavar="PATH")
    args = parser.parse_args()

    try:
        manifest = load_manifest(_path_in_pack(args.pack, args.manifest))
        output = _path_in_pack(args.pack, args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        reconstruct(args.pack, manifest).save(output, format="PNG")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
