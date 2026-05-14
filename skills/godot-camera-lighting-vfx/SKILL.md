---
name: godot-camera-lighting-vfx
description: >
  Set up camera framing, camera follow, parallax, lighting, environment, particles, screen effects, and visual polish for Godot scenes from screenshots, mockups, concept art, or gameplay plans. Use this skill for 2D and 3D scenes when the reference implies a camera angle, mood, lighting style, depth, VFX, explosions, glow, weather, fog, shake, zoom, or cinematic framing.
---

# Godot Camera Lighting VFX

Make the scene readable and aligned with the reference. Camera and lighting decisions should support gameplay first, visual match second.

## Visual Direction Brief

Create:

```markdown
## Camera / Lighting / VFX Plan
Camera type:
Camera behavior:
Framing target:
Bounds:
Lighting mood:
Depth/parallax:
VFX:
Performance risks:
```

## Camera Patterns

| Scene | Camera |
|---|---|
| 2D platformer | `Camera2D` follows player with smoothing and bounds |
| 2D top-down | `Camera2D` follows player or room center |
| 2D arena | fixed or soft-follow camera constrained to arena |
| UI/menu | no gameplay camera; use `Control` layout |
| 3D first-person | `Camera3D` under player/camera pivot |
| 3D third-person | follow rig with offset or spring arm |
| 3D isometric | orthographic `Camera3D` angled downward |
| cutscene | fixed cameras or path/marker sequence |

## 2D Visual Depth

Use:
- `ParallaxBackground` / `ParallaxLayer` for scrolling backgrounds.
- Foreground occluders for depth, but keep player readable.
- `CanvasModulate` for global color mood.
- `PointLight2D` / `DirectionalLight2D` if the project uses 2D lighting.
- `GPUParticles2D` for dust, sparkles, smoke, fire, magic.

Avoid overusing particles when they obscure gameplay.

## 3D Lighting And Environment

Use:
- `DirectionalLight3D` for sun/moon.
- `OmniLight3D` / `SpotLight3D` for local lamps, torches, effects.
- `WorldEnvironment` for ambient light, sky, fog, glow.
- Simple materials for blockout readability.

In prototypes, prioritize clear silhouettes and navigable space.

## VFX Defaults

| Visual cue | Godot implementation |
|---|---|
| glow/magic | particles + light + optional bloom |
| fire/sparks | `GPUParticles2D/3D` |
| impact | short burst particles + camera shake |
| collectible sparkle | looping particles or animated sprite |
| wind/rain/snow | screen/world particles |
| damage feedback | flash material/modulate + shake |

## Camera Shake

Use small, event-driven shake. Do not shake continuously unless the scene calls for it.

Common triggers:
- player damage
- explosion
- boss landing
- heavy attack
- object destruction

## Reference Matching Rules

From screenshot/mockup:
- Match camera angle and framing before detailed effects.
- Match color temperature and contrast broadly.
- Use parallax/depth only if the reference has layered background or side-scrolling cues.
- Use lights/VFX as functional readability markers, not only decoration.

## Checklist

```markdown
[ ] Camera sees the intended gameplay area
[ ] Camera follows or stays fixed intentionally
[ ] Bounds prevent showing empty/off-reference space
[ ] Lighting makes player/enemies/interactables readable
[ ] VFX communicates gameplay state
[ ] Effects do not obscure UI or hazards
[ ] Performance is reasonable for target platform
```
