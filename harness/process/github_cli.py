"""GitHubCli - runs the GitHub command line, gh, in one folder, as Git runs git: the one way the framework asks GitHub
for something, such as publishing a release."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# A release uploads its notes and waits on GitHub.
_COMMAND_TIMEOUT_SECONDS = 120


class GitHubCliError(RuntimeError):
    """Raised when gh is not installed, or a gh command fails."""


class GitHubCli:
    def __init__(self, folder: Path | str) -> None:
        self.folder = Path(folder)

    def run(self, *args: str) -> str:
        """Run gh with args in the folder and answer its output."""
        gh = shutil.which("gh")
        if gh is None:
            raise GitHubCliError("the GitHub CLI (gh) is not installed: install it from https://cli.github.com and sign in with gh auth login")
        command = f"gh {' '.join(args)}"
        try:
            answer = subprocess.run([gh, *args], cwd=self.folder, capture_output=True, text=True, encoding="utf-8", timeout=_COMMAND_TIMEOUT_SECONDS,
                                    check=False, stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired as exc:
            raise GitHubCliError(f"{command} exceeded {_COMMAND_TIMEOUT_SECONDS} seconds in {self.folder}") from exc
        if answer.returncode != 0:
            raise GitHubCliError(f"{command} failed in {self.folder}: {(answer.stderr or answer.stdout).strip()}")
        return answer.stdout.strip()
