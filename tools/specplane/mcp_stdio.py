"""Thin stdio MCP wrapping the same kernel as the CLI.

Catalog: retrieve, blast, impact, check_sync, list_gaps, run. Validate, promote, and reconcile are CLI-only.
No infer, specify, or implement tools.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from impact import format_impact, impact  # noqa: E402
from kernel import (  # noqa: E402
    blast,
    check_sync,
    format_blast,
    format_check_sync,
    format_list_gaps,
    format_retrieve,
    format_run,
    list_gaps,
    load_kernel,
    retrieve,
    run_sensors,
)
from validate import resolve_spec_root  # noqa: E402

MCP_TOOLS = ("retrieve", "blast", "impact", "check_sync", "list_gaps", "run")

_SCHEMAS: dict[str, dict[str, Any]] = {
    "retrieve": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "spec_root": {"type": "string"},
        },
        "required": ["id"],
    },
    "blast": {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "spec_root": {"type": "string"},
        },
        "required": ["id"],
    },
    "impact": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "SpecPlane id or open change folder. No git diff required.",
            },
            "spec_root": {"type": "string"},
        },
        "required": ["id"],
    },
    "check_sync": {
        "type": "object",
        "properties": {
            "spec_root": {"type": "string"},
            "changed_ids": {
                "type": "string",
                "description": "Comma-separated SpecPlane ids",
            },
            "change": {
                "type": "string",
                "description": "Scope coverage to specs/changes/<slug> (same as CLI --change)",
            },
        },
        "required": [],
    },
    "list_gaps": {
        "type": "object",
        "properties": {"spec_root": {"type": "string"}},
        "required": [],
    },
    "run": {
        "type": "object",
        "properties": {
            "change": {
                "type": "string",
                "description": "Open specs/changes/<slug> (same as CLI --change). Required.",
            },
            "spec_root": {"type": "string"},
            "repo": {
                "type": "string",
                "description": "Working directory for bound checks (default: cwd)",
            },
        },
        "required": ["change"],
    },
}


def tool_descriptors() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": f"SpecPlane kernel {name} (same function as the CLI)",
            "inputSchema": _SCHEMAS[name],
        }
        for name in MCP_TOOLS
    ]


def _kernel_from_args(arguments: dict[str, Any] | None):
    arguments = arguments or {}
    raw = arguments.get("spec_root")
    spec_root = resolve_spec_root(Path(raw) if raw else None, Path.cwd())
    if not spec_root.is_dir():
        raise FileNotFoundError(f"spec root does not exist: {spec_root}")
    return load_kernel(spec_root)


def dispatch(name: str, arguments: dict[str, Any] | None) -> str:
    arguments = arguments or {}
    if name not in MCP_TOOLS:
        raise ValueError(f"unknown tool: {name}")
    kernel = _kernel_from_args(arguments)
    if name == "retrieve":
        payload = retrieve(kernel, str(arguments.get("id") or ""))
        if payload is None:
            raise KeyError(f"not found: {arguments.get('id')}")
        return format_retrieve(payload)
    if name == "blast":
        payload = blast(kernel, str(arguments.get("id") or ""))
        if payload is None:
            raise KeyError(f"not found: {arguments.get('id')}")
        return format_blast(payload)
    if name == "impact":
        payload = impact(kernel, str(arguments.get("id") or ""))
        if payload is None:
            raise KeyError(f"not found: {arguments.get('id')}")
        return format_impact(payload)
    if name == "check_sync":
        raw_ids = str(arguments.get("changed_ids") or "")
        changed_ids = [part.strip() for part in raw_ids.split(",") if part.strip()]
        change_slug = str(arguments.get("change") or "").strip() or None
        return format_check_sync(
            check_sync(kernel, changed_ids, change_slug=change_slug)
        )
    if name == "run":
        change = str(arguments.get("change") or "").strip()
        if not change:
            raise ValueError("change is required")
        raw_repo = str(arguments.get("repo") or "").strip()
        repo = Path(raw_repo).resolve() if raw_repo else Path.cwd().resolve()
        return format_run(run_sensors(kernel, change, repo=repo))
    return format_list_gaps(list_gaps(kernel))


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    msg_id = message.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "specplane", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tool_descriptors()},
        }
    if method == "tools/call":
        params = message.get("params") or {}
        name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        try:
            text = dispatch(name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"content": [{"type": "text", "text": text}]},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": str(exc)},
            }
    if msg_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def _read_message(stdin) -> dict[str, Any] | None:
    header: dict[str, str] = {}
    while True:
        line = stdin.readline()
        if line == "":
            return None
        stripped = line.strip()
        if stripped == "":
            break
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            header[key.strip().lower()] = value.strip()
    length = int(header.get("content-length") or "0")
    if length <= 0:
        return None
    body = stdin.read(length)
    loaded = json.loads(body)
    if not isinstance(loaded, dict):
        return None
    return loaded


def serve(stdin=None, stdout=None) -> None:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    while True:
        message = _read_message(stdin)
        if message is None:
            return
        reply = handle_message(message)
        if reply is None:
            continue
        payload = json.dumps(reply)
        stdout.write(f"Content-Length: {len(payload.encode('utf-8'))}\r\n\r\n{payload}")
        stdout.flush()


if __name__ == "__main__":
    serve()
