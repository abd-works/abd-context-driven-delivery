"""agentic_tdd — cursor-agent test library and capability CLI.

Public API (test library):
    AgentSession   — persistent chat session
    AgentResult    — structured run outcome
    JudgeResult    — AI judge outcome
    AgentTest      — base pytest class (Given / When / Then)

Capability CLI (extends capability):
    build  — compile-check and structurally validate test files
    run    — execute the test suite with pytest
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import json
import os
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

# ---------------------------------------------------------------------------
# Import CapabilityCli and Capability from capability
# ---------------------------------------------------------------------------
_CDD_CAP = Path(__file__).resolve().parents[1] / "capability" / "capability.py"
_spec = importlib.util.spec_from_file_location("capability", _CDD_CAP)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("capability", _mod)
_spec.loader.exec_module(_mod)

Capability = _mod.Capability
_BaseCli = _mod.CapabilityCli

_CAPABILITY_ROOT = Path(__file__).resolve().parent
_CDD_DIR = _CAPABILITY_ROOT / ".cdd"

_CHAT_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    sys.__stdout__.write(f"[agentic_tdd {ts}] {msg}\n")
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
    if not cdd_dir.is_dir():
        return []
    if files is not None:
        mds = [cdd_dir / f for f in files if (cdd_dir / f).is_file()]
    else:
        mds = sorted(cdd_dir.glob("*.md"))
    return [f"# {md.name}\n\n{md.read_text(encoding='utf-8')}" for md in mds]


class AgentTest:
    """Base pytest class providing Given / When / Then helpers for cursor-agent tests."""

    cdd_dir: ClassVar[Path | None] = None
    default_rubric: ClassVar[str] = (
        "Validate that the shape and intent of the actual output matches the expected."
    )

    @staticmethod
    def assert_authenticated() -> None:
        exe = AgentSession._launcher()
        if exe is None:
            pytest.fail("cursor-agent not on PATH")
        result = subprocess.run([exe, "status"], capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            pytest.fail("cursor-agent not authenticated — run `cursor-agent login` first")

    @staticmethod
    def _assemble_prompt(*, guidance: str = "", prompt: str, context: str = "") -> str:
        parts: list[str] = [prompt]
        if context:
            parts.append(f"## Artifact\n\n{context}")
        if guidance:
            parts.append(f"## Standing Guidance\n\n{guidance}")
        return "\n\n---\n\n".join(parts)

    @staticmethod
    def _parse_judge_result(stdout: str) -> tuple[str, str]:
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

    def given_guidance(self, cdd_dir: Path | None = None, *, files: list[str] | None = None) -> str:
        parts: list[str] = []
        parts += _load_cdd(_CDD_DIR)
        consumer_dir = cdd_dir or self.cdd_dir
        if consumer_dir is None:
            subclass_file = Path(inspect.getfile(type(self)))
            consumer_dir = (subclass_file.parent / ".." / ".cdd").resolve()
        if consumer_dir != _CDD_DIR:
            parts += _load_cdd(consumer_dir, files=files)
        return "\n\n---\n\n".join(parts)

    def given_context(self, content: str) -> str:
        return content

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
        _log(f"when_agent_invoked: session={session_file.name}, "
             f"guidance={len(guidance)}chars, context={len(context)}chars, prompt={len(prompt)}chars")
        full_prompt = self._assemble_prompt(guidance=guidance, prompt=prompt, context=context)
        _log(f"full prompt assembled: {len(full_prompt)}chars total")
        session = AgentSession.get_or_create(session_file, workspace)
        return session.run(full_prompt, workspace, timeout_seconds=timeout_seconds)

    def ai_judge(
        self,
        *,
        output: str,
        rubric: str,
        workspace: Path,
        session_file: Path,
        timeout_seconds: int = 120,
    ) -> JudgeResult:
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

    @staticmethod
    def write_actual(actual_dir: Path, *, output: str, verdict: JudgeResult) -> None:
        """Persist agent output and judge verdict to actual_dir for inspection."""
        actual_dir.mkdir(parents=True, exist_ok=True)
        (actual_dir / "output.md").write_text(output, encoding="utf-8")
        (actual_dir / "verdict.md").write_text(
            f"{verdict.verdict}\n\n{verdict.reason}\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Capability CLI
# ---------------------------------------------------------------------------

class CapabilityCli(_BaseCli):
    """agentic-tdd capability CLI."""

    def _dispatch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == "build":
            return self._build()
        if args.command == "run":
            return self._run(args)
        return super()._dispatch(args, parser)

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = super()._build_parser()
        sub = parser._subparsers._group_actions[0]
        sub.add_parser("build", help="Compile-check and structurally validate all test files")
        run_p = sub.add_parser("run", help="Execute the agent test suite")
        run_p.add_argument("path", nargs="?", help="Path to test file or directory")
        run_p.add_argument("-v", "--verbose", action="store_true")
        return parser

    def _build(self) -> int:
        test_files = [
            p for p in sorted(_CAPABILITY_ROOT.rglob("test_*.py"))
            if "{" not in p.name and "examples" not in p.parts
        ]
        if not test_files:
            print("No test files found.")
            return 0

        failures: list[str] = []
        for py in test_files:
            rel = py.relative_to(_CAPABILITY_ROOT)
            issues = _check_test_file(py)
            if issues:
                failures.append(str(rel))
                print(f"FAIL  {rel}")
                for issue in issues:
                    print(f"      - {issue}")
            else:
                print(f"OK    {rel}")

        if failures:
            print(f"\n{len(failures)} file(s) failed.")
            return 1
        print(f"\nAll {len(test_files)} test file(s) OK.")
        return 0

    def _run(self, args: argparse.Namespace) -> int:
        target = Path(args.path).resolve() if args.path else _CAPABILITY_ROOT
        cmd = [sys.executable, "-m", "pytest", str(target)]
        if args.verbose:
            cmd.append("-v")
        env = os.environ.copy()
        pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(_CAPABILITY_ROOT) + (os.pathsep + pp if pp else "")
        return subprocess.run(cmd, env=env).returncode


# ---------------------------------------------------------------------------
# build helpers
# ---------------------------------------------------------------------------

def _check_test_file(path: Path) -> list[str]:
    issues: list[str] = []
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        issues.append(f"syntax error: {result.stderr.strip()}")
        return issues
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        issues.append(f"parse error: {exc}")
        return issues

    base_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name)

    all_methods: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    all_methods.append(item.name)

    call_attrs: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                call_attrs.append(node.func.attr)
            elif isinstance(node.func, ast.Name):
                call_attrs.append(node.func.id)

    if "AgentTest" not in imported:
        issues.append("does not import AgentTest from agentic_tdd")
    if "AgentTest" not in base_names:
        issues.append("no class inherits AgentTest")
    if not any(m.startswith("test_") for m in all_methods):
        issues.append("no test_ methods found")
    if "when_agent_invoked" not in call_attrs:
        issues.append("no call to when_agent_invoked (When step missing)")

    return issues


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    cap = Capability(_CAPABILITY_ROOT)
    return CapabilityCli(cap).execute(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
