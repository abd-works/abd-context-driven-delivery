"""Run by an IDE before it connects to the cdd server: start the server when none answers, then name the project.

The installer copies this file to ``~/.cdd/connect.py``. In Claude Code the cdd plugin runs it as its server's
``headersHelper`` with the chat's folder as its argument. It prints the headers to send, so every request says which
project its chat works on. A language adapter runs it with ``--address`` and reads the server's address from it too, so
only the server reads and writes the file it publishes its address in."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HOME = Path(__file__).resolve().parent
ADDRESS_FLAG = "--address"
# Claude Code runs a chat's tools, this script among them, with the chat's id in this variable. The id stays the same
# when the chat moves to another folder, which the folder Claude Code fills into the arguments does not.
CHAT_ID_VARIABLE = "CLAUDE_CODE_SESSION_ID"
# The chat header always goes, so the server never refuses a second time for a chat this script has already named:
# an IDE that gives no chat id sends this in its place.
UNNAMED_CHAT = "unnamed"


# An install swaps the pinned runtime in place, and for those seconds its code cannot be imported. The script waits that
# long rather than exit, because a header helper that prints nothing leaves its chat cut off from cdd until a reload.
RUNTIME_SWAP_SECONDS = 30
RUNTIME_RETRY_SECONDS = 0.5


def main() -> None:
    import_runtime()
    from harness.mcp.cdd_home import CddHome
    from harness.agent_tools.claude_chat_process import ClaudeChatProcess
    from harness.mcp.mcp_daemon import CHAT_HEADER, CHAT_PROCESS_HEADER, PROJECT_HEADER, McpDaemon

    daemon = McpDaemon(CddHome(HOME))
    daemon.ensure()
    process = ClaudeChatProcess.from_ancestors()
    chat_process = {CHAT_PROCESS_HEADER: str(process.pid)} if process is not None else {}
    print(json.dumps(answer(sys.argv[1:], daemon.url, PROJECT_HEADER, CHAT_HEADER, chat_process)))


def import_runtime() -> None:
    """Put the pinned runtime on the import path and import the modules main needs, retrying while an install swaps it.
    The last failure is raised once the swap has taken longer than an install ever does."""
    waited = 0.0
    while True:
        try:
            _import_pinned_runtime()
            return
        except (OSError, ValueError, KeyError, ImportError) as failure:
            if waited >= RUNTIME_SWAP_SECONDS:
                raise
            if isinstance(failure, ImportError):
                _forget_partial_imports()
        time.sleep(RUNTIME_RETRY_SECONDS)
        waited += RUNTIME_RETRY_SECONDS


def _import_pinned_runtime() -> None:
    runtime = json.loads((HOME / "runtime.json").read_text(encoding="utf-8"))
    if runtime["source"] not in sys.path:
        sys.path.insert(0, runtime["source"])
    import harness.agent_tools.claude_chat_process  # noqa: F401
    import harness.mcp.mcp_daemon  # noqa: F401


def _forget_partial_imports() -> None:
    """A failed import can leave half-loaded harness modules behind, which the next try would reuse."""
    for name in [name for name in sys.modules if name == "harness" or name.startswith("harness.")]:
        del sys.modules[name]


def answer(arguments: list[str], url: str, project_header: str, chat_header: str, chat_process: dict[str, str] | None = None) -> dict:
    """What the script prints: the headers alone for an IDE's ``headersHelper``, or, asked with ``--address``, the
    server's address with the headers, for a language adapter that connects on its own. A Claude Code chat's id goes
    in the chat header, and chat_process, the header naming the Claude Code process that runs this script, goes with
    it, so the server reads the folder the chat's session works in now on every call. A language adapter is a server
    of its own, such as the session board, that serves every chat, so it names only its project: carrying the chat
    that happened to start it would make the cdd server follow that chat's folder instead."""
    is_language_adapter = ADDRESS_FLAG in arguments
    headers = {
        project_header: project_folder([word for word in arguments if word != ADDRESS_FLAG]),
        chat_header: UNNAMED_CHAT if is_language_adapter else os.environ.get(CHAT_ID_VARIABLE, "").strip() or UNNAMED_CHAT,
        **({} if is_language_adapter else chat_process or {}),
    }
    return {"url": url, "headers": headers} if is_language_adapter else headers


def project_folder(arguments: list[str]) -> str:
    """The chat's folder: the cdd plugin passes ``${CLAUDE_PROJECT_DIR}``, which Claude Code fills in with it. An IDE
    that passes nothing runs this script in the open project. Text still reading ``${`` was never filled in."""
    named = arguments[0] if arguments else ""
    return named if named and not named.startswith("${") else os.getcwd()


if __name__ == "__main__":
    main()
