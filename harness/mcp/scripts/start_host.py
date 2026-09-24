"""Start the CDD MCP stdio host the same way Cursor does."""
from __future__ import annotations

import os
import sys
from pathlib import Path


class StartHost:
    """Parse start_host CLI flags and load toolset refs."""

    FALLBACK_REPO = Path(__file__).resolve().parents[3]

    def toolset_refs(self, value: str) -> tuple[str, ...]:
        return tuple(ref.strip() for ref in value.split(",") if ref.strip())

    def arg_after(self, args: list[str], flag: str) -> str:
        if flag not in args:
            return ""
        index = args.index(flag)
        if index + 1 >= len(args):
            return ""
        return str(args[index + 1])

    def find_cdd_repo(self, start: Path | str | None = None) -> Path:
        """Workspace first, then this script's checkout. Worktrees must not pin __file__."""
        here = Path(start or os.getcwd()).resolve()
        for candidate in (here, *here.parents):
            if (candidate / "installation" / "installer.py").is_file():
                return candidate
        return self.FALLBACK_REPO


def main() -> None:
    starter = StartHost()
    argv = [str(item) for item in sys.argv[1:]]
    requested = (
        starter.arg_after(argv, "--repo")
        or os.environ.get("CDD_REPO")
        or os.getcwd()
    )
    repo = starter.find_cdd_repo(requested)
    os.chdir(repo)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["CDD_REPO"] = str(repo)
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from installation.installer import Installer

    installer = Installer(repo=repo)
    installer.ensure_import_path()
    from harness.mcp.mcp_server import HostPid, McpHost

    toolsets = starter.arg_after(argv, "--toolsets") or os.environ.get("MCP_TOOLSET_REFS", "")
    refs = starter.toolset_refs(toolsets)
    if not refs:
        refs = tuple(installer.collect_toolsets())
    HostPid.from_ide(repo / ".cursor").claim()
    McpHost.from_refs(refs, repo=str(repo), project=str(repo)).run()


if __name__ == "__main__":
    main()
