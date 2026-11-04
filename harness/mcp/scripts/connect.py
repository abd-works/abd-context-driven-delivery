"""Run by an IDE before it connects to the cdd server: start the server when none answers, then name the project.

The installer copies this file to ``~/.cdd/connect.py``, and Claude Code runs it in the chat's own folder as the cdd
entry's ``headersHelper``. It prints the headers to send, so every request says which project its chat works on."""
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
    print(json.dumps({PROJECT_HEADER: os.getcwd()}))


if __name__ == "__main__":
    main()
