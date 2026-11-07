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
    from harness.installation.repository_toolsets import RepositoryToolsets
    from harness.mcp.cdd_home import CddHome
    from harness.mcp.mcp_daemon import McpDaemon
    from harness.mcp.mcp_server import McpHost

    source = Path.cwd().resolve()
    # The server imports every toolset of the checkout it runs from by its full name.
    toolsets = RepositoryToolsets(source)
    toolsets.ensure_import_path()
    daemon = McpDaemon(CddHome(), port=arguments.port)
    listener = daemon.claim_port()
    if listener is None:
        return
    refs = tuple(ref.strip() for ref in arguments.toolsets.split(",") if ref.strip())
    host = McpHost.from_refs(refs, repo=str(source)) if refs else McpHost.from_repo(source)
    host.serve(daemon, listener)


if __name__ == "__main__":
    main()
