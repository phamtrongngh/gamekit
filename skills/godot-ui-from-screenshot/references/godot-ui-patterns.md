# Godot UI Patterns — Quick Reference

Ready-to-use snippets for common UI patterns in game menus.

---

## Nine-Patch Button (button with nice border, scalable)

```gdscript
# When button needs to preserve border radius when resizing
var nine_patch = NinePatchRect.new()
nine_patch.texture = load("res://assets/ui/btn_play_normal.png")
# Patch margins = area to preserve when scaling (pixels)
nine_patch.patch_margin_left = 20
nine_patch.patch_margin_right = 20
nine_patch.patch_margin_top = 12
nine_patch.patch_margin_bottom = 12
```

---

## Button with StyleBoxFlat pure code (no texture needed)

```gdscript
func make_button_style(bg: Color, border: Color, radius: int = 16) -> StyleBoxFlat:
    var s = StyleBoxFlat.new()
    s.bg_color = bg
    s.set_border_width_all(3)
    s.border_color = border
    s.set_corner_radius_all(radius)
    s.shadow_color = Color(0, 0, 0, 0.35)
    s.shadow_size = 8
    s.shadow_offset = Vector2(0, 4)
    s.content_margin_left = 24
    s.content_margin_right = 24
    s.content_margin_top = 14
    s.content_margin_bottom = 14
    return s

func apply_button_theme(btn: Button, normal_color: Color, border_color: Color) -> void:
    var normal = make_button_style(normal_color, border_color)
    var pressed = make_button_style(normal_color.darkened(0.2), border_color)
    pressed.shadow_size = 3
    pressed.shadow_offset = Vector2(0, 1)
    var hover = make_button_style(normal_color.lightened(0.12), border_color)
    btn.add_theme_stylebox_override("normal", normal)
    btn.add_theme_stylebox_override("pressed", pressed)
    btn.add_theme_stylebox_override("hover", hover)
    btn.add_theme_stylebox_override("focus", normal)  # remove focus rectangle
```

---

## HUD Panel (score display top-left)

```gdscript
# Rounded panel containing icon + label
func make_hud_panel(icon_texture: Texture2D, value: String) -> PanelContainer:
    var panel = PanelContainer.new()
    var style = StyleBoxFlat.new()
    style.bg_color = Color(0.1, 0.05, 0.25, 0.85)
    style.set_border_width_all(2)
    style.border_color = Color("#F5C842")
    style.set_corner_radius_all(20)
    style.content_margin_left = 12
    style.content_margin_right = 16
    style.content_margin_top = 8
    style.content_margin_bottom = 8
    panel.add_theme_stylebox_override("panel", style)

    var hbox = HBoxContainer.new()
    var icon = TextureRect.new()
    icon.texture = icon_texture
    icon.custom_minimum_size = Vector2(28, 28)
    icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
    hbox.add_child(icon)

    var label = Label.new()
    label.text = value
    hbox.add_child(label)
    panel.add_child(hbox)
    return panel
```

---

## Popup Settings (overlay)

```gdscript
# settings_popup.gd
extends CanvasLayer

func _ready() -> void:
    hide()
    $Overlay.gui_input.connect(_on_overlay_clicked)

func _on_overlay_clicked(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        hide()

func show_popup() -> void:
    show()
    # Animate in
    $Panel.scale = Vector2(0.8, 0.8)
    $Panel.modulate.a = 0.0
    var tw = create_tween().set_parallel(true)
    tw.tween_property($Panel, "scale", Vector2.ONE, 0.25).set_ease(Tween.EASE_OUT)
    tw.tween_property($Panel, "modulate:a", 1.0, 0.2)
```

---

## Entrance animation (scene just loaded)

```gdscript
# Apply to entire screen
func _ready() -> void:
    await get_tree().process_frame  # wait 1 frame for layout to complete
    modulate.a = 0.0
    var tween = create_tween().set_parallel(true)
    tween.tween_property(self, "modulate:a", 1.0, 0.35)
    # Optionally: buttons slide up
    for i in range($MenuButtons.get_child_count()):
        var btn = $MenuButtons.get_child(i)
        var original_pos = btn.position
        btn.position.y += 40
        tween.tween_property(btn, "position:y", original_pos.y, 0.4 + i * 0.08)\
            .set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
```

---

## Anchor presets (responsive layout)

```gdscript
# Center completely
control.set_anchor(SIDE_LEFT, 0.5)
control.set_anchor(SIDE_RIGHT, 0.5)
control.set_anchor(SIDE_TOP, 0.5)
control.set_anchor(SIDE_BOTTOM, 0.5)
control.set_offset(SIDE_LEFT, -width / 2)
control.set_offset(SIDE_RIGHT, width / 2)
control.set_offset(SIDE_TOP, -height / 2)
control.set_offset(SIDE_BOTTOM, height / 2)

# Stretch full screen (background)
bg.set_anchors_preset(Control.PRESET_FULL_RECT)
```

---

## Scene transition with fade

```gdscript
# autoload/scene_manager.gd
func goto_scene(path: String) -> void:
    var tween = get_tree().create_tween()
    tween.tween_method(_set_screen_alpha, 0.0, 1.0, 0.25)
    await tween.finished
    get_tree().change_scene_to_file(path)

func _set_screen_alpha(a: float) -> void:
    $FadeOverlay.modulate.a = a  # Black ColorRect covering full screen
```

---

## Placeholder scene (when target scene doesn't exist yet)

```gdscript
# placeholder.gd
extends Control
@export var scene_name: String = "Coming Soon"

func _ready() -> void:
    $Label.text = scene_name
    $BackButton.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/ui/main_menu.tscn"))
```

Quick create:
```bash
# Create placeholder scene with script
python scripts/make_placeholder.py --name "Shop" --back-to "main_menu"
```
