"""Copy the SpecPlane kit into a product repo. No CI. No kernel specs/."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

CLI_FILES = (
    "cli.py",
    "kernel.py",
    "validate.py",
    "drift.py",
    "initkit.py",
    "mcp_stdio.py",
    "README.md",
    "requirements.txt",
    "specplane.config.json.example",
)

SPEC_DIR_NAMES = (
    "capabilities",
    "foundations",
    "containers",
    "components",
    "changes",
)

AGENTS_MARK = "# SpecPlane (this product)"

CONSUMING_AGENTS = """# SpecPlane (this product)

This project uses SpecPlane v9.1.0. Specs live in `specs/`. Schema files live in `specplane/`.

Do not ingest `specplane/core_prompt/specplane_schema_prompt_v9.1.0.md` into a coding session.

1. For spec work, open `specplane/core_prompt/applicable/README.md` and load only the section for the task.
2. Skills: specplane-bootstrap, specplane-author, specplane-implement, specplane-validate.
3. Product requests in natural language use **specplane-implement**. PRE: retrieve when a promise might move (if unsure, retrieve). POST: check_sync --changed-ids. Typos skip retrieve. Do not slurp `specs/`.
4. Optional: if `tools/specplane/cli.py` is present, the agent runs it in-session. Do not add git hooks or CI jobs unless you choose to.

Rules:
- Filename without extension equals `meta.id`.
- Capability Phase 1 is valid without architecture.
- Bidirectional links in the same change (`implements` ↔ `realized_by`, `uses` ↔ `used_by`).
- Changelog on live 5C files when `meta.version` changes. In-flight work lives in `specs/changes/`.
- Specs before code when behavior, contracts, events, rollout, security, or how the product is obtained change. Trivial work (typo/4px/rename): no retrieve. If unsure, retrieve.
"""


def default_kit_root() -> Path:
    here = Path(__file__).resolve().parent
    checkout = here.parent.parent
    if is_kit_root(checkout):
        return checkout
    bundled = here / "_specplane_kit"
    if is_kit_root(bundled):
        return bundled
    return checkout


def kit_commit(kit_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=kit_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def is_kit_root(path: Path) -> bool:
    return (path / "specplane" / "core_prompt").is_dir() and (
        path / ".agents" / "skills"
    ).is_dir()


def _copy_named_dirs(src_parent: Path, dest_parent: Path, prefix: str) -> int:
    dest_parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if not src_parent.is_dir():
        return 0
    for child in sorted(src_parent.iterdir()):
        if child.is_dir() and child.name.startswith(prefix):
            target = dest_parent / child.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(child, target)
            count += 1
    return count


def _write_agents(dest: Path) -> str:
    path = dest / "AGENTS.md"
    if not path.exists():
        path.write_text(CONSUMING_AGENTS, encoding="utf-8")
        return "wrote AGENTS.md"
    text = path.read_text(encoding="utf-8")
    if AGENTS_MARK in text:
        return "AGENTS.md already has a SpecPlane block (left in place)"
    sep = "" if text.endswith("\n") else "\n"
    path.write_text(text + sep + "\n" + CONSUMING_AGENTS, encoding="utf-8")
    return "appended SpecPlane block to AGENTS.md"


def _write_claude(dest: Path) -> None:
    path = dest / "CLAUDE.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "AGENTS.md" in text:
            return
        sep = "" if text.endswith("\n") else "\n"
        path.write_text(text + sep + "\n@AGENTS.md\n", encoding="utf-8")
        return
    path.write_text("@AGENTS.md\n", encoding="utf-8")


def _empty_specs(dest: Path) -> None:
    root = dest / "specs"
    for name in SPEC_DIR_NAMES:
        folder = root / name
        folder.mkdir(parents=True, exist_ok=True)
        keep = folder / ".gitkeep"
        if not keep.exists() and not any(folder.iterdir()):
            keep.write_text("", encoding="utf-8")


def init_kit(
    dest: Path,
    kit_root: Path,
    *,
    with_cli: bool = True,
    force: bool = False,
) -> tuple[int, list[str]]:
    dest = dest.resolve()
    kit_root = kit_root.resolve()
    notes: list[str] = []

    if dest == kit_root:
        return 1, ["dest is the kit root; refuse to init onto SpecPlane itself"]
    if not is_kit_root(kit_root):
        return 1, [f"not a SpecPlane kit root: {kit_root}"]

    dest.mkdir(parents=True, exist_ok=True)
    specplane_dest = dest / "specplane"
    if specplane_dest.exists() and not force:
        return 1, [f"{specplane_dest} already exists (pass --force to replace the kit copy)"]

    if specplane_dest.exists():
        shutil.rmtree(specplane_dest)
    shutil.copytree(kit_root / "specplane", specplane_dest)
    notes.append("copied specplane/")

    skills = _copy_named_dirs(kit_root / ".agents" / "skills", dest / ".agents" / "skills", "specplane-")
    cursor_skills = _copy_named_dirs(
        kit_root / ".cursor" / "skills", dest / ".cursor" / "skills", "specplane-"
    )
    notes.append(f"copied {skills} agent skill(s), {cursor_skills} cursor skill(s)")

    rules_src = kit_root / ".cursor" / "rules"
    rules_dest = dest / ".cursor" / "rules"
    rules_dest.mkdir(parents=True, exist_ok=True)
    rule_count = 0
    if rules_src.is_dir():
        for rule in sorted(rules_src.glob("specplane-*.mdc")):
            shutil.copy2(rule, rules_dest / rule.name)
            rule_count += 1
    notes.append(f"copied {rule_count} cursor rule(s)")

    if with_cli:
        tools_dest = dest / "tools" / "specplane"
        tools_dest.mkdir(parents=True, exist_ok=True)
        tools_src = kit_root / "tools" / "specplane"
        for name in CLI_FILES:
            src = tools_src / name
            if src.is_file():
                shutil.copy2(src, tools_dest / name)
        notes.append("copied tools/specplane CLI (not testdata)")
    else:
        notes.append("skipped CLI (--kit-only)")

    config = {
        "version": 1,
        "schemaVersion": "9.1.0",
        "specRoot": "specs",
        "strictMode": False,
        "kitCommit": kit_commit(kit_root),
    }
    (dest / "specplane.config.json").write_text(
        json.dumps(config, indent=2) + "\n", encoding="utf-8"
    )
    notes.append("wrote specplane.config.json")

    notes.append(_write_agents(dest))
    _write_claude(dest)
    _empty_specs(dest)
    notes.append("created empty specs/ folders (no example capability)")

    github = dest / ".github" / "workflows"
    if github.exists():
        notes.append("left existing .github/workflows untouched")
    notes.append("did not copy specs/ from the kit")
    notes.append("did not write GitHub Actions or git hooks")
    notes.append("next: open this repo in your editor and ask for a Phase 1 capability")
    return 0, notes
