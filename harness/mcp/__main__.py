"""Command-line entry point for the CDD MCP stdio host: ``python -m harness.mcp --toolsets a:B,c:D``."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CDD MCP server over stdio.")
    parser.add_argument(
        "--toolsets",
        default=os.environ.get("MCP_TOOLSET_REFS", ""),
        help="Comma-separated module:Class toolset references.",
    )
    arguments = parser.parse_args()
    # harness.agent_tools must load before harness.mcp.mcp_server, which imports it back.
    import harness.agent_tools  # noqa: F401
    from harness.mcp.mcp_server import McpHost

    refs = tuple(ref.strip() for ref in arguments.toolsets.split(",") if ref.strip())
    repo = Path.cwd()
    project = Path(os.environ.get("CDD_PROJECT") or repo)
    McpHost.from_refs(refs, repo=str(repo), project=str(project)).run()


if __name__ == "__main__":
    main()
