---
name: godot-ui-from-screenshot
description: >
  Use this skill whenever the user provides a screenshot, mockup, or concept image of a game UI
  and wants it implemented in Godot. Triggers include: uploading a UI image and saying "make this scene",
  "build this UI", "implement this screen", "recreate this menu", "build this in Godot", or
  any combination of a UI image + a Godot task. Also triggers when user says "pixel-perfect",
  "exactly like the image", or "match the design". This skill bridges the gap between a flat image and
  a working Godot UI scene — including asset extraction, color analysis, layout inference,
  and navigation logic. If the reference image is an in-game scene with characters, enemies, terrain,
  props, 3D space, or gameplay objects rather than primarily UI, use godot-scene-from-reference first
  and treat this skill as the specialized UI/HUD branch.
---

# Godot UI From Screenshot

Transform a UI concept image into a working Godot scene — with layout, button logic, fonts, colors,
and navigation. This skill enables working from just a single flat image, without needing Figma or source files.

For broader screenshots or mockups that include in-game characters, enemies, terrain, props, collision,
camera framing, or 3D space, use `godot-scene-from-reference` as the orchestrator. Return to this skill
only for the UI-specific portions such as menus, HUD overlays, popups, shops, inventory, settings, and
button navigation.

---

## Process Overview

```
PHASE 1: ANALYZE   →   PHASE 2: ASSET   →   PHASE 3: INFER   →   PHASE 4: BUILD   →   PHASE 5: VERIFY
(read image)           (extract assets)     (infer logic)        (build scene)         (compare)
```

Do not skip any phase. Each phase feeds into the next.

---

## PHASE 1 — ANALYZE (Systematic Image Reading)

View the image with vision and complete the following table before doing anything else.

### 1.1 Layout inventory

List EVERY component visible in the image, in order from top to bottom:

```
[index] | [component type]     | [estimated position]  | [content]
--------|----------------------|-----------------------|---------------------------
  1     | Label (score)        | top-left              | "BEST 1740" + trophy icon
  2     | Button (settings)    | top-right             | gear icon
  3     | Logo / Title         | center-top            | "GEMONITE" stylized text
  4     | Button (primary)     | center                | "PLAY"
  ...
```

### 1.2 Color extraction

Extract colors from the image by sampling pixels in representative areas:

```
Main background color:    #______  (largest empty area)
Normal button color:      #______  (main button fill)
Button border color:      #______  (button border/stroke)
Primary text color:       #______  (text on button)
Secondary text color:     #______  (label, score, icon text)
Accent/glow color:        #______  (glow, highlight, sparkle)
```

If the image has gradients: note both start and end colors.

### 1.3 Typography

```
Main font style (logo/title): [serif/sans/display/pixel/handwritten] + identifying characteristics
Button text font style:       [style] + uppercase or not?
HUD/score font style:         [style]
Icon font (UTF-8 symbols)?    [yes/no]
```

To match fonts: read `references/font-matching.md`.

### 1.4 Proportions (estimated from image)

Assume default Godot mobile viewport = **1080 × 1920** (portrait) or **1920 × 1080** (landscape).
Estimate as percentage of width/height:

```
Logo:           top ~__% height, width ~__% screen width
PLAY button:    center-y ~__%, height ~__px, width ~__% screen
Button gap:     ~__px between buttons
Top HUD:        ~__px from top, ~__px from left/right edge
```

### 1.5 Visual effects checklist

```
[ ] Drop shadow on text
[ ] Glow/bloom on button or logo
[ ] Gradient background
[ ] Particle or sparkle decoration
[ ] Multi-layer border/stroke (e.g., gold outer border, dark inner border)
[ ] Background scroll/parallax (cannot infer from static image)
[ ] Nine-patch button (requires asset extraction)
```

---

## PHASE 2 — ASSET (Extract and Prepare Assets)

### 2.1 Check existing assets

Before creating new assets, always search the repo:

```bash
find . -name "*.png" -o -name "*.svg" -o -name "*.webp" | grep -i "button\|bg\|logo\|icon\|gem\|ui"
find . -path "*/assets/*" -o -path "*/sprites/*" -o -path "*/ui/*"
```

If suitable assets are found → use them directly, no need to recreate.

### 2.2 Extract assets from image (when source assets unavailable)

**Background:** Crop the entire image as background if it cannot be separated. Use Python:

```python
# scripts/extract_bg.py
from PIL import Image
img = Image.open("screenshot.png")
img.save("res://assets/ui/bg_main_menu.png")
```

**Button texture (if nine-patch needed):**
```python
# Crop button region, detect bounding box
# Note: buttons often have glow padding outside — crop closer to solid color area
bbox = (x1, y1, x2, y2)  # estimated from PHASE 1
button_img = img.crop(bbox)
button_img.save("res://assets/ui/btn_play_normal.png")
```

**Icon / Logo:** If logo is rasterized text (text drawn in image), DO NOT crop and use as image.
Reason: will be pixelated at all other resolutions. Instead → recreate with Label + font (see PHASE 4).

**Asset rembg (remove background):**
If project has local rembg service running (`http://localhost:5001/remove-bg`):
```python
import requests
with open("cropped_element.png", "rb") as f:
    r = requests.post("http://localhost:5001/remove-bg", files={"file": f})
with open("element_nobg.png", "wb") as f:
    f.write(r.content)
```

### 2.3 Name and organize assets

```
res://assets/ui/
├── bg_[screen_name].png       # background
├── btn_[name]_normal.png      # button states
├── btn_[name]_pressed.png
├── icon_[name].png            # individual icons
└── panel_[name].png           # frame/panel if any
```

---

## PHASE 3 — INFER (Infer What the Image Doesn't Show)

Static images don't contain: navigation flow, animation, states, responsive behavior.
Use the convention table below to infer reasonable defaults.

### 3.1 Navigation flow

**ASK USER IF UNCLEAR.** If user doesn't specify, use convention:

```
Button label → Default inferred scene
────────────────────────────────────────
PLAY / START     → res://scenes/game/game.tscn (or level_select.tscn if multiple levels)
SHOP / STORE     → res://scenes/ui/shop.tscn
SETTINGS         → popup SettingsPopup (don't change scene)
TROPHIES / RANK  → leaderboard.tscn or popup
TUG OF WAR       → res://scenes/game/tug_of_war.tscn
QUIT / EXIT      → get_tree().quit()
BACK (←)         → get_tree().change_scene_to_file(previous) or popup close
```

If target scene doesn't exist: create placeholder scene with Label "Coming Soon".

### 3.2 Button states

Godot `Button` / `TextureButton` needs at least 3 states:

```
Normal:   fill color from PHASE 1
Hover:    lighten 10-15% (desktop only — mobile has no hover)
Pressed:  darken 15-20% + scale(0.97) or offset y+2px
Disabled: desaturate + alpha 0.5
```

If using `StyleBoxFlat`: set `draw_center=true`, adjust `corner_radius` to match.
If using `TextureButton`: need to crop separate pressed button image or use modulate.

### 3.3 Animation defaults by game genre

Read game name / genre from UI to infer:

```
Identified genre  → Default entrance animation
─────────────────────────────────────────────────
Match-3 / Casual  → fade in + scale from 0.8→1.0, duration 0.4s, ease Out
RPG / Fantasy     → slide up from bottom + fade, duration 0.5s
Arcade            → flash + bounce, duration 0.3s
Puzzle            → simple fade in, duration 0.3s
```

**Gemonite** (gem + cave visual) → Match-3/Casual → use scale + fade entrance.

### 3.4 Viewport and responsive

```gdscript
# Always use anchors instead of absolute position
# Pattern for screen with 3 vertical buttons:
VBoxContainer with:
  anchor: CENTER (0.5, 0.5, 0.5, 0.5)
  offset: -half_width, -half_height, +half_width, +half_height
  separation: 20px (or according to PHASE 1)
```

---

## PHASE 4 — BUILD (Build Godot Scene)

### 4.1 Standard scene structure

```
[Scene root - Control]
├── Background (TextureRect) — stretch mode: EXPAND_FIT_WIDTH_PROPORTIONAL
├── HUD_Top (HBoxContainer) — anchor top-left, top-right
│   ├── ScorePanel (Panel or NinePatchRect)
│   │   ├── TrophyIcon (TextureRect)
│   │   └── ScoreLabel (Label)
│   └── SettingsButton (Button)
├── Logo (Label or TextureRect) — anchor center-top
├── MenuButtons (VBoxContainer) — anchor center
│   ├── PlayButton (Button)
│   ├── [OtherButton1] (Button)
│   └── [OtherButton2] (Button)
└── Decorations (Node2D, optional) — particle/gem sprites
```

### 4.2 Button styling with StyleBoxFlat

```gdscript
# In code or theme resource:
var style = StyleBoxFlat.new()
style.bg_color = Color("#6B3FA0")         # color from PHASE 1
style.border_width_top = 3
style.border_width_bottom = 3
style.border_width_left = 3
style.border_width_right = 3
style.border_color = Color("#F5C842")     # border color from PHASE 1
style.corner_radius_top_left = 12
style.corner_radius_top_right = 12
style.corner_radius_bottom_left = 12
style.corner_radius_bottom_right = 12
style.shadow_color = Color(0, 0, 0, 0.4)
style.shadow_size = 6
style.shadow_offset = Vector2(0, 3)
button.add_theme_stylebox_override("normal", style)
```

Create pressed style: clone + darken bg_color + adjust shadow.

### 4.3 Font

**Priority order:**
1. Font available in repo → use directly
2. Free Google Fonts matching style → download and import to `res://assets/fonts/`
3. Fallback: default Godot font + bold + letter_spacing

See `references/font-matching.md` to choose font by visual style.

### 4.4 Script navigation

```gdscript
# main_menu.gd
extends Control

func _ready() -> void:
    _setup_animations()

func _on_play_button_pressed() -> void:
    get_tree().change_scene_to_file("res://scenes/game/game.tscn")

func _on_settings_button_pressed() -> void:
    $SettingsPopup.show()

func _on_shop_button_pressed() -> void:
    get_tree().change_scene_to_file("res://scenes/ui/shop.tscn")

func _setup_animations() -> void:
    # Entrance animation — scale + fade
    modulate.a = 0.0
    scale = Vector2(0.85, 0.85)
    var tween = create_tween()
    tween.set_parallel(true)
    tween.tween_property(self, "modulate:a", 1.0, 0.4)
    tween.tween_property(self, "scale", Vector2.ONE, 0.4).set_ease(Tween.EASE_OUT)
```

### 4.5 Scene registration

After creating scene, check and update if needed:
```bash
# Check main scene in project.godot
grep "run/main_scene" project.godot

# If need to set as main scene:
# Open Godot Editor → Project → Project Settings → Application → Run → Main Scene
```

---

## PHASE 5 — VERIFY (Check Results)

After building, run through this checklist. Mark each item:

### Visual checklist (compare with original image)
```
[ ] Background matches color / overall texture
[ ] Logo / title text correct content, font similar
[ ] Button count correct, label text correct
[ ] Button colors match (±10% tolerance acceptable)
[ ] Button border/outline displays
[ ] Icons in buttons display at correct position
[ ] Top HUD (score, settings) at correct position
[ ] No elements cropped or overflowing viewport
```

### Functional checklist
```
[ ] Each button connected to pressed() signal
[ ] Target scene exists (or has placeholder)
[ ] No Godot errors when running scene
[ ] Scene runs at 1080×1920 viewport
[ ] Back navigation works (if applicable)
```

### Gap report

After verification, list clearly:
- **Completed**: [list]
- **Close match (90%+)**: [item and reason for minor deviation]
- **Still missing / needs user input**: [item, reason, how to fix if more assets available]

---

## Quick reference — Questions to ask user

Ask BEFORE BUILDING if unclear. Combine into 1 message:

```
To do this accurately, I need to confirm:

1. [If multiple buttons] Where does [ButtonName] lead? Does that scene already exist?
2. Viewport target: portrait 1080×1920 or landscape 1920×1080?
3. Is this scene the main scene (first scene when game runs) or called from another scene?
4. Is there a specific font being used in the project? (font name or path in repo)
5. [If complex animation seen] What entrance animation effects do you want?
```

Don't ask more than 5 questions at once. If nothing is blocking, proceed with convention defaults from PHASE 3.

---

## Handling special cases

### Low quality / cropped image

If image is compressed, dark, or only shows part:
- Focus on what's clearly visible
- Note clearly which parts are "estimated" in code comments
- Use placeholder colors for unclear areas

### Assets stuck to background

When elements (gem, character, decoration) are stuck to background in image:
- If rembg service available: use it to separate
- If not: create placeholder shape with `ColorRect` + `StyleBoxFlat`
- Add comment: `# TODO: replace with original asset when available`

### Logo is stylized text (cannot extract)

```
DON'T:  Crop logo from image → use as TextureRect (pixelated)
DO:     Find similar font → use Label with:
        - large font size
        - outline width 3-5px
        - shadow
        - uppercase
        Or if pixel-perfect needed: ask user to provide original logo file
```

### Game already has many scenes

When project already has code:
```bash
# Survey scene structure first
find . -name "*.tscn" | head -30
find . -name "*.gd" | head -30
grep -r "change_scene_to_file\|change_scene" --include="*.gd" | head -20
```
Understand current flow before integrating, don't overwrite scenes in use.

---

## Reference files

- `references/font-matching.md` — Google Font selection table by visual style
- `references/godot-ui-patterns.md` — Code snippets for common UI patterns
- `scripts/extract_assets.py` — Python script to extract assets from screenshot
