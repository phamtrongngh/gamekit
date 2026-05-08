# Godot Engine Tools Reference

## Entrypoint

Run every capability through:

```bash
python3 scripts/godot_mcp_cli.py <tool> --json '<json-args>'
```

The CLI prints JSON to stdout for success and failure. Successful responses use:

```json
{"ok": true, "tool": "tool_name", "result": {...}}
```

Failures use:

```json
{"ok": false, "tool": "tool_name", "error": "message"}
```

## Environment

- `GODOT_PATH`: Override executable auto-detection.
- `GODOT_MCP_DEBUG=true`: Print additional runtime diagnostics to stderr.

## Tools

### launch_editor

Args:

```json
{"project_path": "/abs/path/to/project"}
```

Launch the Godot editor for the given project.

### run_project

Args:

```json
{"project_path": "/abs/path/to/project", "scene": "res://scenes/main.tscn"}
```

Run the project in debug mode and persist process state for later log retrieval.

### get_debug_output

Args: `{}`

Return current runtime status plus captured stdout/stderr from the latest `run_project`.

### stop_project

Args: `{}`

Terminate the active runtime if one exists.

### get_godot_version

Args: `{}`

Return the detected Godot executable and `--version` output.

### list_projects

Args:

```json
{"directory": "/abs/search/root", "recursive": true}
```

Search for directories containing `project.godot`.

### get_project_info

Args:

```json
{"project_path": "/abs/path/to/project"}
```

Return project metadata, top-level structure buckets, and configured main scene if present.

### create_scene

Args:

```json
{"project_path": "/abs/path/to/project", "scene_path": "scenes/new_scene.tscn", "root_node_type": "Node2D"}
```

### add_node

Args:

```json
{
  "project_path": "/abs/path/to/project",
  "scene_path": "scenes/new_scene.tscn",
  "parent_node_path": "root",
  "node_type": "Sprite2D",
  "node_name": "PlayerSprite",
  "properties": {"position": {"x": 64, "y": 64}}
}
```

### load_sprite

Args:

```json
{
  "project_path": "/abs/path/to/project",
  "scene_path": "scenes/new_scene.tscn",
  "node_path": "root/PlayerSprite",
  "texture_path": "assets/player.png"
}
```

### export_mesh_library

Args:

```json
{
  "project_path": "/abs/path/to/project",
  "scene_path": "scenes/tileset_source.tscn",
  "output_path": "resources/tiles.meshlib",
  "mesh_item_names": ["Grass", "Stone"]
}
```

### save_scene

Args:

```json
{"project_path": "/abs/path/to/project", "scene_path": "scenes/new_scene.tscn", "new_path": "scenes/new_scene_variant.tscn"}
```

### get_uid

Args:

```json
{"project_path": "/abs/path/to/project", "file_path": "scripts/player.gd"}
```

### update_project_uids

Args:

```json
{"project_path": "/abs/path/to/project"}
```

## Notes

- The CLI accepts either `snake_case` or `camelCase` keys.
- Scene/resource mutations delegate to `scripts/godot_operations.gd`.
- `run_project` stores state in `/tmp/godot_engine_tools_state.json`; logs are cached there for `get_debug_output`.
