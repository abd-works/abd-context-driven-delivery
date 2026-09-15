"""Command-line entry point for the CDD MCP stdio host."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_KIT_ROOT = Path(__file__).resolve().parents[2]
if str(_KIT_ROOT) not in sys.path:
    sys.path.insert(0, str(_KIT_ROOT))

from mcp_server.mcp_host import build_host


def _toolset_refs(value: str) -> tuple[str, ...]:
    return tuple(ref.strip() for ref in value.split(",") if ref.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CDD MCP server over stdio.")
    parser.add_argument(
        "--toolsets",
        default=os.environ.get("MCP_TOOLSET_REFS", ""),
        help="Comma-separated module:Class toolset references.",
    )
    arguments = parser.parse_args()
    build_host(_toolset_refs(arguments.toolsets)).run()


if __name__ == "__main__":
    main()
