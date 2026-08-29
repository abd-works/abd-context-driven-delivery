# @toolset-manifest python -m tools manifest cli_agent.cli_agent:CliAgent
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Slash /cli-agent — SubAgent turn policy, IDE CLI spawn instead of in-chat Task."""
from __future__ import annotations

import json
import os
import re
import shutil
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
        if "--mode" in argv:
            if "ask" in argv:
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


class _CliSession:
    """Append-only structured log for a cli-agent session: cli-agent-session.jsonl."""

    filename = "cli-agent-session.jsonl"

    def path_for(self, work) -> Path:
        folder = getattr(work, "folder", None)
        if folder:
            return Path(folder) / self.filename
        name = getattr(work, "name", "") or "work"
        root = getattr(work, "path", None) or "."
        return Path(root) / ".context" / "sessions" / name / self.filename

    def _append(self, work, record: dict) -> None:
        path = self.path_for(work)
        path.parent.mkdir(parents=True, exist_ok=True)
        record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def session_start(self, work, doer: str, judge: str, doer_pid: int, judge_pid: int, doer_transcript: str, judge_transcript: str) -> None:
        self._append(work, {
            "kind": "session_start",
            "doer": doer,
            "doer_pid": doer_pid,
            "doer_transcript": doer_transcript,
            "judge": judge,
            "judge_pid": judge_pid,
            "judge_transcript": judge_transcript,
        })

    def spawn(self, work, role: str, resume: str, prompt: str, argv: str) -> None:
        self._append(work, {
            "kind": "spawn",
            "role": role,
            "resume": resume,
            "prompt": prompt,
            "argv": argv,
        })

    def jobs_enqueued(self, work, jobs: list) -> None:
        self._append(work, {"kind": "jobs_enqueued", "jobs": jobs})

    def job_start(self, work, prompt: str) -> None:
        self._append(work, {"kind": "job_start", "prompt": prompt})

    def job_complete(self, work, prompt: str) -> None:
        self._append(work, {"kind": "job_complete", "prompt": prompt})

    def verdict(self, work, result: str, notes: str = "") -> None:
        self._append(work, {"kind": "verdict", "result": result, "notes": notes})


class _Pickup:
    """Fail launch if the doer transcript does not take the new job."""

    not_taken_up = (
        "NOT TAKEN UP: the doer did not accept the new job. "
        "Do not wait. A live pid is not proof the Turn started."
    )
    _user_mark = '"role":"user"'

    def cursor_transcript(self, workspace: str, resume: str) -> Path:
        resume = (resume or "").strip()
        raw = str(Path(workspace).resolve())
        slug = raw.replace(":", "").replace("\\", "-").replace("/", "-")
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
        return

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
        if work.agent_open:
            agent._ide = vendor._copy_policy(vendor._resumed(work.cli_doer, work.cli_judge))
            return work
        if not work.cli_doer:
            work.associate_cli("doer", vendor._create_chat(agent._workspace_root()))
        if agent._judge_job and vendor.judge and not work.cli_judge:
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
        spawner.append_log(workspace, argv, role, session=self._session)
        result = spawner.start(argv, workspace, existing_pid=existing_pid, _skip_log=True)
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

    @property
    def ide(self) -> IdeCli:
        if self._ide is None:
            self._ide = IdeCli()._detect()
        return self._ide

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
            name = space.work_sessions[0].name
        if not name:
            name = self._session_slug_from_folder()
        space.open_work_session(name)
        self._work = space
        self._session = space.current_work_session.name
        return space.current_work_session

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

    def _await_pickup(self, resume: str, before: int) -> None:
        pickup = _Pickup()
        path = pickup.cursor_transcript(self._workspace_root(), resume)
        if pickup.accepted(path, before, seconds=self.ide.pickup_seconds):
            return
        raise RuntimeError(pickup.not_taken_up)

    def _should_judge(self, tools, actions) -> bool:
        """Judge when tools/actions are listed, or when judge is explicitly set."""
        return bool(self.ide._listed(tools) or self.ide._listed(actions) or self.ide.judge)

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
        results = self.ide._detect()._launch_all(
            self.job,
            self._workspace_root(),
            judge_prompt,
            use_judge=bool(judge_prompt),
        )
        failed = self._first_failure(results)
        if failed is not None:
            raise RuntimeError(
                failed.stderr.strip() or failed.text.strip() or "IDE CLI exited non-zero"
            )
        self._record_cli_binding(results)
        self._await_pickup(resume, before)
        return results

    def _record_cli_binding(self, results: list[IdeCliResult]) -> None:
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
        _CliSession().session_start(
            work,
            doer=work.cli_doer,
            judge=work.cli_judge,
            doer_pid=work.cli_doer_pid,
            judge_pid=work.cli_judge_pid,
            doer_transcript=str(pickup.cursor_transcript(ws, work.cli_doer)),
            judge_transcript=str(pickup.cursor_transcript(ws, work.cli_judge)),
        )
        for spawned in results:
            role = _CliSpawner().spawn_role(spawned.argv)
            resume = work.cli_doer if role == "doer" else work.cli_judge
            _CliSession().spawn(
                work,
                role=role,
                resume=resume,
                prompt=self.job,
                argv=" ".join(spawned.argv),
            )

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
        session_log = _CliSession().path_for(work)
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
    def enqueue_jobs(self, jobs: list[dict]) -> str:
        """Add jobs to the queue. Each job is a dict with keys: prompt, tools (optional), actions (optional).

        Replaces the current queue with the provided list. Call before launch_sessions to pre-load work.
        Returns the number of jobs now on the queue.
        """
        work = self._attach_cli_sessions()
        JobQueue().save(work, list(jobs or []))
        _CliSession().jobs_enqueued(work, list(jobs or []))
        return f"job_queue: {len(jobs)}"

    @agent_tool
    def launch_next(self) -> str:
        """Send the head job from the queue to the doer. Leave it on the queue until the judge PASSes."""
        work = self._attach_cli_sessions()
        item = JobQueue().peek(work)
        if item is None:
            raise RuntimeError(JobQueue.empty)
        if item.get("prompt"):
            self.task_prompt = str(item["prompt"])
        _CliSession().job_start(work, prompt=str(item.get("prompt") or ""))
        return self.launch_sessions(
            item.get("tools") or [],
            item.get("actions") or None,
        )

    @agent_tool
    def complete_job(self) -> dict | None:
        """Judge PASS: drop the finished head job. Call launch_next next if more jobs remain."""
        work = self._attach_cli_sessions()
        item = JobQueue().peek(work)
        result = JobQueue().pop(work)
        _CliSession().job_complete(work, prompt=str((item or {}).get("prompt") or ""))
        return result

    @agent_tool
    def record_verdict(self, result: str, notes: str = "") -> str:
        """Record a judge verdict (PASS or FAIL) to the session log. Call this after validating a Turn."""
        work = self._attach_cli_sessions()
        _CliSession().verdict(work, result=result.strip().upper(), notes=notes)
        return result.strip().upper()

    @prompt(name="cli-agent")
    @sub_agent
    @agent_tool
    def launch_sessions(self, tools: list[object], actions: list[object] | None = None, prompt: str | None = None, judge: bool | str | dict | None = None) -> str:
        """Run the listed context tools and actions through the IDE CLI as a non-blocking sub-agent.

        CliAgent handles all session and workspace setup internally — do not manage those yourself. The parent's role is to launch, then monitor and unblock. The CLI decides each Turn; model, mode, and agent_mode are fixed on this ide instance and must not be passed per call.

        ## Steps

        1. **Launch.** Pass workspace (and session when known). Do not touch workspace or session utilities — let CliAgent handle all of that. If launch reports NOT TAKEN UP, stop immediately.
        2. **Monitor.** The session report includes exact file paths — read them directly (do not recurse). Key files: `doer log`, `judge log`, `events log`, `job queue`, `doer jsonl`, `judge jsonl`. Watch with a 30s /loop (Cursor) or poll periodically otherwise. Report back to the user.
        3. **Unblock on three judge FAILs.** If the doer has stopped waiting, act — do not just report the status. See details below.

        ## What to always include in the prompt you pass to the doer

        The prompt must tell the doer:
        - The task in plain language.
        - The toolset reference so it can call tools: `toolset: cli_agent.cli_agent:CliAgent` with the same workspace and session.
        - Which queue tools to use and when:
            - `enqueue_jobs(jobs)` — set up all jobs upfront. Each job: `{prompt, tools, actions}`.
            - `launch_next()` — run the head job. Call once per judge PASS to advance the queue.
            - `complete_job()` — pop the finished head before calling launch_next.

        ## Judge

        CliAgent spawns both the doer and the judge automatically — the parent (you) never launches, prompts, or scores the judge. CliAgent generates the judge's instructions internally from the job and tools. A judge is spawned when tools or actions are listed, or when the user explicitly requests one.

        After the doer calls finish_turn, the doer sends the judge file and waits for PASS or FAIL. That exchange is entirely between the doer and judge CLIs. Three FAILs: the doer stops and waits for the parent to intervene (see below).

        ## If the doer stopped after three judge FAILs

        1. Read the judge FAIL — check the transcript and named leftovers in the workspace.
        2. Revise the job prompt and cli-agent-task.txt to target those exact gaps.
        3. Send one continue resume to the doer. Do not stack prompts. Do not drive with -p.
        """
        if prompt:
            self.task_prompt = prompt
        if judge is not None:
            self.judge = judge
        self._bring_in_kits(tools, actions)
        self._judge_job = self._should_judge(tools, actions)
        work = self._attach_cli_sessions()
        hanging, later = self._described_turn(tools, actions)
        self.job = self.ide._turn_prompt(hanging, later)
        if self._judge_job and work.cli_judge:
            self.job += "\n" + self.ide._doer_ask_judge(
                work.cli_judge, self._workspace_root()
            )
        results = self._spawn_worker(tools, hanging, actions)
        return self._session_report(work, results)


