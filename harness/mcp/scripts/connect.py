"""Run by an IDE before it connects to the cdd server: start the server when none answers, then name the project.

The installer copies this file to ``~/.cdd/connect.py``. In Claude Code the cdd plugin runs it as its server's
``headersHelper`` with the chat's folder as its argument. It prints the headers to send, so every request says which
project its chat works on."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent


def main() -> None:
    runtime = json.loads((HOME / "runtime.json").read_text(encoding="utf-8"))
    sys.path.insert(0, runtime["source"])
    from harness.mcp.cdd_home import CddHome
    from harness.mcp.mcp_daemon import PROJECT_HEADER, McpDaemon

    McpDaemon(CddHome(HOME)).ensure()
    print(json.dumps({PROJECT_HEADER: project_folder(sys.argv[1:])}))


def project_folder(arguments: list[str]) -> str:
    """The chat's folder: the cdd plugin passes ``${CLAUDE_PROJECT_DIR}``, which Claude Code fills in with it. An IDE
    that passes nothing runs this script in the open project. Text still reading ``${`` was never filled in."""
    named = arguments[0] if arguments else ""
    return named if named and not named.startswith("${") else os.getcwd()


if __name__ == "__main__":
    main()
