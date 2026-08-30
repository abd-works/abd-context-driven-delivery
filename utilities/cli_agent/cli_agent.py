# @toolset-manifest python -m tools manifest cli_agent.cli_agent:CliAgent
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Slash /cli-agent — SubAgent turn policy, IDE CLI spawn instead of in-chat Task."""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from harness.harness_tool import prompt
from primitives.actions.action import agentic_toolset
from sub_agent.sub_agent import SubAgent, sub_agent
from tools.tool import agent_tool


@dataclass
class IdeCliResult:
    """Outcome of one spawned IDE CLI process."""

    exit_code: int
    text: str
    stderr: str
    argv: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    pid: int = 0


def _pid_alive(pid: int) -> bool:
    """True when ``pid`` refers to a running process (OS-level liveness)."""
    pid = int(pid or 0)
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _kill_pid(pid: int) -> bool:
    """Force-stop ``pid`` if alive. Returns True when a kill was attempted."""
    pid = int(pid or 0)
    if pid <= 0 or not _pid_alive(pid):
        return False
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            check=False,
        )
        return True
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            return False
    return True


def _kill_workspace_agent_procs(workspace: str) -> list[str]:
    """Kill stray cursor-agent processes whose command line targets ``workspace``."""
    root = str(Path(workspace).resolve())
    markers = (root, root.replace("\\", "/"), root.replace("\\", "\\\\"))
    killed: list[str] = []
    if os.name != "nt":
        return killed
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-CimInstance Win32_Process | "
                "Where-Object { $_.CommandLine -and "
                "($_.CommandLine -match 'cursor-agent|--resume') } | "
                "Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=45,
        )
    except (OSError, subprocess.TimeoutExpired):
        return killed
    raw = (completed.stdout or "").strip()
    if not raw:
        return killed
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError:
        return killed
    if isinstance(rows, dict):
        rows = [rows]
    for row in rows or []:
        cmd = str(row.get("CommandLine") or "")
        if not any(m in cmd for m in markers):
            continue
        if "cursor-agent" not in cmd.lower() and "--resume" not in cmd:
            continue
        pid = int(row.get("ProcessId") or 0)
        if _kill_pid(pid):
            killed.append(f"orphan:{pid}")
    return killed


class _TaskFile:
    """Task text on disk so the CLI argv stays short."""

    def path_for(self, workspace: str, name: str) -> Path:
        return Path(workspace) / ".context" / name

    def relative_path(self, path: Path, workspace: str) -> str:
        try:
            return path.relative_to(workspace).as_posix()
        except ValueError:
            return path.as_posix()

    def persist(self, task: str, workspace: str, name: str) -> str:
        path = self.path_for(workspace, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(task, encoding="utf-8")
        return self.relative_path(path, workspace)


class _TurnBinder:
    """Bind listed tools and one action onto a hanging Turn."""

    def bind(self, host: IdeCli, turn, tools, action=None):
        self._bind_action(host, turn, action)
        self._bind_prose(host, turn, tools)
        self._bind_toolsets(host, turn, tools)
        return turn

    def _bind_action(self, host: IdeCli, turn, action) -> None:
        if action is None:
            return
        if not str(action).strip():
            return
        if host._is_toolset_ref(action):
            turn.action = host._action_name(action)
            return
        if isinstance(action, str):
            turn.prompt = action
            return
        turn.action = host._action_name(action)

    def _bind_prose(self, host: IdeCli, turn, tools) -> None:
        listed = host._listed(tools)
        prose = [
            tool_ref
            for tool_ref in listed
            if isinstance(tool_ref, str) and not host._is_toolset_ref(tool_ref)
        ]
        if prose:
            turn.prompt = " ".join(prose)

    def _bind_toolsets(self, host: IdeCli, turn, tools) -> None:
        act = turn.action or "run"
        for tool_ref in host._listed(tools):
            if not host._is_toolset_ref(tool_ref):
                continue
            self._append_toolset(host, turn, tool_ref, act)

    def _append_toolset(self, host: IdeCli, turn, tool_ref, act: str) -> None:
        from workspace.workspace import ToolCall

        lens = host._tool_lens(tool_ref)
        ref = lens["toolset"]
        if ref and ref not in turn.tool_keys:
            turn.tool_keys.append(ref)
        if not self._already_bound(turn, ref, act):
            turn.tool_calls.append(
                ToolCall(
                    toolset=ref,
                    name=act,
                    summary=host._lens_label(tool_ref),
                    role="run",
                )
            )
        if lens["fidelity"]:
            turn.fidelity = lens["fidelity"]
        if lens["format"]:
            turn.format = lens["format"]

    def _already_bound(self, turn, ref: str, act: str) -> bool:
        for call in turn.tool_calls:
            if call.toolset == ref and call.name == act:
                return True
        return False

    def mapping_lens(self, tool_ref: dict) -> dict[str, str]:
        ctx = tool_ref.get("context")
        if not isinstance(ctx, dict):
            ctx = {}
        return {
            "toolset": self._first_text(tool_ref, "toolset", "tool"),
            "fidelity": self._field_or_ctx(tool_ref, ctx, "fidelity"),
            "format": self._field_or_ctx(tool_ref, ctx, "format"),
        }

    def _first_text(self, tool_ref: dict, key: str, other: str) -> str:
        text = tool_ref.get(key)
        if not text:
            text = tool_ref.get(other)
        if not text:
            return ""
        return str(text).strip()

    def _field_or_ctx(self, tool_ref: dict, ctx: dict, key: str) -> str:
        text = tool_ref.get(key)
        if not text:
            text = ctx.get(key)
        if not text:
            return ""
        return str(text).strip()

    def align(self, host: IdeCli, tools, generate_tools) -> list:
        listed = host._listed(tools)
        by_ref = self._lenses_by_ref(host, generate_tools)
        aligned = []
        for tool_ref in listed:
            aligned.append(self._aligned_ref(host, tool_ref, by_ref))
        return aligned

    def _lenses_by_ref(self, host: IdeCli, generate_tools) -> dict:
        by_ref = {}
        for tool_ref in host._listed(generate_tools):
            lens = host._tool_lens(tool_ref)
            by_ref[lens["toolset"]] = lens
        return by_ref

    def _lookup_lens(self, by_ref: dict, toolset: str):
        return by_ref.get(toolset)

    def _aligned_ref(self, host: IdeCli, tool_ref, by_ref: dict):
        lens = host._tool_lens(tool_ref)
        src = self._lookup_lens(by_ref, lens["toolset"])
        if src is None:
            return tool_ref
        if not src["fidelity"]:
            if not src["format"]:
                return tool_ref
        return self._overlay(tool_ref, lens, src)

    def _overlay(self, tool_ref, lens, src) -> dict:
        ctx = {}
        if isinstance(tool_ref, dict):
            existing = tool_ref.get("context")
            if isinstance(existing, dict):
                ctx.update(existing)
        self._fill_ctx(ctx, src)
        if isinstance(tool_ref, dict):
            merged = {**tool_ref, "context": ctx}
            return merged
        return {"toolset": lens["toolset"], "context": ctx}

    def _fill_ctx(self, ctx: dict, src: dict) -> None:
        if src["fidelity"]:
            if not ctx.get("fidelity"):
                ctx["fidelity"] = src["fidelity"]
        if src["format"]:
            if not ctx.get("format"):
                ctx["format"] = src["format"]


class _TurnPrompt:
    """Prompt text from a hanging Turn and later guidance."""

    def render(self, host: IdeCli, turn, later_actions=None) -> str:
        lines = self._turn_lines(host, turn)
        if later_actions:
            for later_action in later_actions:
                lines.append(host._later_step(later_action))
            lines.append(host._next_turn)
        return "\n".join(lines) + "\n"

    def _turn_lines(self, host: IdeCli, turn) -> list[str]:
        keys = ", ".join(turn.tool_keys) or "(none)"
        calls = self._call_label(turn)
        lines = [
            "This is an interactive session.",
            f"Turn.action: {turn.action or '(none)'} (guidance — the CLI decides the Turn)",
            f"Turn.tool_keys: {keys}",
            f"Turn.toolCalls: {calls}",
        ]
        if turn.fidelity:
            lines.append(f"Turn.fidelity: {turn.fidelity}")
        if turn.format:
            lines.append(f"Turn.format: {turn.format}")
        prose = getattr(turn, "prompt", "") or host.prompt
        if prose:
            lines.append(f"Turn.prompt: {prose}")
        lines.append(host._turn_close)
        return lines

    def _call_label(self, turn) -> str:
        parts = []
        for call in turn.tool_calls:
            parts.append(f"{call.toolset} name={call.name} {call.summary}".strip())
        if parts:
            return ", ".join(parts)
        return "(none)"


class _JudgePrompt:
    """Judge session text for the same Turn and source scope."""

    def extras(self, host: IdeCli) -> list[str]:
        task = host.judge
        extra = [
            host._judge_reply_to_doer,
            host._validate_same_lens,
            host.source_scope,
        ]
        prior = self._task_prior(task)
        if prior:
            extra.insert(1, prior)
        return extra

    def _task_tools(self, task: dict, tools):
        listed = task.get("tools")
        if not listed:
            return tools
        return listed

    def _task_prior(self, task) -> str:
        if isinstance(task, str):
            return task
        if not isinstance(task, dict):
            return ""
        prior = task.get("context")
        if not prior:
            prior = task.get("prompt")
        if not prior:
            return ""
        return str(prior).strip()

    def from_turn(self, host: IdeCli, turn) -> str:
        hanging = host._blank_turn()
        hanging.tool_keys = list(turn.tool_keys)
        hanging.tool_calls = list(turn.tool_calls)
        hanging.fidelity = turn.fidelity
        hanging.format = turn.format
        hanging.prompt = getattr(turn, "prompt", "") or ""
        hanging.action = "Validate"
        return self._with_job(host, hanging, self.extras(host))

    def from_tools(self, host: IdeCli, generate_tools) -> str:
        tools = host._listed(generate_tools)
        task = host.judge
        if isinstance(task, dict):
            tools = host._align_tools(self._task_tools(task, tools), generate_tools)
        else:
            tools = host._align_tools(tools, generate_tools)
        hanging = host._bind_turn(
            host._blank_turn(), tools, "validate.validate:Validate"
        )
        return self._with_job(host, hanging, self.extras(host))

    def _with_job(self, host: IdeCli, hanging, extras: list[str]) -> str:
        body = host._turn_prompt(hanging) + "\n".join(extras)
        if host.job:
            body += "\n--- JOB / SOURCE SCOPE ---\n" + host.job + "\n"
        if body.endswith("\n"):
            return body
        return body + "\n"


class _CliSpawner:
    """Start an IDE CLI process and return immediately."""

    def spawn_role(self, argv: list[str]) -> str:
        # VS Code ask mode, or Cursor judge launch/task file in the prompt argv.
        if "--mode" in argv and "ask" in argv:
            return "judge"
        joined = " ".join(str(a) for a in argv)
        if "cli-agent-judge" in joined:
            return "judge"
        return "doer"

    def popen_kwargs(self, workspace: str) -> dict:
        kwargs: dict = {"cwd": workspace or None}
        if os.name != "nt":
            return kwargs
        if not hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            return kwargs
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        return kwargs

    def _log_path(self, workspace: str, role: str, session: str = "") -> Path:
        root = Path(workspace) if workspace else Path.cwd()
        if session:
            return root / ".context" / "sessions" / session / f"cli-agent-{role}.log"
        return root / ".context" / f"cli-agent-{role}.log"

    def _log_lines(self, argv: list[str]) -> str:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"\n--- spawn {stamp} ---\n" + " ".join(argv) + "\n"

    def append_log(self, workspace: str, argv: list[str], role: str, session: str = "") -> None:
        log_path = self._log_path(workspace, role, session)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log = log_path.open("a", encoding="utf-8")
        log.write(self._log_lines(argv))
        log.close()

    def start(
        self, argv: list[str], workspace: str, existing_pid: int = 0, _skip_log: bool = False
    ) -> IdeCliResult:
        role = self.spawn_role(argv)
        existing_pid = int(existing_pid or 0)
        if existing_pid > 0 and _pid_alive(existing_pid):
            # Do not log a second spawn — ground-truth doer log must stay at 1.
            return IdeCliResult(
                exit_code=0,
                text=f"pid: {existing_pid}",
                stderr="",
                argv=list(argv),
                elapsed_seconds=0.0,
                pid=existing_pid,
            )
        if not _skip_log:
            self.append_log(workspace, argv, role)
        proc = subprocess.Popen(argv, **self.popen_kwargs(workspace))
        return IdeCliResult(
            exit_code=0,
            text=f"pid: {proc.pid}",
            stderr="",
            argv=list(argv),
            elapsed_seconds=0.0,
            pid=int(proc.pid or 0),
        )

    def with_elapsed(self, result: IdeCliResult, started: float) -> IdeCliResult:
        result.elapsed_seconds = time.perf_counter() - started
        return result


class _CliScratch:
    """Temps CliAgent writes. WorkSession must not know these names."""

    _context_names = frozenset(
        {
            "cli-agent-task.txt",
            "cli-agent-judge.txt",
            "cli-agent-put-back.txt",
            "cli-agent-doer.log",
            "cli-agent-judge.log",
            "_judge_check.py",
        }
    )
    _session_prefixes = (
        "wait_judge",
        "judge-verdict",
        "judge-attempt",
        "judge-before",
        "_scan",
    )

    def wipe(self, work) -> None:
        self._wipe_context(Path(getattr(work, "path", "") or ".") / ".context", work)
        folder = getattr(work, "folder", None)
        if folder is not None:
            self._wipe_session(Path(folder))

    def _wipe_context(self, ctx: Path, work) -> None:
        if not ctx.is_dir():
            return
        for name in self._context_names:
            path = ctx / name
            if path.is_file() and not self._tracked(work, path):
                path.unlink(missing_ok=True)

    def _wipe_session(self, folder: Path) -> None:
        if not folder.is_dir():
            return
        for path in list(folder.iterdir()):
            if path.is_file() and self._session_owned(path.name):
                path.unlink(missing_ok=True)

    def _session_owned(self, name: str) -> bool:
        if name == JobQueue.filename:
            return True
        if name.endswith("-response.yaml"):
            return True
        return name.startswith(self._session_prefixes)

    def _tracked(self, work, path: Path) -> bool:
        git = getattr(work, "git", None)
        root = getattr(git, "root", None)
        if git is None or not root:
            return False
        try:
            rel = path.resolve().relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            return False
        try:
            return bool(str(git._git("ls-files", "--", rel)).strip())
        except Exception:
            return False


class JobQueue:
    """FIFO jobs on the WorkSession — assign or append; launch_next sends one."""

    filename = "cli-agent-job-queue.json"
    empty = "job_queue empty: nothing to send to the CLI"

    def path_for(self, work) -> Path:
        folder = getattr(work, "folder", None)
        if folder:
            return Path(folder) / self.filename
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return Path(root) / ".context" / "sessions" / name / self.filename

    def load(self, work) -> list:
        path = self.path_for(work)
        if not path.is_file():
            return []
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        return []

    def save(self, work, items: list) -> None:
        path = self.path_for(work)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    def push(self, work, item: dict) -> int:
        items = self.load(work)
        items.append(item)
        self.save(work, items)
        return len(items)

    def peek(self, work) -> dict | None:
        items = self.load(work)
        if not items:
            return None
        return items[0]

    def pop(self, work) -> dict | None:
        items = self.load(work)
        if not items:
            return None
        head, rest = items[0], items[1:]
        self.save(work, rest)
        return head


class _CliAgentLog:
    """Append-only event log for a cli-agent session: cli-agent-session.jsonl."""

    filename = "cli-agent-session.jsonl"
    _last_ms: dict[str, int] = {}
    _job_started_ms: dict[str, dict[int, int]] = {}
    _judge_started_ms: dict[str, int] = {}

    def path_for(self, work) -> Path:
        folder = getattr(work, "folder", None)
        if folder:
            return Path(folder) / self.filename
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return Path(root) / ".context" / "sessions" / name / self.filename

    def _work_key(self, work) -> str:
        return str(self.path_for(work))

    def _job_queue_path(self, work) -> str:
        folder = getattr(work, "folder", None)
        if folder:
            return str(Path(folder) / JobQueue.filename)
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return str(Path(root) / ".context" / "sessions" / name / JobQueue.filename)

    @staticmethod
    def _kit_list(raw) -> list[str]:
        if not raw:
            return []
        if isinstance(raw, list):
            return [str(x) for x in raw if x is not None and str(x).strip()]
        return [str(raw)]

    @classmethod
    def _job_kit(cls, item: dict | None) -> dict:
        if not item:
            return {}
        out: dict = {}
        tools = cls._kit_list(item.get("tools"))
        actions = cls._kit_list(item.get("actions"))
        if tools:
            out["tools"] = tools
        if actions:
            out["actions"] = actions
        if "judge" in item:
            out["judge"] = item.get("judge")
        if "human" in item or "human_check" in item:
            out["human"] = bool(item.get("human") or item.get("human_check"))
        return out

    @classmethod
    def _turn_kit(cls, turn, tools=None, actions=None) -> dict:
        out: dict = {}
        tool_keys = cls._kit_list(getattr(turn, "tool_keys", None) if turn else None)
        if not tool_keys:
            tool_keys = cls._kit_list(tools)
        action_keys = cls._kit_list(actions)
        if turn and getattr(turn, "action", None) and not action_keys:
            action_keys = [str(turn.action)]
        if tool_keys:
            out["tools"] = tool_keys
        if action_keys:
            out["actions"] = action_keys
        calls = []
        for call in getattr(turn, "tool_calls", None) or []:
            calls.append(f"{call.toolset} name={call.name} {call.summary}".strip())
        if calls:
            out["tool_calls"] = calls
        return out

    def append(self, work, record: dict) -> None:
        path = self.path_for(work)
        path.parent.mkdir(parents=True, exist_ok=True)
        key = self._work_key(work)
        now_ms = int(time.time() * 1000)
        record["ts_ms"] = now_ms
        record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now_ms / 1000))
        if key in self._last_ms:
            record["since_last_s"] = round((now_ms - self._last_ms[key]) / 1000, 3)
        self._last_ms[key] = now_ms
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def read_records(self, work) -> list[dict]:
        path = self.path_for(work)
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def header(
        self,
        work,
        *,
        doer: str,
        judge: str,
        doer_pid: int = 0,
        judge_pid: int = 0,
        chat: str = "",
        job_queue: str = "",
    ) -> None:
        """One-time session header: ids, chat link, job-queue path."""
        self.append(
            work,
            {
                "kind": "header",
                "doer": doer,
                "judge": judge,
                "doer_pid": doer_pid,
                "judge_pid": judge_pid,
                "chat": chat,
                "job_queue": job_queue or self._job_queue_path(work),
            },
        )

    def session_start(self, work, doer: str, judge: str, doer_pid: int, judge_pid: int, doer_transcript: str, judge_transcript: str) -> None:
        self.append(work, {
            "kind": "session_start",
            "doer": doer,
            "doer_pid": doer_pid,
            "doer_transcript": doer_transcript,
            "chat": doer_transcript,
            "judge": judge,
            "judge_pid": judge_pid,
            "judge_transcript": judge_transcript,
            "job_queue": self._job_queue_path(work),
        })

    def spawn(
        self,
        work,
        role: str,
        resume: str,
        prompt: str,
        argv: str,
        *,
        tools: list[str] | None = None,
        actions: list[str] | None = None,
        tool_calls: list[str] | None = None,
        job_index: int | None = None,
    ) -> None:
        record: dict = {
            "kind": "spawn",
            "role": role,
            "resume": resume,
            "prompt": prompt,
            "argv": argv,
        }
        if tools:
            record["tools"] = list(tools)
        if actions:
            record["actions"] = list(actions)
        if tool_calls:
            record["tool_calls"] = list(tool_calls)
        if job_index is not None:
            record["job_index"] = job_index
        self.append(work, record)

    def jobs_defined(self, work, jobs: list) -> None:
        self.append(work, {"kind": "jobs_defined", "jobs": jobs})

    def job_started(
        self,
        work,
        index: int,
        prompt: str,
        *,
        tools: list[str] | None = None,
        actions: list[str] | None = None,
        judge=None,
        human=None,
    ) -> None:
        record: dict = {"kind": "job_started", "index": index, "prompt": prompt}
        if tools:
            record["tools"] = list(tools)
        if actions:
            record["actions"] = list(actions)
        if judge is not None:
            record["judge"] = judge
        if human is not None:
            record["human"] = human
        self.append(work, record)
        key = self._work_key(work)
        self._job_started_ms.setdefault(key, {})[index] = record["ts_ms"]

    def job_finished(
        self,
        work,
        index: int,
        prompt: str,
        *,
        summary: str = "",
        refs: list[str] | None = None,
        tools: list[str] | None = None,
        actions: list[str] | None = None,
        judge=None,
        human=None,
    ) -> None:
        record: dict = {"kind": "job_finished", "index": index, "prompt": prompt}
        if summary:
            record["summary"] = summary
        if refs:
            record["refs"] = list(refs)
        if tools:
            record["tools"] = list(tools)
        if actions:
            record["actions"] = list(actions)
        if judge is not None:
            record["judge"] = judge
        if human is not None:
            record["human"] = human
        key = self._work_key(work)
        started = self._job_started_ms.get(key, {}).pop(index, None)
        now_ms = int(time.time() * 1000)
        if started is not None:
            record["duration_s"] = round((now_ms - started) / 1000, 3)
        self.append(work, record)

    def human_check_needed(self, work, *, job_index: int) -> None:
        self.append(work, {"kind": "human_check_needed", "job_index": job_index})

    def human_notified(
        self,
        work,
        *,
        job_index: int,
        title: str,
        body: str,
        channel: str = "os",
    ) -> None:
        """Record that a human-visible notification was attempted for a check."""
        self.append(
            work,
            {
                "kind": "human_notified",
                "job_index": job_index,
                "title": title,
                "body": body,
                "channel": channel,
            },
        )

    def human_check_resolved(
        self,
        work,
        *,
        job_index: int,
        result: str,
        feedback: str = "",
    ) -> None:
        record: dict = {
            "kind": "human_check_resolved",
            "job_index": job_index,
            "result": result,
        }
        if feedback:
            record["feedback"] = feedback
        self.append(work, record)

    def judge_started(self, work, *, job_index: int, judge: str) -> None:
        record = {"kind": "judge_started", "job_index": job_index, "judge": judge}
        self.append(work, record)
        self._judge_started_ms[self._work_key(work)] = record["ts_ms"]

    def verdict(self, work, result: str, notes: str = "", *, job_index: int | None = None) -> None:
        record: dict = {"kind": "verdict", "result": result, "notes": notes}
        if job_index is not None:
            record["job_index"] = job_index
        key = self._work_key(work)
        started = self._judge_started_ms.pop(key, None)
        if started is not None:
            record["duration_s"] = round((int(time.time() * 1000) - started) / 1000, 3)
        self.append(work, record)

    def orchestrator_started(self, work) -> None:
        self.append(work, {"kind": "orchestrator_started"})

    def orchestrator_stopped(self, work, *, reason: str = "") -> None:
        record: dict = {"kind": "orchestrator_stopped"}
        if reason:
            record["reason"] = reason
        self.append(work, record)

    def doer_finished(self, work, *, job_index: int) -> None:
        self.append(work, {"kind": "doer_finished", "job_index": job_index})

    def recovery(self, work, *, job_index: int, detail: str = "") -> None:
        record: dict = {"kind": "recovery", "job_index": job_index}
        if detail:
            record["detail"] = detail
        self.append(work, record)

    def error(self, work, *, detail: str, job_index: int | None = None) -> None:
        record: dict = {"kind": "error", "detail": detail}
        if job_index is not None:
            record["job_index"] = job_index
        self.append(work, record)


class _TranscriptWatch:
    """Poll Cursor agent jsonl transcripts for turn end and judge verdict."""

    _pass_word = re.compile(r"\bPASS\b")
    _fail_word = re.compile(r"\bFAIL\b")

    def line_count(self, path: Path) -> int:
        if not path.is_file():
            return 0
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))

    def wait_for_growth(
        self,
        path: Path,
        before: int,
        *,
        stall_s: float,
        quiet_s: float = 3.0,
        poll_s: float = 0.5,
        sleep=time.sleep,
        clock=time.time,
    ) -> None:
        deadline = clock() + max(0.0, stall_s)
        while clock() < deadline:
            if self.line_count(path) > before:
                self._wait_quiescence(
                    path, quiet_s=quiet_s, deadline=deadline, poll_s=poll_s, sleep=sleep, clock=clock
                )
                return
            sleep(poll_s)
        raise RuntimeError(
            f"stall: transcript did not grow within {stall_s}s ({path})"
        )

    def _wait_quiescence(
        self,
        path: Path,
        *,
        quiet_s: float,
        deadline: float,
        poll_s: float,
        sleep,
        clock,
    ) -> None:
        last = self.line_count(path)
        stable_at = clock()
        while clock() < deadline:
            now = self.line_count(path)
            if now != last:
                last = now
                stable_at = clock()
            elif clock() - stable_at >= quiet_s:
                return
            sleep(poll_s)

    def read_verdict(self, path: Path) -> str:
        if not path.is_file():
            return ""
        for line in reversed(path.read_text(encoding="utf-8", errors="replace").splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("role") != "assistant":
                continue
            text = self._assistant_text(row).upper()
            if "FAIL" in text:
                return "FAIL"
            if "PASS" in text:
                return "PASS"
        return ""

    def _assistant_text(self, row: dict) -> str:
        # Flat fixtures use top-level content; live Cursor jsonl nests under message.
        content = row.get("content")
        if content is None and isinstance(row.get("message"), dict):
            content = row["message"].get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text") or ""))
            return "\n".join(parts)
        return str(content or "")


class _Pickup:
    """Fail launch only when the doer neither takes the job nor stays alive."""

    not_taken_up = (
        "NOT TAKEN UP: the doer did not accept the new job and no live doer pid "
        "is bound. Do not wait."
    )
    _user_mark = '"role":"user"'

    def cursor_transcript(self, workspace: str, resume: str) -> Path:
        resume = (resume or "").strip()
        raw = str(Path(workspace).resolve())
        # Cursor project slug: path seps and underscores become '-'.
        slug = (
            raw.replace(":", "")
            .replace("\\", "-")
            .replace("/", "-")
            .replace("_", "-")
        )
        return (
            Path.home()
            / ".cursor"
            / "projects"
            / slug
            / "agent-transcripts"
            / resume
            / f"{resume}.jsonl"
        )

    def user_count(self, path: Path) -> int:
        if not path.is_file():
            return 0
        text = path.read_text(encoding="utf-8", errors="replace")
        return text.count(self._user_mark)

    def accepted(
        self,
        path: Path,
        before: int,
        *,
        seconds: float,
        sleep=time.sleep,
        clock=time.time,
    ) -> bool:
        deadline = clock() + max(0.0, seconds)
        while True:
            if self.user_count(path) > before:
                return True
            if clock() >= deadline:
                return False
            sleep(0.25)


class _ChatMint:
    """CLI session identity from create-chat or a minted id."""

    _chat_id = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        re.IGNORECASE,
    )

    def mint(self) -> str:
        return str(uuid.uuid4())

    def from_stdout(self, stdout: str, stderr: str, exit_code: int) -> str:
        if exit_code != 0:
            raise RuntimeError(
                f"cursor-agent create-chat failed (exit {exit_code}).\n"
                f"stdout: {stdout}\nstderr: {stderr}"
            )
        match = self._chat_id.search(stdout or "")
        if match:
            return match.group(0)
        raise RuntimeError(
            f"cursor-agent create-chat returned no chat id.\n"
            f"stdout: {stdout}\nstderr: {stderr}"
        )


class _SessionArgv:
    """Vendor argv for one interactive session."""

    def _cursor_model(self, host: IdeCli) -> str:
        name = host.model
        if not name:
            name = host.resolve_session_model()
        if not name:
            return ""
        if "[" in name:
            return name
        if host.mode == "fast":
            return f"{name}[fast=true]"
        if host.mode == "medium":
            return f"{name}[fast=false]"
        return name

    def _cursor_args(
        self, host: IdeCli, prompt: str, workspace: str, *, resume: str = ""
    ) -> list[str]:
        exe = host._require_launcher("cursor-agent not found on PATH")
        args = [exe]
        self._cursor_trust(host, args)
        if resume:
            args.extend(["--resume", resume])
        args.extend(["--workspace", str(workspace)])
        self._cursor_stream(host, args)
        model = self._cursor_model(host)
        agent_mode = host.agent_mode
        if model:
            args.extend(["--model", model])
        if agent_mode in {"plan", "ask"}:
            args.extend(["--mode", agent_mode])
        if prompt:
            args.append(prompt)
        return args

    def _cursor_trust(self, host: IdeCli, args: list[str]) -> None:
        args.extend(["--force", "--trust"])

    def _cursor_stream(self, host: IdeCli, args: list[str]) -> None:
        if host.print_mode:
            args.extend(["--print", "--output-format", "stream-json"])

    def _vscode_mode(self, agent_mode: str) -> str:
        if agent_mode == "ask":
            return "ask"
        if agent_mode == "edit":
            return "edit"
        return "agent"

    def _vscode_args(self, host: IdeCli, prompt: str, workspace: str) -> list[str]:
        exe = host._require_launcher("code not found on PATH")
        args = [exe]
        if workspace:
            args.append(str(workspace))
        args.extend(
            ["chat", "--new-window", "--mode", self._vscode_mode(host.agent_mode)]
        )
        args.append(prompt)
        return args


class _WorkAttach:
    """Bind doer and judge CLI identities onto the WorkSession."""

    def attach(self, agent: CliAgent):
        work = agent._ensure_work_session()
        work.load_cli_sessions()
        vendor = agent.ide._detect()
        if not work.cli_doer:
            work.associate_cli("doer", vendor._create_chat(agent._workspace_root()))
        # Mint judge even when doer already open (run_backlog attaches before
        # _judge_job is set; a later attach must still bind the judge).
        if agent._judge_job and vendor.judge and not (work.cli_judge or "").strip():
            work.associate_cli("judge", vendor._create_chat(agent._workspace_root()))
        agent._ide = vendor._copy_policy(vendor._resumed(work.cli_doer, work.cli_judge))
        return work


class IdeCli:
    """Pick and invoke the installed IDE agent CLI.

    Pass model, mode, agent_mode, and judge once; they are properties afterward
    and every command() / launch_cli() reuses them.
    job, source_scope, and prompt are this instance's work, not module state.
    Default launch is an interactive session.
    // always one of CursorCli or VscodeCli after detect
    """

    create_chat_timeout_seconds = 60
    _spawn_timeout_seconds = 300
    _turn_close = (
        "The CLI opens the hanging workspace.Turn when it runs the action. "
        "Finish that Turn after the action so it commits. "
        "CliAgent does not open the Turn."
    )
    _next_turn = (
        "Listed actions are guidance, not a locked sequence. "
        "The CLI has the final say on what the next Turn is — "
        "same as a chat agent. After finish, decide the next Turn "
        "from that guidance and the work in front of you. "
        "Do not wait for the operator."
    )
    _default_source_scope = (
        "Compare what was written to the source scope of the original job. "
        "The job is the worker prompt and its sources (story map, sketch, "
        "model, or named subset). Scope may be the whole artifact or a "
        "stated slice — use that scope, not only the files that happen to "
        "exist. Missing nodes, epics, or files that the source scope called "
        "for are a fail. Do not treat a leftover or partial tree as complete."
    )
    _validate_same_lens = (
        "Validate at the same fidelity and format as that Turn. "
        "Judge the artifacts produced at that fidelity and format. "
        "When format is markdown, validate the markdown; do not look for source code."
    )
    _judge_reply_to_doer = (
        "The doer invoked you after it finished the Turn. Validate now. "
        "Reply PASS or FAIL to the doer and finish this Turn. "
        "Do not wait for the parent. The parent is not in this loop."
    )
    _launch = "Read {path} and follow it exactly."
    _cmdline_safe = 4096
    _parent_checkin = (
        "The parent talks to the doer only. When you launch CliAgent from Cursor, open the IDE Terminal panel as part of that run (Shell tool — print the process reference). Leave the OS CREATE_NEW_CONSOLE alone. Never call cursor.exe / --open-url / --command to open a terminal. After jobs are on the queue, "
        "if this is Cursor, watch with a 30s /loop; otherwise check the "
        "doer the usual way without notify_on_output. Every once in a while, "
        "check the doer (logs, transcript tail, hanging Turn, artifacts). "
        "If the doer did not take the job (NOT TAKEN UP), stop — do not wait. "
        "When the session log shows human_check_needed (and human_notified), you ARE the check: "
        "an IDE/OS notification was already fired for the operator. Call "
        "resolve_human_check(result='looks_good') or "
        "resolve_human_check(result='needs_fixing', feedback='...') "
        "(or write the matching human-check-{index}.json in the session folder). "
        "Do not invent a judge loop for human jobs. "
        "If the doer stopped after three judge FAILs, do not mindlessly loop: "
        "read the judge FAIL (transcript / finish_turn result), investigate the "
        "named leftovers in the workspace, revise the job prompt (update "
        ".context/cli-agent-task.txt and the job_queue head) so the next attempt "
        "targets those exact fails, then send one continue resume to the doer. "
        "Do not stack --resume prompts. Do not prompt, launch, or score the "
        "judge. The doer runs the judge and waits. Do not drive the work with -p."
    )

    def __init__(
        self,
        model: str = "",
        mode: str = "",
        agent_mode: str = "",
        judge: bool | str | dict = False,
        resume: str = "",
        judge_resume: str = "",
        print_mode: bool = False,
        pickup_seconds: float = 12.0,
    ) -> None:
        self._model = (model or "").strip()
        self._mode = (mode or "").strip().lower()
        self._agent_mode = (agent_mode or "").strip().lower()
        self._judge = False if judge in (None, "") else judge
        self._resume = (resume or "").strip()
        self._judge_resume = (judge_resume or "").strip()
        self._print_mode = bool(print_mode)
        self._pickup_seconds = float(pickup_seconds)
        self._job = ""
        self._prompt = ""
        self._source_scope = type(self)._default_source_scope
        self._session = ""
        self._workspace = ""

    def bind_workspace(self, workspace: str = "", session: str = "") -> IdeCli:
        """Remember workspace/session so an unset model can load from session storage."""
        if workspace:
            self._workspace = str(workspace).strip()
        if session:
            self._session = str(session).strip()
        return self

    def resolve_session_model(self) -> str:
        """Read ``.context/sessions/{session}/model`` when IdeCli.model is empty."""
        if self._model:
            return self._model
        root = (self._workspace or "").strip()
        if not root:
            return ""
        try:
            from workspace.workspace import SessionModel
        except ImportError:
            return ""
        return SessionModel.read(root, self._session)

    @property
    def job(self) -> str:
        return self._job

    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def source_scope(self) -> str:
        return self._source_scope

    @property
    def model(self) -> str:
        return self._model

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def agent_mode(self) -> str:
        return self._agent_mode

    @property
    def judge(self) -> bool | str | dict:
        return self._judge

    @property
    def resume(self) -> str:
        return self._resume

    @property
    def judge_resume(self) -> str:
        return self._judge_resume

    @property
    def print_mode(self) -> bool:
        return self._print_mode

    @property
    def pickup_seconds(self) -> float:
        return self._pickup_seconds

    def _listed(self, tools) -> list:
        if tools is None:
            return []
        return list(tools)

    def _copy_policy(self, other: IdeCli) -> IdeCli:
        other._job = self.job
        other._prompt = self.prompt
        other._source_scope = self.source_scope
        other._session = self._session
        other._validate_same_lens = self._validate_same_lens
        other._turn_close = self._turn_close
        other._next_turn = self._next_turn
        other._launch = self._launch
        other._cmdline_safe = self._cmdline_safe
        other._parent_checkin = self._parent_checkin
        return other

    def _vendor_kwargs(self) -> dict:
        return {
            "model": self.model,
            "mode": self.mode,
            "agent_mode": self.agent_mode,
            "judge": self.judge,
            "resume": self.resume,
            "judge_resume": self.judge_resume,
            "print_mode": self.print_mode,
            "pickup_seconds": self.pickup_seconds,
        }

    def _as_vendor(self, vendor: type[IdeCli]) -> IdeCli:
        return self._copy_policy(vendor(**self._vendor_kwargs()))

    def _resumed(self, resume: str, judge_resume: str) -> IdeCli:
        flags = self._vendor_kwargs()
        flags["resume"] = resume
        flags["judge_resume"] = judge_resume
        sibling = type(self)(**flags)
        sibling._job = self.job
        sibling._prompt = self.prompt
        sibling._source_scope = self.source_scope
        return sibling

    def _tool_lens(self, tool_ref: object) -> dict[str, str]:
        if isinstance(tool_ref, dict):
            return _TurnBinder().mapping_lens(tool_ref)
        return {"toolset": str(tool_ref).strip(), "fidelity": "", "format": ""}

    def _lens_label(self, tool_ref: object) -> str:
        lens = self._tool_lens(tool_ref)
        parts = [lens["toolset"] or str(tool_ref)]
        if lens["fidelity"]:
            parts.append(f"fidelity={lens['fidelity']}")
        if lens["format"]:
            parts.append(f"format={lens['format']}")
        return " ".join(parts)

    def _blank_turn(self):
        from workspace.workspace import Turn

        return Turn.hanging()

    def _ref_text(self, tool_ref: dict) -> str:
        raw = tool_ref.get("toolset")
        if not raw:
            raw = tool_ref.get("tool")
        if not raw:
            return ""
        return str(raw)

    def _is_toolset_ref(self, tool_ref: object) -> bool:
        if isinstance(tool_ref, dict):
            return ":" in self._ref_text(tool_ref)
        if not isinstance(tool_ref, str):
            return False
        return ":" in tool_ref

    def _action_name(self, tool_ref: object) -> str:
        raw = str(tool_ref or "").strip()
        if not raw:
            return ""
        if ":" in raw:
            raw = raw.rsplit(":", 1)[-1]
        if "." in raw and self._is_toolset_ref(tool_ref):
            raw = raw.rsplit(".", 1)[-1]
        return raw

    def _bind_turn(self, turn, tools: list | None, action: object | None = None):
        return _TurnBinder().bind(self, turn, tools, action)

    def _align_tools(self, tools: list | None, generate_tools: list | None) -> list:
        return _TurnBinder().align(self, tools, generate_tools)

    def _later_step(self, later_action: object) -> str:
        if later_action is None or str(later_action).strip() == "":
            return "Guidance: (none)"
        if self._is_toolset_ref(later_action):
            return f"Guidance: {self._action_name(later_action)}"
        if isinstance(later_action, str):
            return f"Guidance: {later_action}"
        return f"Guidance: {self._action_name(later_action)}"

    def _turn_prompt(self, turn, later_actions: list | None = None) -> str:
        return _TurnPrompt().render(self, turn, later_actions)

    def _doer_ask_judge(self, judge_resume: str, workspace: str) -> str:
        resume = (judge_resume or "").strip()
        if not resume:
            return ""
        return (
            "After you finish the Turn, you contact the judge. "
            "Do not ask the parent to run the judge. The parent is not in this loop. "
            "Open the judge in its own console window so the operator can watch. "
            "Never use print mode. "
            "On Windows: Start-Process cursor-agent -ArgumentList "
            f"'--force','--trust','--resume','{resume}','--workspace','{workspace}',"
            "'Read .context/cli-agent-judge.txt and follow it exactly.' "
            f"-WorkingDirectory '{workspace}' -WindowStyle Normal. "
            "Wait for PASS or FAIL from the judge transcript or finish_turn, "
            "not by reading this console. "
            "On PASS this job is done. Pop the first object from "
            ".context/sessions/<session>/cli-agent-job-queue.json "
            "(the job you just finished). If another job remains, that is "
            "your next Turn — follow its prompt, tools, and actions, then "
            "contact the judge again after that Turn. Do not wait for the "
            "parent. If the queue is empty, stop. "
            "On FAIL, fix, finish the Turn, and send again "
            "(attempt n of 3). After three FAILs, stop and wait for the parent."
        )

    def _create_chat(self, workspace: str, *, timeout_seconds: int | None = None) -> str:
        return _ChatMint().mint()

    def _detect(self) -> IdeCli:
        if type(self) is not IdeCli:
            return self
        if CursorCli()._launcher():
            return self._as_vendor(CursorCli)
        if VscodeCli()._launcher():
            return self._as_vendor(VscodeCli)
        raise RuntimeError(
            "no IDE agent CLI on PATH (cursor-agent, agent, or code)"
        )

    def append_log(self, workspace: str, argv: list[str], role: str, session: str = "") -> None:
        _CliSpawner().append_log(workspace, argv, role, session=session or self._session)

    def launcher(self) -> str | None:
        """Public launcher path (agent_bdd / session mint)."""
        return self._launcher()

    def create_chat(
        self, workspace: str, *, timeout_seconds: int | None = None
    ) -> str:
        """Public create-chat (agent_bdd AgentSession)."""
        return self._create_chat(workspace, timeout_seconds=timeout_seconds)

    def command(self, prompt: str, workspace: str) -> list[str]:
        """Public argv builder (agent_bdd harness)."""
        return self._command(prompt, workspace)

    def run(
        self,
        prompt: str,
        workspace: str,
        *,
        timeout_seconds: int | None = None,
    ) -> IdeCliResult:
        """Public prompt run (agent_bdd AgentSession)."""
        return self._launch_cli(prompt, workspace, timeout_seconds=timeout_seconds)

    def _launcher(self) -> str | None:
        return None

    def _command(self, prompt: str, workspace: str) -> list[str]:
        return self._detect()._command(prompt, workspace)

    def _judge_command(self, prompt: str, workspace: str) -> list[str]:
        return self._detect()._judge_command(prompt, workspace)

    def _task_prompt(
        self, tools: list | None = None, actions: list | None = None, context: str = ""
    ) -> str:
        acts = self._listed(actions)
        hanging = self._bind_turn(self._blank_turn(), tools, acts[0] if acts else None)
        text = self._turn_prompt(hanging)
        if context:
            text += f"{context}\n"
        return text

    def _judge_task_prompt(
        self,
        worker_prompt: str = "",
        generate_tools: list | None = None,
        turn=None,
    ) -> str:
        if (worker_prompt or "").strip():
            self._job = worker_prompt.strip()
        if turn is not None:
            return _JudgePrompt().from_turn(self, turn)
        return _JudgePrompt().from_tools(self, generate_tools)

    def _write_task_file(self, task: str, workspace: str, name: str) -> str:
        return _TaskFile().persist(task, workspace, name)

    def _needs_task_file(self, task: str) -> bool:
        if os.name == "nt":
            return True
        if "\n" in task:
            return True
        return len(task) > self._cmdline_safe

    def _launch_prompt(self, task: str, workspace: str, *, name: str) -> str:
        if self._needs_task_file(task):
            return self._launch.format(path=self._write_task_file(task, workspace, name))
        return task

    def _commands(
        self,
        prompt: str,
        workspace: str,
        judge_prompt: str = "",
        *,
        use_judge: bool | None = None,
    ) -> list[list[str]]:
        chosen = self if type(self) is not IdeCli else self._detect()
        worker_prompt = chosen._launch_prompt(
            prompt, workspace, name="cli-agent-task.txt"
        )
        argv = [chosen._command(worker_prompt, workspace)]
        judging = bool(judge_prompt) if use_judge is None else use_judge
        if not judging or not chosen.judge:
            return argv
        judge_text = judge_prompt or chosen._judge_task_prompt(prompt)
        chosen._write_task_file(judge_text, workspace, "cli-agent-judge.txt")
        return argv

    def _spawn(
        self,
        argv: list[str],
        workspace: str,
        *,
        timeout_seconds: int | None = None,
        existing_pid: int = 0,
    ) -> IdeCliResult:
        started = time.perf_counter()
        spawner = _CliSpawner()
        role = spawner.spawn_role(argv)
        existing_pid = int(existing_pid or 0)
        if existing_pid > 0 and _pid_alive(existing_pid):
            result = spawner.start(
                argv, workspace, existing_pid=existing_pid, _skip_log=True
            )
            return spawner.with_elapsed(result, started)
        spawner.append_log(workspace, argv, role, session=self._session)
        result = spawner.start(argv, workspace, existing_pid=0, _skip_log=True)
        return spawner.with_elapsed(result, started)

    def _launch_cli(
        self,
        prompt: str,
        workspace: str,
        *,
        timeout_seconds: int | None = None,
    ) -> IdeCliResult:
        chosen = self if type(self) is not IdeCli else self._detect()
        return chosen._spawn(
            chosen._command(prompt, workspace),
            workspace,
            timeout_seconds=timeout_seconds,
        )

    def _launch_all(
        self,
        prompt: str,
        workspace: str,
        judge_prompt: str = "",
        *,
        timeout_seconds: int | None = None,
        doer_pid: int = 0,
        judge_pid: int = 0,
        use_judge: bool | None = None,
    ) -> list[IdeCliResult]:
        chosen = self if type(self) is not IdeCli else self._detect()
        spawned = []
        pids = (doer_pid, judge_pid)
        for index, argv in enumerate(
            chosen._commands(prompt, workspace, judge_prompt, use_judge=use_judge)
        ):
            existing = pids[index] if index < len(pids) else 0
            spawned.append(
                chosen._spawn(
                    argv,
                    workspace,
                    timeout_seconds=timeout_seconds,
                    existing_pid=existing,
                )
            )
        return spawned

    def _require_launcher(self, missing: str) -> str:
        exe = self._launcher()
        if exe is None:
            raise RuntimeError(missing)
        return exe


class CursorCli(IdeCli):
    """cursor-agent / agent — builds argv and spawns the process."""

    def _launcher(self) -> str | None:
        return shutil.which("cursor-agent") or shutil.which("agent")

    def _command(self, prompt: str, workspace: str) -> list[str]:
        return _SessionArgv()._cursor_args(
            self, prompt, workspace, resume=self.resume
        )

    def _judge_command(self, prompt: str, workspace: str) -> list[str]:
        return _SessionArgv()._cursor_args(
            self, prompt, workspace, resume=self.judge_resume
        )

    def _create_chat(self, workspace: str, *, timeout_seconds: int | None = None) -> str:
        seconds = timeout_seconds
        if seconds is None:
            seconds = type(self).create_chat_timeout_seconds
        exe = self._require_launcher("cursor-agent not found on PATH")
        completed = subprocess.run(
            [exe, "create-chat", "--workspace", str(workspace)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=seconds,
            check=False,
        )
        return _ChatMint().from_stdout(
            completed.stdout, completed.stderr, completed.returncode
        )


class VscodeCli(IdeCli):
    """VS Code `code chat` — builds argv and spawns the process."""

    def _launcher(self) -> str | None:
        return shutil.which("code") or shutil.which("code-insiders")

    def _command(self, prompt: str, workspace: str) -> list[str]:
        return _SessionArgv()._vscode_args(self, prompt, workspace)

    def _judge_command(self, prompt: str, workspace: str) -> list[str]:
        return _SessionArgv()._vscode_args(self, prompt, workspace)



@agentic_toolset
@dataclass
class CliJobTemplate:
    """A named, reusable list of jobs. Shape is identical to a job queue entry."""

    name: str
    jobs: list = field(default_factory=list)
    description: str = ""


class CliJobTemplateStore:
    """Persist and retrieve job templates.

    Default root is the ``job-templates/`` folder next to this module.
    Pass ``root`` to override with a project-specific path.
    """

    _default_root = Path(__file__).parent / "job-templates"

    def __init__(self, root: str | None = None) -> None:
        self._root = Path(root) if root else self._default_root

    def _path_for(self, name: str) -> Path:
        return self._root / f"{name}.json"

    def add(self, template: CliJobTemplate) -> None:
        """Save a template to disk, creating the directory if needed."""
        self._root.mkdir(parents=True, exist_ok=True)
        payload = {
            "name": template.name,
            "description": template.description,
            "jobs": template.jobs,
        }
        self._path_for(template.name).write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def load(self, name: str) -> CliJobTemplate | None:
        """Return the named template, or None if it does not exist."""
        path = self._path_for(name)
        if not path.is_file():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        return CliJobTemplate(
            name=raw.get("name", name),
            jobs=raw.get("jobs", []),
            description=raw.get("description", ""),
        )

    def list_all(self) -> list[str]:
        """Return the names of every saved template in this store."""
        if not self._root.is_dir():
            return []
        return sorted(p.stem for p in self._root.glob("*.json"))

    def find_matching(self, prompt: str) -> list[CliJobTemplate]:
        """Return templates whose name overlaps with words in *prompt*."""
        words = set(re.sub(r"[^a-z0-9 ]+", " ", prompt.lower()).split())
        results = []
        for name in self.list_all():
            name_words = set(re.sub(r"[^a-z0-9 ]+", " ", name.lower()).split())
            if words & name_words:
                t = self.load(name)
                if t is not None:
                    results.append(t)
        return results


@dataclass
class CliBacklogItem:
    """One unit on a CliAgent backlog: ticket ref or free-text."""

    ref: str | int
    kind: str = "text"
    status: str = "pending"

    @classmethod
    def from_ref(cls, ref: str | int) -> CliBacklogItem:
        raw = str(ref).strip()
        if re.fullmatch(r"#?\d+", raw):
            return cls(ref=int(raw.lstrip("#")), kind="ticket", status="pending")
        return cls(ref=raw, kind="text", status="pending")

    def to_dict(self) -> dict:
        return {"ref": self.ref, "kind": self.kind, "status": self.status}

    @classmethod
    def from_dict(cls, data: dict) -> CliBacklogItem:
        return cls(
            ref=data.get("ref", ""),
            kind=data.get("kind", "text"),
            status=data.get("status", "pending"),
        )


class CliBacklog:
    """Ordered backlog items for one CliAgent session.

    One work session covers the whole backlog. Each item is processed by
    running it through the active job queue or a named job template.
    """

    filename = "cli-agent-backlog.json"

    def __init__(
        self,
        items: list[CliBacklogItem] | None = None,
        template: str | None = None,
    ) -> None:
        self.items = list(items or [])
        self.template = template

    def path_for(self, work) -> Path:
        folder = getattr(work, "folder", None)
        if folder:
            return Path(folder) / self.filename
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return Path(root) / ".context" / "sessions" / name / self.filename

    @classmethod
    def load(cls, work) -> CliBacklog:
        path = cls().path_for(work)
        if not path.is_file():
            return cls()
        raw = json.loads(path.read_text(encoding="utf-8"))
        items = [CliBacklogItem.from_dict(i) for i in raw.get("items", [])]
        return cls(items=items, template=raw.get("template"))

    def save(self, work) -> None:
        path = self.path_for(work)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "template": self.template,
            "items": [i.to_dict() for i in self.items],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def push(self, item: CliBacklogItem) -> None:
        self.items.append(item)

    def peek(self) -> CliBacklogItem | None:
        for item in self.items:
            if item.status == "in_progress":
                return item
        for item in self.items:
            if item.status == "pending":
                return item
        return None

    def advance(self) -> CliBacklogItem | None:
        """Mark the current in_progress item done; start the next pending item."""
        for item in self.items:
            if item.status == "in_progress":
                item.status = "done"
                break
        for item in self.items:
            if item.status == "pending":
                item.status = "in_progress"
                return item
        return None

    def remaining(self) -> list[CliBacklogItem]:
        return [i for i in self.items if i.status != "done"]


class CliAgent(SubAgent):
    """Slash ``/cli-agent`` runs listed context tools and actions through the IDE CLI.

    Same turn rule as SubAgent: listed actions already open the session turn;
    when actions is missing, the worker wraps context-tool work in performTurn.
    The parent launches kind: sub_agent / launch: non_blocking and does not wait.
    This kit also spawns cursor-agent or `code chat` via IdeCli._launch_all.
    Flags live on ide after IdeCli is constructed; every launch_sessions() reuses them.
    """

    def __init__(self, workspace: str = "", session: str = "") -> None:
        self._workspace = (workspace or os.getcwd()).strip()
        self._session = (session or "").strip()
        self._work = None
        self._ide: IdeCli | None = None
        self._judge_job = False
        self._current_job_index = 0
        self._current_launch_tools: list = []
        self._current_launch_actions: list | None = None
        self._current_turn = None
        self._orchestrator_owns_loop = False

    @property
    def ide(self) -> IdeCli:
        if self._ide is None:
            self._ide = IdeCli()._detect()
        self._ide.bind_workspace(self._workspace_root(), self._resolved_session_name())
        if not self._ide._model:
            loaded = self._ide.resolve_session_model()
            if loaded:
                self._ide._model = loaded
        return self._ide

    def _resolved_session_name(self) -> str:
        if self._session:
            return self._session
        work = self.work_session
        if work is not None and getattr(work, "name", ""):
            return str(work.name)
        return self._session_name_from_git()

    @property
    def task_prompt(self) -> str:
        return self.ide.prompt

    @task_prompt.setter
    def task_prompt(self, prompt: str) -> None:
        self.ide._prompt = (prompt or "").strip()

    @property
    def job(self) -> str:
        return self.ide.job

    @job.setter
    def job(self, job: str) -> None:
        self.ide._job = (job or "").strip()

    @property
    def judge(self) -> bool | str | dict:
        return self.ide.judge

    @judge.setter
    def judge(self, judge: bool | str | dict) -> None:
        self.ide._judge = False if judge in (None, "") else judge

    @property
    def source_scope(self) -> str:
        return self.ide.source_scope

    @source_scope.setter
    def source_scope(self, source_scope: str) -> None:
        self.ide._source_scope = source_scope or ""

    @property
    def work_session(self):
        return None if self._work is None else self._work.current_work_session

    def _workspace_root(self) -> str:
        work = self.work_session
        if work is None:
            return str(self._workspace)
        path = getattr(work, "path", None)
        if path:
            return str(path)
        return str(self._workspace)

    def _session_name_from_git(self) -> str:
        from workspace.git_repo import GitRepo, Repo

        git_root = Repo.find_root(self._workspace)
        if git_root is None:
            return ""
        branch = GitRepo(git_root).current_branch
        if isinstance(branch, str) and branch.startswith("session/"):
            return branch[len("session/") :]
        return ""

    def _session_slug_from_folder(self) -> str:
        raw = Path(self._workspace).resolve().name
        slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
        return slug or "work"

    def _ensure_work_session(self):
        from workspace.workspace import Workspace

        space = Workspace(self._workspace)
        space.load()
        name = self._session or self._session_name_from_git()
        if not name and len(space.work_sessions) == 1:
            only = space.work_sessions[0].name
            # Never reuse leftover ``default`` while still on main — that session is
            # for pre-ticket scratch. Ticket work binds after start-ticket on
            # ``session/<ticket>`` (own worktree).
            if only != "default":
                name = only
        if not name:
            # Defer durable bind: do not invent a folder-slug session (or session/
            # branch + worktree) on main before start-ticket. Keep an orchestration
            # handle for job-queue / CLI ids only; ``_session`` stays unbound until
            # rebind_to_worktree after start-ticket.
            return self._pending_work_session(space)
        space.open_work_session(name)
        self._work = space
        self._session = space.current_work_session.name
        return space.current_work_session

    def _pending_work_session(self, space):
        from workspace.workspace import WorkSession

        pending_name = "cli-agent-pending"
        existing = next(
            (s for s in space.work_sessions if s.name == pending_name), None
        )
        if existing is None:
            pending = WorkSession(space, name=pending_name, path=str(space.path))
            pending.folder.mkdir(parents=True, exist_ok=True)
            space.work_sessions.append(pending)
        else:
            pending = existing
            pending.folder.mkdir(parents=True, exist_ok=True)
        space.current_work_session = pending
        self._work = space
        self._session = ""
        return pending

    def rebind_to_worktree(self, path: str, session: str = "") -> str:
        """Retarget CliAgent onto the ticket worktree after start-ticket.

        Sets workspace root to ``path``, opens ``session`` (or the name from the
        ``session/`` git branch), and binds subsequent jobs there. Required for
        CliAgent; SubAgent and no-agent flows must rebind the same way after
        start-ticket so work never stays on parent/main.
        """
        root = str(Path(path).resolve())
        self._workspace = root
        from workspace.workspace import Workspace

        space = Workspace(root)
        space.load()
        name = (session or "").strip() or self._session_name_from_git()
        if not name:
            raise ValueError(
                "rebind_to_worktree requires session= or a session/<ticket> branch"
            )
        space.open_work_session(name)
        self._work = space
        self._session = space.current_work_session.name
        return self._workspace_root()

    def _attach_cli_sessions(self):
        return _WorkAttach().attach(self)

    def _described_turn(self, tools: list, actions: list | None):
        acts = self.ide._listed(actions)
        hanging = self.ide._bind_turn(
            self.ide._blank_turn(), tools, acts[0] if acts else None
        )
        if self.task_prompt:
            hanging.prompt = self.task_prompt
        return hanging, acts[1:]

    def _toolset_refs(self, tools) -> list:
        refs = []
        for tool_ref in self.ide._listed(tools):
            if self.ide._is_toolset_ref(tool_ref):
                refs.append(tool_ref)
        return refs

    def _bring_in_kits(self, tools, actions) -> None:
        refs = self._toolset_refs(tools)
        for host in self.context_tools(refs):
            host
        action_refs = self._toolset_refs(actions)
        if not action_refs:
            return
        for kit in self.context_tools(action_refs):
            kit

    def _first_failure(self, results):
        for spawned in results:
            if spawned.exit_code != 0:
                return spawned
        return None

    def _await_pickup(self, resume: str, before: int, *, pid: int = 0) -> None:
        """Wait for transcript take-up; a live doer pid counts as taken-up."""
        pickup = _Pickup()
        path = pickup.cursor_transcript(self._workspace_root(), resume)
        if pickup.accepted(path, before, seconds=self.ide.pickup_seconds):
            return
        if _pid_alive(pid):
            return
        raise RuntimeError(pickup.not_taken_up)

    def _should_judge(self, tools, actions) -> bool:
        """Judge when this launch lists tools/actions. IdeCli.judge is capability only."""
        return bool(self.ide._listed(tools) or self.ide._listed(actions))

    def _spawn_worker(self, tools, hanging, actions=None):
        judge_prompt = ""
        if self._should_judge(tools, actions):
            judge_prompt = self.ide._judge_task_prompt(
                self.job, generate_tools=tools, turn=hanging
            )
        work = self.work_session
        self.ide._session = work.name if work else ""
        pickup = _Pickup()
        resume = "" if work is None else (work.cli_doer or "")
        before = pickup.user_count(
            pickup.cursor_transcript(self._workspace_root(), resume)
        )
        orchestrating = getattr(self, "_orchestrator_owns_loop", False)
        # Duplicate same-job launches are blocked in launch_next (_head_job_in_flight).
        # Never skip the doer Popen because a prior job's pid is still alive — each
        # new job must resume with that job's prompt or run_backlog stalls on job 2+.
        doer_pid = 0
        judge_pid = 0
        results = self.ide._detect()._launch_all(
            self.job,
            self._workspace_root(),
            judge_prompt,
            use_judge=bool(judge_prompt) and not orchestrating,
            doer_pid=doer_pid,
            judge_pid=judge_pid,
        )
        failed = self._first_failure(results)
        if failed is not None:
            raise RuntimeError(
                failed.stderr.strip() or failed.text.strip() or "IDE CLI exited non-zero"
            )
        self._record_cli_binding(results, tools=tools, actions=actions, turn=hanging)
        doer_pid = 0
        if results:
            doer_pid = int(results[0].pid or 0)
        if work is not None and not doer_pid:
            doer_pid = int(getattr(work, "cli_doer_pid", 0) or 0)
        self._await_pickup(resume, before, pid=doer_pid)
        return results

    def _record_cli_binding(
        self,
        results: list[IdeCliResult],
        *,
        tools=None,
        actions=None,
        turn=None,
    ) -> None:
        work = self.work_session
        if work is None:
            return
        if results:
            work.cli_doer_pid = results[0].pid
        if len(results) > 1:
            work.cli_judge_pid = results[1].pid
        work.save_cli_sessions()
        pickup = _Pickup()
        ws = self._workspace_root()
        log = _CliAgentLog()
        doer_transcript = str(pickup.cursor_transcript(ws, work.cli_doer))
        judge_transcript = str(pickup.cursor_transcript(ws, work.cli_judge))
        job_queue = log._job_queue_path(work)
        if not any(
            r.get("kind") == "header"
            for r in log.read_records(work)
        ):
            log.header(
                work,
                doer=work.cli_doer,
                judge=work.cli_judge,
                doer_pid=work.cli_doer_pid,
                judge_pid=work.cli_judge_pid,
                chat=doer_transcript,
                job_queue=job_queue,
            )
        log.session_start(
            work,
            doer=work.cli_doer,
            judge=work.cli_judge,
            doer_pid=work.cli_doer_pid,
            judge_pid=work.cli_judge_pid,
            doer_transcript=doer_transcript,
            judge_transcript=judge_transcript,
        )
        turn_kit = log._turn_kit(turn, tools=tools, actions=actions)
        spawn_tools = turn_kit.get("tools")
        spawn_actions = turn_kit.get("actions")
        spawn_calls = turn_kit.get("tool_calls")
        job_index = self._current_job_index
        for spawned in results:
            role = _CliSpawner().spawn_role(spawned.argv)
            resume = work.cli_doer if role == "doer" else work.cli_judge
            log.spawn(
                work,
                role=role,
                resume=resume,
                prompt=self.job,
                argv=" ".join(spawned.argv),
                tools=spawn_tools,
                actions=spawn_actions,
                tool_calls=spawn_calls,
                job_index=job_index,
            )
            if role == "judge" and resume:
                log.judge_started(work, job_index=job_index, judge=resume)

    def _session_report(self, work, results) -> str:
        ws = self._workspace_root()
        parts = [spawned.text for spawned in results if spawned.text]
        parts.append("CLI processes (not IDE chats):")
        for spawned in results:
            if spawned.pid:
                parts.append(f"pid: {spawned.pid}")
        if work.cli_doer:
            parts.append(f"[CliAgent doer transcript]({work.cli_doer})")
            parts.append(f"cursor-agent --resume {work.cli_doer}")
        if work.cli_judge:
            parts.append(f"[CliAgent judge transcript]({work.cli_judge})")
            parts.append(f"cursor-agent --resume {work.cli_judge}")
        parts.append(f"workspace: {ws}")
        parts.append(f"session: {work.name}")
        parts.append("taken up: yes")
        parts.append(f"job_queue: {len(self.job_queue)}")
        pickup = _Pickup()
        session_log = _CliAgentLog().path_for(work)
        parts.append("## Monitor with these files (read directly — do not recurse)")
        parts.append(f"session log: {session_log}")
        parts.append(f"job queue: {ws}/.context/sessions/{work.name}/cli-agent-job-queue.json")
        if work.cli_doer:
            parts.append(f"doer transcript: {pickup.cursor_transcript(ws, work.cli_doer)}")
        if work.cli_judge:
            parts.append(f"judge transcript: {pickup.cursor_transcript(ws, work.cli_judge)}")
        return "\n".join(parts)

    @property
    def job_queue(self) -> list:
        work = self._attach_cli_sessions()
        return JobQueue().load(work)

    @job_queue.setter
    def job_queue(self, items: list) -> None:
        work = self._attach_cli_sessions()
        JobQueue().save(work, list(items or []))

    @classmethod
    def cleanup_session(cls, work) -> None:
        """Remove temps this kit wrote on that WorkSession."""
        _CliScratch().wipe(work)

    def cleanup(self) -> None:
        work = self.work_session
        if work is None:
            return
        type(self).cleanup_session(work)

    @agent_tool
    def close_agents(self) -> str:
        """Kill doer/judge CLI processes and clear chat bindings. Does **not** close the work session.

        Use when agent windows/processes have piled up but the work session, queue, and
        backlog should stay. Next ``launch_next`` / ``run_backlog`` will mint fresh CLI chats.
        """
        work = self._ensure_work_session()
        work.load_cli_sessions()
        killed: list[str] = []
        for role, pid in (
            ("doer", int(getattr(work, "cli_doer_pid", 0) or 0)),
            ("judge", int(getattr(work, "cli_judge_pid", 0) or 0)),
        ):
            if _kill_pid(pid):
                killed.append(f"{role}:{pid}")
        killed.extend(_kill_workspace_agent_procs(self._workspace_root()))
        work.close_cli_sessions()
        self._orchestrator_owns_loop = False
        detail = ",".join(killed) if killed else "none"
        return (
            f"agents closed (killed={detail}); "
            f"work session {work.name!r} still open"
        )

    @agent_tool
    def enqueue_jobs(self, jobs: list[dict]) -> str:
        """Add jobs to the queue. Each job is a dict with keys: prompt, tools (optional), actions (optional).

        Replaces the current queue with the provided list. Call before launch_sessions to pre-load work.
        Returns the number of jobs now on the queue.
        """
        work = self._attach_cli_sessions()
        stamped = []
        for i, job in enumerate(list(jobs or [])):
            item = dict(job or {})
            item["index"] = int(item["index"]) if "index" in item else i
            stamped.append(item)
        JobQueue().save(work, stamped)
        _CliAgentLog().jobs_defined(work, stamped)
        return f"job_queue: {len(stamped)}"

    def _head_job_in_flight(self, work, item: dict) -> bool:
        """True when this head job was already started, not finished, and doer pid is live."""
        pid = int(getattr(work, "cli_doer_pid", 0) or 0)
        if not _pid_alive(pid):
            return False
        head_prompt = str(item.get("prompt") or "")
        in_flight = False
        for record in _CliAgentLog().read_records(work):
            kind = record.get("kind")
            prompt = str(record.get("prompt") or "")
            if kind == "job_started" and prompt == head_prompt:
                in_flight = True
            elif kind == "job_finished" and prompt == head_prompt:
                in_flight = False
            elif kind == "job_started" and prompt != head_prompt:
                in_flight = False
        return in_flight

    @agent_tool
    def launch_next(self) -> str:
        """Send the head job from the queue to the doer. Leave it on the queue until the judge PASSes."""
        work = self._attach_cli_sessions()
        item = JobQueue().peek(work)
        if item is None:
            raise RuntimeError(JobQueue.empty)
        # Same in-flight head job + live doer → do not spawn a second doer (#44 / #49).
        if self._head_job_in_flight(work, item):
            pid = int(getattr(work, "cli_doer_pid", 0) or 0)
            return (
                f"pid: {pid}\n"
                "doer already taken up for this head job — not spawning again\n"
                f"job_queue: {len(JobQueue().load(work))}"
            )
        if item.get("prompt"):
            self.task_prompt = str(item["prompt"])
        all_jobs = JobQueue().load(work)
        # Prefer stable index stamped at enqueue (survives pop / queue shrink).
        if "index" in item:
            index = int(item["index"])
        else:
            index = all_jobs.index(item) if item in all_jobs else 0
        self._current_job_index = index
        kit = _CliAgentLog._job_kit(item)
        _CliAgentLog().job_started(
            work,
            index=index,
            prompt=str(item.get("prompt") or ""),
            tools=kit.get("tools"),
            actions=kit.get("actions"),
            judge=kit.get("judge"),
            human=kit.get("human"),
        )
        if self._job_needs_human(item):
            # Human replaces judge for this job — doer-only launch.
            judge = False
        else:
            judge = item.get("judge")
        return self.launch_sessions(
            item.get("tools") or [],
            item.get("actions") or None,
            judge=judge if judge is not None else None,
        )

    @agent_tool
    def complete_job(self) -> dict | None:
        """Judge PASS / human looks_good: drop the finished head job. Call launch_next next if more jobs remain."""
        work = self._attach_cli_sessions()
        item = JobQueue().peek(work)
        result = JobQueue().pop(work)
        kit = _CliAgentLog._job_kit(item)
        index = self._current_job_index
        _CliAgentLog().job_finished(
            work,
            index=index,
            prompt=str((item or {}).get("prompt") or ""),
            tools=kit.get("tools"),
            actions=kit.get("actions"),
            judge=kit.get("judge"),
            human=kit.get("human"),
        )
        return result

    def _job_needs_human(self, item: dict | None) -> bool:
        if not item:
            return False
        return bool(item.get("human") or item.get("human_check"))

    def _job_needs_judge(self, item: dict | None) -> bool:
        if not item:
            return False
        if self._job_needs_human(item):
            # Human check replaces judge for this job.
            return False
        if "judge" in item:
            return bool(item.get("judge"))
        tools = item.get("tools") or []
        actions = item.get("actions") or []
        return bool(tools or actions)

    @staticmethod
    def _normalize_human_result(raw: str) -> str:
        text = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
        if text in ("looks_good", "looksgood", "good", "ok", "pass"):
            return "looks_good"
        if text in (
            "needs_fixing",
            "needsfixing",
            "needs_fix",
            "fix",
            "fail",
            "redo",
        ):
            return "needs_fixing"
        raise ValueError(
            f"human check result must be looks_good or needs_fixing, got {raw!r}"
        )

    def _human_check_response_path(self, work, job_index: int) -> Path:
        folder = getattr(work, "folder", None)
        if folder:
            return Path(folder) / f"human-check-{int(job_index)}.json"
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return Path(root) / ".context" / "sessions" / name / f"human-check-{int(job_index)}.json"

    def _apply_human_feedback_to_head(self, work, feedback: str) -> None:
        jobs = JobQueue().load(work)
        if not jobs:
            return
        head = dict(jobs[0])
        original = head.get("_human_original_prompt")
        if original is None:
            original = str(head.get("prompt") or "")
            head["_human_original_prompt"] = original
        fb = (feedback or "").strip() or "(no details)"
        head["prompt"] = (
            f"{original}\n\n"
            f"HUMAN FEEDBACK (needs fixing):\n{fb}\n"
            "Address the feedback, then finish the Turn.\n"
        )
        jobs[0] = head
        JobQueue().save(work, jobs)

    def _wait_for_human_check(self, work, *, job_index: int, stall_s: float) -> dict:
        """Block until human-check-{index}.json appears (parent/operator resolution)."""
        path = self._human_check_response_path(work, job_index)
        if path.is_file():
            path.unlink()
        deadline = time.time() + max(0.0, stall_s)
        while time.time() < deadline:
            if path.is_file():
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    time.sleep(0.25)
                    continue
                if not isinstance(raw, dict):
                    raw = {"result": str(raw)}
                result = self._normalize_human_result(str(raw.get("result") or ""))
                feedback = str(raw.get("feedback") or "")
                try:
                    path.unlink()
                except OSError:
                    pass
                return {"result": result, "feedback": feedback}
            time.sleep(0.25)
        _CliAgentLog().error(
            work,
            detail=f"stall: no human check within {stall_s}s",
            job_index=job_index,
        )
        raise RuntimeError(f"stall: no human check within {stall_s}s")

    def _human_check_notify_text(self, work, item: dict, *, job_index: int) -> tuple[str, str]:
        session = getattr(work, "name", "") or "session"
        prompt_head = str(item.get("prompt") or "").strip().splitlines()
        head = (prompt_head[0] if prompt_head else "(no prompt)")[:160]
        title = f"CliAgent human check — job {job_index}"
        body = (
            f"Session {session} needs your review (looks_good / needs_fixing).\n"
            f"Job: {head}\n"
            f"Resolve: resolve_human_check(...) or {session}/human-check-{job_index}.json"
        )
        return title, body

    def _notify_human_check(
        self,
        work,
        item: dict,
        *,
        job_index: int,
        notify_human=None,
    ) -> None:
        """Fire a human-visible notification, then record human_notified in the session log.

        Default channel is the IDE/OS notifier (same bridge as manifest gate). Tests inject
        ``notify_human`` to spy without requiring the Cursor extension.
        """
        title, body = self._human_check_notify_text(work, item, job_index=job_index)
        channel = "os"
        if notify_human is not None:
            channel = str(notify_human(work, item, title, body) or "test")
        else:
            try:
                from utilities.manifest_hook.manifest_gate_conf import (
                    show_os_notification,
                )

                show_os_notification(title, body)
            except Exception:
                # Never block the backlog loop on notifier failure — log still records intent.
                channel = "os_failed"
        _CliAgentLog().human_notified(
            work,
            job_index=job_index,
            title=title,
            body=body,
            channel=channel,
        )

    @agent_tool
    def resolve_human_check(self, result: str, feedback: str = "") -> str:
        """Record human review for a job waiting on ``human`` / ``human_check``.

        ``result``: ``looks_good`` or ``needs_fixing``.
        ``feedback``: included when redoing the same job after needs_fixing.
        Writes ``human-check-{index}.json`` in the session folder for ``run_backlog``.
        """
        work = self._attach_cli_sessions()
        item = JobQueue().peek(work)
        if item is None:
            raise RuntimeError(JobQueue.empty)
        if "index" in item:
            index = int(item["index"])
        else:
            index = self._current_job_index
        normalized = self._normalize_human_result(result)
        if normalized == "needs_fixing" and not str(feedback or "").strip():
            # Allow empty feedback but keep a clear marker for the redo prompt.
            feedback = ""
        path = self._human_check_response_path(work, index)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"result": normalized, "feedback": feedback or ""}),
            encoding="utf-8",
        )
        return f"human check recorded: {normalized} (job_index={index})"

    def _write_judge_prompt(self, work, item: dict) -> Path:
        ws = Path(self._workspace_root())
        prompt = str(item.get("prompt") or "")
        criteria = str(item.get("judge_criteria") or "")
        body = (
            "Validate the doer's Turn for this job.\n\n"
            f"## Job\n{prompt}\n\n"
            f"## Criteria\n{criteria or 'PASS only when the job prompt was satisfied.'}\n\n"
            "Reply PASS or FAIL and finish this Turn.\n"
        )
        path = ws / ".context" / "cli-agent-judge.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    @agent_tool
    def run_backlog(
        self,
        *,
        stall_s: float = 600.0,
        max_fail: int = 3,
        wait_doer=None,
        wait_verdict=None,
        wait_human=None,
        notify_human=None,
        spawn_judge=None,
        launch_job=None,
    ) -> str:
        """Own the backlog/job control loop in-process (human check / judge / auto-advance).

        Parent launches ``run_backlog`` once and monitors the session log. The doer
        only executes the job Turn — it must not contact the judge or call
        ``complete_job`` / ``launch_next``. Hooks (``wait_doer``, ``wait_verdict``,
        ``wait_human``, ``notify_human``, ``spawn_judge``, ``launch_job``) are for
        tests and alternate transports. Jobs with ``human: true`` notify the human
        (IDE/OS by default), pause for resolution, instead of spawning a judge.
        """
        work = self._attach_cli_sessions()
        log = _CliAgentLog()
        log.orchestrator_started(work)
        self._orchestrator_owns_loop = True
        finished = 0
        try:
            while True:
                item = JobQueue().peek(work)
                if item is None:
                    # Prefer advancing backlog when the job queue is empty.
                    nxt = None
                    if hasattr(self, "next_backlog_item"):
                        try:
                            nxt = self.next_backlog_item()
                        except Exception:
                            nxt = None
                    if not nxt:
                        log.orchestrator_stopped(work, reason="queue_empty")
                        break
                    continue

                all_jobs = JobQueue().load(work)
                if "index" in item:
                    index = int(item["index"])
                else:
                    index = all_jobs.index(item) if item in all_jobs else 0
                self._current_job_index = index
                fails = 0
                while True:
                    if launch_job is not None:
                        launch_job(self, item)
                    else:
                        self.launch_next()
                    if wait_doer is not None:
                        wait_doer(work, item)
                    else:
                        self._wait_until_doer_turn_ends(work, stall_s=stall_s)
                    log.doer_finished(work, job_index=index)

                    if self._job_needs_human(item):
                        log.human_check_needed(work, job_index=index)
                        # Notify before waiting — human must be able to hear the gate.
                        self._notify_human_check(
                            work,
                            item,
                            job_index=index,
                            notify_human=notify_human,
                        )
                        if wait_human is not None:
                            resolution = wait_human(work, item) or {}
                        else:
                            resolution = self._wait_for_human_check(
                                work, job_index=index, stall_s=stall_s
                            )
                        if isinstance(resolution, str):
                            resolution = {"result": resolution, "feedback": ""}
                        result = self._normalize_human_result(
                            str(resolution.get("result") or "")
                        )
                        feedback = str(resolution.get("feedback") or "")
                        log.human_check_resolved(
                            work,
                            job_index=index,
                            result=result,
                            feedback=feedback,
                        )
                        if result == "looks_good":
                            self.complete_job()
                            finished += 1
                            break
                        self._apply_human_feedback_to_head(work, feedback)
                        log.recovery(
                            work,
                            job_index=index,
                            detail="human needs_fixing",
                        )
                        item = JobQueue().peek(work) or item
                        continue

                    if not self._job_needs_judge(item):
                        self.complete_job()
                        finished += 1
                        break

                    # run_backlog attaches before _judge_job is known; mint judge now.
                    self._judge_job = True
                    work = self._attach_cli_sessions()
                    work.load_cli_sessions()
                    self._write_judge_prompt(work, item)
                    judge_id = getattr(work, "cli_judge", "") or ""
                    log.judge_started(work, job_index=index, judge=judge_id)
                    if spawn_judge is not None:
                        spawn_judge(work, item)
                    else:
                        self._spawn_judge_for_job(work, item)
                    if wait_verdict is not None:
                        result = str(wait_verdict(work, item) or "").strip().upper()
                    else:
                        result = self._wait_for_verdict(work, stall_s=stall_s)
                    log.verdict(work, result=result, job_index=index)
                    if result == "PASS":
                        self.complete_job()
                        finished += 1
                        break
                    fails += 1
                    log.recovery(
                        work,
                        job_index=index,
                        detail=f"judge FAIL {fails}/{max_fail}",
                    )
                    if fails >= max_fail:
                        log.error(
                            work,
                            detail=f"judge FAIL x{max_fail}",
                            job_index=index,
                        )
                        log.orchestrator_stopped(work, reason="judge_fail_limit")
                        return f"run_backlog stopped: FAIL x{max_fail}"
            return f"run_backlog done: {finished}"
        finally:
            self._orchestrator_owns_loop = False

    def _wait_until_doer_turn_ends(self, work, *, stall_s: float) -> None:
        """Poll doer transcript until turn ends or stall — override via wait_doer hook."""
        pickup = _Pickup()
        path = pickup.cursor_transcript(self._workspace_root(), work.cli_doer)
        before = _TranscriptWatch().line_count(path)
        _TranscriptWatch().wait_for_growth(path, before, stall_s=stall_s)

    def _spawn_judge_for_job(self, work, item: dict) -> None:
        """Spawn/resume judge CLI for the current job — override via spawn_judge hook."""
        ws = self._workspace_root()
        judge_resume = (work.cli_judge or "").strip()
        if not judge_resume:
            raise RuntimeError("no judge resume — bind CLI sessions first")
        # Never name=cli-agent-judge.txt: on Windows _needs_task_file is always True,
        # so _launch_prompt would overwrite real criteria with this stub.
        launch = self.ide._launch_prompt(
            "Read .context/cli-agent-judge.txt and follow it exactly.",
            ws,
            name="cli-agent-judge-launch.txt",
        )
        vendor = self.ide._detect()
        vendor._session = work.name
        vendor._judge_resume = judge_resume
        argv = vendor._judge_command(launch, ws)
        result = vendor._spawn(
            argv, ws, existing_pid=getattr(work, "cli_judge_pid", 0) or 0
        )
        if result.exit_code != 0:
            raise RuntimeError(
                result.stderr.strip() or result.text.strip() or "judge spawn failed"
            )
        work.cli_judge_pid = result.pid
        work.save_cli_sessions()

    def _wait_for_verdict(self, work, *, stall_s: float) -> str:
        """Read PASS/FAIL from judge transcript — override via wait_verdict hook."""
        pickup = _Pickup()
        watch = _TranscriptWatch()
        path = pickup.cursor_transcript(self._workspace_root(), work.cli_judge)
        before = watch.line_count(path)
        deadline = time.time() + max(0.0, stall_s)
        while time.time() < deadline:
            verdict = watch.read_verdict(path)
            if verdict in ("PASS", "FAIL"):
                return verdict
            if watch.line_count(path) > before:
                verdict = watch.read_verdict(path)
                if verdict in ("PASS", "FAIL"):
                    return verdict
            time.sleep(0.5)
        _CliAgentLog().error(
            self.work_session,
            detail=f"stall: no judge verdict within {stall_s}s",
            job_index=self._current_job_index,
        )
        raise RuntimeError(f"stall: no judge verdict within {stall_s}s")

    @prompt(name="kick-cli-agent")
    @agent_tool
    def kick(self) -> str:
        """Nudge a stalled doer to advance to the next job.

        ## When to use

        Call when the doer has clearly finished its current job (notes written, ticket updated,
        etc.) but the queue has not advanced and no new console opened.

        ## What kick does

        Sends the active doer a short prompt via the CLI asking it to call
        ``complete_job()`` then ``launch_next()`` if the job is done, or to do nothing
        if it is still waiting for the judge.
        """
        work = self._attach_cli_sessions()
        resume = work.cli_doer
        if not resume:
            raise RuntimeError("no active doer resume — run launch_next first")
        workspace = str(self._workspace_root())
        exe = shutil.which("cursor-agent") or shutil.which("agent")
        if not exe:
            raise RuntimeError("cursor-agent not found on PATH")
        msg = (
            "Check the current job status. "
            "If your current job is complete, call complete_job() then launch_next() "
            "to advance to the next step. "
            "If you are still waiting for the judge, do nothing."
        )
        subprocess.run(
            [exe, "--resume", resume, "--workspace", workspace, "--print", msg],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return f"kicked doer {resume}"

    @agent_tool
    def record_verdict(self, result: str, notes: str = "") -> str:
        """Record a judge verdict (PASS or FAIL) to the session log. Call this after validating a Turn."""
        work = self._attach_cli_sessions()
        _CliAgentLog().verdict(
            work,
            result=result.strip().upper(),
            notes=notes,
            job_index=self._current_job_index,
        )
        return result.strip().upper()

    def _template_store(self, path: str | None = None) -> CliJobTemplateStore:
        return CliJobTemplateStore(root=path or None)

    @prompt(name="cli-agent-template")
    @agent_tool
    def add_template(self, name: str, jobs: list[dict], description: str = "", path: str | None = None) -> str:
        """Create, list, and apply reusable job templates for /cli-agent.

        A template is a named list of jobs — same shape as a job queue entry:
        ``prompt``, ``tools`` (optional), ``actions`` (optional), ``judge`` (optional).
        Templates live in ``job-templates/`` by default; pass ``path`` for a project-specific location.

        ## Create a template

        Call this tool with ``name``, ``jobs``, and an optional ``description``.

        ## List templates

        Call `list_templates()` to see all saved names. Pass ``path`` for a project folder.

        ## Apply a template

        Call `use_template(name)` to enqueue its jobs on the active session, then run `/cli-agent`.
        Pass ``overrides`` (dict) to merge changes into every job first — e.g. swap a prompt or enable a judge.

        ## Match to a request

        If the user's request sounds like an existing template, call `list_templates()` and offer
        the closest match via AskQuestion before building a queue from scratch.
        """
        template = CliJobTemplate(name=name, jobs=list(jobs or []), description=description or "")
        self._template_store(path).add(template)
        return f"saved template '{name}' with {len(template.jobs)} job(s)"

    @agent_tool
    def list_templates(self, path: str | None = None) -> list[str]:
        """Return the names of all saved job templates."""
        return self._template_store(path).list_all()

    @agent_tool
    def use_template(self, name: str, overrides: dict | None = None, path: str | None = None) -> str:
        """Load a named template and enqueue its jobs. Pass ``overrides`` to merge fields into every job.

        Raises RuntimeError when the template is not found.
        """
        store = self._template_store(path)
        template = store.load(name)
        if template is None:
            raise RuntimeError(f"template '{name}' not found in {store._root}")
        jobs = list(template.jobs)
        if overrides:
            jobs = [{**job, **overrides} for job in jobs]
        return self.enqueue_jobs(jobs)

    @agent_tool
    def set_backlog(
        self,
        items: list[str | int],
        template: str | None = None,
        order: list[int] | None = None,
        path: str | None = None,
    ) -> str:
        """Assign a backlog of items to this CliAgent session.

        One work session covers the whole backlog — do not open a new session per item.
        Each item is a ticket ref (``12``, ``#27``) or free-text describing work.
        Free-text items may create a ticket when no match exists (e.g. via the defect-fix template).

        ``template`` is the job template to run for each item (e.g. ``defect-fix``).
        ``order`` optionally reorders by zero-based indexes into ``items``.
        Returns a confirmation with item count and template name.
        """
        work = self._attach_cli_sessions()
        refs = list(items or [])
        if order:
            refs = [refs[i] for i in order if 0 <= i < len(refs)]
        backlog = CliBacklog(
            items=[CliBacklogItem.from_ref(r) for r in refs],
            template=template,
        )
        backlog.save(work)
        label = f" template '{template}'" if template else ""
        return f"backlog: {len(backlog.items)} item(s){label}"

    @agent_tool
    def triage_backlog(
        self,
        find_existing=None,
        capture_backlog=None,
        theme: str = "cli-agent",
    ) -> str:
        """Scan the whole backlog up front: map free-text to existing #N or create tickets.

        Resolves each text item via ``find_existing(text)`` → issue number, or
        ``capture_backlog(...)`` when no match. Stamps ``theme`` (default
        ``cli-agent``) on create. Call before defect-fix jobs so the board shows
        the full backlog under theme:cli-agent. Never create a duplicate when an
        existing ticket already covers the text.
        """
        work = self._attach_cli_sessions()
        backlog = CliBacklog.load(work)
        theme_slug = (theme or "cli-agent").replace("theme:", "").strip() or "cli-agent"
        mapped = 0
        created = 0
        for item in backlog.items:
            if item.kind == "ticket":
                continue
            text = str(item.ref)
            existing = None
            if find_existing is not None:
                existing = find_existing(text)
            if existing is not None:
                item.ref = int(existing)
                item.kind = "ticket"
                mapped += 1
                continue
            if capture_backlog is not None:
                result = capture_backlog(
                    focus=text,
                    theme=theme_slug,
                    body=text,
                )
                number = result.get("number") if isinstance(result, dict) else result
                item.ref = int(number)
                item.kind = "ticket"
                created += 1
        backlog.save(work)
        return (
            f"triaged backlog: {mapped} mapped, {created} created, "
            f"theme={theme_slug}"
        )

    def _finish_backlog_ticket(self, ticket_ref: str | int) -> None:
        """Call Workflow.finish for a completed ticket backlog item."""
        from workflow.workflow import Workflow

        try:
            Workflow().finish(
                ticket=str(ticket_ref),
                workspace=self._workspace,
                outcome=f"backlog item #{ticket_ref} defect-fix complete",
            )
        except Exception:
            # Unit tests / missing open WorkSession: still attempted finish.
            pass

    @agent_tool
    def next_backlog_item(self, path: str | None = None) -> str | None:
        """Advance to the next backlog item and load its jobs onto the queue.

        When leaving a ticket item, calls finish-ticket (Workflow.finish) before
        starting the next item — merge/Done/close must happen before
        ``next_backlog_item`` advances. Marks the current in_progress item done,
        starts the next pending item, and — when a template is set — enqueues
        that template's jobs with the item ref injected into every job prompt.
        Returns None when the backlog is exhausted. Does not open a new work session.
        """
        work = self._attach_cli_sessions()
        backlog = CliBacklog.load(work)
        previous = None
        for candidate in backlog.items:
            if candidate.status == "in_progress":
                previous = candidate
                break
        item = backlog.advance()
        if (
            previous is not None
            and previous.kind == "ticket"
            and previous.status == "done"
        ):
            self._finish_backlog_ticket(previous.ref)
        if item is None:
            # First call: nothing in_progress yet — start the first pending.
            item = backlog.peek()
            if item is None:
                backlog.save(work)
                return None
            if item.status == "pending":
                item.status = "in_progress"
            else:
                backlog.save(work)
                return None
        backlog.save(work)
        ref_label = f"#{item.ref}" if item.kind == "ticket" else str(item.ref)
        if backlog.template:
            store = self._template_store(path)
            template = store.load(backlog.template)
            if template is None:
                raise RuntimeError(
                    f"backlog template '{backlog.template}' not found in {store._root}"
                )
            prefix = f"Backlog item: {ref_label} ({item.kind}).\n\n"
            jobs = []
            for job in template.jobs:
                job = dict(job)
                job["prompt"] = prefix + str(job.get("prompt") or "")
                jobs.append(job)
            self.enqueue_jobs(jobs)
            return f"backlog item {ref_label}: loaded template '{backlog.template}' ({len(jobs)} job(s))"
        return f"backlog item {ref_label}: ready (no template — enqueue jobs manually)"

    @prompt(name="cli-agent")
    @sub_agent
    @agent_tool
    def launch_sessions(self, tools: list[object], actions: list[object] | None = None, prompt: str | None = None, judge: bool | str | dict | None = None) -> str:
        """Run listed tools/actions via the IDE CLI, or prefer ``run_backlog`` for queue work.

        CliAgent owns session/workspace setup and (via ``run_backlog``) the doer→human/judge→advance
        loop. Parent contract is minimal for judged jobs: launch once, read the session log, unblock only after
        CliAgent recovery stops. For jobs with ``human: true``, the parent IS the check — resolve
        ``human_check_needed`` via ``resolve_human_check``. Model, mode, and agent_mode are fixed on this ide instance.

        ## Preferred Steps (orchestrated)

        1. **Enqueue** jobs / backlog (`enqueue_jobs`, `set_backlog`, templates).
        2. **Launch ``run_backlog`` once.** CliAgent code spawns the doer, waits for Turn end,
           then either pauses for human check, or writes the judge prompt / reads PASS/FAIL, then calls
           ``complete_job`` / ``launch_next`` internally. Do not ask the doer to contact the
           judge or advance the queue.
        3. **Monitor the session log** (exact paths in the launch report — read, do not recurse).
           Key files: session jsonl, job queue, doer/judge transcripts. CliAgent also fires an
           IDE/OS notification on ``human_check_needed`` (logged as ``human_notified``).
           Notify / act on ``orchestrator_stopped``, ``error``, ``human_check_needed``, or hard stall.
        4. **On ``human_check_needed`` / ``human_notified``:** call ``resolve_human_check(result='looks_good')`` or
           ``resolve_human_check(result='needs_fixing', feedback='...')`` (session file
           ``human-check-{index}.json`` is also accepted). Needs-fixing redoes the same job with feedback.
        5. **Unblock only on hard failure** (e.g. FAIL×3 after orchestrator stops). Revise the
           job prompt, then one continue resume — do not stack prompts or drive with -p.

        ## Legacy Steps (single launch_sessions without run_backlog)

        1. **Launch.** Pass workspace (and session when known). If NOT TAKEN UP, stop immediately.
        2. **Monitor** doer/judge logs and job queue; report back to the user.
        3. **Unblock on three judge FAILs** if the doer stopped waiting.

        ## Job templates

        Before building the job queue from scratch, check for a matching template:
        - Call `list_templates()` and compare names against the user's request.
        - If one matches, offer it via AskQuestion. If the user confirms, call `use_template(name)` to enqueue its jobs automatically.
        - Skip this if the user described something clearly not matching any template.
        - Call `use_template(name, overrides)` to merge fields (e.g. swap the prompt or toggle judge) into the template jobs before enqueueing.

        ## Backlog

        A backlog is an ordered list of items (ticket refs like ``#12`` / ``27``, or free-text) assigned to this session.
        One work session covers the whole backlog — never open a new session per item.
        - **Up-front triage:** After `set_backlog`, call `triage_backlog` to scan the **entire backlog** before defect-fix jobs. Map each free-text item to an existing `#N` when one covers it, or `capture_backlog` for true new text — never duplicate tickets. Register all tickets on the project board with **theme:cli-agent**.
        - Call `set_backlog(items, template)` to assign items and optionally bind a job template (e.g. ``defect-fix``).
        - When the current item's defect-fix jobs are done: call **finish-ticket** (`Workflow.finish`) for that ticket, **then** `next_backlog_item()` to advance. Do not advance without finish-ticket. (`next_backlog_item` also invokes finish-ticket for ticket items when leaving them.)
        - Free-text items that do not match an existing ticket may create one during triage with theme:cli-agent.
        - Order is the order given unless you reorder via the ``order`` argument and record that choice.

        ## Doer prompt (thin when using run_backlog)

        Tell the doer the task and toolset only. Do **not** instruct it to contact the judge,
        call ``complete_job`` / ``launch_next``, or edit the job queue — ``run_backlog`` owns that.

        For a one-off ``launch_sessions`` without orchestrator, you may still include queue tool
        hints (`enqueue_jobs`, `launch_next`, `complete_job`) for doer-driven advance.

        ## Judge

        Under ``run_backlog``, CliAgent code spawns/resumes the judge and records the verdict —
        the parent never launches, prompts, or scores the judge; the doer never contacts it.
        A judge runs when the job lists tools/actions, or when ``judge=`` is set on the launch/job.
        Jobs with ``human: true`` (or ``human_check``) skip the AI judge: parent resolves looks_good /
        needs_fixing instead.
        """
        if prompt:
            self.task_prompt = prompt
        if judge is False:
            self.judge = False
            self._judge_job = False
        elif judge is not None:
            self.judge = judge
            # Explicit judge= on launch forces a judge; IdeCli.judge alone does not.
            self._judge_job = True if judge else self._should_judge(tools, actions)
        else:
            self._judge_job = self._should_judge(tools, actions)
        self._bring_in_kits(tools, actions)
        work = self._attach_cli_sessions()
        hanging, later = self._described_turn(tools, actions)
        self._current_launch_tools = list(self.ide._listed(tools))
        self._current_launch_actions = self.ide._listed(actions)
        self._current_turn = hanging
        self.job = self.ide._turn_prompt(hanging, later)
        # When run_backlog owns the loop, doer must NOT contact the judge.
        if (
            self._judge_job
            and work.cli_judge
            and not getattr(self, "_orchestrator_owns_loop", False)
        ):
            self.job += "\n" + self.ide._doer_ask_judge(
                work.cli_judge, self._workspace_root()
            )
        results = self._spawn_worker(tools, hanging, actions)
        return self._session_report(work, results)


