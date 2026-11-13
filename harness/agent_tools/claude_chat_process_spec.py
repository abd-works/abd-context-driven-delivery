"""Specs for finding the Claude Code chat process that started the cdd header helper."""
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import after, before, context, description, it

from harness.agent_tools.claude_chat_process import ClaudeChatProcess

SHELL = 41
CHAT = 42
DESKTOP_APP = 43


class StandInProcessTree:
    """The operating system's process tree, standing in for it: this process runs under a shell, under the chat's
    Claude Code process, under the desktop app."""

    def __init__(self, claude_processes: set[int]) -> None:
        self._parents = {os.getpid(): SHELL, SHELL: CHAT, CHAT: DESKTOP_APP}
        self._claude_processes = claude_processes

    def parent_of(self, pid: int) -> int | None:
        return self._parents.get(pid)

    def runs_claude(self, pid: int) -> bool:
        return pid in self._claude_processes


with description("the Claude Code chat a header helper runs for"):
    with before.each:
        self.config = Path(tempfile.mkdtemp())
        self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
        os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
        (self.config / "sessions").mkdir()

    with after.each:
        if self.prior_config is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

    with context("that Claude Code has recorded in its sessions folder"):
        with before.each:
            (self.config / "sessions" / f"{CHAT}.json").write_text('{"cwd": "C:/dev/shop"}', encoding="utf-8")

        with it("should be the process that record names"):
            expect(ClaudeChatProcess.from_ancestors(StandInProcessTree(set())).pid).to(equal(CHAT))

    with context("that Claude Code has not recorded yet, as while the desktop app keeps it in a spare folder"):
        with it("should be the nearest process running Claude Code's own executable"):
            found = ClaudeChatProcess.from_ancestors(StandInProcessTree({CHAT, DESKTOP_APP}))
            expect(found.pid).to(equal(CHAT))

    with context("with no Claude Code process above the helper"):
        with it("should be none"):
            expect(ClaudeChatProcess.from_ancestors(StandInProcessTree(set()))).to(be_none)
