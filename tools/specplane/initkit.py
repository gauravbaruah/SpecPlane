"""Copy the SpecPlane kit into a product repo. No CI. No kernel specs/."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

CLI_FILES = (
    "cli.py",
    "kernel.py",
    "impact.py",
    "validate.py",
    "drift.py",
    "initkit.py",
    "mcp_stdio.py",
    "README.md",
    "requirements.txt",
    "specplane.config.json.example",
    "view.py",
    "ci_gate.py",
    "telemetry.py",
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

Nouns, verbs, and the loop are in `specplane/dialect.md`.

1. For spec work, open `specplane/core_prompt/applicable/README.md` and load only the section for the task.
2. Skills: specplane-bootstrap, specplane-author, specplane-flows, specplane-implement, specplane-validate, specplane-infer, specplane-explain.
3. Product requests in natural language use **specplane-implement**. PRE: retrieve when a promise might move (if unsure, retrieve). POST: check_sync --change <slug> --changed-ids, then run --change <slug>. If this change already has a check, bind it (`run.unittest` or `run.argv`). Do not invent a test so SpecPlane has something to run. Do not parse `test_strategy`. Unbound `must:` is `not_run` on `run`, not a pass and not a certificate. `run` invokes bound checks only; it does not create tests or certify behavior. Typos skip retrieve. Do not slurp `specs/`.
4. Optional: if `tools/specplane/cli.py` is present, the agent runs it in-session. Do not add git hooks or CI jobs unless you choose to.

Rules:
- Filename without extension equals `meta.id`.
- Capability Phase 1 is valid without architecture.
- Bidirectional links in the same change (`implements` ↔ `realized_by`, `uses` ↔ `used_by`).
- Changelog on live 5C files when `meta.version` changes. In-flight work lives in `specs/changes/`.
- Brownfield (an existing repo): use specplane-infer. The coding agent walks one named root and writes Phase 1 YAML tagged inferred. Greenfield stays specplane-bootstrap. There is no scan CLI and no infer CLI. `promote --ids` makes named inferred ids live. Greenfield can declare `implementation.realization.paths` without infer. `reconcile` checks that join; it does not write code or parse source. It is CLI-only.
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


_RECOVERY = (
    "Something went wrong. Delete specplane/, the specplane-* skills and rules, "
    "tools/specplane/, and specplane.config.json, then run init again. Leave specs/ alone."
)


def _copy_named_dirs(src_parent: Path, dest_parent: Path, prefix: str) -> int:
    dest_parent.mkdir(parents=True, exist_ok=True)
    count = 0
    if not src_parent.is_dir():
        return 0
    incoming: set[str] = set()
    for child in sorted(src_parent.iterdir()):
        if child.is_dir() and child.name.startswith(prefix):
            incoming.add(child.name)
            target = dest_parent / child.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(child, target)
            count += 1
    for child in list(dest_parent.iterdir()):
        if child.is_dir() and child.name.startswith(prefix) and child.name not in incoming:
            shutil.rmtree(child)
    return count


def _copy_rules(kit_root: Path, dest: Path) -> int:
    rules_src = kit_root / ".cursor" / "rules"
    rules_dest = dest / ".cursor" / "rules"
    rules_dest.mkdir(parents=True, exist_ok=True)
    incoming: set[str] = set()
    if rules_src.is_dir():
        for rule in sorted(rules_src.glob("specplane-*.mdc")):
            incoming.add(rule.name)
            shutil.copy2(rule, rules_dest / rule.name)
    for rule in list(rules_dest.glob("specplane-*.mdc")):
        if rule.name not in incoming:
            rule.unlink()
    return len(incoming)


def _copy_cli(kit_root: Path, dest: Path, *, force: bool) -> None:
    tools_dest = dest / "tools" / "specplane"
    tools_dest.mkdir(parents=True, exist_ok=True)
    tools_src = kit_root / "tools" / "specplane"
    viewer_dest = tools_dest / "viewer"
    if viewer_dest.exists():
        shutil.rmtree(viewer_dest)
    if force:
        for child in list(tools_dest.iterdir()):
            if child.is_file() and child.name not in CLI_FILES:
                child.unlink()
    for name in CLI_FILES:
        src = tools_src / name
        if src.is_file():
            shutil.copy2(src, tools_dest / name)
    viewer_src = tools_src / "viewer"
    if viewer_src.is_dir():
        shutil.copytree(viewer_src, viewer_dest)


def _clear_generated_view(dest: Path) -> None:
    generated = dest / ".specplane" / "view"
    if generated.exists():
        shutil.rmtree(generated)


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


_VIEW_IGNORE = "**/.specplane/view/"


def _ensure_view_gitignore(dest: Path) -> None:
    path = dest / ".gitignore"
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    if _VIEW_IGNORE in existing:
        return
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + _VIEW_IGNORE + "\n", encoding="utf-8")


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

    try:
        if specplane_dest.exists():
            shutil.rmtree(specplane_dest)
        shutil.copytree(kit_root / "specplane", specplane_dest)
        notes.append("copied specplane/")

        skills = _copy_named_dirs(
            kit_root / ".agents" / "skills", dest / ".agents" / "skills", "specplane-"
        )
        cursor_skills = _copy_named_dirs(
            kit_root / ".cursor" / "skills", dest / ".cursor" / "skills", "specplane-"
        )
        notes.append(f"copied {skills} agent skill(s), {cursor_skills} cursor skill(s)")

        rule_count = _copy_rules(kit_root, dest)
        notes.append(f"copied {rule_count} cursor rule(s)")

        if with_cli:
            _copy_cli(kit_root, dest, force=force)
            notes.append("copied tools/specplane CLI (not testdata)")
        else:
            notes.append("skipped CLI (--kit-only)")

        if force:
            _clear_generated_view(dest)
            notes.append("deleted generated .specplane/view/ so the next specplane view rebuilds")

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
        _ensure_view_gitignore(dest)
        notes.append("ignored generated **/.specplane/view/")

        notes.append(_write_agents(dest))
        _write_claude(dest)
        _empty_specs(dest)
        notes.append("created empty specs/ folders (no example capability)")
    except (OSError, shutil.Error) as exc:
        notes.append(str(exc))
        notes.append(_RECOVERY)
        return 1, notes

    github = dest / ".github" / "workflows"
    if github.exists():
        notes.append("left existing .github/workflows untouched")
    notes.append("did not copy specs/ from the kit")
    notes.append("did not write GitHub Actions or git hooks")
    notes.append("next: open this repo in your editor and ask for a Phase 1 capability")
    return 0, notes


def _remove_tree(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _remove_prefixed_dirs(parent: Path, prefix: str) -> list[str]:
    removed: list[str] = []
    if not parent.is_dir():
        return removed
    for child in list(parent.iterdir()):
        if child.is_dir() and child.name.startswith(prefix):
            shutil.rmtree(child)
            removed.append(child.name)
    return removed


def _prune_empty(path: Path) -> None:
    if path.is_dir() and not any(path.iterdir()):
        path.rmdir()


def _strip_block(path: Path, block: str) -> str:
    """Remove one exact block. Delete the file when nothing else remains."""
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if block.strip() not in text:
        return ""
    updated = text.replace(block, "")
    updated = updated.replace("\n\n\n", "\n\n").strip()
    if not updated:
        path.unlink()
        return f"removed {path.name}"
    path.write_text(updated + "\n", encoding="utf-8")
    return f"removed the SpecPlane block from {path.name}"


def _strip_claude_pointer(dest: Path) -> str:
    path = dest / "CLAUDE.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    if text.strip() == "@AGENTS.md":
        path.unlink()
        return "removed CLAUDE.md"
    return ""


def _strip_view_gitignore(dest: Path) -> str:
    path = dest / ".gitignore"
    if not path.is_file():
        return ""
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() != _VIEW_IGNORE
    ]
    if len(lines) == len(path.read_text(encoding="utf-8").splitlines()):
        return ""
    if not any(line.strip() for line in lines):
        path.unlink()
    else:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return "removed the generated-view gitignore line"


def _is_product_checkout(dest: Path) -> bool:
    """This repo, not a destination init copied into."""
    return (dest / "pyproject.toml").is_file() and (
        dest / "specs" / "capabilities" / "capability.specplane_retrieve.yaml"
    ).is_file()


def uninstall_kit(dest: Path) -> tuple[int, list[str]]:
    """Remove the kit init copied. Leave specs/ in place. Do not remove the Python package."""
    dest = dest.resolve()
    if _is_product_checkout(dest):
        return 1, ["dest is the SpecPlane checkout; refuse to uninstall it"]

    notes: list[str] = []
    try:
        kit = dest / "specplane"
        if kit.exists():
            _remove_tree(kit)
            notes.append("removed specplane/")

        for parent in (
            dest / ".agents" / "skills",
            dest / ".cursor" / "skills",
        ):
            for name in _remove_prefixed_dirs(parent, "specplane-"):
                notes.append(f"removed {parent.relative_to(dest) / name}")
            _prune_empty(parent)
            _prune_empty(parent.parent)

        rules = dest / ".cursor" / "rules"
        if rules.is_dir():
            for rule in list(rules.glob("specplane-*.mdc")):
                rule.unlink()
                notes.append(f"removed .cursor/rules/{rule.name}")
            _prune_empty(rules)
            _prune_empty(rules.parent)

        tools = dest / "tools" / "specplane"
        if tools.exists():
            _remove_tree(tools)
            notes.append("removed tools/specplane/")
            _prune_empty(tools.parent)

        config = dest / "specplane.config.json"
        if config.is_file():
            config.unlink()
            notes.append("removed specplane.config.json")

        generated = dest / ".specplane" / "view"
        if generated.exists():
            _clear_generated_view(dest)
            notes.append("removed generated .specplane/view/")
        _prune_empty(dest / ".specplane")

        agents = _strip_block(dest / "AGENTS.md", CONSUMING_AGENTS)
        if agents:
            notes.append(agents)
        claude = _strip_claude_pointer(dest)
        if claude:
            notes.append(claude)
        ignore = _strip_view_gitignore(dest)
        if ignore:
            notes.append(ignore)
    except (OSError, shutil.Error) as exc:
        notes.append(str(exc))
        return 1, notes

    if not notes:
        notes.append("nothing to remove")
    if (dest / "specs").exists():
        notes.append("left specs/ in place")
    notes.append("left the specplane command installed")
    return 0, notes
