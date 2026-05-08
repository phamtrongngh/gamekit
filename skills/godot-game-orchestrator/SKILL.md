---
name: godot-game-orchestrator
description: >
  Master orchestrator for Godot 2D game development workflows. This skill coordinates godot-engine-tools, godot-2d-expert, and game-asset-analyzer to deliver complete, working game features. Use this skill whenever the user asks to: "create a game", "add a feature", "build a level", "make a character", "implement gameplay", or any task requiring multiple steps across scene creation, asset integration, and code implementation. This skill ensures the correct workflow: analyze assets first → use CLI tools to create scenes/nodes → write GDScript logic → test. When in doubt about workflow order, trigger this skill.
---

# Godot Game Orchestrator

This skill is your **workflow brain** for Godot 2D game development. It doesn't replace the other skills — it tells you **when and how** to use them together in the right order.

---

## Core Principle

**Never manually create `.tscn` files or guess asset dimensions.**  
Always follow this pipeline:

```
Assets → Analysis → Scene Structure → Implementation → Testing
```

---

## The Correct Workflow

### Phase 1: Asset Analysis (if assets are involved)

**When:** User provides images (PNG/JPG) or references visual assets.

**Action:** Trigger `game-asset-analyzer` skill FIRST.

```bash
# For each asset:
1. Run: sips -g pixelWidth -g pixelHeight "path/to/asset.png"
2. Use view_image to analyze visual features
3. Generate .meta.yaml sidecar file
```

**Output:** `.meta.yaml` files with precise offsets, collision radii, anchor points.

**Why:** You need exact pixel measurements before positioning nodes in Godot. Guessing leads to misalignment bugs.

---

### Phase 2: Scene Creation (use CLI, not manual files)

**When:** Need to create new scenes or add nodes to existing scenes.

**Action:** Use `godot-engine-tools` skill and its CLI.

**WRONG approach (causes errors):**
```bash
# ❌ DON'T manually create .tscn files
echo '[gd_scene ...]' > player.tscn
```

**CORRECT approach:**
```bash
# ✅ Use the CLI tools
python3 scripts/godot_mcp_cli.py create_scene --json '{"project_path": "/path/to/project", "scene_path": "res://scenes/player.tscn", "root_type": "CharacterBody2D", "root_name": "Player"}'

# ✅ Add child nodes
python3 scripts/godot_mcp_cli.py add_node --json '{"project_path": "/path/to/project", "scene_path": "res://scenes/player.tscn", "parent_path": "Player", "node_type": "Sprite2D", "node_name": "Sprite"}'

# ✅ Load sprite with metadata
python3 scripts/godot_mcp_cli.py load_sprite --json '{"project_path": "/path/to/project", "scene_path": "res://scenes/player.tscn", "sprite_node_path": "Player/Sprite", "texture_path": "res://assets/player.png", "offset_x": 0, "offset_y": -12}'
```

**Why:** The CLI uses Godot's internal scene format correctly. Manual files break on import.

---

### Phase 3: GDScript Implementation

**When:** Scene structure is ready, now need game logic.

**Action:** Use `godot-2d-expert` skill to write GDScript.

**Read the .meta.yaml first:**
```bash
cat assets/player.meta.yaml
```

**Then write idiomatic GDScript:**
```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_velocity: float = -400.0

@onready var sprite := $Sprite2D

func _physics_process(delta: float) -> void:
    # Use metadata-driven offsets if needed
    velocity.x = Input.get_axis("move_left", "move_right") * speed
    move_and_slide()
```

**Why:** GDScript is the only language for Godot 2D. Use static typing and @export.

---

### Phase 4: Testing & Iteration

**When:** Implementation is complete.

**Action:** Use `godot-engine-tools` to run and debug.

```bash
# Run the project
python3 scripts/godot_mcp_cli.py run_project --json '{"project_path": "/path/to/project"}'

# Get debug output
python3 scripts/godot_mcp_cli.py get_debug_output --json '{}'

# Stop when done
python3 scripts/godot_mcp_cli.py stop_project --json '{}'
```

**Why:** Catch errors early before presenting to user.

---

## Decision Tree: Which Skill to Use?

```
User request
    │
    ├─ Mentions image/asset/sprite/texture?
    │   └─ YES → game-asset-analyzer (generate .meta.yaml)
    │       └─ THEN continue to next step
    │
    ├─ Need to create/modify scene structure?
    │   └─ YES → godot-engine-tools (use CLI, not manual files)
    │       └─ THEN continue to next step
    │
    ├─ Need to write game logic/behavior?
    │   └─ YES → godot-2d-expert (write GDScript)
    │       └─ Read .meta.yaml first if assets involved
    │
    └─ Need to run/test/debug?
        └─ YES → godot-engine-tools (run_project, get_debug_output)
```

---

## Common Workflows (End-to-End)

### Workflow A: Create a Player Character

```
1. [game-asset-analyzer] Analyze player.png → player.meta.yaml
2. [godot-engine-tools] create_scene → player.tscn (CharacterBody2D)
3. [godot-engine-tools] add_node → Sprite2D, CollisionShape2D
4. [godot-engine-tools] load_sprite → use offsets from .meta.yaml
5. [godot-2d-expert] Write player.gd with movement logic
6. [godot-engine-tools] run_project → test movement
```

### Workflow B: Add a Collectible Item

```
1. [game-asset-analyzer] Analyze coin.png → coin.meta.yaml
2. [godot-engine-tools] create_scene → coin.tscn (Area2D)
3. [godot-engine-tools] add_node → Sprite2D, CollisionShape2D
4. [godot-engine-tools] load_sprite → use collision_radius from .meta.yaml
5. [godot-2d-expert] Write coin.gd with collection logic + signals
6. [godot-2d-expert] Update player.gd to connect to coin signals
```

### Workflow C: Build a Weapon System

```
1. [game-asset-analyzer] Analyze cannon.png → cannon.meta.yaml
2. [game-asset-analyzer] Analyze bullet.png → bullet.meta.yaml
3. [godot-engine-tools] create_scene → cannon.tscn (Node2D)
4. [godot-engine-tools] load_sprite → use barrel_tip offset from .meta.yaml
5. [godot-engine-tools] create_scene → bullet.tscn (Area2D)
6. [godot-2d-expert] Write cannon.gd with spawn logic at barrel_tip
7. [godot-2d-expert] Write bullet.gd with movement + collision
8. [godot-engine-tools] run_project → verify spawn position
```

### Workflow D: Create a Level with Tilemap

```
1. [game-asset-analyzer] Analyze tile assets → .meta.yaml for each
2. [godot-engine-tools] launch_editor → manually create TileSet (complex UI)
3. [godot-engine-tools] create_scene → level.tscn (Node2D)
4. [godot-engine-tools] add_node → TileMapLayer
5. [godot-2d-expert] Write level.gd for dynamic tile placement if needed
```

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Manual Scene File Creation
```bash
# WRONG - causes import errors
cat > player.tscn << 'EOF'
[gd_scene load_steps=2 format=3]
...
EOF
```
**Fix:** Use `create_scene` CLI tool.

---

### ❌ Anti-Pattern 2: Guessing Asset Dimensions
```gdscript
# WRONG - hardcoded guess
var sprite_offset = Vector2(15, -8)  # where did these come from?
```
**Fix:** Generate `.meta.yaml` first, read it, use documented offsets.

---

### ❌ Anti-Pattern 3: Skipping CLI for Node Creation
```bash
# WRONG - trying to edit .tscn with sed/awk
sed -i 's/type="Node2D"/type="CharacterBody2D"/' scene.tscn
```
**Fix:** Use `add_node` CLI tool.

---

### ❌ Anti-Pattern 4: Writing C# Instead of GDScript
```csharp
// WRONG - Godot 2D uses GDScript only
public class Player : CharacterBody2D { }
```
**Fix:** Always use `.gd` files with `extends` keyword.

---

### ❌ Anti-Pattern 5: Not Testing Before Presenting
```
[writes code] → [shows to user] → [user finds it doesn't run]
```
**Fix:** Always `run_project` + `get_debug_output` before final answer.

---

## Skill Coordination Rules

1. **Asset-first rule:** If user mentions any visual element, analyze it BEFORE creating scenes.

2. **CLI-only rule:** NEVER manually create/edit `.tscn` files. Always use `godot_mcp_cli.py`.

3. **Metadata-driven rule:** Read `.meta.yaml` before setting any position/offset/radius in code.

4. **GDScript-only rule:** Never suggest C#/C++. All scripts are `.gd` files.

5. **Test-before-present rule:** Run the project and verify it works before showing to user.

6. **One-skill-at-a-time rule:** Don't mix skill contexts. Finish asset analysis, THEN move to scene creation, THEN write code.

---

## When to Use This Orchestrator Skill

Trigger this skill when:
- User asks to "create a game" or "add a feature" (multi-step workflow)
- User provides assets but you're unsure of the order of operations
- You catch yourself about to manually create a `.tscn` file
- You're about to guess pixel offsets instead of measuring them
- The task spans multiple skills and you need workflow guidance

**This skill doesn't write code or analyze images itself** — it tells you which other skill to invoke and in what order.

---

## Quick Reference Card

| Task | Skill | Tool/Command |
|------|-------|--------------|
| Measure asset dimensions | game-asset-analyzer | `sips -g pixelWidth -g pixelHeight` |
| Analyze asset features | game-asset-analyzer | `view_image` + generate `.meta.yaml` |
| Create new scene | godot-engine-tools | `create_scene` |
| Add node to scene | godot-engine-tools | `add_node` |
| Load sprite texture | godot-engine-tools | `load_sprite` |
| Write game logic | godot-2d-expert | Write `.gd` file with `extends` |
| Run project | godot-engine-tools | `run_project` |
| Debug output | godot-engine-tools | `get_debug_output` |
| Stop project | godot-engine-tools | `stop_project` |

---

## Example: Full Feature Implementation

**User request:** "Add a cannon that shoots fireballs"

**Orchestrator response:**

```
Step 1: Analyze assets
→ game-asset-analyzer: cannon.png → cannon.meta.yaml (barrel_tip offset)
→ game-asset-analyzer: fireball.png → fireball.meta.yaml (collision_radius)

Step 2: Create scene structure
→ godot-engine-tools: create_scene cannon.tscn (Node2D)
→ godot-engine-tools: add_node Sprite2D to cannon
→ godot-engine-tools: load_sprite with cannon.png
→ godot-engine-tools: create_scene fireball.tscn (Area2D)
→ godot-engine-tools: add_node Sprite2D, CollisionShape2D to fireball
→ godot-engine-tools: load_sprite with fireball.png

Step 3: Implement logic
→ godot-2d-expert: Write cannon.gd
  - Read cannon.meta.yaml for barrel_tip offset
  - Preload fireball scene
  - Spawn at barrel_tip position on input
→ godot-2d-expert: Write fireball.gd
  - Read fireball.meta.yaml for collision_radius
  - Move forward with velocity
  - Emit signal on area_entered

Step 4: Test
→ godot-engine-tools: run_project
→ godot-engine-tools: get_debug_output (check for errors)
→ godot-engine-tools: stop_project

Step 5: Present to user
→ Show file paths, key code snippets, next steps
```

---

## Summary

This orchestrator skill ensures you:
1. ✅ Analyze assets before using them
2. ✅ Use CLI tools instead of manual file creation
3. ✅ Write metadata-driven GDScript
4. ✅ Test before presenting
5. ✅ Follow a logical, error-free workflow

**Remember:** The other skills are your tools. This skill is your blueprint for using them correctly.
