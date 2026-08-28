# @toolset-manifest python -m tools manifest cli_agent.cli_agent:CliAgent
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Slash /cli-agent — SubAgent turn policy, IDE CLI spawn instead of in-chat Task."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from harness.harness_tool import prompt as prompt_name
from primitives.actions.action import agent_instructions, agentic_toolset
from sub_agent.sub_agent import SubAgent, sub_agent

@dataclass
class IdeCliResult:
    """Outcome of one spawned IDE CLI process."""

    exit_code: int
    text: str
    stderr: str
    argv: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    pid: int = 0


class IdeCli:
    """Pick and invoke the installed IDE agent CLI.

    Pass model, mode, agent_mode, and judge once; they are properties afterward
    and every command() / run() reuses them.
    job, source_scope, and prompt are this instance's work, not module state.
    Default launch is an interactive session.
    // always one of CursorCli or VscodeCli after detect
    """

    turn_close = (
        "The CLI opens the hanging workspace.Turn when it runs the action. "
        "Finish that Turn after the action so it commits. "
        "CliAgent does not open the Turn."
    )
    next_turn = (
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
    validate_same_lens = (
        "Validate at the same fidelity and format as that Turn. "
        "Judge the artifacts produced at that fidelity and format. "
        "When format is markdown, validate the markdown; do not look for source code."
    )
    launch = "Read {path} and follow it exactly."
    cmdline_safe = 4096
    parent_checkin = (
        "The parent does not block on the CLI. Every once in a while, check "
        "the CLI (logs, transcript tail, hanging Turn, artifacts) and report "
        "back how it is doing. Do not drive the work with -p."
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
        job: str = "",
        prompt: str = "",
        source_scope: str = "",
    ) -> None:
        self._model = (model or "").strip()
        self._mode = (mode or "").strip().lower()
        self._agent_mode = (agent_mode or "").strip().lower()
        self._judge = False if judge in (None, "") else judge
        self._resume = (resume or "").strip()
        self._judge_resume = (judge_resume or "").strip()
        self._print_mode = bool(print_mode)
        self._job = (job or "").strip()
        self._prompt = (prompt or "").strip()
        self._source_scope = (source_scope or "").strip() or type(self)._default_source_scope

    @property
    def job(self) -> str:
        return self._job

    @job.setter
    def job(self, value: str) -> None:
        self._job = (value or "").strip()

    @property
    def prompt(self) -> str:
        return self._prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self._prompt = (value or "").strip()

    @property
    def source_scope(self) -> str:
        return self._source_scope

    @source_scope.setter
    def source_scope(self, value: str) -> None:
        self._source_scope = value or type(self)._default_source_scope

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

    def _copy_policy(self, other: IdeCli) -> IdeCli:
        other.job = self.job
        other.prompt = self.prompt
        other.source_scope = self.source_scope
        other.validate_same_lens = self.validate_same_lens
        other.turn_close = self.turn_close
        other.next_turn = self.next_turn
        other.launch = self.launch
        other.cmdline_safe = self.cmdline_safe
        other.parent_checkin = self.parent_checkin
        return other

    def _as_vendor(self, vendor: type[IdeCli]) -> IdeCli:
        return self._copy_policy(
            vendor(
                model=self.model,
                mode=self.mode,
                agent_mode=self.agent_mode,
                judge=self.judge,
                resume=self.resume,
                judge_resume=self.judge_resume,
                print_mode=self.print_mode,
                job=self.job,
                prompt=self.prompt,
                source_scope=self.source_scope,
            )
        )

    def tool_lens(self, item: object) -> dict[str, str]:
        """Fidelity and format on one tools item (string or mapping)."""
        if isinstance(item, dict):
            ctx = item.get("context") if isinstance(item.get("context"), dict) else {}
            return {
                "toolset": str(item.get("toolset") or item.get("tool") or "").strip(),
                "fidelity": str(item.get("fidelity") or ctx.get("fidelity") or "").strip(),
                "format": str(item.get("format") or ctx.get("format") or "").strip(),
            }
        return {"toolset": str(item).strip(), "fidelity": "", "format": ""}

    def lens_label(self, item: object) -> str:
        """Prompt token: toolset plus fidelity= and format= when set."""
        lens = self.tool_lens(item)
        parts = [lens["toolset"] or str(item)]
        if lens["fidelity"]:
            parts.append(f"fidelity={lens['fidelity']}")
        if lens["format"]:
            parts.append(f"format={lens['format']}")
        return " ".join(parts)

    def blank_turn(self):
        """Turn fields only — do not open a WorkSession."""
        from workspace.workspace import Turn

        return Turn.hanging()

    def is_toolset_ref(self, item: object) -> bool:
        """True when the item is a module:Class toolset, not prose."""
        if isinstance(item, dict):
            raw = str(item.get("toolset") or item.get("tool") or "")
            return ":" in raw
        return isinstance(item, str) and ":" in item

    def action_name(self, item: object) -> str:
        raw = str(item or "").strip()
        if not raw:
            return ""
        if ":" in raw:
            raw = raw.rsplit(":", 1)[-1]
        if "." in raw and self.is_toolset_ref(item):
            raw = raw.rsplit(".", 1)[-1]
        return raw

    def bind_turn(self, turn, tools: list | None, action: object | None = None):
        """Reuse workspace.Turn: optional action, many tool_keys and toolCalls."""
        from workspace.workspace import ToolCall

        if action is not None and str(action).strip():
            if self.is_toolset_ref(action):
                turn.action = self.action_name(action)
            elif isinstance(action, str):
                turn.prompt = action
                if not turn.action:
                    turn.action = ""
            else:
                turn.action = self.action_name(action)
        act = turn.action or "run"
        prose = [
            item
            for item in (tools or [])
            if isinstance(item, str) and not self.is_toolset_ref(item)
        ]
        if prose:
            turn.prompt = " ".join(prose)
        for item in tools or []:
            if not self.is_toolset_ref(item):
                continue
            lens = self.tool_lens(item)
            ref = lens["toolset"]
            if ref and ref not in turn.tool_keys:
                turn.tool_keys.append(ref)
            already = any(
                call.toolset == ref and call.name == act for call in turn.tool_calls
            )
            if not already:
                turn.tool_calls.append(
                    ToolCall(
                        toolset=ref,
                        name=act,
                        summary=self.lens_label(item),
                        role="run",
                    )
                )
            if lens["fidelity"]:
                turn.fidelity = lens["fidelity"]
            if lens["format"]:
                turn.format = lens["format"]
        return turn

    def align_tools(self, tools: list | None, generate_tools: list | None) -> list:
        """Copy generate fidelity/format onto matching judge tools."""
        by_ref = {
            self.tool_lens(item)["toolset"]: self.tool_lens(item)
            for item in generate_tools or []
        }
        aligned: list = []
        for item in tools or []:
            lens = self.tool_lens(item)
            src = by_ref.get(lens["toolset"])
            if src is None or not (src["fidelity"] or src["format"]):
                aligned.append(item)
                continue
            ctx = {}
            if isinstance(item, dict) and isinstance(item.get("context"), dict):
                ctx.update(item["context"])
            if src["fidelity"] and not ctx.get("fidelity"):
                ctx["fidelity"] = src["fidelity"]
            if src["format"] and not ctx.get("format"):
                ctx["format"] = src["format"]
            if isinstance(item, dict):
                aligned.append({**item, "context": ctx})
            else:
                aligned.append({"toolset": lens["toolset"], "context": ctx})
        return aligned

    def later_step(self, item: object) -> str:
        """One suggested follow-on — not a mandated next Turn."""
        if item is None or str(item).strip() == "":
            return "Guidance: (none)"
        if self.is_toolset_ref(item):
            return f"Guidance: {self.action_name(item)}"
        if isinstance(item, str):
            return f"Guidance: {item}"
        return f"Guidance: {self.action_name(item)}"

    def turn_prompt(self, turn, later_actions: list | None = None) -> str:
        """Prompt text from this instance's Turn fields and later guidance."""
        keys = ", ".join(turn.tool_keys) or "(none)"
        calls = ", ".join(
            f"{call.toolset} name={call.name} {call.summary}".strip()
            for call in turn.tool_calls
        ) or "(none)"
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
        prose = getattr(turn, "prompt", "") or self.prompt
        if prose:
            lines.append(f"Turn.prompt: {prose}")
        lines.append(self.turn_close)
        if later_actions:
            lines.extend(self.later_step(item) for item in later_actions)
            lines.append(self.next_turn)
        return "\n".join(lines) + "\n"

    def create_chat(self, workspace: str, *, timeout_seconds: int = 60) -> str:
        """Identity for one CLI session. Cursor creates a chat; others mint an id."""
        return str(uuid.uuid4())

    def detect(self) -> IdeCli:
        """Return CursorCli or VscodeCli from PATH, keeping these properties.

        -> CursorCli.launcher
        -> VscodeCli.launcher
        // prefer cursor-agent when both exist
        """
        if type(self) is not IdeCli:
            return self
        if CursorCli().launcher():
            return self._as_vendor(CursorCli)
        if VscodeCli().launcher():
            return self._as_vendor(VscodeCli)
        raise RuntimeError(
            "no IDE agent CLI on PATH (cursor-agent, agent, or code)"
        )

    def launcher(self) -> str | None:
        return None

    def command(self, prompt: str, workspace: str) -> list[str]:
        """Argv for one prompt in workspace, including this instance's flags."""
        return self.detect().command(prompt, workspace)

    def judge_command(self, prompt: str, workspace: str) -> list[str]:
        """Argv for the separate judge session (same vendor, read-only)."""
        return self.detect().judge_command(prompt, workspace)

    def task_prompt(
        self, tools: list | None = None, actions: list | None = None, context: str = ""
    ) -> str:
        """Worker-shaped task text: context tools, actions, and optional context."""
        acts = list(actions or [])
        hanging = self.bind_turn(self.blank_turn(), tools, acts[0] if acts else None)
        text = self.turn_prompt(hanging)
        if context:
            text += f"{context}\n"
        return text

    def judge_task_prompt(
        self,
        worker_prompt: str = "",
        generate_tools: list | None = None,
        turn=None,
    ) -> str:
        """Judge the same Turn: same tool_keys, action Validate."""
        if (worker_prompt or "").strip():
            self.job = worker_prompt.strip()
        task = self.judge
        extras = [self.validate_same_lens, self.source_scope]
        if isinstance(task, str):
            extras.insert(0, task)
        elif isinstance(task, dict):
            prior = str(task.get("context") or task.get("prompt") or "").strip()
            if prior:
                extras.insert(0, prior)
        if turn is not None:
            hanging = self.blank_turn()
            hanging.tool_keys = list(turn.tool_keys)
            hanging.tool_calls = list(turn.tool_calls)
            hanging.fidelity = turn.fidelity
            hanging.format = turn.format
            hanging.prompt = getattr(turn, "prompt", "") or ""
            hanging.action = "Validate"
            body = self.turn_prompt(hanging) + "\n".join(extras)
            if self.job:
                body += "\n--- JOB / SOURCE SCOPE ---\n" + self.job + "\n"
            return body if body.endswith("\n") else body + "\n"
        tools = generate_tools
        if isinstance(task, dict):
            tools = self.align_tools(task.get("tools") or generate_tools or [], generate_tools)
        else:
            tools = self.align_tools(generate_tools or [], generate_tools)
        hanging = self.bind_turn(self.blank_turn(), tools, "validate.validate:Validate")
        body = self.turn_prompt(hanging) + "\n".join(extras)
        if self.job:
            body += "\n--- JOB / SOURCE SCOPE ---\n" + self.job + "\n"
        return body if body.endswith("\n") else body + "\n"

    def write_task_file(self, task: str, workspace: str, name: str) -> str:
        """Write task text under workspace and return the relative path."""
        path = Path(workspace) / ".context" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(task, encoding="utf-8")
        try:
            return path.relative_to(workspace).as_posix()
        except ValueError:
            return path.as_posix()

    def launch_prompt(self, task: str, workspace: str, *, name: str) -> str:
        """Argv-safe prompt: one line, or this.launch pointing at the written file."""
        if os.name == "nt" or "\n" in task or len(task) > self.cmdline_safe:
            return self.launch.format(path=self.write_task_file(task, workspace, name))
        return task

    def commands(
        self, prompt: str, workspace: str, judge_prompt: str = ""
    ) -> list[list[str]]:
        """Doer argv, then judge argv when judge is set."""
        chosen = self if type(self) is not IdeCli else self.detect()
        worker_prompt = chosen.launch_prompt(
            prompt, workspace, name="cli-agent-task.txt"
        )
        argv = [chosen.command(worker_prompt, workspace)]
        if not chosen.judge:
            return argv
        judge_text = judge_prompt or chosen.judge_task_prompt(prompt)
        judge_launch = chosen.launch_prompt(
            judge_text, workspace, name="cli-agent-judge.txt"
        )
        argv.append(chosen.judge_command(judge_launch, workspace))
        return argv

    def spawn(
        self,
        argv: list[str],
        workspace: str,
        *,
        timeout_seconds: int = 300,
    ) -> IdeCliResult:
        """Start an interactive session and return. Do not wait."""
        started = time.perf_counter()
        root = Path(workspace) if workspace else Path.cwd()
        logs = root / ".context"
        logs.mkdir(parents=True, exist_ok=True)
        role = "judge" if "--mode" in argv and "ask" in argv else "doer"
        log_path = logs / f"cli-agent-{role}.log"
        log = log_path.open("a", encoding="utf-8")
        log.write(f"\n--- spawn {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        log.write(" ".join(argv) + "\n")
        log.close()
        kwargs: dict = {"cwd": workspace or None}
        if os.name == "nt" and hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        proc = subprocess.Popen(argv, **kwargs)
        return IdeCliResult(
            exit_code=0,
            text=f"pid: {proc.pid}",
            stderr="",
            argv=list(argv),
            elapsed_seconds=time.perf_counter() - started,
            pid=int(proc.pid or 0),
        )

    def run(
        self,
        prompt: str,
        workspace: str,
        *,
        timeout_seconds: int = 300,
    ) -> IdeCliResult:
        """Build worker argv and spawn the IDE CLI."""
        chosen = self if type(self) is not IdeCli else self.detect()
        return chosen.spawn(
            chosen.command(prompt, workspace),
            workspace,
            timeout_seconds=timeout_seconds,
        )

    def run_all(
        self,
        prompt: str,
        workspace: str,
        judge_prompt: str = "",
        *,
        timeout_seconds: int = 300,
    ) -> list[IdeCliResult]:
        """Spawn the doer, and the judge when judge is set."""
        chosen = self if type(self) is not IdeCli else self.detect()
        return [
            chosen.spawn(argv, workspace, timeout_seconds=timeout_seconds)
            for argv in chosen.commands(prompt, workspace, judge_prompt)
        ]

    def _require_launcher(self, missing: str) -> str:
        exe = self.launcher()
        if exe is None:
            raise RuntimeError(missing)
        return exe


class CursorCli(IdeCli):
    """cursor-agent / agent — builds argv and spawns the process."""

    _chat_id = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        re.IGNORECASE,
    )

    def launcher(self) -> str | None:
        return shutil.which("cursor-agent") or shutil.which("agent")

    def command(self, prompt: str, workspace: str) -> list[str]:
        return self._session_args(
            prompt, workspace, agent_mode=self.agent_mode, resume=self.resume
        )

    def judge_command(self, prompt: str, workspace: str) -> list[str]:
        return self._session_args(
            prompt, workspace, agent_mode=self.agent_mode, resume=self.judge_resume
        )

    def create_chat(self, workspace: str, *, timeout_seconds: int = 60) -> str:
        exe = self._require_launcher("cursor-agent not found on PATH")
        completed = subprocess.run(
            [exe, "create-chat", "--workspace", str(workspace)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"cursor-agent create-chat failed (exit {completed.returncode}).\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        match = self._chat_id.search(completed.stdout or "")
        if not match:
            raise RuntimeError(
                f"cursor-agent create-chat returned no chat id.\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        return match.group(0)

    def _cursor_model(self) -> str:
        name = self.model
        if not name:
            return ""
        if "[" in name:
            return name
        if self.mode == "fast":
            return f"{name}[fast=true]"
        if self.mode == "medium":
            return f"{name}[fast=false]"
        return name

    def _session_args(
        self,
        prompt: str,
        workspace: str,
        *,
        agent_mode: str,
        resume: str,
    ) -> list[str]:
        exe = self._require_launcher("cursor-agent not found on PATH")
        args = [exe]
        if self.print_mode:
            args.extend(["-p", "--force", "--trust"])
        else:
            args.extend(["--force", "--trust"])
        if resume:
            args.extend(["--resume", resume])
        args.extend(["--workspace", str(workspace)])
        if self.print_mode:
            args.extend(
                ["--output-format", "stream-json", "--stream-partial-output"]
            )
        model = self._cursor_model()
        if model:
            args.extend(["--model", model])
        if agent_mode in {"plan", "ask"}:
            args.extend(["--mode", agent_mode])
        if prompt:
            args.append(prompt)
        return args


class VscodeCli(IdeCli):
    """VS Code `code chat` — builds argv and spawns the process."""

    def launcher(self) -> str | None:
        return shutil.which("code") or shutil.which("code-insiders")

    def command(self, prompt: str, workspace: str) -> list[str]:
        return self._chat_args(prompt, workspace, agent_mode=self.agent_mode)

    def judge_command(self, prompt: str, workspace: str) -> list[str]:
        return self._chat_args(prompt, workspace, agent_mode=self.agent_mode)

    def _vscode_mode(self, agent_mode: str) -> str:
        if agent_mode == "ask":
            return "ask"
        if agent_mode == "edit":
            return "edit"
        return "agent"

    def _chat_args(
        self, prompt: str, workspace: str, *, agent_mode: str
    ) -> list[str]:
        exe = self._require_launcher("code not found on PATH")
        args = [exe]
        if workspace:
            args.append(str(workspace))
        args.extend(
            [
                "chat",
                "--new-window",
                "--mode",
                self._vscode_mode(agent_mode),
            ]
        )
        args.append(prompt)
        return args


@agentic_toolset
class CliAgent(SubAgent):
    """Slash ``/cli-agent`` runs listed context tools and actions through the IDE CLI.

    Same turn rule as SubAgent: listed actions already open the session turn;
    when actions is missing, the worker wraps context-tool work in performTurn.
    The parent launches kind: sub_agent / launch: non_blocking and does not wait.
    This kit also spawns cursor-agent or `code chat` via IdeCli.run_all.
    Flags live on ide after IdeCli is constructed; every run() reuses them.
    """

    def __init__(
        self,
        model: str = "",
        mode: str = "",
        agent_mode: str = "",
        judge: bool | str | dict = False,
        workspace: str = "",
        session: str = "",
        prompt: str = "",
        print_mode: bool = False,
        ide: IdeCli | None = None,
    ) -> None:
        self._workspace = (workspace or os.getcwd()).strip()
        self._session = (session or "").strip()
        self._work = None
        self._ide = ide or IdeCli(
            model=model,
            mode=mode,
            agent_mode=agent_mode,
            judge=judge,
            print_mode=print_mode,
            prompt=prompt,
        )
        if prompt and not self._ide.prompt:
            self._ide.prompt = prompt.strip()

    @property
    def ide(self) -> IdeCli:
        return self._ide

    @property
    def prompt(self) -> str:
        return self.ide.prompt

    @prompt.setter
    def prompt(self, value: str) -> None:
        self.ide.prompt = (value or "").strip()

    @property
    def job(self) -> str:
        return self.ide.job

    @job.setter
    def job(self, value: str) -> None:
        self.ide.job = (value or "").strip()

    @property
    def source_scope(self) -> str:
        return self.ide.source_scope

    @source_scope.setter
    def source_scope(self, value: str) -> None:
        self.ide.source_scope = value or ""

    @property
    def workspace(self) -> str:
        work = self.work_session
        if work is not None:
            git = getattr(work, "git", None)
            root = getattr(git, "root", None)
            if root is not None:
                return str(root)
            path = getattr(work, "path", None)
            if path:
                return str(path)
        return self._workspace

    @property
    def session(self) -> str:
        return self._session

    @property
    def work_session(self):
        return None if self._work is None else self._work.current_work_session

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

    def ensure_work_session(self):
        """Open or create the workspace session this CLI run belongs to.

        A folder with no `.context/sessions` is still a workspace path —
        `open_work_session` creates the workspace and the work session.
        """
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
        work = self.ensure_work_session()
        work.load_cli_sessions()
        vendor = self.ide.detect()
        if not work.cli_doer:
            work.associate_cli("doer", vendor.create_chat(self.workspace))
        if vendor.judge and not work.cli_judge:
            work.associate_cli("judge", vendor.create_chat(self.workspace))
        self._ide = vendor._copy_policy(
            type(vendor)(
                model=vendor.model,
                mode=vendor.mode,
                agent_mode=vendor.agent_mode,
                judge=vendor.judge,
                resume=work.cli_doer,
                judge_resume=work.cli_judge,
                print_mode=vendor.print_mode,
                job=vendor.job,
                prompt=vendor.prompt,
                source_scope=vendor.source_scope,
            )
        )
        return work

    def _described_turn(self, tools: list, actions: list | None):
        """Suggested Turn shape plus later items as guidance. The CLI decides each Turn."""
        acts = list(actions or [])
        hanging = self.ide.bind_turn(self.ide.blank_turn(), tools, acts[0] if acts else None)
        if self.prompt:
            hanging.prompt = self.prompt
        return hanging, acts[1:]

    def _worker_prompt(self, tools: list, actions: list | None) -> str:
        hanging, later = self._described_turn(tools, actions)
        return self.ide.turn_prompt(hanging, later)

    @prompt_name(name="cli-agent")
    @sub_agent
    @agent_instructions
    def run(self, tools: list, actions: list | None = None) -> str:
        """Run this prompt, the listed context tools, and any listed actions via the IDE CLI.

        tools — context tools (same arguments.tools as iterate / repair / generate).
        actions — optional guidance (kits, utilities, or prompts). The CLI
        decides each Turn.

        Reuse this instance's ide (model, mode, agent_mode, judge). Do not pass
        those per run.

        The parent must not call start_work_session, open, or ensure_started.
        Pass workspace (and session when known) on this kit. This run opens or
        resumes the WorkSession, switches to that path, binds doer and judge,
        then starts an interactive session. If ide.judge is set, a second
        process is the judge. The judge uses the same tools, fidelity, and
        format, and compares written artifacts to the source scope of the
        original job (whole artifact or a stated slice). Missing source
        nodes are a fail. Markdown generate is judged as markdown.

        When this is launched from a chat, always include a process reference
        so a person can get at the CLI: pid when known, and each cursor-agent
        --resume id. Those ids are CLI sessions, not IDE chats — do not wrap
        them as chat links.

        The parent sees kind: sub_agent / launch: non_blocking and does not wait.
        The parent does not block on the CLI. Every once in a while, check
        the CLI (logs, transcript tail, hanging Turn, artifacts) and report
        back how it is doing. Do not drive the work with -p.
        ide.detect().run_all starts the interactive session(s) and returns.

        -> IdeCli.detect
        -> IdeCli.run_all
        -> IdeCli.spawn

        Give the CLI the tools, a suggested first Turn, and any later items as
        guidance. The CLI decides each Turn. Do not wait for the operator.
        """
        """Bring in every listed context tool (AgenticToolset.context_tools)."""
        refs = [item for item in (tools or []) if self.ide.is_toolset_ref(item)]
        for host in self.context_tools(refs):
            host
        action_refs = [item for item in (actions or []) if self.ide.is_toolset_ref(item)]
        if action_refs:
            """Name each listed action kit as guidance — the CLI decides the Turns."""
            for kit in self.context_tools(action_refs):
                kit
        work = self._attach_cli_sessions()
        hanging, later = self._described_turn(tools, actions)
        self.job = self.ide.turn_prompt(hanging, later)
        judge_prompt = (
            self.ide.judge_task_prompt(self.job, generate_tools=tools, turn=hanging)
            if self.ide.judge
            else ""
        )
        results = self.ide.detect().run_all(self.job, self.workspace, judge_prompt)
        failed = next((item for item in results if item.exit_code != 0), None)
        if failed is not None:
            raise RuntimeError(
                failed.stderr.strip() or failed.text.strip() or "IDE CLI exited non-zero"
            )
        parts = [item.text for item in results if item.text]
        parts.append("CLI processes (not IDE chats):")
        for item in results:
            if item.pid:
                parts.append(f"pid: {item.pid}")
        if work.cli_doer:
            parts.append(f"cursor-agent --resume {work.cli_doer}")
        if work.cli_judge:
            parts.append(f"cursor-agent --resume {work.cli_judge}")
        parts.append(f"workspace: {self.workspace}")
        parts.append(f"session: {work.name}")
        return "\n".join(parts)
