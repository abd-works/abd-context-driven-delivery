"""Real tools-CLI runner for ChatAgent slash prompts (not stub turns)."""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agents.agent import AgentSession, ToolCall, Turn, _SlashManifest
from primitives.tools.repo_paths import repo_python, repo_root

_ECHO_BODY = re.compile(r"/echo\s+fence\s+(.+)", re.IGNORECASE | re.DOTALL)
_BDD_TOKEN = re.compile(r"/bdd\.(\w+)", re.IGNORECASE)
_PATH_SKIP = frozenset({"for", "to", "and", "on", "with", "the", "a", "an"})
_OK_LINE = re.compile(r"^ok:\s*(.+)$", re.IGNORECASE)
_ERROR_LINE = re.compile(r"^error:\s*(.+)$", re.IGNORECASE)


def assert_tools_response(stdout: str, *, stderr: str = "") -> str:
    """Raise when tools CLI stdout reports failure or omits ok."""
    text = (stdout or "").strip()
    if not text:
        detail = (stderr or "").strip() or "(empty response)"
        raise RuntimeError(f"tools run produced no response: {detail}")
    ok_value = ""
    error_detail = ""
    for line in text.splitlines():
        ok_match = _OK_LINE.match(line.strip())
        if ok_match:
            ok_value = ok_match.group(1).strip().lower()
            continue
        error_match = _ERROR_LINE.match(line.strip())
        if error_match and not error_detail:
            error_detail = error_match.group(1).strip()
    if not ok_value:
        raise RuntimeError(f"tools run produced no ok response: {text}")
    if ok_value in ("false", "no", "0"):
        raise RuntimeError(f"tools run failed: {error_detail or text}")
    return text


@dataclass
class ToolsCliRunner:
    """Open a Turn, invoke real ``python -m tools run`` for known slashes, finish Turn."""

    workspace: Path

    def run_for_prompt(
        self, session: AgentSession, prompt: str
    ) -> Turn.Guidance | None:
        tokens = _SlashManifest.tokens(prompt)
        if not tokens:
            return None
        action = " ".join(tokens)
        turn = session.mint_turn(action=action)
        for token in tokens:
            tool_call = _SlashManifest.tool_call_for(token)
            self._invoke_token(prompt, token)
            tool_call.ok = True
            turn.append_tool(tool_call)
        turn.finish(subject=action)
        return turn.guidance

    def _invoke_token(self, prompt: str, token: str) -> None:
        bare = token.lstrip("/").split(".")[0].lower()
        if bare == "echo":
            body = self._echo_body(prompt)
            yaml_body = (
                "toolset: echo.echo:Echo\n"
                "tool: fence\n"
                f"arguments:\n  body: {self._yaml_quote(body)}\n"
            )
            self._run_yaml(yaml_body)
            return
        if _BDD_TOKEN.match(token):
            self._run_bdd(prompt, token)
            return
        raise RuntimeError(f"ChatAgent tools CLI does not support slash {token!r} yet")

    def _run_bdd(self, prompt: str, token: str) -> None:
        match = _BDD_TOKEN.match(token)
        fidelity = (match.group(1) if match else "behavior").lower()
        path = self._path_after_token(prompt, token)
        lines = [
            "toolset: context_tools.bdd.bdd:Bdd",
            "context:",
            f"  fidelity: {fidelity}",
        ]
        if path:
            lines.append(f"  path: {path}")
        lines.append("action: guidance")
        self._run_yaml("\n".join(lines) + "\n")

    @staticmethod
    def _path_after_token(prompt: str, token: str) -> str:
        idx = prompt.find(token)
        if idx < 0:
            return ""
        rest = prompt[idx + len(token) :].strip()
        if not rest:
            return ""
        word = rest.split()[0].rstrip(".,;")
        if word.lower() in _PATH_SKIP:
            return ""
        return word

    @staticmethod
    def _echo_body(prompt: str) -> str:
        match = _ECHO_BODY.search(prompt)
        if match:
            return match.group(1).strip().rstrip(".")
        return prompt.strip()

    @staticmethod
    def _yaml_quote(text: str) -> str:
        escaped = text.replace("'", "''")
        return f"'{escaped}'"

    def _run_yaml(self, yaml_body: str) -> str:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        completed = subprocess.run(
            [repo_python(), "-m", "tools", "run", "-"],
            input=yaml_body,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_root(),
            check=False,
            env=env,
        )
        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()
        if completed.returncode != 0:
            raise RuntimeError(
                f"tools run failed ({completed.returncode}): {stderr or stdout}"
            )
        return assert_tools_response(stdout, stderr=stderr)
