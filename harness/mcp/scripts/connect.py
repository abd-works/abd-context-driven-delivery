"""Run by an IDE before it connects to the cdd server: start the server when none answers, then name the project.

The installer copies this file to ``~/.cdd/connect.py``. In Claude Code the cdd plugin runs it as its server's
``headersHelper`` with the chat's folder as its argument. It prints the headers to send, so every request says which
project its chat works on. A language adapter runs it with ``--address`` and reads the server's address from it too, so
only the server reads and writes the file it publishes its address in."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent
ADDRESS_FLAG = "--address"


def main() -> None:
    runtime = json.loads((HOME / "runtime.json").read_text(encoding="utf-8"))
    sys.path.insert(0, runtime["source"])
    from harness.mcp.cdd_home import CddHome
    from harness.mcp.mcp_daemon import PROJECT_HEADER, McpDaemon

    daemon = McpDaemon(CddHome(HOME))
    daemon.ensure()
    print(json.dumps(answer(sys.argv[1:], daemon.url, PROJECT_HEADER)))


def answer(arguments: list[str], url: str, project_header: str) -> dict:
    """What the script prints: the headers alone for an IDE's ``headersHelper``, or, asked with ``--address``, the
    server's address with the headers, for a language adapter that connects on its own."""
    headers = {project_header: project_folder([word for word in arguments if word != ADDRESS_FLAG])}
    return {"url": url, "headers": headers} if ADDRESS_FLAG in arguments else headers


def project_folder(arguments: list[str]) -> str:
    """The chat's folder: the cdd plugin passes ``${CLAUDE_PROJECT_DIR}``, which Claude Code fills in with it. An IDE
    that passes nothing runs this script in the open project. Text still reading ``${`` was never filled in."""
    named = arguments[0] if arguments else ""
    return named if named and not named.startswith("${") else os.getcwd()


if __name__ == "__main__":
    main()
