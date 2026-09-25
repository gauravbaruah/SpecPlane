#!/usr/bin/env python3
"""Flag code changes that landed without spec updates (and the reverse).

Coarse path-name reminder. The declared file↔promise check is ``reconcile``.
This script does not read source bodies and does not replace that command.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SPEC_PREFIXES = ("specs/",)
IGNORE_PREFIXES = (
    ".github/",
    "tools/specplane/",
    "specplane/",
    "docs/",
    "legacy/",
    ".agents/",
    ".cursor/",
)


def git_files(scope: str, repo: Path) -> list[str]:
    if scope == "changed":
        cmd = ["git", "diff", "--name-only", "HEAD"]
        staged = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"], cwd=repo, text=True
        ).splitlines()
        unstaged = subprocess.check_output(cmd, cwd=repo, text=True).splitlines()
        return sorted({line.strip() for line in staged + unstaged if line.strip()})
    out = subprocess.check_output(["git", "ls-files"], cwd=repo, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def classify(files: list[str]) -> tuple[list[str], list[str]]:
    specs = [
        path
        for path in files
        if path.startswith(SPEC_PREFIXES) and path.endswith((".yaml", ".yml"))
    ]
    code = [
        path
        for path in files
        if path not in specs
        and not any(path.startswith(prefix) for prefix in IGNORE_PREFIXES)
        and not path.endswith((".md", ".png", ".json"))
    ]
    return specs, code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SpecPlane drift reminder (local/agent; not a git hook)"
    )
    parser.add_argument("--scope", choices=["changed", "full"], default="changed")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    files = git_files(args.scope, repo)
    specs, code = classify(files)
    has_specs = (repo / "specs").is_dir()

    blockers: list[str] = []
    warnings: list[str] = []

    if args.scope == "changed" and has_specs and code and not specs:
        blockers.append(
            "Code changed without spec YAML updates in this change set."
        )
    if args.scope == "changed" and specs and not code:
        warnings.append("Specs changed without code changes; confirm that is intentional.")

    print("Spec drift report")
    print("- named join: reconcile (this report does not compare declared paths)")
    print(f"- scope: {args.scope}")
    print(f"- spec_files: {len(specs)}")
    print(f"- code_files: {len(code)}")
    for path in specs:
        print(f"  spec: {path}")
    for path in code:
        print(f"  code: {path}")
    for msg in blockers:
        print(f"BLOCKER: {msg}")
    for msg in warnings:
        print(f"WARN: {msg}")

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
