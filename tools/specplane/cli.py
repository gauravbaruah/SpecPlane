#!/usr/bin/env python3
"""SpecPlane kernel CLI: validate, retrieve, blast, check_sync.

Simple commands. Agents call them. No LLM in the loop.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kernel import (  # noqa: E402
    blast,
    check_sync,
    format_blast,
    format_check_sync,
    format_retrieve,
    load_kernel,
    map_changed_files,
    retrieve,
    structural_validate,
)
from validate import resolve_spec_root  # noqa: E402


def git_changed_files(repo: Path) -> list[str]:
    try:
        staged = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"], cwd=repo, text=True
        ).splitlines()
        unstaged = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"], cwd=repo, text=True
        ).splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return sorted({line.strip() for line in staged + unstaged if line.strip()})


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


def cmd_check_sync(args: argparse.Namespace) -> int:
    spec_root = resolve_spec_root(args.spec_root, args.config_dir)
    if not spec_root.is_dir():
        sys.stderr.write(f"spec root does not exist: {spec_root} (pass --spec-root)\n")
        return 1
    kernel = load_kernel(spec_root)
    changed_ids = [part for part in (args.changed_ids or "").split(",") if part.strip()]
    changed_ids = [part.strip() for part in changed_ids]
    if not changed_ids:
        repo = (args.repo or Path.cwd()).resolve()
        files = git_changed_files(repo)
        changed_ids = map_changed_files(kernel, files)
    payload = check_sync(kernel, changed_ids)
    print(format_check_sync(payload), end="")
    if payload["ok"]:
        return 0
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SpecPlane kernel CLI (validate / retrieve / blast / check_sync)"
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

    p_blast = sub.add_parser("blast", help="Computed affects tree; foundations are terminal")
    add_root_args(p_blast)
    p_blast.add_argument("spec_id", help="SpecPlane id or start node")
    p_blast.set_defaults(func=cmd_blast)

    p_sync = sub.add_parser(
        "check_sync",
        help="Fail if changed ids are not covered by an open change, or blast is empty",
    )
    add_root_args(p_sync)
    p_sync.add_argument(
        "--changed-ids",
        default="",
        help="Comma-separated SpecPlane ids (default: spec YAML in git diff)",
    )
    p_sync.add_argument("--repo", type=Path, default=None, help="Git repo for default changed set")
    p_sync.set_defaults(func=cmd_check_sync)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
