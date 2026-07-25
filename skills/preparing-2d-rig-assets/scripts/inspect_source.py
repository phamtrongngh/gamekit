#!/usr/bin/env python3
"""Inspect artwork and write a lossless RGBA-normalized PNG."""

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

from PIL import Image


LOW_RESOLUTION_LIMIT = 256


def _alpha_component_count(alpha: Image.Image) -> int:
    """Return the number of 4-connected non-transparent alpha regions."""
    width, height = alpha.size
    pixels = alpha.load()
    visited: set[tuple[int, int]] = set()
    components = 0

    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0 or (x, y) in visited:
                continue
            components += 1
            visited.add((x, y))
            queue = deque([(x, y)])
            while queue:
                current_x, current_y = queue.popleft()
                for neighbor_x, neighbor_y in (
                    (current_x - 1, current_y),
                    (current_x + 1, current_y),
                    (current_x, current_y - 1),
                    (current_x, current_y + 1),
                ):
                    if (
                        0 <= neighbor_x < width
                        and 0 <= neighbor_y < height
                        and (neighbor_x, neighbor_y) not in visited
                        and pixels[neighbor_x, neighbor_y] != 0
                    ):
                        visited.add((neighbor_x, neighbor_y))
                        queue.append((neighbor_x, neighbor_y))
    return components


def inspect_source(source: Path, normalized: Path) -> dict:
    """Normalize *source* to RGBA and return deterministic inspection metadata."""
    source = Path(source)
    normalized = Path(normalized)
    source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()

    with Image.open(source) as input_image:
        rgba = input_image.convert("RGBA")

    normalized.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(normalized, format="PNG")

    width, height = rgba.size
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    alpha_bbox = list(bbox) if bbox is not None else None
    edges_touched: list[str] = []
    if bbox is not None:
        if bbox[0] == 0:
            edges_touched.append("left")
        if bbox[1] == 0:
            edges_touched.append("top")
        if bbox[2] == width:
            edges_touched.append("right")
        if bbox[3] == height:
            edges_touched.append("bottom")
    warnings: list[str] = []

    if bbox is None:
        warnings.append("EMPTY_ALPHA")
    elif edges_touched:
        warnings.append("TOUCHES_CANVAS_EDGE")
    if width < LOW_RESOLUTION_LIMIT or height < LOW_RESOLUTION_LIMIT:
        warnings.append("LOW_RESOLUTION")

    return {
        "width": width,
        "height": height,
        "mode": "RGBA",
        "alpha_bbox": alpha_bbox,
        "edges_touched": edges_touched,
        "alpha_component_count": _alpha_component_count(alpha),
        "source_sha256": source_sha256,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect source artwork and write a normalized RGBA PNG."
    )
    parser.add_argument("source", type=Path, metavar="SOURCE")
    parser.add_argument("--normalized", type=Path, required=True, metavar="PATH")
    parser.add_argument("--report", type=Path, required=True, metavar="PATH")
    args = parser.parse_args()

    try:
        report = inspect_source(args.source, args.normalized)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
