#!/usr/bin/env python3
"""Thin MCP catalog + dispatch uses the same kernel as the CLI."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from kernel import format_check_sync, format_retrieve, load_kernel, retrieve, check_sync  # noqa: E402
from mcp_stdio import MCP_TOOLS, dispatch, handle_message, tool_descriptors  # noqa: E402

GOLDEN = ROOT / "testdata" / "golden" / "messy_auth" / "specs"
SCOPED = ROOT / "testdata" / "golden" / "scoped_coverage" / "specs"


class McpCatalogTests(unittest.TestCase):
    def test_exactly_four_tools(self) -> None:
        self.assertEqual(MCP_TOOLS, ("retrieve", "blast", "check_sync", "list_gaps"))
        names = [row["name"] for row in tool_descriptors()]
        self.assertEqual(names, list(MCP_TOOLS))
        self.assertNotIn("validate", names)

    def test_tools_list_rpc(self) -> None:
        reply = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert reply is not None
        names = [row["name"] for row in reply["result"]["tools"]]
        self.assertEqual(names, ["retrieve", "blast", "check_sync", "list_gaps"])

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


if __name__ == "__main__":
    unittest.main()
