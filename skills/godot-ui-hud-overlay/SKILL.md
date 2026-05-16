---
name: godot-ui-hud-overlay
description: >
  Build gameplay HUDs and UI overlays for Godot scenes from screenshots, mockups, reference briefs, or gameplay requirements. Use this skill for health bars, score, timers, minimaps, inventory slots, dialogue boxes, mobile controls, prompts, pause buttons, ammo, ability cooldowns, boss bars, objective text, and any UI layered over an in-game scene.
---

# Godot UI HUD Overlay

HUD belongs in a `CanvasLayer`, separated from world nodes. It should react to game signals and stay responsive across viewports.

## HUD Brief

Create:

```markdown
## HUD Plan
HUD elements:
Data sources:
Signals to connect:
Viewport/orientation:
Safe margins:
Input controls:
Scene path:
```

## Standard Tree

```text
HUDLayer (CanvasLayer)
└── HUDRoot (Control)
    ├── TopBar
    │   ├── Health
    │   ├── Score
    │   └── Timer
    ├── ObjectivePrompt
    ├── DialogueBox
    ├── BossBar
    ├── MobileControls
    └── PauseButton
```

Use only the branches required by the scene.

## Layout Rules

- Use anchors and containers, not fixed absolute positions, unless matching a fixed-resolution prototype.
- Keep top-left/top-right HUD clear of notches and mobile safe areas.
- Use `Control` nodes for UI, not `Node2D`.
- Use theme overrides or a theme resource for repeated styling.
- Keep HUD logic thin: receive signals, update labels/bars/icons.

## Data Flow

Good pattern:

```text
Player/GameState emits signal -> HUD receives -> HUD updates visual state
```

Avoid:

```text
HUD polls deep paths like ../../World/Player/HealthComponent every frame
```

## Common Elements

| Element | Godot node |
|---|---|
| health bar | `ProgressBar` or `TextureProgressBar` |
| score/currency | `Label` + optional icon |
| inventory slots | `GridContainer` |
| cooldown | `TextureProgressBar` or icon with overlay |
| prompt | `PanelContainer` + `Label` |
| dialogue | `PanelContainer` + text label and speaker label |
| mobile joystick/buttons | `TouchScreenButton` or custom `Control` buttons |
| minimap | `SubViewportContainer` or simplified `Control` map |

## Reference-Based HUD

From screenshots:
- Capture visible HUD positions, colors, icon count, labels, and hierarchy.
- Infer data only when conventional: hearts = health, coins = currency, timer = countdown/countup.
- If exact icons are unavailable, use placeholders or existing project assets.
- Use `imagegen` for missing bitmap HUD icons, portraits, badges, or UI mockup pieces only when Godot-native controls or existing vector assets are not a better fit.

## Checklist

```markdown
[ ] HUD is in CanvasLayer
[ ] HUDRoot uses anchors/containers
[ ] Signals or explicit update methods drive data
[ ] Elements match visible reference priorities
[ ] Text fits at target viewport
[ ] Mobile controls do not cover core action
[ ] Pause/dialogue overlays block input only when intended
```
