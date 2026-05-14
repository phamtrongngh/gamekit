#!/usr/bin/env python3
"""
extract_assets.py — Extract assets from game UI screenshot

Usage:
    python extract_assets.py --image screenshot.png --output res://assets/ui/ --analyze
    python extract_assets.py --image screenshot.png --crop 100,200,500,300 --name btn_play

Options:
    --image     Source image path
    --output    Output directory (default: ./extracted/)
    --analyze   Only analyze colors, don't crop
    --crop      Crop specific region: x1,y1,x2,y2
    --name      Output filename (no extension needed)
    --bg        Save original image as background (resize to 1080x1920)
"""

import sys
import argparse
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Need to install: pip install Pillow numpy")
    sys.exit(1)


def analyze_colors(img: Image.Image) -> dict:
    """Extract dominant colors from image"""
    img_rgb = img.convert("RGB")
    pixels = np.array(img_rgb).reshape(-1, 3)

    # Sample at characteristic regions
    w, h = img.size
    regions = {
        "center":      img_rgb.crop((w//4, h//4, 3*w//4, 3*h//4)),
        "top_center":  img_rgb.crop((w//3, 0, 2*w//3, h//4)),
        "bottom":      img_rgb.crop((0, 3*h//4, w, h)),
    }

    results = {}
    for name, region in regions.items():
        region_pixels = np.array(region).reshape(-1, 3)
        avg = region_pixels.mean(axis=0).astype(int)
        results[f"avg_{name}"] = f"#{avg[0]:02X}{avg[1]:02X}{avg[2]:02X}"

    # Find prominent color (exclude very dark/bright areas)
    mask = (pixels.max(axis=1) > 30) & (pixels.max(axis=1) < 240)
    filtered = pixels[mask]
    if len(filtered) > 0:
        dominant = filtered.mean(axis=0).astype(int)
        results["dominant"] = f"#{dominant[0]:02X}{dominant[1]:02X}{dominant[2]:02X}"

    # Sample pixels at corners (usually background)
    corners = [img_rgb.getpixel((10, 10)), img_rgb.getpixel((w-10, 10)),
               img_rgb.getpixel((10, h-10)), img_rgb.getpixel((w-10, h-10))]
    avg_corner = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    results["background_estimate"] = f"#{avg_corner[0]:02X}{avg_corner[1]:02X}{avg_corner[2]:02X}"

    return results


def extract_background(img: Image.Image, output_path: Path, target_size=(1080, 1920)):
    """Save original image as background, resize if needed"""
    out = output_path / "bg_main_menu.png"
    resized = img.resize(target_size, Image.LANCZOS)
    resized.save(out)
    print(f"✓ Background saved: {out} ({target_size[0]}×{target_size[1]})")
    return out


def crop_region(img: Image.Image, bbox: tuple, name: str, output_path: Path):
    """Crop specific region and save"""
    cropped = img.crop(bbox)
    out = output_path / f"{name}.png"
    cropped.save(out)
    print(f"✓ Cropped '{name}': {bbox} → {out}")
    return out


def estimate_button_regions(img: Image.Image) -> list:
    """
    Estimate button regions based on high contrast colors.
    This is a simple heuristic — results need manual review.
    """
    img_gray = np.array(img.convert("L"))
    h, w = img_gray.shape

    # Find horizontal bands with high contrast (usually buttons)
    row_variance = np.var(img_gray, axis=1)
    threshold = row_variance.mean() * 1.5

    in_band = False
    bands = []
    start = 0
    for y, var in enumerate(row_variance):
        if var > threshold and not in_band:
            in_band = True
            start = y
        elif var <= threshold and in_band:
            in_band = False
            if y - start > 20:  # at least 20px tall
                bands.append((0, start, w, y))

    print(f"  Found {len(bands)} potential regions (button/element):")
    for i, b in enumerate(bands):
        print(f"  [{i}] y={b[1]}..{b[3]} (height={b[3]-b[1]}px)")
    return bands


def print_analysis_report(img: Image.Image, colors: dict):
    w, h = img.size
    print(f"\n{'='*50}")
    print(f"IMAGE ANALYSIS REPORT")
    print(f"{'='*50}")
    print(f"Size: {w} × {h}px")
    print(f"Aspect: {'portrait' if h > w else 'landscape'}")
    print(f"\n--- COLOR ANALYSIS ---")
    for key, color in colors.items():
        print(f"  {key:25s}: {color}")
    print(f"\n--- LAYOUT HINTS ---")
    print(f"  Viewport target: 1080 × 1920 (mobile portrait)")
    print(f"  Scale factor X: {1080/w:.3f}x")
    print(f"  Scale factor Y: {1920/h:.3f}x")
    print(f"\n--- NEXT STEPS ---")
    print(f"  1. Use colors above to fill PHASE 1 Color Extraction")
    print(f"  2. Crop background: --bg flag")
    print(f"  3. Crop each button: --crop x1,y1,x2,y2 --name btn_play")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="Extract assets from game UI screenshot")
    parser.add_argument("--image", required=True, help="Input screenshot path")
    parser.add_argument("--output", default="./extracted/", help="Output directory")
    parser.add_argument("--analyze", action="store_true", help="Analyze colors only")
    parser.add_argument("--crop", help="Crop region: x1,y1,x2,y2")
    parser.add_argument("--name", help="Output filename (no extension)")
    parser.add_argument("--bg", action="store_true", help="Save as background")
    parser.add_argument("--detect-buttons", action="store_true", help="Auto-detect button regions")
    args = parser.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"❌ File not found: {img_path}")
        sys.exit(1)

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    img = Image.open(img_path)
    print(f"✓ Loaded: {img_path.name} ({img.size[0]}×{img.size[1]})")

    colors = analyze_colors(img)

    if args.analyze or (not args.crop and not args.bg and not args.detect_buttons):
        print_analysis_report(img, colors)

    if args.bg:
        extract_background(img, output_path)

    if args.crop:
        if not args.name:
            print("❌ --crop requires --name")
            sys.exit(1)
        try:
            bbox = tuple(int(x) for x in args.crop.split(","))
            if len(bbox) != 4:
                raise ValueError
        except ValueError:
            print("❌ --crop format: x1,y1,x2,y2 (4 integers)")
            sys.exit(1)
        crop_region(img, bbox, args.name, output_path)

    if args.detect_buttons:
        print("\n--- AUTO-DETECT BUTTON REGIONS ---")
        estimate_button_regions(img)
        print("(Results are suggestions only — use --crop to extract each region)")


if __name__ == "__main__":
    main()
