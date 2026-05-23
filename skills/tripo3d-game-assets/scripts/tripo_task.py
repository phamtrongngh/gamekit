#!/usr/bin/env python3
"""Submit, poll, and download Tripo3D OpenAPI task outputs."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = os.environ.get("TRIPO_BASE_URL", "https://api.tripo3d.ai/v2/openapi").rstrip("/")
FINAL_STATUSES = {"success", "failed", "banned", "expired", "cancelled", "unknown"}


class TripoApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        code: int | None = None,
        retry_after: str | None = None,
        trace_id: str | None = None,
        payload: Any = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.code = code
        self.retry_after = retry_after
        self.trace_id = trace_id
        self.payload = payload


def api_key() -> str:
    key = os.environ.get("TRIPO_API_KEY")
    if not key:
        raise SystemExit("TRIPO_API_KEY is required in the environment.")
    return key


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def request_json(method: str, path: str, payload: Any | None = None) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key()}",
        "Accept": "application/json",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            trace_id = resp.headers.get("X-Tripo-Trace-ID")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        trace_id = exc.headers.get("X-Tripo-Trace-ID")
        retry_after = exc.headers.get("Retry-After")
        try:
            err_payload = json.loads(raw)
        except json.JSONDecodeError:
            err_payload = {"raw": raw}
        raise TripoApiError(
            f"HTTP {exc.code}: {err_payload}",
            http_status=exc.code,
            code=err_payload.get("code") if isinstance(err_payload, dict) else None,
            retry_after=retry_after,
            trace_id=trace_id,
            payload=err_payload,
        ) from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TripoApiError(f"Non-JSON response: {raw[:500]}", trace_id=trace_id) from exc

    code = parsed.get("code")
    if code not in (0, None):
        raise TripoApiError(
            parsed.get("message", f"Tripo API error code {code}"),
            code=code,
            trace_id=trace_id,
            payload=parsed,
        )

    data = parsed.get("data", parsed)
    if not isinstance(data, dict):
        data = {"value": data}
    return data, parsed, trace_id


def submit_task(payload: dict[str, Any]) -> tuple[str, dict[str, Any], str | None]:
    data, full_response, trace_id = request_json("POST", "/task", payload)
    task_id = data.get("task_id")
    if not task_id:
        raise TripoApiError(f"Task response did not include task_id: {full_response}", trace_id=trace_id, payload=full_response)
    return str(task_id), full_response, trace_id


def query_task(task_id: str) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    return request_json("GET", f"/task/{urllib.parse.quote(task_id)}")


def retry_seconds(error: TripoApiError, default_interval: float) -> float:
    if error.retry_after:
        try:
            return max(float(error.retry_after), default_interval)
        except ValueError:
            return default_interval
    if error.http_status == 429 or error.code in {1007, 2000}:
        return min(default_interval * 2, 60.0)
    return 0.0


def slug_piece(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return value.strip("._-") or "url"


def collect_urls(value: Any, prefix: str = "output") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(collect_urls(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(collect_urls(child, f"{prefix}.{index}"))
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        found.append((prefix, value))
    return found


def extension_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix
    if suffix and len(suffix) <= 8:
        return suffix
    return ".bin"


def download_url(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as resp, path.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 512)
            if not chunk:
                break
            f.write(chunk)


def download_outputs(task_data: dict[str, Any], out_dir: Path) -> dict[str, str]:
    output = task_data.get("output", {})
    urls = collect_urls(output)
    downloads: dict[str, str] = {}
    used_names: set[str] = set()

    for label, url in urls:
        base = slug_piece(label.removeprefix("output."))
        name = f"{base}{extension_from_url(url)}"
        counter = 2
        while name in used_names:
            name = f"{base}_{counter}{extension_from_url(url)}"
            counter += 1
        used_names.add(name)
        dest = out_dir / name
        download_url(url, dest)
        downloads[label] = str(dest)

    if downloads:
        write_json(out_dir / "downloads.json", downloads)
    return downloads


def poll_task(task_id: str, out_dir: Path, interval: float, timeout_seconds: float, download: bool) -> dict[str, Any]:
    started = time.monotonic()
    last_status = None

    while True:
        try:
            task_data, full_response, trace_id = query_task(task_id)
        except TripoApiError as exc:
            sleep_for = retry_seconds(exc, interval)
            if sleep_for <= 0:
                raise
            print(f"Transient API limit for {task_id}; sleeping {sleep_for:.1f}s", file=sys.stderr)
            time.sleep(sleep_for)
            continue

        status = str(task_data.get("status", "unknown"))
        if status != last_status:
            progress = task_data.get("progress")
            queue = task_data.get("queuing_num")
            left = task_data.get("running_left_time")
            print(f"{task_id}: status={status} progress={progress} queue={queue} eta={left}", file=sys.stderr)
            last_status = status

        if trace_id:
            task_data.setdefault("_trace_ids", []).append(trace_id)

        write_json(out_dir / "task.latest.json", task_data)
        write_json(out_dir / "response.latest.json", full_response)

        if status in FINAL_STATUSES:
            write_json(out_dir / f"task.{status}.json", task_data)
            if status == "success" and download:
                downloads = download_outputs(task_data, out_dir)
                print(f"Downloaded {len(downloads)} output URL(s).", file=sys.stderr)
            return task_data

        if time.monotonic() - started > timeout_seconds:
            raise TimeoutError(f"Timed out waiting for task {task_id} after {timeout_seconds:.0f}s")

        time.sleep(interval)


def command_submit(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    payload = read_json(Path(args.payload))
    task_id, response, trace_id = submit_task(payload)
    write_json(out_dir / "submit_response.json", response)
    (out_dir / "task_id.txt").write_text(f"{task_id}\n", encoding="utf-8")
    if trace_id:
        (out_dir / "submit_trace_id.txt").write_text(f"{trace_id}\n", encoding="utf-8")
    print(task_id)
    return 0


def command_poll(args: argparse.Namespace) -> int:
    poll_task(args.task_id, Path(args.out_dir), args.poll_interval, args.timeout, args.download)
    return 0


def command_run(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    payload = read_json(Path(args.payload))
    task_id, response, trace_id = submit_task(payload)
    write_json(out_dir / "submit_response.json", response)
    (out_dir / "task_id.txt").write_text(f"{task_id}\n", encoding="utf-8")
    if trace_id:
        (out_dir / "submit_trace_id.txt").write_text(f"{trace_id}\n", encoding="utf-8")
    print(task_id)
    if not args.no_poll:
        poll_task(task_id, out_dir, args.poll_interval, args.timeout, args.download)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit", help="Submit a task payload and print task_id.")
    submit.add_argument("--payload", required=True, help="Path to JSON task payload.")
    submit.add_argument("--out-dir", default=".", help="Directory for response files.")
    submit.set_defaults(func=command_submit)

    poll = subparsers.add_parser("poll", help="Poll an existing task_id.")
    poll.add_argument("--task-id", required=True)
    poll.add_argument("--out-dir", default=".", help="Directory for task response and downloads.")
    poll.add_argument("--poll-interval", type=float, default=2.0)
    poll.add_argument("--timeout", type=float, default=1800.0)
    poll.add_argument("--download", action="store_true", help="Download URL values from output on success.")
    poll.set_defaults(func=command_poll)

    run = subparsers.add_parser("run", help="Submit a payload, then poll until final status.")
    run.add_argument("--payload", required=True, help="Path to JSON task payload.")
    run.add_argument("--out-dir", default=".", help="Directory for response files and downloads.")
    run.add_argument("--poll-interval", type=float, default=2.0)
    run.add_argument("--timeout", type=float, default=1800.0)
    run.add_argument("--download", action="store_true", help="Download URL values from output on success.")
    run.add_argument("--no-poll", action="store_true", help="Only submit the task.")
    run.set_defaults(func=command_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except TripoApiError as exc:
        print(f"Tripo API error: {exc}", file=sys.stderr)
        if exc.trace_id:
            print(f"Trace ID: {exc.trace_id}", file=sys.stderr)
        if exc.payload is not None:
            print(json.dumps(exc.payload, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
