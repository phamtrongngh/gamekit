#!/usr/bin/env python3
"""Reference layer extraction helper for flattened game screenshots.

This script intentionally produces reviewable candidates, not guaranteed
production-clean assets. It uses only Pillow so it can run in lightweight
agent environments.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat


MANIFEST_NAME = "asset_manifest.json"


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def norm_box_to_pixels(box: Sequence[float], width: int, height: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    return (
        clamp(round(left * width), 0, width),
        clamp(round(top * height), 0, height),
        clamp(round(right * width), 0, width),
        clamp(round(bottom * height), 0, height),
    )


def pixel_box(box: Sequence[float], width: int, height: int, normalized: bool) -> tuple[int, int, int, int]:
    if normalized:
        return norm_box_to_pixels(box, width, height)
    left, top, right, bottom = [round(v) for v in box]
    return (
        clamp(left, 0, width),
        clamp(top, 0, height),
        clamp(right, 0, width),
        clamp(bottom, 0, height),
    )


def crop_inner_box(crop: Image.Image, box: Sequence[float]) -> tuple[int, int, int, int]:
    width, height = crop.size
    return norm_box_to_pixels(box, width, height)


def rounded_rect_mask(size: tuple[int, int], radius_ratio: float = 0.18) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    radius = max(1, round(min(width, height) * radius_ratio))
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(max(1, round(min(width, height) * 0.01))))


def ellipse_mask(size: tuple[int, int]) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width - 1, height - 1), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(max(1, round(min(width, height) * 0.01))))


def alpha_from_dark_background(crop: Image.Image, threshold: int = 42, softness: int = 24) -> Image.Image:
    """Approximate alpha by making very dark pixels transparent.

    This is useful for bright UI/logo crops on dark fantasy backgrounds. It is
    intentionally conservative and should be user-reviewed.
    """

    rgb = crop.convert("RGB")
    gray = rgb.convert("L")
    alpha = Image.new("L", crop.size, 255)
    src = gray.load()
    dst = alpha.load()
    width, height = crop.size
    for y in range(height):
        for x in range(width):
            value = src[x, y]
            if value <= threshold:
                dst[x, y] = 0
            elif value < threshold + softness:
                dst[x, y] = round(255 * (value - threshold) / softness)
    return alpha.filter(ImageFilter.GaussianBlur(1))


def apply_alpha(crop: Image.Image, alpha_mode: str | None) -> Image.Image:
    if not alpha_mode or alpha_mode == "none":
        return crop.convert("RGBA")
    result = crop.convert("RGBA")
    if alpha_mode == "rounded_rect":
        result.putalpha(rounded_rect_mask(result.size))
    elif alpha_mode == "ellipse":
        result.putalpha(ellipse_mask(result.size))
    elif alpha_mode == "dark_background":
        result.putalpha(alpha_from_dark_background(result))
    else:
        raise ValueError(f"Unsupported alpha mode: {alpha_mode}")
    return result


def erase_regions(crop: Image.Image, regions: Iterable[Sequence[float]]) -> Image.Image:
    """Roughly remove text/icons from a crop using a blurred local patch."""

    result = crop.convert("RGBA")
    for region in regions:
        left, top, right, bottom = crop_inner_box(result, region)
        if right <= left or bottom <= top:
            continue

        pad_x = max(8, round((right - left) * 0.20))
        pad_y = max(8, round((bottom - top) * 0.30))
        sample_box = (
            clamp(left - pad_x, 0, result.width),
            clamp(top - pad_y, 0, result.height),
            clamp(right + pad_x, 0, result.width),
            clamp(bottom + pad_y, 0, result.height),
        )
        sample = result.crop(sample_box)
        blurred = sample.filter(ImageFilter.GaussianBlur(max(6, round(min(sample.size) * 0.12))))
        patch = blurred.crop((left - sample_box[0], top - sample_box[1], right - sample_box[0], bottom - sample_box[1]))

        feather = Image.new("L", (right - left, bottom - top), 0)
        draw = ImageDraw.Draw(feather)
        radius = max(4, round(min(feather.size) * 0.20))
        draw.rounded_rectangle((0, 0, feather.width - 1, feather.height - 1), radius=radius, fill=255)
        feather = feather.filter(ImageFilter.GaussianBlur(max(2, radius // 2)))
        result.paste(patch, (left, top), feather)
    return result


def export_asset(source: Image.Image, asset: dict, out_dir: Path, normalized: bool) -> Path:
    box = pixel_box(asset["bbox"], source.width, source.height, normalized)
    crop = source.crop(box).convert("RGBA")

    if asset.get("erase_regions"):
        crop = erase_regions(crop, asset["erase_regions"])

    crop = apply_alpha(crop, asset.get("alpha"))

    name = asset["name"]
    path = out_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    crop.save(path)
    return path


def make_background_candidate(source: Image.Image, asset: dict, out_dir: Path, normalized: bool) -> Path:
    result = source.convert("RGBA")
    for region in asset.get("erase_source_regions", []):
        left, top, right, bottom = pixel_box(region, source.width, source.height, normalized)
        if right <= left or bottom <= top:
            continue
        target = result.crop((left, top, right, bottom))
        blurred = target.filter(ImageFilter.GaussianBlur(max(12, round(min(target.size) * 0.18))))
        mask = Image.new("L", target.size, 0)
        draw = ImageDraw.Draw(mask)
        radius = max(8, round(min(target.size) * 0.08))
        draw.rounded_rectangle((0, 0, target.width - 1, target.height - 1), radius=radius, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(max(6, radius)))
        result.paste(blurred, (left, top), mask)

    out_path = out_dir / asset["name"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(out_path)
    return out_path


def mean_brightness(path: Path) -> int:
    image = Image.open(path).convert("L").resize((1, 1))
    return round(ImageStat.Stat(image).mean[0])


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def make_review_sheet(assets_dir: Path, out_path: Path, manifest_path: Path | None = None) -> None:
    files = sorted(
        p for p in assets_dir.rglob("*")
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not files:
        raise SystemExit(f"No image assets found in {assets_dir}")

    metadata = {}
    if manifest_path and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        metadata = {asset["name"]: asset for asset in manifest.get("assets", [])}

    thumb_w, thumb_h = 260, 180
    label_h = 74
    margin = 18
    cols = 2
    rows = math.ceil(len(files) / cols)
    sheet = Image.new("RGB", (cols * (thumb_w + margin) + margin, rows * (thumb_h + label_h + margin) + margin), "#20202a")
    draw = ImageDraw.Draw(sheet)
    font = load_font(16)
    small = load_font(12)

    for index, path in enumerate(files):
        col = index % cols
        row = index // cols
        x = margin + col * (thumb_w + margin)
        y = margin + row * (thumb_h + label_h + margin)
        cell = Image.new("RGB", (thumb_w, thumb_h), "#2c2c38")
        img = Image.open(path).convert("RGBA")
        img.thumbnail((thumb_w - 18, thumb_h - 18), Image.Resampling.LANCZOS)
        px = (thumb_w - img.width) // 2
        py = (thumb_h - img.height) // 2
        checker = Image.new("RGB", img.size, "#393944")
        cdraw = ImageDraw.Draw(checker)
        step = 12
        for yy in range(0, img.height, step):
            for xx in range(0, img.width, step):
                if (xx // step + yy // step) % 2 == 0:
                    cdraw.rectangle((xx, yy, xx + step - 1, yy + step - 1), fill="#4a4a56")
        checker.paste(img, (0, 0), img)
        cell.paste(checker, (px, py))
        sheet.paste(cell, (x, y))

        asset = metadata.get(path.name, {})
        confidence = asset.get("confidence", "unknown")
        strategy = asset.get("strategy", "unknown")
        brightness = mean_brightness(path)
        draw.text((x, y + thumb_h + 8), path.name, fill="#ffffff", font=font)
        draw.text((x, y + thumb_h + 30), f"{strategy} | confidence: {confidence}", fill="#d8d8e8", font=small)
        draw.text((x, y + thumb_h + 48), f"{img.width}x{img.height} preview | brightness {brightness}", fill="#b8b8c8", font=small)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def starter_main_menu_manifest(image_path: Path) -> dict:
    return {
        "source_image": str(image_path),
        "coordinate_space": "normalized",
        "requires_user_approval": True,
        "notes": (
            "Starter fantasy portrait menu decomposition. Review crop boxes and "
            "confidence before extraction."
        ),
        "assets": [
            {
                "name": "background.png",
                "role": "clean-ish background candidate with main UI blurred out",
                "strategy": "background_clean_candidate",
                "bbox": [0.0, 0.0, 1.0, 1.0],
                "erase_source_regions": [
                    [0.02, 0.02, 0.33, 0.11],
                    [0.83, 0.02, 0.98, 0.11],
                    [0.04, 0.14, 0.97, 0.31],
                    [0.22, 0.32, 0.80, 0.64],
                ],
                "alpha": "none",
                "confidence": "low",
                "notes": "One-image cleanup is approximate; generated/source background is cleaner.",
            },
            {
                "name": "logo.png",
                "role": "Gemonite title logo",
                "strategy": "crop_with_alpha_candidate",
                "bbox": [0.045, 0.135, 0.965, 0.318],
                "alpha": "dark_background",
                "confidence": "medium",
                "notes": "Keeps glow padding; dark-background alpha may remove some shadow.",
            },
            {
                "name": "primary_button.png",
                "role": "empty Play-style main button",
                "strategy": "empty_ui_candidate",
                "bbox": [0.235, 0.336, 0.765, 0.432],
                "erase_regions": [[0.28, 0.23, 0.72, 0.78]],
                "alpha": "rounded_rect",
                "confidence": "medium",
                "notes": "Text removal is blurred candidate; user approval required.",
            },
            {
                "name": "secondary_button.png",
                "role": "empty secondary menu button",
                "strategy": "empty_ui_candidate",
                "bbox": [0.245, 0.452, 0.755, 0.545],
                "erase_regions": [[0.12, 0.22, 0.88, 0.78]],
                "alpha": "rounded_rect",
                "confidence": "medium",
                "notes": "Based on Tug of War button; text removal is approximate.",
            },
            {
                "name": "shop_button.png",
                "role": "empty shop-size button candidate",
                "strategy": "empty_ui_candidate",
                "bbox": [0.245, 0.555, 0.755, 0.650],
                "erase_regions": [[0.12, 0.22, 0.88, 0.78]],
                "alpha": "rounded_rect",
                "confidence": "medium",
                "notes": "Includes cart area unless erase box is widened.",
            },
            {
                "name": "settings_icon_button.png",
                "role": "top-right settings icon button",
                "strategy": "crop_with_alpha_candidate",
                "bbox": [0.825, 0.024, 0.965, 0.105],
                "alpha": "ellipse",
                "confidence": "high",
                "notes": "Circular crop candidate.",
            },
            {
                "name": "score_panel.png",
                "role": "top-left best score panel",
                "strategy": "crop_reference",
                "bbox": [0.028, 0.030, 0.318, 0.107],
                "alpha": "rounded_rect",
                "confidence": "medium",
                "notes": "Contains baked score text; rebuild as code_native if dynamic.",
            },
            {
                "name": "bottom_decoration.png",
                "role": "foreground cannon/gems/bomb decorations",
                "strategy": "crop_reference",
                "bbox": [0.000, 0.665, 1.000, 0.985],
                "alpha": "none",
                "confidence": "medium",
                "notes": "Often better baked into background unless interactive.",
            },
        ],
    }


def write_manifest(manifest: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / MANIFEST_NAME
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return path


def command_init_main_menu(args: argparse.Namespace) -> None:
    image_path = Path(args.image).resolve()
    Image.open(image_path).verify()
    manifest_path = write_manifest(starter_main_menu_manifest(image_path), Path(args.out_dir))
    print(f"Wrote starter manifest: {manifest_path}")
    print("Review and edit crop boxes before running extract.")


def command_extract(args: argparse.Namespace) -> None:
    image_path = Path(args.image).resolve()
    manifest_path = Path(args.manifest).resolve()
    out_dir = Path(args.out_dir).resolve()
    manifest = json.loads(manifest_path.read_text())
    normalized = manifest.get("coordinate_space", "normalized") == "normalized"
    source = Image.open(image_path).convert("RGBA")
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = []
    for asset in manifest.get("assets", []):
        if asset.get("strategy") == "background_clean_candidate":
            path = make_background_candidate(source, asset, out_dir, normalized)
        else:
            path = export_asset(source, asset, out_dir, normalized)
        exported.append(path)
        print(path)

    review_path = out_dir.parent / "asset_review_sheet.png"
    make_review_sheet(out_dir, review_path, manifest_path)
    print(f"Review sheet: {review_path}")
    print("Stop here and ask the user to approve or revise these assets.")


def command_review(args: argparse.Namespace) -> None:
    make_review_sheet(
        Path(args.assets_dir).resolve(),
        Path(args.out).resolve(),
        Path(args.manifest).resolve() if args.manifest else None,
    )
    print(f"Wrote review sheet: {Path(args.out).resolve()}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create reviewable asset candidates from a reference image.")
    sub = parser.add_subparsers(required=True)

    init = sub.add_parser("init-main-menu", help="Create starter manifest for a portrait fantasy main menu.")
    init.add_argument("--image", required=True)
    init.add_argument("--out-dir", required=True)
    init.set_defaults(func=command_init_main_menu)

    extract = sub.add_parser("extract", help="Extract assets from a manifest.")
    extract.add_argument("--image", required=True)
    extract.add_argument("--manifest", required=True)
    extract.add_argument("--out-dir", required=True)
    extract.set_defaults(func=command_extract)

    review = sub.add_parser("review", help="Create a contact sheet for extracted assets.")
    review.add_argument("--assets-dir", required=True)
    review.add_argument("--out", required=True)
    review.add_argument("--manifest")
    review.set_defaults(func=command_review)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
