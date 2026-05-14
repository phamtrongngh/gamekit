# Font Matching Guide

Font selection table based on visual style identified from image.

## How to identify font style from image

| Visible characteristics | Style category |
|---|---|
| Large, rounded, glossy, gold/yellow colors | Fantasy Display |
| Pixel/blocky, retro | Pixel / Retro |
| Handwritten, curved | Handwritten |
| Simple, bold, sans | Bold Sans |
| Classic serif | Serif / Classic |

---

## Fantasy / Game Display (for logo, large titles)

```
Visual: Bold, rounded corners, gold/jewel colors, glow effect
→ Fredoka One         (Google Fonts) — rounded, friendly
→ Baloo 2             (Google Fonts) — chunky, playful
→ Lilita One          (Google Fonts) — heavy, impactful
→ Titan One           (Google Fonts) — game-like, bold
→ Boogaloo            (Google Fonts) — rounded, casual
→ Righteous           (Google Fonts) — geometric, slightly fantasy
```

**Gemonite logo specifically:** → try `Titan One` or `Lilita One` + outline + gold color

---

## Button Text (CTA, menu items)

```
Visual: ALL CAPS, medium weight, readable on colored background
→ Nunito              (Google Fonts) — rounded, very readable
→ Poppins Bold        (Google Fonts) — clean, modern
→ Fredoka One         (Google Fonts) — if casual feel wanted
→ Coiny               (Google Fonts) — coin/game aesthetic
→ Russo One           (Google Fonts) — bold, industrial
```

---

## HUD / Score (numbers, small labels)

```
Visual: Compact, legible at small size
→ Oswald              (Google Fonts) — condensed, strong
→ Barlow Condensed    (Google Fonts) — clean condensed
→ Exo 2              (Google Fonts) — techy, game-like
→ Rajdhani            (Google Fonts) — HUD/dashboard feel
```

---

## Pixel / Retro

```
→ Press Start 2P     (Google Fonts) — classic 8-bit
→ VT323              (Google Fonts) — terminal/pixel
→ Silkscreen         (Google Fonts) — clean pixel
```

---

## Installing fonts in Godot

1. Download `.ttf` from Google Fonts
2. Copy to `res://assets/fonts/`
3. In Godot Editor: drag `.ttf` into Font slot of Label/Button
4. Or in code:
```gdscript
var font = load("res://assets/fonts/TitanOne-Regular.ttf")
label.add_theme_font_override("font", font)
label.add_theme_font_size_override("font_size", 48)
```

## Text effects to match game logo

```gdscript
# Outline (instead of using image)
label.add_theme_constant_override("outline_size", 4)
label.add_theme_color_override("font_outline_color", Color("#3A1A6E"))

# Shadow
label.add_theme_constant_override("shadow_offset_x", 2)
label.add_theme_constant_override("shadow_offset_y", 4)
label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))

# Gold gradient (use LabelSettings or simple shader)
```
