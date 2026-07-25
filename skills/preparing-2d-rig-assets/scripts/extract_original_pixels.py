#!/usr/bin/env python3
"""Extract selected source pixels without changing their RGBA values."""

import argparse
from pathlib import Path

from PIL import Image


def extract(source: Path, mask: Path, layer: Path, provenance: Path) -> None:
    """Write an RGBA layer and its binary ``L`` provenance mask.

    Selected pixels are copied verbatim from the RGBA-normalized source; they are
    deliberately not alpha-multiplied by mask values.
    """
    source = Path(source)
    mask = Path(mask)
    layer = Path(layer)
    provenance = Path(provenance)

    with Image.open(source) as source_image:
        rgba_source = source_image.convert("RGBA")
    with Image.open(mask) as mask_image:
        binary_mask = mask_image.convert("L")

    if rgba_source.size != binary_mask.size:
        raise ValueError("Source and mask dimensions must match")

    mask_data = list(binary_mask.get_flattened_data())
    if any(value not in (0, 255) for value in mask_data):
        raise ValueError("Mask must be binary (0 or 255)")

    source_data = list(rgba_source.get_flattened_data())
    output = Image.new("RGBA", rgba_source.size)
    output.putdata(
        [
            source_pixel if mask_value == 255 else (0, 0, 0, 0)
            for source_pixel, mask_value in zip(source_data, mask_data)
        ]
    )

    layer.parent.mkdir(parents=True, exist_ok=True)
    provenance.parent.mkdir(parents=True, exist_ok=True)
    output.save(layer, format="PNG")
    binary_mask.save(provenance, format="PNG")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract exact RGBA source pixels selected by a binary mask."
    )
    parser.add_argument("source", type=Path, metavar="SOURCE")
    parser.add_argument("mask", type=Path, metavar="MASK")
    parser.add_argument("--layer", type=Path, required=True, metavar="PATH")
    parser.add_argument("--provenance", type=Path, required=True, metavar="PATH")
    args = parser.parse_args()

    try:
        extract(args.source, args.mask, args.layer, args.provenance)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
