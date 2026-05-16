---
name: godot-scene-verification
description: >
  Verify Godot scenes after implementation. Use this skill after building or modifying any Godot scene, level, UI screen, character, enemy, object interaction, collision setup, camera, or scene-from-reference workflow. It checks project run errors, scene loading, missing resources, node paths, signals, collisions, viewport layout, gameplay basics, and reference-match gaps.
---

# Godot Scene Verification

Do not stop after creating files. Run or inspect the scene and report concrete results.

Use the project-configured Godot MCP server from `Coding-Solo/godot-mcp` to run projects, capture debug output, stop running instances, inspect project info, and create/modify scenes safely. Use the local Godot CLI/headless workflow only for operations outside the MCP tool surface, and report any verification limits.

## Verification Report

Always finish with:

```markdown
## Verification
Run status:
Scene tested:
Errors/warnings:
Functional checks:
Visual/reference checks:
Remaining gaps:
```

## Basic Checks

```markdown
[ ] Project opens/runs without fatal errors
[ ] Target scene loads
[ ] No missing script/resource errors
[ ] Node paths used by scripts exist
[ ] Signals connect without runtime errors
[ ] Inputs required by scripts exist or are documented
[ ] Placeholders are intentional and named
```

## Gameplay Scene Checks

```markdown
[ ] Player spawns safely
[ ] Player can move according to scene type
[ ] Camera frames player/action
[ ] Collision blocks intended walls/ground
[ ] Hazards/triggers fire only when intended
[ ] Collectibles/interactables respond
[ ] Enemies spawn and perform basic behavior
[ ] Scene bounds prevent obvious escape/fall issues
[ ] HUD updates from game state/signals
```

## UI/HUD Checks

```markdown
[ ] Text fits inside controls
[ ] Buttons/controls are clickable
[ ] HUD does not cover critical gameplay
[ ] Anchors work at target viewport sizes
[ ] Popups pause/block input only when intended
```

## Reference Match Checks

For scene-from-reference tasks:

```markdown
[ ] Scene category matches reference
[ ] Camera/view matches reference
[ ] Main entities exist and are placed plausibly
[ ] Important objects/terrain/HUD are represented
[ ] Color/lighting/style direction is recognizable
[ ] Missing source assets are replaced with clear placeholders
[ ] Assumptions are documented
```

## Debug Workflow

1. Use Godot MCP `run_project` for project execution.
2. Capture debug output with MCP.
3. Fix fatal errors first.
4. Fix missing resources and broken node paths.
5. Verify interactions manually or with a minimal test scene.
6. Stop the running project with MCP/local tooling.

If a GUI/editor step is required and unavailable, state the limitation and verify what can be verified headlessly.

## Common Failure Patterns

| Symptom | Likely cause |
|---|---|
| `Node not found` | script path does not match scene tree |
| missing resource | asset path wrong or not imported |
| character falls forever | no collision under spawn or wrong masks |
| enemy ignores player | detection mask/group mismatch |
| button does nothing | signal not connected or target scene missing |
| HUD not updating | no signal connection or wrong data owner |
| camera shows empty area | wrong camera enabled, offset, or bounds |

## Final Gap Report

Be explicit:
- Completed.
- Verified.
- Not verified and why.
- Placeholder/assumption list.
- Recommended next implementation step.
