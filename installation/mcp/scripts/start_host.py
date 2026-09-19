"""Start the CDD MCP stdio host the same way Cursor does."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]


def _toolset_refs(value: str) -> tuple[str, ...]:
    return tuple(ref.strip() for ref in value.split(",") if ref.strip())


def _manifest() -> dict:
    path = _REPO / ".cursor" / "mcp.json"
    if not path.is_file():
        return {}
    from installation.mcp.mcp_server import McpHost

    servers = json.loads(path.read_text(encoding="utf-8")).get("mcpServers") or {}
    return McpHost.server_entry_from_manifest(servers)


def _arg_after(args: list[str], flag: str) -> str:
    if flag not in args:
        return ""
    index = args.index(flag)
    if index + 1 >= len(args):
        return ""
    return str(args[index + 1])


def main() -> None:
    os.chdir(_REPO)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ.setdefault("CDD_REPO", str(_REPO))
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    from installation.installer import Installer

    Installer.ensure_import_path(_REPO)
    from installation.mcp.mcp_server import McpHost, claim_host_pid, host_pid_path

    argv = [str(item) for item in sys.argv[1:]]
    manifest = _manifest()
    manifest_args = [str(item) for item in manifest.get("args") or []]
    toolsets = (
        _arg_after(argv, "--toolsets")
        or _arg_after(manifest_args, "--toolsets")
        or os.environ.get("MCP_TOOLSET_REFS", "")
    )
    repo = _arg_after(argv, "--repo") or _arg_after(manifest_args, "--repo") or str(_REPO)
    claim_host_pid(host_pid_path(_REPO / ".cursor"))
    McpHost.build(_toolset_refs(toolsets), repo=repo, project=repo).run()


if __name__ == "__main__":
    main()
