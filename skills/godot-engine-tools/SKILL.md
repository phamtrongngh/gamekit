---
name: godot-engine-tools
description: >
  Automate local Godot project operations through a bundled CLI — no editor needed. Use this skill (not ad-hoc shell commands) whenever the task involves engine automation: launching the editor or running a project headlessly, capturing debug output, stopping a running process, discovering projects, inspecting project structure, or programmatically creating/modifying scenes and nodes (add_node, load_sprite, export_mesh_library, save_scene, get_uid, update_project_uids). Prefer this over godot-2d-expert when the goal is automation and CLI execution rather than game-logic code or GDScript patterns.
---

# Godot Engine Tools

Use the bundled CLI instead of re-implementing Godot automation ad hoc.

## Quick Start

1. Read [references/tool-reference.md](references/tool-reference.md) for the tool names, arguments, and output shape.
2. Prefer `python3 scripts/godot_mcp_cli.py <tool> --json '<args>'`.
3. Set `GODOT_PATH` when auto-detection fails.
4. Keep one active runtime at a time. `run_project`, `get_debug_output`, and `stop_project` share a persisted state file in `/tmp`.

## Workflow

### Inspect and run projects

- Use `get_godot_version` first if the environment is uncertain.
- Use `list_projects` to discover projects and `get_project_info` to inspect one before editing.
- Use `launch_editor` for interactive editor work.
- Use `run_project` to execute a project in debug mode.
- Use `get_debug_output` after a run to capture stdout, stderr, and recent logs.
- Use `stop_project` before starting another run.

### Modify scenes and resources

- Use the CLI subcommands `create_scene`, `add_node`, `load_sprite`, `export_mesh_library`, `save_scene`, `get_uid`, and `update_project_uids`.
  - Scene/resource mutations delegate to the bundled GDScript; the CLI normalizes both `snake_case` and `camelCase` keys.
  - For complex node edits, inspect the scene path and intended parent path first; failed operations return stderr and a non-zero exit code.

## Constraints

- Require a valid local Godot installation. Auto-detection covers common paths on macOS, Linux, and Windows; override with `GODOT_PATH`.
- Reject paths containing `..` for project, scene, and file inputs.
- Do not run `run_project` twice without stopping the previous process unless you intentionally replace the saved runtime state.
