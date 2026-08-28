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

from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from sub_agent.sub_agent import SubAgent, sub_agent

CMDLINE_SAFE = 4096

JUDGE_TASK = """\
You are an AI judge.
Evaluate OUTPUT against RUBRIC.
Reply with ONLY one JSON object on one line - no markdown, no code fences, no commentary.
The JSON must have keys verdict (PASS or FAIL) and reason (one sentence).

--- RUBRIC ---
{rubric}

--- OUTPUT ---
{output}
"""

LAUNCH = "Read {path} and follow it exactly."
JUDGE_LAUNCH = LAUNCH

_CHAT_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


@dataclass
class IdeCliResult:
    """Outcome of one spawned IDE CLI process."""

    exit_code: int
    text: str
    stderr: str
    argv: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0


class IdeCli:
    """Pick and invoke the installed IDE agent CLI.

    Pass model, mode, agent_mode, and judge once; they are properties afterward
    and every command() / run() reuses them.
    judge is the judge task: False, a validation string, or tools/actions/context
    like the worker run. Launch is the same for worker and judge: put the task
    on argv, or write it and pass LAUNCH when it is longer than CMDLINE_SAFE.
    // always one of CursorCli or VscodeCli after detect
    """

    def __init__(
        self,
        model: str = "",
        mode: str = "",
        agent_mode: str = "",
        judge: bool | str | dict = False,
        resume: str = "",
        judge_resume: str = "",
    ) -> None:
        self._model = (model or "").strip()
        self._mode = (mode or "").strip().lower()
        self._agent_mode = (agent_mode or "").strip().lower()
        self._judge = False if judge in (None, "") else judge
        self._resume = (resume or "").strip()
        self._judge_resume = (judge_resume or "").strip()

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

    def _as_vendor(self, vendor: type[IdeCli]) -> IdeCli:
        return vendor(
            model=self.model,
            mode=self.mode,
            agent_mode=self.agent_mode,
            judge=self.judge,
            resume=self.resume,
            judge_resume=self.judge_resume,
        )

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
        tool_names = ", ".join(str(item) for item in (tools or [])) or "(none)"
        action_names = ", ".join(str(item) for item in (actions or [])) or (
            "(none — use performTurn)"
        )
        text = (
            "Run the listed context tools and actions through this IDE CLI session. "
            "Do not treat this as an in-chat Task.\n"
            f"Context tools: {tool_names}\n"
            f"Actions: {action_names}\n"
        )
        if context:
            text += f"{context}\n"
        return text

    def judge_task_prompt(self, worker_prompt: str = "") -> str:
        """Full judge task text. Same shape as the worker: string or tools/actions/context."""
        task = self.judge
        if isinstance(task, str):
            return task
        if isinstance(task, dict):
            return self.task_prompt(
                task.get("tools") or [],
                task.get("actions"),
                str(task.get("context") or task.get("prompt") or ""),
            )
        return worker_prompt

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
        """Argv-safe prompt: the task itself, or LAUNCH pointing at the written file."""
        if len(task) <= CMDLINE_SAFE:
            return task
        return LAUNCH.format(path=self.write_task_file(task, workspace, name))

    def commands(
        self, prompt: str, workspace: str, judge_prompt: str = ""
    ) -> list[list[str]]:
        """Worker argv, plus judge argv when judge is set. Same launch for both."""
        chosen = self if type(self) is not IdeCli else self.detect()
        worker_prompt = chosen.launch_prompt(
            prompt, workspace, name="cli-agent-task.txt"
        )
        argv = [chosen.command(worker_prompt, workspace)]
        if chosen.judge:
            task = judge_prompt or chosen.judge_task_prompt(prompt)
            argv.append(
                chosen.judge_command(
                    chosen.launch_prompt(
                        task, workspace, name="cli-agent-judge.txt"
                    ),
                    workspace,
                )
            )
        return argv

    def spawn(
        self,
        argv: list[str],
        workspace: str,
        *,
        timeout_seconds: int = 300,
    ) -> IdeCliResult:
        """Run argv as a subprocess. This is the backend CLI call."""
        started = time.perf_counter()
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            cwd=workspace or None,
            check=False,
        )
        return IdeCliResult(
            exit_code=completed.returncode,
            text=completed.stdout or "",
            stderr=completed.stderr or "",
            argv=list(argv),
            elapsed_seconds=time.perf_counter() - started,
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
        """Spawn the worker, then the judge when judge is set."""
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

    def launcher(self) -> str | None:
        return shutil.which("cursor-agent") or shutil.which("agent")

    def command(self, prompt: str, workspace: str) -> list[str]:
        return self._print_args(
            prompt, workspace, agent_mode=self.agent_mode, resume=self.resume
        )

    def judge_command(self, prompt: str, workspace: str) -> list[str]:
        return self._print_args(
            prompt, workspace, agent_mode="ask", resume=self.judge_resume
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
        match = _CHAT_ID_RE.search(completed.stdout or "")
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

    def _print_args(
        self,
        prompt: str,
        workspace: str,
        *,
        agent_mode: str,
        resume: str,
    ) -> list[str]:
        exe = self._require_launcher("cursor-agent not found on PATH")
        args = [
            exe,
            "-p",
            "--force",
            "--trust",
        ]
        if resume:
            args.extend(["--resume", resume])
        args.extend(
            [
                "--workspace",
                str(workspace),
                "--output-format",
                "stream-json",
                "--stream-partial-output",
            ]
        )
        model = self._cursor_model()
        if model:
            args.extend(["--model", model])
        if agent_mode in {"plan", "ask"}:
            args.extend(["--mode", agent_mode])
        args.append(prompt)
        return args


class VscodeCli(IdeCli):
    """VS Code `code chat` — builds argv and spawns the process."""

    def launcher(self) -> str | None:
        return shutil.which("code") or shutil.which("code-insiders")

    def command(self, prompt: str, workspace: str) -> list[str]:
        return self._chat_args(prompt, workspace, agent_mode=self.agent_mode)

    def judge_command(self, prompt: str, workspace: str) -> list[str]:
        return self._chat_args(prompt, workspace, agent_mode="ask")

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
        )

    @property
    def ide(self) -> IdeCli:
        return self._ide

    @property
    def workspace(self) -> str:
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
        self._ide = type(vendor)(
            model=vendor.model,
            mode=vendor.mode,
            agent_mode=vendor.agent_mode,
            judge=vendor.judge,
            resume=work.cli_doer,
            judge_resume=work.cli_judge,
        )
        return work

    def _worker_prompt(self, tools: list, actions: list | None) -> str:
        tool_names = ", ".join(str(item) for item in tools) or "(none)"
        action_names = ", ".join(str(item) for item in (actions or [])) or (
            "(none — use performTurn)"
        )
        return (
            "Run the listed context tools and actions through this IDE CLI session. "
            "Do not treat this as an in-chat Task.\n"
            f"Context tools: {tool_names}\n"
            f"Actions: {action_names}\n"
        )

    @prompt(name="cli-agent")
    @sub_agent
    @agent_instructions
    def run(self, tools: list, actions: list | None = None) -> str:
        """Run this prompt, the listed context tools, and any listed actions via the IDE CLI.

        tools — context tools (same arguments.tools as iterate / repair / generate).
        actions — optional other action kits to run with those context tools.

        Reuse this instance's ide (model, mode, agent_mode, judge). Do not pass
        those per run.

        The parent sees kind: sub_agent / launch: non_blocking and does not wait.
        This method also calls ide.detect().run_all which subprocess-runs
        cursor-agent or code chat. If ide.judge is true, a second process is the judge.

        -> IdeCli.detect
        -> IdeCli.run_all
        -> IdeCli.spawn

        When actions is listed and non-empty: run each listed action with the listed
        context tools. Listed action kits already open the work session and turn.
        Do not wrap those in performTurn.

        When actions is missing or empty: run performTurn
        (workspace.workspace:Turn, action: performTurn) around the listed
        context-tool work — open the hanging turn, each context tool as its own
        tools run, then finish_turn. Report branch and commit back to the parent.
        """
        """Bring in every listed context tool (AgenticToolset.context_tools)."""
        for host in self.context_tools(tools):
            host
        if actions:
            """Run every listed action kit with those context tools. Do not wrap those in performTurn."""
            for kit in self.context_tools(actions):
                kit
        else:
            """Run performTurn (workspace.workspace:Turn, action: performTurn) around the listed context-tool work: open the hanging turn, each context tool as its own tools run, finish_turn; report branch and commit."""
        self._attach_cli_sessions()
        results = self.ide.detect().run_all(
            self._worker_prompt(tools, actions), self.workspace
        )
        failed = next((item for item in results if item.exit_code != 0), None)
        if failed is not None:
            raise RuntimeError(
                failed.stderr.strip() or failed.text.strip() or "IDE CLI exited non-zero"
            )
        return "\n".join(item.text for item in results if item.text)
