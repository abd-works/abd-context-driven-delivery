"""The cursor-agent command line that agent specs drive."""
from __future__ import annotations

import re
import shutil
import subprocess

CREATE_CHAT_TIMEOUT_SECONDS = 60
_CHAT_ID = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE
)


class CursorAgentNotFound(RuntimeError):
    """Neither ``cursor-agent`` nor ``agent`` is on PATH."""

    def __init__(self) -> None:
        super().__init__("cursor-agent not found on PATH")


class ChatNotCreated(RuntimeError):
    """``cursor-agent create-chat`` failed or printed no chat id."""

    def __init__(self, reason: str, completed: subprocess.CompletedProcess[str]) -> None:
        super().__init__(
            f"cursor-agent create-chat {reason}.\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )


class CursorCli:
    """Starts cursor-agent chats and builds the command that sends one a prompt.

    ``resume`` is the chat a command continues; ``print_mode`` makes the agent
    stream JSON to stdout instead of opening its terminal UI.
    """

    def __init__(self, resume: str = "", print_mode: bool = False) -> None:
        self._resume = resume.strip()
        self._print_mode = print_mode

    @property
    def launcher(self) -> str | None:
        return shutil.which("cursor-agent") or shutil.which("agent")

    def create_chat(self, workspace: str) -> str:
        completed = subprocess.run(
            [self._required_launcher(), "create-chat", "--workspace", workspace],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CREATE_CHAT_TIMEOUT_SECONDS,
            check=False,
        )
        if completed.returncode != 0:
            raise ChatNotCreated(f"failed (exit {completed.returncode})", completed)
        match = _CHAT_ID.search(completed.stdout or "")
        if match is None:
            raise ChatNotCreated("returned no chat id", completed)
        return match.group(0)

    def command(self, prompt: str, workspace: str) -> list[str]:
        args = [self._required_launcher(), "--force", "--trust"]
        if self._resume:
            args.extend(["--resume", self._resume])
        args.extend(["--workspace", workspace])
        if self._print_mode:
            args.extend(["--print", "--output-format", "stream-json"])
        if prompt:
            args.append(prompt)
        return args

    def _required_launcher(self) -> str:
        launcher = self.launcher
        if launcher is None:
            raise CursorAgentNotFound()
        return launcher
