#!/usr/bin/env python3
"""Slice a game asset sprite sheet using bbox entries from a JSON manifest."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


BBox = tuple[int, int, int, int]


def fail(message: str) -> None:
	print(f"error: {message}", file=sys.stderr)
	raise SystemExit(1)


def load_manifest(path: Path) -> dict[str, Any]:
	try:
		with path.open("r", encoding="utf-8") as file:
			data = json.load(file)
	except FileNotFoundError:
		fail(f"manifest not found: {path}")
	except json.JSONDecodeError as exc:
		fail(f"manifest is not valid JSON: {exc}")
	if not isinstance(data, dict):
		fail("manifest root must be a JSON object")
	if not isinstance(data.get("assets"), list):
		fail("manifest must contain an assets array")
	return data


def sanitize_name(name: str) -> str:
	stem = Path(name).stem
	stem = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem).strip("_").lower()
	return stem or "asset"


def parse_bbox(asset: dict[str, Any], sheet_size: tuple[int, int]) -> BBox:
	raw = asset.get("bbox_px")
	if raw is None:
		fail(f"asset {asset.get('name', '<unnamed>')} is missing bbox_px")
	if isinstance(raw, dict):
		if {"x", "y", "width", "height"} <= raw.keys():
			values = [raw["x"], raw["y"], raw["width"], raw["height"]]
		elif {"x", "y", "w", "h"} <= raw.keys():
			values = [raw["x"], raw["y"], raw["w"], raw["h"]]
		else:
			fail(f"asset {asset.get('name', '<unnamed>')} bbox_px object must use x/y/width/height")
	elif isinstance(raw, list) and len(raw) == 4:
		values = raw
	else:
		fail(f"asset {asset.get('name', '<unnamed>')} bbox_px must be [x, y, width, height]")

	try:
		x, y, width, height = [int(round(float(value))) for value in values]
	except (TypeError, ValueError):
		fail(f"asset {asset.get('name', '<unnamed>')} bbox_px contains a non-numeric value")

	if width <= 0 or height <= 0:
		fail(f"asset {asset.get('name', '<unnamed>')} bbox_px width and height must be positive")

	sheet_width, sheet_height = sheet_size
	if x < 0 or y < 0 or x + width > sheet_width or y + height > sheet_height:
		fail(
			f"asset {asset.get('name', '<unnamed>')} bbox_px {values} is outside "
			f"sheet size {sheet_width}x{sheet_height}"
		)
	return (x, y, x + width, y + height)


def alpha_bounds(image: Image.Image) -> BBox | None:
	alpha = image.getchannel("A")
	box = alpha.getbbox()
	if box is None:
		return None
	return tuple(int(value) for value in box)  # type: ignore[return-value]


def expand_box(box: BBox, padding: int, bounds: tuple[int, int]) -> BBox:
	x0, y0, x1, y1 = box
	width, height = bounds
	return (
		max(0, x0 - padding),
		max(0, y0 - padding),
		min(width, x1 + padding),
		min(height, y1 + padding),
	)


def rects_overlap(a: BBox, b: BBox) -> bool:
	return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def check_overlaps(entries: list[dict[str, Any]]) -> None:
	for index, left in enumerate(entries):
		for right in entries[index + 1 :]:
			if rects_overlap(left["crop_rect"], right["crop_rect"]):
				fail(
					"crop regions overlap after padding: "
					f"{left['name']} {left['crop_rect']} and {right['name']} {right['crop_rect']}"
				)


def checkerboard(size: tuple[int, int], square: int = 12) -> Image.Image:
	width, height = size
	base = Image.new("RGBA", size, (232, 232, 232, 255))
	draw = ImageDraw.Draw(base)
	for y in range(0, height, square):
		for x in range(0, width, square):
			if (x // square + y // square) % 2:
				draw.rectangle((x, y, x + square - 1, y + square - 1), fill=(204, 204, 204, 255))
	return base


def make_review_sheet(entries: list[dict[str, Any]], out_path: Path) -> None:
	if not entries:
		return
	font = ImageFont.load_default()
	cell_width = 220
	cell_height = 250
	columns = min(4, max(1, math.ceil(math.sqrt(len(entries)))))
	rows = math.ceil(len(entries) / columns)
	sheet = Image.new("RGBA", (columns * cell_width, rows * cell_height), (28, 28, 32, 255))
	draw = ImageDraw.Draw(sheet)

	for index, entry in enumerate(entries):
		col = index % columns
		row = index // columns
		origin_x = col * cell_width
		origin_y = row * cell_height
		draw.rectangle((origin_x, origin_y, origin_x + cell_width - 1, origin_y + cell_height - 1), outline=(74, 74, 82, 255))
		preview_area = (cell_width - 24, cell_height - 58)
		thumb = Image.open(entry["output_path"]).convert("RGBA")
		thumb.thumbnail(preview_area, Image.Resampling.LANCZOS)
		bg = checkerboard(preview_area)
		paste_x = origin_x + 12 + (preview_area[0] - thumb.width) // 2
		paste_y = origin_y + 12 + (preview_area[1] - thumb.height) // 2
		sheet.alpha_composite(bg, (origin_x + 12, origin_y + 12))
		sheet.alpha_composite(thumb, (paste_x, paste_y))
		label = f"{entry['name']}  {entry['size'][0]}x{entry['size'][1]}"
		draw.text((origin_x + 12, origin_y + cell_height - 38), label[:34], fill=(245, 245, 245, 255), font=font)
		draw.text((origin_x + 12, origin_y + cell_height - 22), entry["strategy"][:34], fill=(184, 198, 255, 255), font=font)

	sheet.save(out_path)


def slice_assets(sheet_path: Path, manifest_path: Path, out_dir: Path, trim_alpha: bool, padding: int) -> list[dict[str, Any]]:
	if padding < 0:
		fail("padding must be zero or positive")
	manifest = load_manifest(manifest_path)
	try:
		sheet = Image.open(sheet_path).convert("RGBA")
	except FileNotFoundError:
		fail(f"sheet not found: {sheet_path}")
	except OSError as exc:
		fail(f"cannot open sheet: {exc}")

	out_dir.mkdir(parents=True, exist_ok=True)
	sheet_size = sheet.size
	entries: list[dict[str, Any]] = []
	seen_names: set[str] = set()

	for index, asset in enumerate(manifest["assets"]):
		if not isinstance(asset, dict):
			fail(f"assets[{index}] must be an object")
		name = sanitize_name(str(asset.get("name", f"asset_{index}")))
		if name in seen_names:
			fail(f"duplicate asset name after sanitizing: {name}")
		seen_names.add(name)

		source_rect = parse_bbox(asset, sheet_size)
		working_rect = source_rect
		if trim_alpha:
			initial_crop = sheet.crop(source_rect)
			local_alpha = alpha_bounds(initial_crop)
			if local_alpha is not None:
				working_rect = (
					source_rect[0] + local_alpha[0],
					source_rect[1] + local_alpha[1],
					source_rect[0] + local_alpha[2],
					source_rect[1] + local_alpha[3],
				)
		crop_rect = expand_box(working_rect, padding, sheet_size)
		entries.append(
			{
				"name": name,
				"source_rect": source_rect,
				"crop_rect": crop_rect,
				"strategy": str(asset.get("strategy", "slice")),
				"source_asset": asset,
			}
		)

	check_overlaps(entries)

	resolved: list[dict[str, Any]] = []
	for entry in entries:
		crop = sheet.crop(entry["crop_rect"])
		output_path = out_dir / f"{entry['name']}.png"
		crop.save(output_path)
		output_entry = {
			"name": entry["name"],
			"output_path": str(output_path),
			"source_rect": list(entry["source_rect"]),
			"crop_rect": list(entry["crop_rect"]),
			"size": [crop.width, crop.height],
			"strategy": entry["strategy"],
		}
		resolved.append(output_entry)

	manifest_out = {
		"sheet": str(sheet_path),
		"manifest": str(manifest_path),
		"trim_alpha": trim_alpha,
		"padding": padding,
		"assets": resolved,
	}
	with (out_dir / "slice_manifest.resolved.json").open("w", encoding="utf-8") as file:
		json.dump(manifest_out, file, indent=2)

	make_review_sheet(resolved, out_dir / "asset_review_sheet.png")
	return resolved


def main() -> None:
	parser = argparse.ArgumentParser(description="Slice a game asset sprite sheet using a JSON manifest.")
	parser.add_argument("--sheet", required=True, type=Path, help="Input sprite sheet PNG.")
	parser.add_argument("--manifest", required=True, type=Path, help="JSON manifest with assets[].bbox_px.")
	parser.add_argument("--out-dir", required=True, type=Path, help="Directory for sliced PNG outputs.")
	parser.add_argument("--trim-alpha", action="store_true", help="Trim transparent pixels inside each bbox before padding.")
	parser.add_argument("--padding", type=int, default=0, help="Pixels to add around the crop after optional trim.")
	args = parser.parse_args()

	assets = slice_assets(args.sheet, args.manifest, args.out_dir, args.trim_alpha, args.padding)
	print(f"sliced {len(assets)} assets into {args.out_dir}")
	print(f"review sheet: {args.out_dir / 'asset_review_sheet.png'}")


if __name__ == "__main__":
	main()
