"""agent_test.py — cursor-agent primitives and AgentTest base class.

Classes:
  AgentSession   — persistent chat session; owns launcher, get_or_create, run
  AgentResult    — structured result (exit_code, stdout, stderr, elapsed)
  JudgeResult    — structured AI judge outcome (verdict, reason)
  AgentTest      — base pytest class with Given / When / Then helpers

AgentTest contract:
  given_guidance()
      Merges base guidance from agent_test/.cdd/ with consumer guidance
      from <subclass_file>/../.cdd/ (resolved from the concrete test class).

  given_context(content)
      Pass artifact text as context (set by the calling test).

  when_agent_invoked(*, guidance, prompt, context, workspace, session_file)
      Assemble and dispatch to cursor-agent; return AgentResult.

  ai_judge(*, output, rubric, workspace, session_file)
      Ask a fresh cursor-agent session to evaluate output against a rubric.
      Returns JudgeResult(verdict, reason) — parseable programmatically.
"""
from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import pytest

# This package's own .cdd/ — always loaded as the base guidance layer.
_CDD_DIR = Path(__file__).parent / ".cdd"

_CHAT_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _log(msg: str) -> None:
    """Write a timestamped log line directly to the real stdout (bypasses pytest capture)."""
    ts = time.strftime("%H:%M:%S")
    sys.__stdout__.write(f"[agent_test {ts}] {msg}\n")
    sys.__stdout__.flush()


# ---------------------------------------------------------------------------
# AgentResult
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentResult:
    """Outcome of a single cursor-agent run."""
    exit_code: int
    stdout: str
    stderr: str
    elapsed_seconds: float

    def ok(self) -> bool:
        return self.exit_code == 0


# ---------------------------------------------------------------------------
# JudgeResult
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JudgeResult:
    """Structured outcome from an AI judge run."""
    verdict: str   # "PASS" | "FAIL" | "ERROR"
    reason: str
    elapsed_seconds: float = 0.0

    def passed(self) -> bool:
        return self.verdict == "PASS"

    def failed(self) -> bool:
        return self.verdict == "FAIL"


# ---------------------------------------------------------------------------
# AgentSession
# ---------------------------------------------------------------------------

@dataclass
class AgentSession:
    """Persistent cursor-agent chat session backed by a JSON file."""
    chat_id: str
    session_file: Path

    @staticmethod
    def _launcher() -> str | None:
        return shutil.which("cursor-agent")

    @classmethod
    def load(cls, session_file: Path) -> "AgentSession | None":
        if not session_file.is_file():
            return None
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            chat_id = str(data.get("chat_id", "")).strip()
        except (OSError, json.JSONDecodeError):
            return None
        return cls(chat_id=chat_id, session_file=session_file) if chat_id else None

    def save(self) -> None:
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(
            json.dumps({"chat_id": self.chat_id}, indent=2), encoding="utf-8"
        )

    @classmethod
    def get_or_create(
        cls, session_file: Path, workspace: Path, *, fresh: bool = False
    ) -> "AgentSession":
        """Return an existing session or create a new one via cursor-agent create-chat."""
        if not fresh:
            existing = cls.load(session_file)
            if existing is not None:
                _log(f"session resumed: {existing.chat_id} ({session_file.name})")
                return existing
        exe = cls._launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        _log(f"creating new session for {session_file.name} in {workspace} ...")
        completed = subprocess.run(
            [exe, "create-chat", "--workspace", str(workspace.resolve())],
            capture_output=True, text=True, timeout=60,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"cursor-agent create-chat failed (exit {completed.returncode}).\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        match = _CHAT_ID_RE.search(completed.stdout)
        if not match:
            raise RuntimeError(
                f"cursor-agent create-chat returned no chat id.\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        session = cls(chat_id=match.group(0), session_file=session_file)
        session.save()
        _log(f"session created: {session.chat_id}")
        return session

    def run(self, prompt: str, workspace: Path, *, timeout_seconds: int = 300) -> AgentResult:
        """Send prompt to cursor-agent via this session; return AgentResult."""
        exe = self._launcher()
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        _log(f"agent run starting (session={self.chat_id[:8]}…, timeout={timeout_seconds}s)")
        _log("=== FULL PROMPT START ===")
        sys.__stdout__.write(prompt + "\n")
        sys.__stdout__.flush()
        _log("=== FULL PROMPT END ===")
        args = [
            exe, "-p", "--force", "--trust",
            "--resume", self.chat_id,
            "--workspace", str(workspace.resolve()),
            "--output-format", "stream-json",
            "--stream-partial-output",
            prompt,
        ]
        narrative: list[str] = []
        raw_lines: list[str] = []
        stderr_buf: list[str] = []
        thread_errors: list[str] = []

        def _on_stdout() -> None:
            try:
                assert proc.stdout
                for raw in proc.stdout:
                    raw_lines.append(raw)
                    try:
                        event = json.loads(raw.strip())
                    except json.JSONDecodeError:
                        sys.__stdout__.write(raw)
                        sys.__stdout__.flush()
                        continue
                    etype = event.get("type", "?")
                    if etype == "assistant":
                        for block in (event.get("message") or {}).get("content") or []:
                            if not isinstance(block, dict):
                                continue
                            btype = block.get("type", "")
                            if btype == "text":
                                text = block.get("text", "")
                                narrative.append(text)
                                sys.__stdout__.write(text)
                                sys.__stdout__.flush()
                            elif btype == "tool_use":
                                name = block.get("name", "?")
                                inp = json.dumps(block.get("input", {}))[:120]
                                _log(f"tool_use: {name}({inp})")
                    elif etype == "tool_result":
                        content = event.get("content", "")
                        preview = str(content)[:120].replace("\n", " ")
                        _log(f"tool_result: {preview}")
                    elif etype == "result":
                        text = event.get("result", "")
                        narrative.append(text)
                        sys.__stdout__.write(text + "\n")
                        sys.__stdout__.flush()
                    elif etype not in ("system", "user"):
                        _log(f"event[{etype}]: {str(event)[:120]}")
            except Exception as exc:  # noqa: BLE001
                msg = f"stdout thread error: {exc}"
                thread_errors.append(msg)
                _log(msg)

        def _on_stderr() -> None:
            try:
                assert proc.stderr
                for chunk in iter(lambda: proc.stderr.read(4096), ""):
                    stderr_buf.append(chunk)
                    sys.__stderr__.write(chunk)
                    sys.__stderr__.flush()
            except Exception as exc:  # noqa: BLE001
                msg = f"stderr thread error: {exc}"
                thread_errors.append(msg)
                _log(msg)

        started = time.perf_counter()
        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        threads = [
            threading.Thread(target=_on_stdout, daemon=True),
            threading.Thread(target=_on_stderr, daemon=True),
        ]
        for t in threads:
            t.start()

        try:
            exit_code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            _log(f"TIMEOUT after {timeout_seconds}s — killing cursor-agent")
            proc.kill()
            proc.wait()
            raise
        for t in threads:
            t.join()

        elapsed = time.perf_counter() - started
        _log(f"agent run finished: exit={exit_code}, elapsed={elapsed:.1f}s, "
             f"narrative={len(''.join(narrative))}chars, thread_errors={thread_errors or 'none'}")
        _log("=== AGENT RESPONSE START ===")
        sys.__stdout__.write("".join(narrative) or "".join(raw_lines))
        sys.__stdout__.write("\n")
        sys.__stdout__.flush()
        _log("=== AGENT RESPONSE END ===")

        return AgentResult(
            exit_code=exit_code,
            stdout="".join(narrative) or "".join(raw_lines),
            stderr="".join(stderr_buf),
            elapsed_seconds=elapsed,
        )


# ---------------------------------------------------------------------------
# AgentTest — base pytest class
# ---------------------------------------------------------------------------

_JUDGE_PROMPT = """\
You are an AI judge. Evaluate the output below against the rubric and reply
with a single JSON object on one line — no code fences, no commentary:

{{"verdict": "PASS" | "FAIL", "reason": "<one sentence>"}}

--- RUBRIC ---
{rubric}

--- OUTPUT ---
{output}
"""


def _load_cdd(cdd_dir: Path, files: list[str] | None = None) -> list[str]:
    """Return formatted guidance strings from .md files in cdd_dir.

    If files is given, load only those filenames (in the order supplied).
    Otherwise load all *.md files in alphabetical order.
    """
    if not cdd_dir.is_dir():
        return []
    if files is not None:
        mds = [cdd_dir / f for f in files if (cdd_dir / f).is_file()]
    else:
        mds = sorted(cdd_dir.glob("*.md"))
    return [f"# {md.name}\n\n{md.read_text(encoding='utf-8')}" for md in mds]


class AgentTest:
    """Base pytest class providing Given / When / Then helpers for cursor-agent tests.

    Guidance layers (merged in order):
      1. agent_test/.cdd/  — base generic contract (shipped with this package)
      2. <subclass>/../.cdd/ — consumer domain guidance (resolved from test file location)

    Subclasses can pin a specific consumer .cdd via the class var:
        class TestMyRule(AgentTest):
            cdd_dir = Path(__file__).parent.parent / ".cdd"

    Usage:
        class TestMyRule(AgentTest):
            def test_example(self, tmp_path):
                guidance = self.given_guidance()
                context  = self.given_context(artifact_text)
                result   = self.when_agent_invoked(
                    guidance=guidance,
                    prompt="Validate `artifact.md` using rule `my-rule`.",
                    context=context,
                    workspace=tmp_path,
                    session_file=SESSION_DIR / "my-rule.json",
                )
                assert "PASS" in result.stdout
    """

    cdd_dir: ClassVar[Path | None] = None

    # --- authentication ---

    @staticmethod
    def assert_authenticated() -> None:
        """pytest.fail if cursor-agent is absent or not authenticated."""
        exe = AgentSession._launcher()
        if exe is None:
            pytest.fail("cursor-agent not on PATH")
        result = subprocess.run([exe, "status"], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail("cursor-agent not authenticated — run `cursor-agent login` first")

    # --- prompt assembly ---

    @staticmethod
    def _assemble_prompt(*, guidance: str = "", prompt: str, context: str = "") -> str:
        """Build the full agent prompt: Task → Artifact → Guidance (task leads so agent acts)."""
        parts: list[str] = [prompt]
        if context:
            parts.append(f"## Artifact\n\n{context}")
        if guidance:
            parts.append(f"## Standing Guidance\n\n{guidance}")
        return "\n\n---\n\n".join(parts)

    # --- judge verdict parsing ---

    @staticmethod
    def _parse_judge_result(stdout: str) -> tuple[str, str]:
        """Extract verdict and reason from the last JSON object in agent stdout."""
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                obj = json.loads(line)
                verdict = str(obj.get("verdict", "")).strip().upper()
                reason = str(obj.get("reason", "")).strip()
                if verdict in ("PASS", "FAIL"):
                    return verdict, reason
            except json.JSONDecodeError:
                continue
        return "ERROR", f"no parseable verdict in output:\n{stdout[:500]}"

    # --- Given ---

    def given_guidance(
        self,
        cdd_dir: Path | None = None,
        *,
        files: list[str] | None = None,
    ) -> str:
        """Merge base guidance (agent_test/.cdd) with consumer guidance.

        Resolution order for consumer .cdd:
          1. cdd_dir argument         — explicit override for this call
          2. self.cdd_dir class var   — subclass-level pin
          3. <subclass_file>/../.cdd  — resolved from the concrete test file

        files: if given, load only these filenames from the consumer .cdd
               (base layer always loads all its own files).
        """
        parts: list[str] = []

        # Layer 1: base guidance from this package (always all files)
        parts += _load_cdd(_CDD_DIR)

        # Layer 2: consumer guidance (optionally filtered to specific files)
        consumer_dir = cdd_dir or self.cdd_dir
        if consumer_dir is None:
            subclass_file = Path(inspect.getfile(type(self)))
            consumer_dir = (subclass_file.parent / ".." / ".cdd").resolve()

        if consumer_dir != _CDD_DIR:
            parts += _load_cdd(consumer_dir, files=files)

        return "\n\n---\n\n".join(parts)

    def given_context(self, content: str) -> str:
        """Accept artifact or example content supplied by the calling test as context."""
        return content

    # --- When ---

    def when_agent_invoked(
        self,
        *,
        guidance: str = "",
        prompt: str,
        context: str = "",
        workspace: Path,
        session_file: Path,
        timeout_seconds: int = 300,
    ) -> AgentResult:
        """Assemble prompt and dispatch via cursor-agent; return AgentResult."""
        _log(f"when_agent_invoked: session={session_file.name}, "
             f"guidance={len(guidance)}chars, context={len(context)}chars, prompt={len(prompt)}chars")
        full_prompt = self._assemble_prompt(guidance=guidance, prompt=prompt, context=context)
        _log(f"full prompt assembled: {len(full_prompt)}chars total")
        session = AgentSession.get_or_create(session_file, workspace)
        return session.run(full_prompt, workspace, timeout_seconds=timeout_seconds)

    # --- AI Judge ---

    def ai_judge(
        self,
        *,
        output: str,
        rubric: str,
        workspace: Path,
        session_file: Path,
        timeout_seconds: int = 120,
    ) -> JudgeResult:
        """Evaluate agent output against a rubric using a fresh cursor-agent session.

        Uses a separate session from the test agent so judge state is isolated.
        Returns JudgeResult(verdict, reason) — assert programmatically:
            verdict = self.ai_judge(output=result.stdout, rubric="...", ...)
            assert verdict.passed(), verdict.reason
        """
        judge_prompt = _JUDGE_PROMPT.format(rubric=rubric, output=output)
        session = AgentSession.get_or_create(session_file, workspace, fresh=True)
        started = time.perf_counter()
        try:
            result = session.run(judge_prompt, workspace, timeout_seconds=timeout_seconds)
        except Exception as exc:
            return JudgeResult(
                verdict="ERROR",
                reason=str(exc),
                elapsed_seconds=time.perf_counter() - started,
            )
        verdict, reason = self._parse_judge_result(result.stdout)
        return JudgeResult(
            verdict=verdict,
            reason=reason,
            elapsed_seconds=result.elapsed_seconds,
        )
