"""Copy kit files into tools/specplane/_specplane_kit for wheel installs."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "tools" / "specplane" / "_specplane_kit"

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
)


def populate_bundle(kit_root: Path | None = None, dest: Path | None = None) -> Path:
    kit_root = (kit_root or ROOT).resolve()
    dest = (dest or BUNDLE).resolve()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest / "__init__.py").write_text("# bundled kit root for wheel installs\n", encoding="utf-8")
    shutil.copytree(kit_root / "specplane", dest / "specplane")

    for src_parent, dest_parent, prefix in (
        (kit_root / ".agents" / "skills", dest / ".agents" / "skills", "specplane-"),
        (kit_root / ".cursor" / "skills", dest / ".cursor" / "skills", "specplane-"),
    ):
        dest_parent.mkdir(parents=True, exist_ok=True)
        if src_parent.is_dir():
            for child in sorted(src_parent.iterdir()):
                if child.is_dir() and child.name.startswith(prefix):
                    shutil.copytree(child, dest_parent / child.name)

    rules_src = kit_root / ".cursor" / "rules"
    rules_dest = dest / ".cursor" / "rules"
    rules_dest.mkdir(parents=True, exist_ok=True)
    if rules_src.is_dir():
        for rule in sorted(rules_src.glob("specplane-*.mdc")):
            shutil.copy2(rule, rules_dest / rule.name)

    tools_dest = dest / "tools" / "specplane"
    tools_dest.mkdir(parents=True)
    tools_src = kit_root / "tools" / "specplane"
    for name in CLI_FILES:
        src = tools_src / name
        if src.is_file():
            shutil.copy2(src, tools_dest / name)
    return dest
