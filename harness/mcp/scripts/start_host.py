"""Start the CDD MCP stdio host the same way Cursor does."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_FALLBACK_REPO = Path(__file__).resolve().parents[3]


def find_cdd_repo(start: Path | str | None = None) -> Path:
    """Workspace first, then this script's checkout. Worktrees must not pin __file__."""
    here = Path(start or os.getcwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "installation" / "installer.py").is_file():
            return candidate
    return _FALLBACK_REPO


def _toolset_refs(value: str) -> tuple[str, ...]:
    return tuple(ref.strip() for ref in value.split(",") if ref.strip())


def _arg_after(args: list[str], flag: str) -> str:
    if flag not in args:
        return ""
    index = args.index(flag)
    if index + 1 >= len(args):
        return ""
    return str(args[index + 1])


def main() -> None:
    argv = [str(item) for item in sys.argv[1:]]
    requested = (
        _arg_after(argv, "--repo")
        or os.environ.get("CDD_REPO")
        or os.getcwd()
    )
    repo = find_cdd_repo(requested)
    os.chdir(repo)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["CDD_REPO"] = str(repo)
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from installation.installer import Installer

    Installer.ensure_import_path(repo)
    from harness.mcp.mcp_server import McpHost, claim_host_pid, host_pid_path

    toolsets = _arg_after(argv, "--toolsets") or os.environ.get("MCP_TOOLSET_REFS", "")
    refs = _toolset_refs(toolsets)
    if not refs:
        refs = tuple(Installer(repo=repo).collect_toolsets())
    claim_host_pid(host_pid_path(repo / ".cursor"))
    McpHost.build(refs, repo=str(repo), project=str(repo)).run()


if __name__ == "__main__":
    main()
