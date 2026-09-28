#!/usr/bin/env python3
"""Compose validate, check_sync, and run for one pull-request diff.

Not a CLI verb. specplane init does not install this or write a workflow.
--apply-diff soft-resets the checkout to the merge base so check_sync's
default changed-set (staged spec YAML and declared paths) sees the PR diff.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CLI = Path(__file__).resolve().parent / "cli.py"


def change_slugs(files: list[str]) -> list[str]:
    """specs/changes/<slug>/ in the diff. _archive is not an open change."""
    slugs: list[str] = []
    for raw in files:
        parts = tuple(part for part in Path(raw).parts if part not in {".", ""})
        for index, part in enumerate(parts[:-1]):
            if part != "changes" or index == 0 or parts[index - 1] != "specs":
                continue
            slug = parts[index + 1]
            if slug == "_archive" or slug.endswith((".yaml", ".yml", ".md")):
                break
            slugs.append(slug)
            break
    return sorted(set(slugs))


def open_change_slugs(repo: Path, files: list[str], spec_root: Path | None = None) -> list[str]:
    """Slugs whose open folder still exists. An archive move is not a folder to run."""
    roots = [repo / "specs" / "changes"]
    if spec_root is not None:
        roots.append(spec_root / "changes")
    found: list[str] = []
    for slug in change_slugs(files):
        if any((root / slug).is_dir() for root in roots):
            found.append(slug)
    return found


def product_root(spec_root: Path) -> Path:
    """Directory that holds specplane.config.json, else the parent of the spec root."""
    current = spec_root.resolve()
    while True:
        if (current / "specplane.config.json").is_file():
            return current
        if current.parent == current:
            return spec_root.resolve().parent
        current = current.parent


def _git(repo: Path, args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL)


def diff_files(repo: Path, base: str) -> tuple[str, list[str]]:
    merge_base = _git(repo, ["merge-base", base, "HEAD"]).strip()
    if not merge_base:
        raise RuntimeError(f"no merge base for {base}")
    out = _git(repo, ["diff", "--name-only", "--diff-filter=ACDMRTUXB", merge_base, "HEAD"])
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return merge_base, files


def _invoke(repo: Path, args: list[str]) -> int:
    completed = subprocess.run([sys.executable, str(CLI), *args], cwd=repo)
    return int(completed.returncode)


def gate(repo: Path, spec_root: Path, base: str, *, apply_diff: bool) -> int:
    repo = repo.resolve()
    spec_root = spec_root.resolve()
    if not apply_diff:
        sys.stderr.write(
            "refusing: pass --apply-diff (soft-resets this checkout to the merge base)\n"
        )
        return 2
    try:
        merge_base, files = diff_files(repo, base)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        sys.stderr.write(f"ci_gate: {exc}\n")
        return 2
    slugs = open_change_slugs(repo, files, spec_root)
    print(
        "ci_gate slugs: " + (", ".join(slugs) if slugs else "(none)"),
        flush=True,
    )
    subprocess.check_call(["git", "reset", "--soft", merge_base], cwd=repo)
    config_dir = product_root(spec_root)
    root = ["--spec-root", str(spec_root), "--config-dir", str(config_dir)]
    repo_args = ["--repo", str(repo)]
    failed = False
    if _invoke(repo, ["validate", *root]) != 0:
        failed = True
    if _invoke(repo, ["check_sync", *root, *repo_args]) != 0:
        failed = True
    for slug in slugs:
        if _invoke(repo, ["check_sync", *root, *repo_args, "--change", slug]) != 0:
            failed = True
        if _invoke(repo, ["run", *root, *repo_args, "--change", slug]) != 0:
            failed = True
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pull-request compose of validate, check_sync, and run")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--spec-root", type=Path, default=Path("specs"))
    parser.add_argument("--base", required=True, help="PR base ref, for example origin/main")
    parser.add_argument(
        "--apply-diff",
        action="store_true",
        help="Soft-reset this checkout so the default changed-set is the PR diff",
    )
    args = parser.parse_args(argv)
    spec_root = args.spec_root if args.spec_root.is_absolute() else args.repo / args.spec_root
    return gate(args.repo, spec_root, args.base, apply_diff=args.apply_diff)


if __name__ == "__main__":
    sys.exit(main())
