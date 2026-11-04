"""The cdd server process: ``python -m harness.mcp [--port N] [--toolsets a:B,c:D]``, run from the checkout it serves."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the one cdd MCP server over HTTP.")
    parser.add_argument("--port", type=int, default=None, help="Port to serve on; CDD_SERVER_PORT, else 47800.")
    parser.add_argument(
        "--toolsets",
        default=os.environ.get("MCP_TOOLSET_REFS", ""),
        help="Comma-separated module:Class toolset references; every annotated toolset in the checkout when empty.",
    )
    arguments = parser.parse_args()
    # harness.agent_tools must load before harness.mcp.mcp_server, which imports it back.
    import harness.agent_tools  # noqa: F401
    from harness.installation.installer import Installer
    from harness.mcp.mcp_daemon import McpDaemon
    from harness.mcp.mcp_server import McpHost

    source = Path.cwd().resolve()
    daemon = McpDaemon(port=arguments.port)
    listener = daemon.claim_port()
    if listener is None:
        return
    refs = tuple(ref.strip() for ref in arguments.toolsets.split(",") if ref.strip())
    if not refs:
        refs = tuple(Installer(repo=source).collect_toolsets())
    McpHost.from_refs(refs, repo=str(source)).serve(daemon, listener)


if __name__ == "__main__":
    main()
