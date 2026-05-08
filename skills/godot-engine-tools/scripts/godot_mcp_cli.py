#!/usr/bin/env python3
"""Local CLI port of the Godot MCP server.

This script mirrors the original MCP tool surface so a Codex skill can invoke
equivalent functionality without requiring dynamic MCP tool registration.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEBUG = os.environ.get("GODOT_MCP_DEBUG", "").lower() == "true"
STATE_PATH = Path("/tmp/godot_engine_tools_state.json")
SCRIPT_DIR = Path(__file__).resolve().parent
OPERATIONS_SCRIPT = SCRIPT_DIR / "godot_operations.gd"

PARAMETER_MAPPINGS = {
    "projectPath": "project_path",
    "scenePath": "scene_path",
    "rootNodeType": "root_node_type",
    "parentNodePath": "parent_node_path",
    "nodeType": "node_type",
    "nodeName": "node_name",
    "texturePath": "texture_path",
    "nodePath": "node_path",
    "outputPath": "output_path",
    "meshItemNames": "mesh_item_names",
    "newPath": "new_path",
    "filePath": "file_path",
}


def log_debug(message: str) -> None:
    if DEBUG:
        print(f"[godot-engine-tools] {message}", file=sys.stderr)


def success(tool: str, result: dict[str, Any]) -> int:
    print(json.dumps({"ok": True, "tool": tool, "result": result}, ensure_ascii=True))
    return 0


def failure(tool: str, message: str, **extra: Any) -> int:
    payload: dict[str, Any] = {"ok": False, "tool": tool, "error": message}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=True))
    return 1


def normalize_parameters(value: Any) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, child in value.items():
            mapped_key = PARAMETER_MAPPINGS.get(key, key)
            normalized[mapped_key] = normalize_parameters(child)
        return normalized
    if isinstance(value, list):
        return [normalize_parameters(item) for item in value]
    return value


def ensure_safe_path(path_value: str, label: str) -> Path:
    if not path_value or ".." in path_value:
        raise ValueError(f"Invalid {label}: {path_value}")
    return Path(path_value).expanduser().resolve()


def detect_godot_path() -> str:
    env_path = os.environ.get("GODOT_PATH")
    candidates: list[str] = []
    if env_path:
        candidates.append(env_path)
    candidates.append("godot")

    home = Path.home()
    system = platform.system().lower()
    if system == "darwin":
        candidates.extend(
            [
                "/Applications/Godot.app/Contents/MacOS/Godot",
                "/Applications/Godot_4.app/Contents/MacOS/Godot",
                str(home / "Applications/Godot.app/Contents/MacOS/Godot"),
                str(home / "Applications/Godot_4.app/Contents/MacOS/Godot"),
            ]
        )
    elif system == "windows":
        candidates.extend(
            [
                r"C:\Program Files\Godot\Godot.exe",
                r"C:\Program Files\Godot_4\Godot.exe",
                str(Path(os.environ.get("USERPROFILE", "")) / "Godot/Godot.exe"),
            ]
        )
    else:
        candidates.extend(
            [
                "/usr/bin/godot",
                "/usr/local/bin/godot",
                "/snap/bin/godot",
                str(home / ".local/bin/godot"),
            ]
        )

    for candidate in candidates:
        if not candidate:
            continue
        try:
            proc = subprocess.run(
                [candidate, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            log_debug(f"Detected Godot at {candidate}: {proc.stdout.strip()}")
            return candidate
        except Exception:
            continue
    raise RuntimeError("Could not find a valid Godot executable. Set GODOT_PATH explicitly.")


def read_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(data: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")


def pid_is_running(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def collect_process_output(pid: int) -> tuple[str, str]:
    try:
        completed = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.stdout.strip(), completed.stderr.strip()
    except Exception as exc:
        return "", str(exc)


def run_tool_process(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    log_debug("Executing: " + " ".join(command))
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def find_projects(directory: Path, recursive: bool) -> list[dict[str, str]]:
    projects: list[dict[str, str]] = []
    if (directory / "project.godot").exists():
        projects.append({"path": str(directory), "name": directory.name})

    try:
        for child in directory.iterdir():
            if not child.is_dir() or child.name.startswith("."):
                continue
            if (child / "project.godot").exists():
                projects.append({"path": str(child), "name": child.name})
            elif recursive:
                projects.extend(find_projects(child, True))
    except PermissionError:
        pass
    return projects


def project_structure(project_path: Path) -> dict[str, list[str]]:
    structure = {"scenes": [], "scripts": [], "assets": [], "other": []}
    for child in project_path.iterdir():
        if not child.is_dir() or child.name.startswith("."):
            continue
        name = child.name.lower()
        if name == "scenes" or "scene" in name:
            structure["scenes"].append(child.name)
        elif name == "scripts" or "script" in name:
            structure["scripts"].append(child.name)
        elif name in {"assets", "textures", "models", "sounds", "music"}:
            structure["assets"].append(child.name)
        else:
            structure["other"].append(child.name)
    return structure


def read_project_config(project_file: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {"name": project_file.parent.name}
    lines = project_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("config/name="):
            metadata["configName"] = stripped.split("=", 1)[1].strip().strip('"')
        elif stripped.startswith("run/main_scene="):
            metadata["mainScene"] = stripped.split("=", 1)[1].strip().strip('"')
        elif stripped.startswith("config/features="):
            metadata["features"] = stripped.split("=", 1)[1].strip()
    return metadata


def operation_params(args: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: args[key] for key in keys if key in args and args[key] is not None}


def call_godot_operation(tool: str, args: dict[str, Any], required_keys: list[str]) -> int:
    for key in required_keys:
        if not args.get(key):
            return failure(tool, f"Missing required argument: {key}")

    project_path = ensure_safe_path(args["project_path"], "project_path")
    if not (project_path / "project.godot").exists():
        return failure(tool, f"Not a valid Godot project: {project_path}")

    godot = detect_godot_path()
    payload = operation_params(
        args,
        [
            "scene_path",
            "root_node_type",
            "parent_node_path",
            "node_type",
            "node_name",
            "properties",
            "texture_path",
            "node_path",
            "output_path",
            "mesh_item_names",
            "new_path",
            "file_path",
            "project_path",
        ],
    )

    command = [
        godot,
        "--headless",
        "--path",
        str(project_path),
        "--script",
        str(OPERATIONS_SCRIPT),
        "resave_resources" if tool == "update_project_uids" else tool,
        json.dumps(payload, ensure_ascii=True),
        "--debug-godot",
    ]
    completed = run_tool_process(command, cwd=project_path)
    if completed.returncode != 0:
        return failure(
            tool,
            "Godot operation failed",
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )
    return success(
        tool,
        {
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "project_path": str(project_path),
        },
    )


def handle_launch_editor(args: dict[str, Any]) -> int:
    tool = "launch_editor"
    project_path = args.get("project_path")
    if not project_path:
        return failure(tool, "Missing required argument: project_path")
    project_dir = ensure_safe_path(project_path, "project_path")
    if not (project_dir / "project.godot").exists():
        return failure(tool, f"Not a valid Godot project: {project_dir}")
    godot = detect_godot_path()
    process = subprocess.Popen(
        [godot, "-e", "--path", str(project_dir)],
        cwd=str(project_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return success(tool, {"project_path": str(project_dir), "pid": process.pid})


def handle_run_project(args: dict[str, Any]) -> int:
    tool = "run_project"
    project_path = args.get("project_path")
    if not project_path:
        return failure(tool, "Missing required argument: project_path")
    project_dir = ensure_safe_path(project_path, "project_path")
    if not (project_dir / "project.godot").exists():
        return failure(tool, f"Not a valid Godot project: {project_dir}")

    state = read_state()
    if pid_is_running(state.get("pid")):
        return failure(tool, "A Godot project is already running", activePid=state.get("pid"))

    godot = detect_godot_path()
    command = [godot, "--path", str(project_dir), "--debug"]
    scene = args.get("scene")
    if scene:
        command.extend(["--scene", scene])

    stdout_log = Path("/tmp/godot_engine_tools_stdout.log")
    stderr_log = Path("/tmp/godot_engine_tools_stderr.log")
    stdout_handle = stdout_log.open("w", encoding="utf-8")
    stderr_handle = stderr_log.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=str(project_dir),
        stdout=stdout_handle,
        stderr=stderr_handle,
        start_new_session=True,
        text=True,
    )
    write_state(
        {
            "pid": process.pid,
            "project_path": str(project_dir),
            "scene": scene,
            "stdoutLog": str(stdout_log),
            "stderrLog": str(stderr_log),
            "startedAt": time.time(),
        }
    )
    return success(
        tool,
        {
            "project_path": str(project_dir),
            "scene": scene,
            "pid": process.pid,
            "stdoutLog": str(stdout_log),
            "stderrLog": str(stderr_log),
        },
    )


def handle_get_debug_output(_: dict[str, Any]) -> int:
    tool = "get_debug_output"
    state = read_state()
    if not state:
        return success(tool, {"running": False, "stdout": "", "stderr": ""})

    pid = state.get("pid")
    stdout = Path(state.get("stdoutLog", ""))
    stderr = Path(state.get("stderrLog", ""))
    running = pid_is_running(pid)
    stdout_text = stdout.read_text(encoding="utf-8", errors="ignore") if stdout.exists() else ""
    stderr_text = stderr.read_text(encoding="utf-8", errors="ignore") if stderr.exists() else ""
    ps_stdout, ps_stderr = collect_process_output(pid) if running else ("", "")
    return success(
        tool,
        {
            "running": running,
            "pid": pid,
            "project_path": state.get("project_path"),
            "scene": state.get("scene"),
            "stdout": stdout_text,
            "stderr": stderr_text,
            "processInfo": ps_stdout,
            "processInfoError": ps_stderr,
        },
    )


def handle_stop_project(_: dict[str, Any]) -> int:
    tool = "stop_project"
    state = read_state()
    pid = state.get("pid")
    if not pid or not pid_is_running(pid):
        return success(tool, {"stopped": False, "message": "No active Godot runtime found"})

    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return success(tool, {"stopped": False, "message": "Process already exited", "pid": pid})
    time.sleep(0.5)
    stopped = not pid_is_running(pid)
    if stopped:
        write_state({})
    return success(tool, {"stopped": stopped, "pid": pid})


def handle_get_godot_version(_: dict[str, Any]) -> int:
    tool = "get_godot_version"
    godot = detect_godot_path()
    completed = run_tool_process([godot, "--version"])
    if completed.returncode != 0:
        return failure(tool, "Failed to read Godot version", stderr=completed.stderr)
    return success(tool, {"godotPath": godot, "version": completed.stdout.strip()})


def handle_list_projects(args: dict[str, Any]) -> int:
    tool = "list_projects"
    directory = args.get("directory")
    if not directory:
        return failure(tool, "Missing required argument: directory")
    search_root = ensure_safe_path(directory, "directory")
    if not search_root.exists():
        return failure(tool, f"Directory does not exist: {search_root}")
    projects = find_projects(search_root, bool(args.get("recursive", False)))
    return success(tool, {"directory": str(search_root), "recursive": bool(args.get("recursive", False)), "projects": projects})


def handle_get_project_info(args: dict[str, Any]) -> int:
    tool = "get_project_info"
    project_path = args.get("project_path")
    if not project_path:
        return failure(tool, "Missing required argument: project_path")
    project_dir = ensure_safe_path(project_path, "project_path")
    project_file = project_dir / "project.godot"
    if not project_file.exists():
        return failure(tool, f"Not a valid Godot project: {project_dir}")
    metadata = read_project_config(project_file)
    result = {
        "project_path": str(project_dir),
        "project_file": str(project_file),
        "metadata": metadata,
        "structure": project_structure(project_dir),
    }
    return success(tool, result)


TOOL_HANDLERS = {
    "launch_editor": handle_launch_editor,
    "run_project": handle_run_project,
    "get_debug_output": handle_get_debug_output,
    "stop_project": handle_stop_project,
    "get_godot_version": handle_get_godot_version,
    "list_projects": handle_list_projects,
    "get_project_info": handle_get_project_info,
    "create_scene": lambda args: call_godot_operation("create_scene", args, ["project_path", "scene_path"]),
    "add_node": lambda args: call_godot_operation("add_node", args, ["project_path", "scene_path", "node_type", "node_name"]),
    "load_sprite": lambda args: call_godot_operation("load_sprite", args, ["project_path", "scene_path", "node_path", "texture_path"]),
    "export_mesh_library": lambda args: call_godot_operation("export_mesh_library", args, ["project_path", "scene_path", "output_path"]),
    "save_scene": lambda args: call_godot_operation("save_scene", args, ["project_path", "scene_path"]),
    "get_uid": lambda args: call_godot_operation("get_uid", args, ["project_path", "file_path"]),
    "update_project_uids": lambda args: call_godot_operation("update_project_uids", args, ["project_path"]),
}


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CLI port of the Godot MCP tools")
    parser.add_argument("tool", choices=sorted(TOOL_HANDLERS))
    parser.add_argument(
        "--json",
        default="{}",
        help="JSON object containing tool arguments. Both snake_case and camelCase are accepted.",
    )
    return parser.parse_args()


def main() -> int:
    ns = parse_cli()
    try:
        raw_args = json.loads(ns.json)
    except json.JSONDecodeError as exc:
        return failure(ns.tool, f"Invalid JSON arguments: {exc}")

    if not isinstance(raw_args, dict):
        return failure(ns.tool, "Tool arguments must decode to a JSON object")

    try:
        normalized_args = normalize_parameters(raw_args)
        return TOOL_HANDLERS[ns.tool](normalized_args)
    except Exception as exc:
        return failure(ns.tool, str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
