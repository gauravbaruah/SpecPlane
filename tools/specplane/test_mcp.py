#!/usr/bin/env python3
"""Thin MCP catalog + dispatch uses the same kernel as the CLI."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kernel import (  # noqa: E402
    check_sync,
    format_check_sync,
    format_retrieve,
    format_run,
    load_kernel,
    retrieve,
    run_sensors,
)
from mcp_stdio import MCP_TOOLS, dispatch, handle_message, tool_descriptors  # noqa: E402

GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"
SCOPED = ROOT / "testdata" / "golden" / "scoped_coverage" / "specs"


class McpCatalogTests(unittest.TestCase):
    def test_catalog_lists_kernel_tools(self) -> None:
        self.assertEqual(MCP_TOOLS, ("retrieve", "blast", "impact", "check_sync", "list_gaps", "run"))
        names = [row["name"] for row in tool_descriptors()]
        self.assertEqual(names, list(MCP_TOOLS))
        self.assertNotIn("validate", names)
        self.assertNotIn("promote", names)
        self.assertNotIn("infer", names)
        self.assertNotIn("specify", names)
        self.assertNotIn("implement", names)
        self.assertNotIn("reconcile", names)

    def test_tools_list_rpc(self) -> None:
        reply = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert reply is not None
        names = [row["name"] for row in reply["result"]["tools"]]
        self.assertEqual(names, ["retrieve", "blast", "impact", "check_sync", "list_gaps", "run"])

    def test_list_gaps_dispatch_matches_kernel(self) -> None:
        text = dispatch("list_gaps", {"spec_root": str(GOLDEN)})
        self.assertIn("no_sensor", text)
        self.assertIn("capability.orphan", text)
        self.assertIn("advisory: true", text)

    def test_retrieve_dispatch_matches_kernel(self) -> None:
        kernel = load_kernel(GOLDEN)
        expected = format_retrieve(retrieve(kernel, "capability.authentication"))
        text = dispatch("retrieve", {"id": "capability.authentication", "spec_root": str(GOLDEN)})
        self.assertEqual(text, expected)

    def test_check_sync_schema_exposes_change(self) -> None:
        schema = next(row["inputSchema"] for row in tool_descriptors() if row["name"] == "check_sync")
        self.assertIn("change", schema["properties"])
        self.assertIn("changed_ids", schema["properties"])

    def test_check_sync_change_scopes_like_cli(self) -> None:
        text = dispatch(
            "check_sync",
            {
                "spec_root": str(SCOPED),
                "changed_ids": "capability.alpha,component.widget",
                "change": "select_output_folder",
            },
        )
        kernel = load_kernel(SCOPED)
        expected = format_check_sync(
            check_sync(
                kernel,
                ["capability.alpha", "component.widget"],
                change_slug="select_output_folder",
            )
        )
        self.assertEqual(text, expected)
        self.assertIn("coverage: fail", text)
        self.assertIn("change: select_output_folder", text)
        self.assertIn("behavior: unverified", text)

    def test_run_requires_change(self) -> None:
        with self.assertRaises(ValueError):
            dispatch("run", {"spec_root": str(GOLDEN)})

    def test_run_dispatch_matches_kernel(self) -> None:
        self.assertEqual(MCP_TOOLS, ("retrieve", "blast", "impact", "check_sync", "list_gaps", "run"))
        names = [row["name"] for row in tool_descriptors()]
        self.assertNotIn("validate", names)
        self.assertNotIn("promote", names)
        self.assertNotIn("infer", names)
        self.assertNotIn("specify", names)
        self.assertNotIn("implement", names)
        self.assertNotIn("reconcile", names)
        repo = Path.cwd()
        text = dispatch(
            "run",
            {"spec_root": str(GOLDEN), "change": "does_not_exist", "repo": str(repo)},
        )
        expected = format_run(
            run_sensors(load_kernel(GOLDEN), "does_not_exist", repo=repo)
        )
        self.assertEqual(text, expected)
        self.assertIn("unknown_change: does_not_exist", text)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "specs"
            folder = root / "changes" / "argv_ok"
            folder.mkdir(parents=True)
            (folder / "proposal.yaml").write_text(
                'change_id: "argv_ok"\nkind: "evolve"\nstatus: "in-flight"\npromise_ids: []\n',
                encoding="utf-8",
            )
            (folder / "success.yaml").write_text(
                yaml.safe_dump(
                    {
                        "sensors": [
                            {
                                "id": "argv_ok",
                                "must": "bound argv exits 0",
                                "run": {"argv": [sys.executable, "-c", "raise SystemExit(0)"]},
                            }
                        ]
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            text = dispatch(
                "run",
                {"spec_root": str(root), "change": "argv_ok", "repo": str(tmp_path)},
            )
            expected = format_run(run_sensors(load_kernel(root), "argv_ok", repo=tmp_path))
        self.assertEqual(text, expected)
        self.assertIn("result: pass", text)
        self.assertIn("behavior: evidence", text)
        self.assertNotIn("verified satisfies the spec", text)


if __name__ == "__main__":
    unittest.main()
