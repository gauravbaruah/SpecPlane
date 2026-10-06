#!/usr/bin/env python3
"""SpecPlane kernel CLI: validate, retrieve, blast, impact, check_sync, reconcile, list_gaps, run, promote, accept, init, context.

Simple commands. Agents call them. No LLM in the loop.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from impact import format_impact, impact  # noqa: E402
from kernel import (  # noqa: E402
    blast,
    build_context,
    check_sync,
    default_changed_ids,
    format_accept,
    format_blast,
    format_check_sync,
    format_context,
    format_list_gaps,
    format_promote,
    format_reconcile,
    format_retrieve,
    format_run,
    list_gaps,
    receipt_validate,
    load_kernel,
    accept_ids,
    promote_change,
    reconcile,
    run_sensors,
    retrieve,
    structural_validate,
)
from initkit import default_kit_root, init_kit, uninstall_kit  # noqa: E402
from validate import resolve_spec_root  # noqa: E402


def _git_lines(repo: Path, args: list[str]) -> list[str]:
    try:
        out = subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def git_changed_files(repo: Path) -> list[str]:
    """Staged + unstaged + untracked (Q115). Paths are relative to repo, not the git toplevel."""
    names = set(_git_lines(repo, ["diff", "--name-only", "--relative", "--cached"]))
    names.update(_git_lines(repo, ["diff", "--name-only", "--relative", "HEAD"]))
    if not names:
        names.update(_git_lines(repo, ["diff", "--name-only", "--relative"]))
    names.update(_git_lines(repo, ["ls-files", "--others", "--exclude-standard"]))
    return sorted(names)


def paths_for_config_dir(repo: Path, config_dir: Path, files: list[str]) -> list[str]:
    """Drop the config-dir prefix when repo is the git toplevel and config lives below it."""
    try:
        prefix = config_dir.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return files
    if not prefix or prefix == ".":
        return files
    prefix = prefix.rstrip("/") + "/"
    adjusted: list[str] = []
    for name in files:
        norm = name.replace("\\", "/")
        if norm.startswith(prefix):
            adjusted.append(norm[len(prefix) :])
        else:
            adjusted.append(norm)
    return adjusted


def add_root_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--spec-root",
        type=Path,
        help="Path to specs/ (default: specplane.config.json specRoot, else ./specs)",
    )
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to search for specplane.config.json",
    )


def cmd_validate(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    report = structural_validate(spec_root)
    for finding in report.findings:
        sys.stderr.write(finding.format() + "\n")
    error_count = len(report.errors)
    warn_count = len(report.warnings)
    print(
        f"Checked {report.file_count} spec(s): {error_count} error(s), {warn_count} warning(s)."
    )
    receipt = receipt_validate(error_count)
    if receipt:
        print(receipt)
    if error_count:
        return 1
    if args.strict_warnings and warn_count:
        return 1
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    payload = retrieve(kernel, args.spec_id)
    if payload is None:
        sys.stderr.write(f"not found: {args.spec_id}\n")
        return 1
    if payload["bit"] == "inferred":
        sys.stderr.write(f"inferred (not live): {args.spec_id}\n")
    print(format_retrieve(payload), end="")
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    payload = build_context(kernel, args.target, args.change or None)
    print(format_context(kernel, payload), end="")
    if payload.get("unknown"):
        sys.stderr.write(f"not found: {args.target}\n")
        return 1
    return 0


def cmd_blast(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    payload = blast(kernel, args.spec_id)
    if payload is None:
        sys.stderr.write(f"not found: {args.spec_id}\n")
        return 1
    print(format_blast(payload), end="")
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    payload = impact(kernel, args.spec_id)
    if payload is None:
        sys.stderr.write(f"not found: {args.spec_id}\n")
        return 1
    print(format_impact(payload), end="")
    return 0


def cmd_check_sync(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    changed_ids = [part.strip() for part in (args.changed_ids or "").split(",") if part.strip()]
    unmapped: list[str] = []
    files: list[str] | None = None
    if not changed_ids:
        repo = (args.repo or Path.cwd()).resolve()
        files = paths_for_config_dir(repo, args.config_dir.resolve(), git_changed_files(repo))
        changed_ids, unmapped = default_changed_ids(kernel, files, repo)
    payload = check_sync(
        kernel,
        changed_ids,
        change_slug=args.change or None,
        changed_files=files,
    )
    if unmapped:
        payload["unmapped_changed"] = unmapped
    print(format_check_sync(payload), end="")
    if payload.get("unknown_change"):
        sys.stderr.write(f"unknown change: {payload['unknown_change']}\n")
    if payload["ok"]:
        return 0
    return 1


def cmd_reconcile(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    repo = (args.repo or Path.cwd()).resolve()
    files = paths_for_config_dir(repo, args.config_dir.resolve(), git_changed_files(repo))
    payload = reconcile(kernel, files, repo=repo)
    print(format_reconcile(payload), end="")
    return 0


def cmd_list_gaps(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    print(format_list_gaps(list_gaps(kernel)), end="")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    repo = (args.repo or Path.cwd()).resolve()
    payload = run_sensors(kernel, args.change, repo=repo)
    print(format_run(payload), end="")
    if payload.get("unknown_change"):
        sys.stderr.write(f"unknown change: {payload['unknown_change']}\n")
    if payload["ok"]:
        return 0
    return 1


def cmd_promote(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    if getattr(args, "ids", ""):
        sys.stderr.write("promote --ids is now accept --ids\n")
        return 1
    slug = str(getattr(args, "slug", "") or "").strip()
    if not slug:
        sys.stderr.write("promote requires a change slug\n")
        return 1
    kernel = load_kernel(spec_root)
    payload = promote_change(kernel, slug)
    if not payload["ok"]:
        for problem in payload["problems"]:
            sys.stderr.write(problem + "\n")
        print(format_promote(payload), end="")
        return 1
    print(format_promote(payload), end="")
    return 0


def cmd_accept(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    spec_ids = [part.strip() for part in (args.ids or "").split(",")]
    payload = accept_ids(kernel, spec_ids)
    if not payload["ok"]:
        for problem in payload["problems"]:
            sys.stderr.write(problem + "\n")
        return 1
    print(format_accept(payload), end="")
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    from mcp_stdio import serve, set_default_spec_root

    if args.spec_root is not None:
        spec_root = resolve_spec_root(args.spec_root, args.config_dir)
        if not spec_root.is_dir():
            sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
            return 1
        set_default_spec_root(spec_root)
    else:
        set_default_spec_root(None)
    serve()
    return 0


def cmd_view(args: argparse.Namespace) -> int:
    from view import build_payload, current_project_id, serve, write_site

    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    out = args.out if args.out is not None else args.config_dir / ".specplane" / "view"
    kernel = load_kernel(spec_root)
    project_id = current_project_id(args.config_dir.resolve())
    write_site(build_payload(kernel, project_id), out)
    return serve(out, args.open_browser, spec_root, project_id)


def cmd_usage(args: argparse.Namespace) -> int:
    from telemetry import read_events, set_enabled, status_lines, usage_report_text

    action = args.usage_command
    if action == "report":
        sys.stdout.write(usage_report_text())
        return 0
    if action == "enable":
        set_enabled(True)
        sys.stdout.write("Local command events are on. Nothing is uploaded.\n")
        sys.stdout.write("Turn off with: usage disable\n")
        return 0
    if action == "disable":
        set_enabled(False)
        sys.stdout.write("Local command events are off.\n")
        return 0
    if action == "show":
        body = read_events()
        if not body.strip():
            sys.stdout.write("No local events.\n")
            return 0
        sys.stdout.write(body if body.endswith("\n") else body + "\n")
        return 0
    for line in status_lines():
        sys.stdout.write(line + "\n")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    dest = (args.dest or Path.cwd()).resolve()
    kit_root = (args.kit_root or default_kit_root()).resolve()
    code, notes = init_kit(
        dest,
        kit_root,
        with_cli=not args.kit_only,
        force=args.force,
    )
    stream = sys.stderr if code else sys.stdout
    for note in notes:
        stream.write(note + "\n")
    return code


def cmd_uninstall(args: argparse.Namespace) -> int:
    dest = (args.dest or Path.cwd()).resolve()
    code, notes = uninstall_kit(dest)
    stream = sys.stderr if code else sys.stdout
    for note in notes:
        stream.write(note + "\n")
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SpecPlane kernel CLI (validate / retrieve / context / blast / impact / check_sync / reconcile / list_gaps / run / promote / accept / init / uninstall / view / usage)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Structural YAML / links / changelog")
    add_root_args(p_val)
    p_val.add_argument("--strict-warnings", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    p_ret = sub.add_parser("retrieve", help="One live graph, leftovers, open delta")
    add_root_args(p_ret)
    p_ret.add_argument("spec_id", help="SpecPlane id (e.g. capability.authentication)")
    p_ret.set_defaults(func=cmd_retrieve)

    p_ctx = sub.add_parser(
        "context",
        help="Task slice for one spec id or one file; an unmatched file stays unmapped",
    )
    add_root_args(p_ctx)
    p_ctx.add_argument("target", help="SpecPlane id or a repo-relative file path")
    p_ctx.add_argument(
        "--change",
        default="",
        help="Name one open specs/changes/<slug> folder as the implementation context",
    )
    p_ctx.set_defaults(func=cmd_context)

    p_blast = sub.add_parser("blast", help="Computed affects tree; foundations are terminal")
    add_root_args(p_blast)
    p_blast.add_argument("spec_id", help="SpecPlane id or start node")
    p_blast.set_defaults(func=cmd_blast)

    p_impact = sub.add_parser(
        "impact",
        help="Explain one affected subgraph and project system, product, quality, governance, ownership",
    )
    add_root_args(p_impact)
    p_impact.add_argument("spec_id", help="SpecPlane id or open change folder")
    p_impact.set_defaults(func=cmd_impact)

    p_sync = sub.add_parser(
        "check_sync",
        help="Declared coverage vs an open change; not behavioral agreement",
    )
    add_root_args(p_sync)
    p_sync.add_argument(
        "--changed-ids",
        default="",
        help="Comma-separated SpecPlane ids (default: spec YAML plus declared path matches)",
    )
    p_sync.add_argument(
        "--change",
        default="",
        help="Scope coverage to this change slug (OPEN or PROMOTED)",
    )
    p_sync.add_argument("--repo", type=Path, default=None, help="Git repo for default changed set")
    p_sync.set_defaults(func=cmd_check_sync)

    p_rec = sub.add_parser(
        "reconcile",
        help="Declared realization.paths vs the tree and changed files; advisory",
    )
    add_root_args(p_rec)
    p_rec.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Git repo whose changed files are compared to declared paths",
    )
    p_rec.set_defaults(func=cmd_reconcile)

    p_gaps = sub.add_parser(
        "list_gaps",
        help="Kernel-generic gap queue (advisory; exit 0)",
    )
    add_root_args(p_gaps)
    p_gaps.set_defaults(func=cmd_list_gaps)

    p_run = sub.add_parser(
        "run",
        help="Invoke checks already bound on one change; not a test runner",
    )
    add_root_args(p_run)
    p_run.add_argument(
        "--change",
        required=True,
        help="Change slug whose success.yaml binds the checks (OPEN or PROMOTED)",
    )
    p_run.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Working directory for bound checks (default: cwd). Env is inherited.",
    )
    p_run.set_defaults(func=cmd_run)

    p_promote = sub.add_parser(
        "promote",
        help="Apply an open change into live YAML and archive it. CLI only.",
    )
    add_root_args(p_promote)
    p_promote.add_argument("slug", nargs="?", default="", help="Open specs/changes/<slug> to promote")
    p_promote.add_argument(
        "--ids",
        default="",
        help=argparse.SUPPRESS,
    )
    p_promote.set_defaults(func=cmd_promote)

    p_accept = sub.add_parser(
        "accept",
        help="Drop inferred on named ids and append a changelog row. CLI only.",
    )
    add_root_args(p_accept)
    p_accept.add_argument(
        "--ids",
        default="",
        help="Comma-separated inferred ids to accept. Required. Never accepts the whole inventory.",
    )
    p_accept.set_defaults(func=cmd_accept)

    p_init = sub.add_parser(
        "init",
        help="Copy the kit into a product repo; create empty specs/ folders",
    )
    p_init.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Product repo (default: cwd). Must not be the SpecPlane kit root.",
    )
    p_init.add_argument(
        "--kit-root",
        type=Path,
        default=None,
        help="SpecPlane clone to copy from (default: parent of tools/specplane)",
    )
    p_init.add_argument(
        "--kit-only",
        action="store_true",
        help="Skip copying tools/specplane CLI files",
    )
    p_init.add_argument(
        "--force",
        action="store_true",
        help="Replace dest/specplane if it already exists",
    )
    p_init.set_defaults(func=cmd_init)

    p_uninstall = sub.add_parser(
        "uninstall",
        help="Remove the kit copy from a product repo. Leave specs/ in place.",
    )
    p_uninstall.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Product repo (default: cwd). Must not be this SpecPlane checkout.",
    )
    p_uninstall.set_defaults(func=cmd_uninstall)

    p_mcp = sub.add_parser(
        "mcp",
        help="Start the stdio MCP server (retrieve, blast, impact, check_sync, list_gaps, run)",
        description=(
            "Start the existing stdio MCP server. "
            "Tools: retrieve, blast, impact, check_sync, list_gaps, run."
        ),
    )
    add_root_args(p_mcp)
    p_mcp.set_defaults(func=cmd_mcp)

    p_view = sub.add_parser(
        "view",
        help="Human readout of retrieve. Generate .specplane/view and serve 127.0.0.1",
    )
    add_root_args(p_view)
    p_view.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory (default: .specplane/view). Still serves.",
    )
    p_view.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Also launch the browser",
    )
    p_view.set_defaults(func=cmd_view)

    def add_usage_command(name: str, help_text: str) -> None:
        parser = sub.add_parser(name, help=help_text)
        actions = parser.add_subparsers(dest="usage_command", required=True)
        for action, action_help in (
            ("status", "Whether the local log is on"),
            ("show", "Print the local events. They stay on this machine."),
            ("enable", "Turn the local log on"),
            ("disable", "Turn the local log off"),
            ("report", "Print counts for the last 30 days. Nothing is sent."),
        ):
            actions.add_parser(action, help=action_help).set_defaults(
                func=cmd_usage, usage_command=action
            )

    add_usage_command(
        "usage",
        "Local command events. On by default. Nothing is uploaded.",
    )
    add_usage_command(
        "telemetry",
        "Alias of usage. Local command events. Nothing is uploaded.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    from telemetry import record_command

    started = time.perf_counter()
    command = "usage"
    code = 1
    try:
        parser = build_parser()
        args = parser.parse_args(argv)
        command = str(args.command or "usage")
        if command in {"usage", "telemetry"}:
            subcommand = str(getattr(args, "usage_command", "") or "")
            if subcommand:
                command = f"usage_{subcommand}"
        code = int(args.func(args))
        return code
    except SystemExit as exc:
        raw = exc.code
        if isinstance(raw, int):
            code = raw
        elif raw is None:
            code = 0
        else:
            code = 1
        raise
    except Exception:
        code = 1
        raise
    finally:
        record_command(command, code, started)


if __name__ == "__main__":
    sys.exit(main())
