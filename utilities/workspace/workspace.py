# @toolset-manifest python -m tools manifest workspace.workspace:Turn
# @toolset-manifest python -m tools manifest workspace.workspace:WorkSession
# @toolset-manifest python -m tools manifest workspace.workspace:Workspace
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Workspace domain — from workspace-eval-oo-sketch §2 / §4."""

from __future__ import annotations

import inspect
import json
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from primitives.actions.action import agentic_toolset
from primitives.instructions import Instruction
from primitives.instructions import instruction
from record_decisions.record_decisions import RecordDecisions
from workspace.context_index import ContextIndex
from workspace.git_repo import GitConnectError, GitRepo, NullGitRepo, Repo
from tools.tool import resource, agent_tool, toolset
from harness.prompt import prompt


@dataclass
class PathOverride:
    """Sparse override: tool + fidelity → workspace-relative path."""

    tool: str
    fidelity: str
    path: str


class SessionPaths:
    """Where files go relative to a workspace path.

    Durable artifacts (sketches, generated markdown, grill-answers) live in
    ``{path}/.context/``. Session temps (session.md, handoff, logs) live in
    ``{path}/.context/sessions/{name}/``. Those two are never the same folder.
    """

    @staticmethod
    def is_session_folder(destination: str | Path) -> bool:
        dest = Path(destination)
        return bool(dest.name) and dest.parent.name == "sessions"

    @staticmethod
    def docs_dir(destination: str | Path) -> Path:
        """Durable artifact dir: ``{path}/.context/`` (sketches, generate, grill-answers).

        Never returns a ``sessions/{name}`` folder. If *destination* is already
        ``.context``, a session folder, or a mistaken sibling under ``.context``
        (``{path}/.context/{session-name}``), walk up to that ``.context``.
        Otherwise ``{destination}/.context/``.
        """
        dest = Path(destination)
        if dest.name == ".context":
            return dest
        if dest.name == "sessions" and dest.parent.name == ".context":
            return dest.parent
        if SessionPaths.is_session_folder(dest):
            return dest.parent.parent
        if dest.parent.name == ".context" and dest.name != "sessions":
            return dest.parent
        return dest / ".context"

    @staticmethod
    def session_dir(destination: str | Path, name: str = "") -> Path:
        """Session temp dir: ``{path}/.context/sessions/{name}/``.

        If *destination* is already a session folder, return it. Otherwise
        *name* is required.
        """
        dest = Path(destination)
        if SessionPaths.is_session_folder(dest):
            return dest
        slug = (name or "").strip()
        if not slug:
            raise ValueError(
                "session name is required when destination is not a session folder"
            )
        return SessionPaths.docs_dir(dest) / "sessions" / slug


docs_dir = SessionPaths.docs_dir
session_dir = SessionPaths.session_dir


@dataclass
class ToolCall:
    """One expand|run record — session trail and openTurn.toolCalls."""

    toolset: str
    name: str
    summary: str
    ok: bool = True
    error: str = ""
    role: str = ""


@dataclass
class TurnCommit:
    """Session-branch commit for a finished Turn — name is the commit subject."""

    name: str
    session_name: str
    tool_names: list[str]
    sha: str


@toolset
class Turn:
    """Turn kit + openTurn state — finish commits/pushes via workSession.git."""

    def __init__(
        self,
        work_session: WorkSession | None = None,
        workspace: str = "",
        session: str = "",
    ) -> None:
        if work_session is None:
            work_session = type(self)._work_session_from_context(workspace, session)
        self.work_session = work_session
        self._workspace_root = workspace
        self._checkout_git: GitRepo | None = None
        self.id = uuid.uuid4().hex[:8]
        self.prompt = ""
        self.result = ""
        self.context = ""
        self.tool_calls: list[ToolCall] = []
        self.change_commit: TurnCommit | None = None
        self.tool_keys: list[str] = []
        self.action = ""
        self.fidelity = ""
        self.format = ""
        self.mistakes: list[Mistake] = []
        self.correction: Correction | None = None
        self.artifact_path = ""

    @classmethod
    def hanging(cls) -> Turn:
        """Turn fields only — do not open a WorkSession."""
        hanging = object.__new__(cls)
        hanging.work_session = None
        hanging.tool_keys = []
        hanging.tool_calls = []
        hanging.action = ""
        hanging.fidelity = ""
        hanging.format = ""
        hanging.prompt = ""
        return hanging

    @staticmethod
    def _work_session_from_context(workspace: str, session: str) -> WorkSession | None:
        root = (workspace or "").strip()
        name = (session or "").strip()
        if not name:
            git_root = Repo.find_root(root or ".")
            if git_root is not None:
                branch = GitRepo(git_root).current_branch
                if isinstance(branch, str) and branch.startswith("session/"):
                    name = branch[len("session/") :]
                    root = root or str(git_root)
        if not name:
            return None
        loaded = Workspace(root or ".")
        loaded.load()
        loaded.open(name=name, path=root or loaded.path)
        return loaded.current_work_session

    @property
    def name(self) -> str:
        parts: list[str] = []
        if self.tool_keys:
            parts.append("-".join(self.tool_keys))
        if self.action:
            parts.append(self.action)
        if self.fidelity:
            parts.append(self.fidelity)
        if self.format:
            parts.append(self.format)
        if not parts:
            raise ValueError(
                "Turn.name unset — open with action via bind_from_host before finish"
            )
        return "-".join(parts)

    def _ensure_named(self) -> None:
        if self.tool_keys or self.action or self.fidelity or self.format:
            return
        session = self.work_session
        if session is not None:
            if session.context_index_key:
                self.tool_keys = [session.context_index_key]
            if session.fidelities:
                self.fidelity = session.fidelities
            if session.format:
                self.format = str(session.format)
        if not (self.tool_keys or self.action or self.fidelity or self.format):
            self.action = "finish"

    @property
    def commit_message(self) -> str:
        return self.name

    def bind_from_host(self, host: Any, *, action: str = "") -> None:
        key = getattr(host, "context_index_key", "") or getattr(
            type(host), "context_index_key", ""
        )
        if key and key not in self.tool_keys:
            self.tool_keys.append(key)
        if action:
            self.action = action
        host_fidelity = getattr(host, "fidelity", "") or ""
        if host_fidelity:
            self.fidelity = host_fidelity
        host_format = getattr(host, "format", None)
        if host_format:
            self.format = str(host_format)
        else:
            session = getattr(getattr(host, "workspace", None), "current_work_session", None)
            session_format = getattr(session, "format", None) if session is not None else None
            if session_format:
                self.format = str(session_format)

    @prompt(name="start-turn")
    @agent_tool
    def open(self, host: ContextToolHost | None = None, *, action: str = "") -> Turn:
        session = None
        if host is not None:
            session = host.workspace.current_work_session
        if session is None:
            session = self.work_session
        if session is None:
            raise RuntimeError("open turn requires currentWorkSession")
        if session.open_turn is None:
            session.open_turn = Turn(work_session=session)
        if host is not None:
            session.open_turn.bind_from_host(host, action=action)
        elif action:
            session.open_turn.action = action
        return session.open_turn

    @prompt(name="finish-turn")
    @agent_tool
    def finish_turn(
        self,
        tools: list[Any] | None = None,
        prompt: str = "",
        result: str = "",
        context: str = "",
    ) -> TurnCommit | None:
        """finish_turn — close the hanging turn, or commit the current checkout if no work session."""
        if tools:
            for host in tools:
                workspace = getattr(host, "workspace", None)
                current = getattr(workspace, "current_work_session", None)
                open_turn = getattr(current, "open_turn", None)
                if open_turn is not None:
                    return self._commit_payload(
                        open_turn.finish(prompt=prompt, result=result, context=context)
                    )
        session = self.work_session
        if session is None:
            return self._commit_payload(
                self.finish(prompt=prompt, result=result, context=context)
            )
        return self._commit_payload(
            session.turn.finish(prompt=prompt, result=result, context=context)
        )

    @staticmethod
    def _commit_payload(change: TurnCommit | None) -> dict[str, Any] | None:
        if change is None:
            return None
        return {
            "name": change.name,
            "session_name": change.session_name,
            "tool_names": list(change.tool_names),
            "sha": change.sha,
        }

    def _git_for_finish(self) -> GitRepo | None:
        if self.work_session is not None:
            return self.work_session.git
        if self._checkout_git is not None:
            return self._checkout_git
        start = (self._workspace_root or "").strip() or "."
        root = Repo.find_root(start)
        if root is None:
            return None
        return GitRepo(root)

    def finish(
        self, prompt: str = "", result: str = "", context: str = ""
    ) -> TurnCommit | None:
        session = self.work_session
        git = self._git_for_finish()
        if git is None:
            return None
        self._ensure_named()
        self.prompt = prompt
        self.result = result
        self.context = context
        run = ToolCall(
            toolset="action",
            name="action_run",
            summary=result or prompt or "action finished",
            role="run",
        )
        if session is not None:
            session.append_trail(run)
        change: TurnCommit | None = None
        dirty = (
            session.dirty if session is not None else git.is_dirty(untracked=False)
        )
        if dirty:
            message = self.name
            if self.correction is not None:
                message = self.correction.correction_commit_message(
                    subject=self.name
                )
            paths = (
                session._commit_paths() if session is not None else [str(git.root)]
            )
            sha = git.commit(paths, message)
            if self.correction is not None:
                self.correction.link(git, sha)
            change = TurnCommit(
                name=self.name,
                session_name=session.name if session is not None else git.current_branch,
                tool_names=[c.name for c in self.tool_calls],
                sha=sha,
            )
            self.change_commit = change
            if session is not None:
                session.turns.append(self)
        if session is not None:
            try:
                git.push()
            except GitConnectError:
                pass
            session.open_turn = None
        else:
            try:
                git.push()
            except GitConnectError:
                pass
        return change

    @prompt(name="mistake")
    @agent_tool
    def record_mistake(
        self,
        *,
        entry_id: str,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        tool: str,
        fidelity: str,
        introducing_commit: str,
    ) -> Mistake:
        session = self.work_session
        if session is None:
            raise RuntimeError("record_mistake requires workSession")
        mistake = Mistake(
            entry_id=entry_id,
            artifact=artifact,
            rule=rule,
            wrong=wrong,
            original=original,
            tool=tool,
            fidelity=fidelity,
            introducing_commit=introducing_commit,
        )
        mistake.annotate(session.git)
        self.mistakes.append(mistake)
        return mistake

    @prompt(name="correction")
    @agent_tool
    def record_correction(
        self,
        entry_ids: list[str],
        *,
        improved: str,
        how: str = "",
        status: str = "fixed",
    ) -> Correction:
        session = self.work_session
        if session is None:
            raise RuntimeError("record_correction requires workSession")
        found = session.git.find_mistakes(entry_ids)
        if not found and self.mistakes:
            wanted = set(entry_ids)
            found = [
                {
                    "entry_id": m.entry_id,
                    "artifact": m.artifact,
                    "rule": m.rule,
                    "wrong": m.wrong,
                    "original": m.original,
                    "tool": m.tool,
                    "fidelity": m.fidelity,
                    "introducing_commit": m.introducing_commit,
                }
                for m in self.mistakes
                if m.entry_id in wanted
            ]
        correction = Correction(improved=improved, how=how, status=status)
        for row in found:
            correction.add(
                Mistake(
                    entry_id=row.get("entry_id", ""),
                    artifact=row.get("artifact", ""),
                    rule=row.get("rule", ""),
                    wrong=row.get("wrong", ""),
                    original=row.get("original", ""),
                    tool=row.get("tool", ""),
                    fidelity=row.get("fidelity", ""),
                    introducing_commit=row.get("introducing_commit", ""),
                )
            )
        self.correction = correction
        return correction


@dataclass
class Mistake:
    """Mistake — annotated on the introducing commit (Git-primary)."""

    entry_id: str
    artifact: str
    rule: str
    wrong: str
    original: str
    tool: str = ""
    fidelity: str = ""
    introducing_commit: str = ""
    correction: Correction | None = None

    def annotate(self, git: GitRepo) -> None:
        if not self.introducing_commit:
            raise ValueError("Mistake.annotate requires introducing_commit")
        git.note(
            self.introducing_commit,
            {
                "entry_id": self.entry_id,
                "artifact": self.artifact,
                "rule": self.rule,
                "wrong": self.wrong,
                "original": self.original,
                "tool": self.tool,
                "fidelity": self.fidelity,
                "introducing_commit": self.introducing_commit,
            },
        )


@dataclass
class Correction:
    """Correction — linked from the fix commit to mistake introducing SHAs."""

    improved: str = ""
    how: str = ""
    status: str = "open"
    mistakes: list[Mistake] = field(default_factory=list)
    fix_commit: str | None = None

    def add(self, mistake: Mistake) -> None:
        if mistake not in self.mistakes:
            self.mistakes.append(mistake)
        mistake.correction = self

    def link(self, git: GitRepo, fix_commit: str) -> None:
        self.fix_commit = fix_commit
        self.status = "fixed"
        entry_ids = [m.entry_id for m in self.mistakes]
        git.note(
            fix_commit,
            {
                "improved": self.improved,
                "how": self.how,
                "status": self.status,
                "entry_ids": ",".join(entry_ids),
                "fix_commit": fix_commit,
            },
        )
        for mistake in self.mistakes:
            if not mistake.introducing_commit:
                continue
            prior = git.read_notes(mistake.introducing_commit)
            prior["fixed_by"] = fix_commit
            git.note(mistake.introducing_commit, prior)

    def correction_commit_message(self, *, subject: str = "correction") -> str:
        lines = [
            subject,
            "",
            f"improved: {self.improved}",
            f"how: {self.how}",
            f"status: {self.status}",
            "",
        ]
        for mistake in self.mistakes:
            lines.append(f"Fixes-Mistake: {mistake.entry_id}")
            if mistake.introducing_commit:
                lines.append(f"Introducing-Commit: {mistake.introducing_commit}")
        return "\n".join(lines)


@dataclass
class Repair:
    """Domain repair bucket on a WorkSession — themed improvement nest (not agentic)."""

    theme: str
    status: str = "backlog"
    work_session: WorkSession | None = None
    asset: str = ""
    violation: str = ""
    mistakes: list[Mistake] = field(default_factory=list)

    def open(self, host: Any, asset: str, violation: str) -> Repair:
        self.asset = asset
        self.violation = violation
        self.status = "backlog"
        session = getattr(getattr(host, "workspace", None), "current_work_session", None)
        if session is not None:
            session.turn
        return self

    def verify_fix(self) -> str:
        return f"verify_fix theme={self.theme} status={self.status}"

    def finish(self, turn: Turn | None = None) -> None:
        self.status = "finished"


class Repairs:
    """WorkSession.repairs — lookup by theme / violation."""

    def __init__(self, session: WorkSession) -> None:
        self._session = session
        self._by_theme: dict[str, Repair] = {}

    def for_violation(self, asset: str, violation: str) -> Repair:
        theme = (violation or asset or "repair").strip() or "repair"
        if theme not in self._by_theme:
            self._by_theme[theme] = Repair(theme=theme, work_session=self._session)
        return self._by_theme[theme]

    def __getitem__(self, theme: str) -> Repair:
        if theme not in self._by_theme:
            self._by_theme[theme] = Repair(theme=theme, work_session=self._session)
        return self._by_theme[theme]

    def __iter__(self):
        return iter(self._by_theme.values())

    def __len__(self) -> int:
        return len(self._by_theme)


@agentic_toolset
class WorkSession:
    """One named work session — owns openTurn, turns, repairs, git; session.md kit."""

    default_workspace_folder: str = "."
    context_index_key: str = ""
    _START_FIELD_KEYS = ("date", "path", "goal", "fidelities", "contexts")
    _END_FIELD_KEYS = ("ended", "outcome", "handoff")
    _END_HEADING = "## End"

    def __init__(
        self,
        workspace: Workspace | str | None = None,
        name: str = "",
        *,
        session: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
        git: GitRepo | None = None,
        started: str | None = None,
        ended: str = "",
        outcome: str = "",
        handoff: str = "",
        body: str = "",
        format: str | None = None,
        workspace_root: str | None = None,
        context_index_key: str | None = None,
        default_workspace_folder: str | None = None,
        host: Any | None = None,
    ) -> None:
        if isinstance(workspace, Workspace):
            parent = workspace
        else:
            root = (workspace or "").strip() or "."
            found = Repo.find_root(root)
            parent = Workspace(str(found) if found is not None else root)
        name = (name or session).strip()
        if not name:
            git_root = Repo.find_root(parent.path)
            if git_root is not None:
                branch = GitRepo(git_root).current_branch
                if isinstance(branch, str) and branch.startswith("session/"):
                    name = branch[len("session/") :]
        self.workspace = parent
        self.name = name
        self.goal = goal
        self.fidelities = fidelities
        self.contexts = contexts
        self.path = path or parent.path
        self.workspace_root = workspace_root if workspace_root is not None else parent.path
        self.git = git if git is not None else self._default_git()
        self.open_turn: Turn | None = None
        self.turns: list[Turn] = []
        self.repairs = Repairs(self)
        self.decisions = RecordDecisions()
        self.scope_paths: list[str] = [str(self.git.root)]
        self.trail: list[ToolCall] = []
        self.format = format
        self._host = host
        self._context_index: str | None = None
        if context_index_key is not None:
            self.context_index_key = context_index_key
        if default_workspace_folder is not None:
            self.default_workspace_folder = default_workspace_folder
        self.started = started if started is not None else date.today().isoformat()
        self.ended = ended
        self.outcome = outcome
        self.handoff = handoff
        self.body = body
        self.cli_doer = ""
        self.cli_judge = ""
        self.cli_doer_pid = 0
        self.cli_judge_pid = 0

    def _default_git(self) -> GitRepo:
        root = Repo.find_root(self.workspace.path)
        if root is None:
            return NullGitRepo()
        return GitRepo(root)

    @property
    def session_branch(self) -> str:
        return f"session/{self.name}"

    @property
    def dirty(self) -> bool:
        return self.git.is_dirty(untracked=False)

    @property
    def turn(self) -> Turn:
        """Turn hangs off the session — present once the session is awake."""
        if self.open_turn is None:
            hanging = Turn(work_session=self)
            if self.context_index_key:
                hanging.tool_keys = [self.context_index_key]
            hanging.fidelity = self.fidelities
            if self.format:
                hanging.format = str(self.format)
            self.open_turn = hanging
        return self.open_turn

    @property
    def docs_dir(self) -> Path:
        """Durable artifacts: sketches, generated files, grill-answers — ``{path}/.context/``."""
        return SessionPaths.docs_dir(self.path)

    @property
    def folder(self) -> Path:
        """Session temps: session.md, handoff, logs."""
        if not self.name:
            raise ValueError(
                "session name is not set - confirm working path and session slug with the "
                "user, then call open before grill/sketch/handoff"
            )
        return SessionPaths.session_dir(self.path, self.name)

    @property
    def log(self) -> Path:
        return self.folder / "logs"

    @property
    def session_md(self) -> Path:
        return self.folder / "session.md"

    @property
    def cli_agent_file(self) -> Path:
        return self.folder / "cli-agent.json"

    def load_cli_sessions(self) -> None:
        binding = self.cli_agent_binding
        if binding.doer or binding.judge:
            self.cli_doer = binding.doer
            self.cli_judge = binding.judge
            self.cli_doer_pid = binding.doer_pid
            self.cli_judge_pid = binding.judge_pid
            return
        path = self.cli_agent_file
        if not path.is_file():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.cli_doer = str(data.get("doer") or "").strip()
        self.cli_judge = str(data.get("judge") or "").strip()
        self.cli_doer_pid = int(data.get("doer_pid") or 0)
        self.cli_judge_pid = int(data.get("judge_pid") or 0)

    def save_cli_sessions(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        self.cli_agent_file.write_text(
            json.dumps(
                {
                    "doer": self.cli_doer,
                    "judge": self.cli_judge,
                    "doer_pid": self.cli_doer_pid,
                    "judge_pid": self.cli_judge_pid,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        self._write_cli_agent_tag()

    def associate_cli(self, role: str, chat_id: str) -> None:
        chat_id = (chat_id or "").strip()
        if role == "judge":
            self.cli_judge = chat_id
        else:
            self.cli_doer = chat_id
        self.save_cli_sessions()

    def close_cli_sessions(self) -> None:
        """Clear doer/judge chat bindings and stop their processes if still alive.

        Does not close the work session — only the CLI agent processes/bindings.
        """
        for pid in (self.cli_doer_pid, self.cli_judge_pid):
            pid = int(pid or 0)
            if pid <= 0:
                continue
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(pid), "/T", "/F"],
                        capture_output=True,
                        check=False,
                    )
                else:
                    os.kill(pid, 15)
            except OSError:
                pass
        self.cli_doer = ""
        self.cli_judge = ""
        self.cli_doer_pid = 0
        self.cli_judge_pid = 0
        if self.cli_agent_file.is_file():
            self.cli_agent_file.unlink()
        self._write_cli_agent_tag(status="closed")

    @property
    def agent_open(self) -> bool:
        return self.cli_agent_binding.open

    @property
    def cli_agent(self):
        """Bound CliAgent for this session, or None if none ran."""
        self.load_cli_sessions()
        binding = self.cli_agent_binding
        if not (self.cli_doer or self.cli_judge or binding.doer or binding.judge):
            return None
        from cli_agent.cli_agent import CliAgent

        self.workspace.current_work_session = self
        agent = CliAgent(workspace=str(self.path), session=self.name)
        agent._work = self.workspace
        return agent

    @property
    def cli_agent_binding(self):
        from git.git import CliAgentBinding

        git = self.git
        reader = getattr(git, "read_cli_agent_tag", None)
        if reader is None:
            return CliAgentBinding()
        try:
            return reader(self.session_branch)
        except Exception:
            return CliAgentBinding()

    def _write_cli_agent_tag(self, status: str = "open") -> None:
        from git.git import CliAgentBinding

        git = self.git
        writer = getattr(git, "write_cli_agent_tag", None)
        if writer is None:
            return
        binding = CliAgentBinding(
            status=status if (self.cli_doer or self.cli_judge) else "closed",
            doer=self.cli_doer,
            doer_pid=self.cli_doer_pid,
            judge=self.cli_judge,
            judge_pid=self.cli_judge_pid,
        )
        if status == "closed":
            binding.status = "closed"
        try:
            writer(self.session_branch, binding)
        except Exception:
            return

    @property
    def context_index(self) -> str:
        return self._context_index or ""

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @property
    def domain_slug(self) -> str:
        return "workspace_session"

    @instruction
    def session_guidance(self) -> Instruction: ...

    @property
    @resource
    def active(self) -> WorkSession:
        return self

    def _take_from(self, other: WorkSession) -> None:
        self.path = other.path
        self.name = other.name
        self.goal = other.goal
        self.fidelities = other.fidelities
        self.contexts = other.contexts
        self.started = other.started
        self.ended = other.ended
        self.outcome = other.outcome
        self.handoff = other.handoff
        self.body = other.body

    def _bind_session_log(self) -> None:
        if self.name:
            from workspace.session_log import SessionLog

            SessionLog.instance().bind(self)

    def attach_host(self, host: Any) -> None:
        self._host = host

    def _resolve_working_area(self, working_area: str | None) -> str:
        if working_area is not None:
            return working_area
        key = self.context_index_key or ""
        indexed = ContextIndex.lookup_root(self.workspace_root, key) if key else None
        if indexed:
            return ContextIndex.root_glob_to_path(self.workspace_root, indexed)
        folder = self.default_workspace_folder or "."
        if folder in (".", ""):
            return self.workspace_root
        return str(Path(self.workspace_root) / folder)

    def to_dict(self) -> dict[str, str | None]:
        try:
            folder = str(self.folder)
        except ValueError:
            folder = None
        return {
            "path": self.path,
            "name": self.name,
            "folder": folder,
            "goal": self.goal or None,
            "fidelities": self.fidelities or None,
            "contexts": self.contexts or None,
            "started": self.started or None,
            "ended": self.ended or None,
            "outcome": self.outcome or None,
            "handoff": self.handoff or None,
            "body": self.body or None,
        }

    def __repr__(self) -> str:
        return f"WorkSession(path={self.path!r}, name={self.name!r})"

    @classmethod
    def load(cls, path: str, name: str) -> WorkSession:
        parent = Workspace(path)
        session = cls(parent, name, path=path, workspace_root=path)
        session._attach_existing_session_worktree()
        md = session.session_md
        if not md.is_file():
            return session
        return cls._parse(md.read_text(encoding="utf-8"), path=path, name=name)

    def _retarget_git(self, root: Path) -> None:
        self.git = GitRepo.open(root)
        self.path = str(root)
        self.workspace_root = str(root)
        self.scope_paths = [str(root)]

    def _session_branch_is_default(self) -> bool:
        default = getattr(self.git, "default_branch", "main") or "main"
        return self.session_branch in {default, "main", "master"}

    def _attach_existing_session_worktree(self) -> None:
        git = self.git
        if getattr(git, "_memory", False) or not self.name:
            return
        if self._session_branch_is_default():
            return
        existing = git.worktree_for(self.session_branch)
        if existing is None:
            return
        if existing.path.resolve() != Path(git.root).resolve():
            self._retarget_git(existing.path)

    def _ensure_session_worktree(self) -> None:
        git = self.git
        if getattr(git, "_memory", False):
            git.checkout_or_create(self.session_branch)
            return
        if self._session_branch_is_default():
            self._try_fetch_pull()
            return
        self._attach_existing_session_worktree()
        git = self.git
        if git.current_branch == self.session_branch:
            self._try_fetch_pull()
            return
        existing = git.worktree_for(self.session_branch)
        if existing is not None:
            self._retarget_git(existing.path)
            self._try_fetch_pull()
            return
        self._try_fetch()
        primary = git.primary_root()
        dest = primary.parent / self._worktree_dirname(primary.name, self.name)
        tree = git.add_worktree(dest, self.session_branch)
        self._retarget_git(tree)
        self._try_fetch_pull()

    @staticmethod
    def _abbrev_repo_name(folder: str) -> str:
        """Abbreviate a clone folder: first token, then first letter of each later token."""
        tokens = [part for part in re.split(r"[-_]+", folder or "") if part]
        if not tokens:
            return folder
        if len(tokens) == 1:
            return tokens[0]
        return tokens[0] + "-" + "".join(token[0] for token in tokens[1:])

    @classmethod
    def _worktree_dirname(cls, repo_folder: str, session_name: str) -> str:
        """Sibling directory `{abbrev}-{ticket-or-short-slug}` next to the primary clone."""
        slug = (session_name or "").strip().strip("-")
        ticket = re.search(r"-(\d+)$", slug)
        short = ticket.group(1) if ticket else slug
        if ticket is None and len(short) > 24:
            short = short[:24].rstrip("-")
        return f"{cls._abbrev_repo_name(repo_folder)}-{short}"

    def _try_fetch(self) -> None:
        try:
            self.git.fetch()
        except GitConnectError:
            return

    def _try_fetch_pull(self) -> None:
        self._try_fetch()
        try:
            self.git.pull()
        except GitConnectError:
            return

    def _try_push(self) -> None:
        try:
            self.git.push()
        except GitConnectError:
            return

    def _land_on_default_branch(self) -> None:
        default = self.git.default_branch
        for candidate in (default, f"origin/{default}", "main", "origin/main"):
            try:
                self.git.merge_from(
                    candidate,
                    message=f"merge {candidate} into {self.session_branch}",
                )
                break
            except GitConnectError:
                continue
        self._try_push()
        try:
            self.git.push_to(default)
        except GitConnectError:
            pass
        occupier = self.git.worktree_for(default)
        if occupier is None:
            try:
                self.git._git("branch", "-f", default, "HEAD")
            except GitConnectError:
                return
            return
        if occupier.path.resolve() == Path(self.git.root).resolve():
            return
        other = GitRepo(occupier.path)
        if other.is_dirty() or other.has_stash():
            return
        try:
            other.merge_from(
                self.session_branch,
                message=f"merge {self.session_branch} into {default}",
            )
        except GitConnectError:
            return

    def _remove_session_worktree_if_clean(self) -> None:
        git = self.git
        if getattr(git, "_memory", False):
            return
        self._try_push()
        if git.is_dirty() or git.has_stash() or git.has_unpushed_commits():
            return
        if git.is_linked_worktree():
            try:
                GitRepo(git.primary_root()).remove_worktree(git.root)
            except GitConnectError:
                pass
        self._remove_empty_checkout_dir()

    def _remove_empty_checkout_dir(self) -> None:
        root = Path(self.path)
        if not root.is_dir():
            return
        try:
            if any(root.iterdir()):
                return
            root.rmdir()
        except OSError:
            return

    def ensure_started(
        self,
        *,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> Path:
        if not self.name:
            raise ValueError("session name is required to create a sprint folder")
        self._ensure_session_worktree()
        self.folder.mkdir(parents=True, exist_ok=True)
        creating = not self.session_md.is_file()
        if creating:
            if goal:
                self.goal = goal
            if fidelities:
                self.fidelities = fidelities
            if contexts:
                self.contexts = contexts
            if not self.started:
                self.started = date.today().isoformat()
            self.session_md.write_text(self._render(), encoding="utf-8")
        return self.session_md

    def open(
        self,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        if name:
            self.name = name
        if goal:
            self.goal = goal
        if fidelities:
            self.fidelities = fidelities
        if contexts:
            self.contexts = contexts
        if path:
            self.path = path
        if not self.name:
            return (
                "need session name — confirm working path and kebab slug with the user, "
                "then call open before grill/sketch"
            )
        self.ensure_started(goal=goal, fidelities=fidelities, contexts=contexts)
        self._bind_session_log()
        self.load_cli_sessions()
        self.read_context_index()
        self.record_context_root()
        consumed = self.consume_handoff()
        opened = (
            "Workspace open. "
            "durable root = path; "
            "sprint docs = folder; "
            "context index loaded when present."
        )
        if not consumed:
            return opened
        return (
            f"{opened} Consumed and deleted the handoff. "
            "Use this text only for this open. "
            "After that, grill-answers, sketches, and generated files are the source of truth.\n\n"
            f"{consumed}"
        )

    def _handoff_search_roots(self) -> list[Path]:
        roots: list[Path] = []
        try:
            roots.append(self.folder)
        except ValueError:
            pass
        roots.append(self.docs_dir)
        if self.name:
            sibling = self.docs_dir / self.name
            if sibling.is_dir() and sibling not in roots:
                roots.append(sibling)
        return roots

    def consume_handoff(self) -> str:
        """Read a live handoff once, then delete it.

        Deletes ``handoff-latest.md``, ``handoff.md``, and ``handoffs/`` under
        the session folder and docs_dir. A consumed handoff is not session state.
        """
        text = ""
        for root in self._handoff_search_roots():
            for name in ("handoff-latest.md", "handoff.md"):
                path = root / name
                if not path.is_file():
                    continue
                if not text:
                    text = path.read_text(encoding="utf-8")
                path.unlink()
            archive = root / "handoffs"
            if archive.is_dir():
                shutil.rmtree(archive)
        if text:
            self.handoff = ""
        return text

    def _ensure_sprint(
        self,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        effective_path = path.strip() or self.path
        effective_name = name.strip() or (self.name or "")
        if not effective_name:
            return (
                "need session name — confirm working path and kebab slug with the user, "
                "then call open before grill/sketch"
            )
        loaded = type(self).load(effective_path, effective_name)
        if loaded.session_md.is_file():
            self._take_from(loaded)
        else:
            self.path = effective_path
            self.name = effective_name
            self.goal = goal
            self.fidelities = fidelities
            self.contexts = contexts
            self.ended = ""
            self.outcome = ""
            self.handoff = ""
            self.started = date.today().isoformat()
        self.ensure_started(goal=goal, fidelities=fidelities, contexts=contexts)
        self._bind_session_log()
        return str(self.session_md.resolve())

    def close(self, *, outcome: str = "", handoff: str = "handoff.md") -> Path:
        self.turn.finish(result=outcome or "session close")
        self.cleanup()
        self.close_cli_sessions()
        if not self.session_md.is_file():
            self.ensure_started()
        self.ended = date.today().isoformat()
        if handoff:
            self.handoff = handoff
        if not outcome and self.handoff:
            outcome = "handoff written"
        if outcome:
            self.outcome = outcome
        self.session_md.write_text(self._render(), encoding="utf-8")
        if self.git.is_dirty():
            try:
                self.git.commit(self._session_artifact_paths(), "close")
            except (GitConnectError, ValueError):
                pass
        self._land_on_default_branch()
        self._remove_session_worktree_if_clean()
        return self.session_md

    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        md = self.close(outcome=outcome, handoff=handoff)
        return str(md.resolve())

    @prompt(name="start-work-session")
    @agent_tool
    def start_work_session(
        self,
        tools: list[Any] | None = None,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
        host: Any | None = None,
    ) -> WorkSession:
        """start_work_session — agent starts or resumes a named work session.

        Non-default session branches isolate in a sibling worktree named
        ``{abbrev}-{ticket}`` (or a short slug) next to the primary clone.
        Stay in the primary clone when the session branch is the default branch.

        Do not call this from a /cli-agent parent. CliAgent opens the session,
        switches to that path, and binds doer/judge. Resume does not rewrite Start.
        """
        if tools:
            for item in tools:
                workspace = getattr(item, "workspace", None)
                if workspace is not None:
                    return workspace.open(
                        host=item,
                        name=name,
                        goal=goal,
                        fidelities=fidelities,
                        contexts=contexts,
                        path=path,
                    )
        if host is not None:
            workspace = getattr(host, "workspace", None)
            if workspace is not None:
                return workspace.open(
                    host=host,
                    name=name or self.name,
                    goal=goal,
                    fidelities=fidelities,
                    contexts=contexts,
                    path=path,
                )
        self.open(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )
        self.workspace.current_work_session = self
        return self

    @prompt(name="finish-work-session")
    @agent_tool
    def finish_work_session(
        self,
        tools: list[Any] | None = None,
        outcome: str = "",
        handoff: str = "handoff.md",
    ) -> str:
        """finish_work_session — close the current work session.

        Commits session artifacts, pushes, merges onto main, then removes the sibling
        worktree automatically when the tree is clean and pushed. Never ask the user
        whether to delete the worktree.
        """
        if tools:
            for item in tools:
                workspace = getattr(item, "workspace", None)
                current = getattr(workspace, "current_work_session", None)
                if current is not None:
                    return current.close_session(outcome=outcome, handoff=handoff)
        if not self.name:
            return "no work session to close"
        return self.close_session(outcome=outcome, handoff=handoff)

    def cleanup(self) -> None:
        """Remove temps this session created. CliAgent temps go through CliAgent."""
        self._wipe_session_logs()
        agent = self.cli_agent
        if agent is not None:
            agent.cleanup()

    def _wipe_session_logs(self) -> None:
        log_dir = self.log
        if not log_dir.is_dir():
            return
        shutil.rmtree(log_dir, ignore_errors=True)

    def _session_artifact_paths(self) -> list[str]:
        return [str(self.session_md)]

    def _commit_paths(self) -> list[str]:
        paths = list(self.scope_paths)
        for extra in self._session_artifact_paths():
            if extra not in paths:
                paths.append(extra)
        return paths

    def append_trail(self, call: ToolCall) -> None:
        self.trail.append(call)
        log_dir = self.log
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        line = (
            f"{ts} toolset={call.toolset} name={call.name} ok={call.ok} "
            f"summary={call.summary}"
        )
        if call.role:
            line += f" role={call.role}"
        if call.error:
            line += f" error={call.error}"
        with (log_dir / "events.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if self.open_turn is not None:
            self.open_turn.tool_calls.append(call)

    def read_context_index(self) -> str:
        path = ContextIndex.context_index_path(self.workspace_root)
        if not path.is_file():
            self._context_index = None
            return f"missing: {path.as_posix()} (no roots recorded yet)"
        text = path.read_text(encoding="utf-8")
        self._context_index = text
        return text

    def record_context_root(self, root: str = "", note: str = "") -> str:
        key = getattr(self, "context_index_key", "") or ""
        if not key:
            return "skipped: this toolset has no context_index_key"
        working = root if root else self.path
        glob = ContextIndex.path_to_root_glob(self.workspace_root, working)
        path = ContextIndex.upsert_entry(self.workspace_root, key, glob, note=note)
        if path.is_file():
            self._context_index = path.read_text(encoding="utf-8")
        return str(path.resolve())

    def _render(self) -> str:
        lines = [
            f"# Session: {self.name}",
            "",
            "## Start",
            "",
            f"- **date:** {self.started}",
            f"- **path:** {self.path}",
            f"- **goal:** {self.goal or '(unset)'}",
            f"- **fidelities:** {self.fidelities or '(unset)'}",
            f"- **contexts:** {self.contexts or '(unset)'}",
            "",
        ]
        if self.body:
            lines.append(self.body.strip("\n"))
            lines.append("")
        if self.ended or self.outcome or self.handoff:
            lines.extend(
                [
                    "## End",
                    "",
                    f"- **ended:** {self.ended or '(unset)'}",
                    f"- **outcome:** {self.outcome or '(unset)'}",
                    f"- **handoff:** {self.handoff or '(unset)'}",
                    "",
                ]
            )
        return "\n".join(lines)

    @classmethod
    def _extract_body(cls, lines: list[str], end_idx: int | None) -> str:
        scope_end = end_idx if end_idx is not None else len(lines)
        last_start_field_idx = -1
        for i in range(scope_end):
            stripped = lines[i].strip()
            if not stripped.startswith("- **") or ":**" not in stripped:
                continue
            key = stripped.partition(":**")[0].removeprefix("- **").strip()
            if key in cls._START_FIELD_KEYS:
                last_start_field_idx = i
        body_start = last_start_field_idx + 1
        if body_start < scope_end and not lines[body_start].strip():
            body_start += 1
        return "\n".join(lines[body_start:scope_end]).strip("\n")

    @classmethod
    def _parse(cls, text: str, *, path: str, name: str) -> WorkSession:
        lines = text.splitlines()
        end_idx = next(
            (i for i, line in enumerate(lines) if line.strip() == cls._END_HEADING),
            None,
        )
        fields: dict[str, str] = {}
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith("- **") or ":**" not in stripped:
                continue
            key, _, value = stripped.partition(":**")
            key = key.removeprefix("- **").strip()
            value = value.strip()
            if value.startswith("(") and value.endswith(")"):
                value = ""
            fields[key] = value
        body = cls._extract_body(lines, end_idx)
        parent = Workspace(path)
        return cls(
            parent,
            name,
            path=fields.get("path") or path,
            goal=fields.get("goal", ""),
            fidelities=fields.get("fidelities", ""),
            contexts=fields.get("contexts", ""),
            started=fields.get("date", "") or date.today().isoformat(),
            ended=fields.get("ended", ""),
            outcome=fields.get("outcome", ""),
            handoff=fields.get("handoff", ""),
            body=body,
            workspace_root=path,
        )


@agentic_toolset
class Workspace:
    """Parent of `.context/` — workSessions, currentWorkSession, pathOverrides."""

    def __init__(self, path: str = "", *, workspace: str = "") -> None:
        self.path = str(Path(workspace or path or "."))
        self.work_sessions: list[WorkSession] = []
        self.current_work_session: WorkSession | None = None
        self.path_overrides: list[PathOverride] = []

    def load(self) -> None:
        self.path_overrides = self._read_overrides()
        sessions_root = Path(self.path) / ".context" / "sessions"
        if not sessions_root.is_dir():
            return
        known = {s.name for s in self.work_sessions}
        for folder in sorted(sessions_root.iterdir()):
            if not folder.is_dir() or folder.name in known:
                continue
            self.work_sessions.append(
                WorkSession(self, folder.name, workspace_root=self.path)
            )

    def save(self) -> Path:
        path = Path(self.path) / ".context" / "context-index.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Path overrides",
            "",
            "| tool | fidelity | path |",
            "|---|---|---|",
        ]
        for row in self.path_overrides:
            lines.append(f"| {row.tool} | {row.fidelity} | {row.path} |")
        if not self.path_overrides:
            lines.append("| *(none)* | | |")
        lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def lookup_path(self, tool: str, fidelity: str) -> str | None:
        for row in self.path_overrides:
            if row.tool == tool and row.fidelity == fidelity:
                return row.path
        return None

    def upsert_path(
        self,
        tool: str,
        fidelity: str,
        path: str,
        default_path: str,
    ) -> None:
        normalized = self._as_workspace_relative(path)
        default = self._as_workspace_relative(default_path)
        self.path_overrides = [
            row
            for row in self.path_overrides
            if not (row.tool == tool and row.fidelity == fidelity)
        ]
        if normalized != default:
            self.path_overrides.append(
                PathOverride(tool=tool, fidelity=fidelity, path=normalized)
            )
        self.save()

    @agent_tool
    def open(
        self,
        host: Any | None = None,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> WorkSession:
        """Open the workspace if it is not already open. The work session's turn and decision records hang off it."""
        effective_name = (
            name or (getattr(host, "_session_name", None) if host is not None else None) or ""
        ).strip()
        if not effective_name:
            raise ValueError(
                "need session name — confirm working path and kebab slug with the user, "
                "then open before grill/sketch"
            )
        working = (
            path
            or (getattr(host, "_raw_path", None) if host is not None else None)
            or self.path
            or ""
        ).strip()
        session = self.open_work_session(
            name=effective_name,
            goal=goal,
            fidelities=fidelities
            or ((getattr(host, "fidelity", "") or "") if host is not None else "")
            or "",
            contexts=contexts,
            path=working or self.path,
            context_index_key=(
                getattr(type(host), "context_index_key", "") if host is not None else ""
            ),
            default_workspace_folder=(
                getattr(type(host), "default_workspace_folder", ".")
                if host is not None
                else "."
            ),
            format=getattr(host, "format", None) if host is not None else None,
            host=host,
        )
        session.read_context_index()
        session.record_context_root()
        session.attach_host(host)
        if hasattr(host, "_session_name"):
            host._session_name = session.name
        return session

    def open_work_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
        *,
        git: GitRepo | None = None,
        context_index_key: str | None = None,
        default_workspace_folder: str | None = None,
        format: str | None = None,
        host: Any | None = None,
    ) -> WorkSession:
        self.load()
        existing = next((s for s in self.work_sessions if s.name == name), None)
        if existing is None:
            session = WorkSession(
                self,
                name,
                goal=goal,
                fidelities=fidelities,
                contexts=contexts,
                path=path or self.path,
                git=git,
                workspace_root=self.path,
                context_index_key=context_index_key,
                default_workspace_folder=default_workspace_folder,
                format=format,
                host=host,
            )
            self.work_sessions.append(session)
        else:
            session = existing
            if git is not None:
                session.git = git
            if goal:
                session.goal = goal
            if fidelities:
                session.fidelities = fidelities
            if contexts:
                session.contexts = contexts
            if path:
                session.path = path
            if context_index_key is not None:
                session.context_index_key = context_index_key
            if default_workspace_folder is not None:
                session.default_workspace_folder = default_workspace_folder
            if format is not None:
                session.format = format
            if host is not None:
                session._host = host
        self.current_work_session = session
        session.open(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path or session.path,
        )
        return session

    def _as_workspace_relative(self, path: str) -> str:
        text = path.replace("\\", "/")
        root = str(Path(self.path).resolve()).replace("\\", "/")
        resolved = str(Path(path).resolve()).replace("\\", "/")
        if resolved == root:
            return "./"
        if resolved.startswith(root + "/"):
            return "./" + resolved[len(root) + 1 :]
        if text.startswith("./"):
            return text
        return text

    def _read_overrides(self) -> list[PathOverride]:
        path = Path(self.path) / ".context" / "context-index.md"
        if not path.is_file():
            return list(self.path_overrides)
        rows: list[PathOverride] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) < 3:
                continue
            tool, fidelity, row_path = parts[0], parts[1], parts[2]
            if tool in {"tool", "---", "*(none)*"} or tool.startswith("---"):
                continue
            if not tool or not fidelity:
                continue
            rows.append(PathOverride(tool=tool, fidelity=fidelity, path=row_path))
        return rows


class ContextToolHost:
    """Spec/host surface from OO — workspace direct; turn/git via currentWorkSession."""

    def __init__(
        self,
        workspace: Workspace,
        *,
        context_index_key: str = "bdd",
        default_workspace_folder: str = "src",
        fidelity: str = "modules",
        git: GitRepo | None = None,
    ) -> None:
        self.workspace = workspace
        self.context_index_key = context_index_key
        self.default_workspace_folder = default_workspace_folder
        self.fidelity = fidelity
        self._git = git
        self.artifact_path = ""

    @property
    def default_path(self) -> str:
        return str(Path(self.workspace.path) / self.default_workspace_folder).replace(
            "\\", "/"
        )

    def resolve_edit_path(self, explicit: str = "") -> str:
        if explicit:
            return explicit.replace("\\", "/")
        override = self.workspace.lookup_path(self.context_index_key, self.fidelity)
        if override:
            if override.startswith("./"):
                return str(Path(self.workspace.path) / override[2:]).replace("\\", "/")
            return override.replace("\\", "/")
        return self.default_path

    def run_action(
        self,
        name: str,
        *,
        path: str = "",
        goal: str = "",
        action: str = "run",
    ) -> WorkSession:
        session = self.workspace.open_work_session(
            name=name,
            goal=goal,
            fidelities=self.fidelity,
            path=path,
            git=self._git,
            context_index_key=self.context_index_key,
            default_workspace_folder=self.default_workspace_folder,
            format=getattr(self, "format", None),
        )
        resolved = self.resolve_edit_path(explicit=path)
        self.artifact_path = resolved
        open_turn = session.turn
        open_turn.action = action
        open_turn.artifact_path = resolved
        self.workspace.upsert_path(
            self.context_index_key,
            self.fidelity,
            resolved,
            self.default_path,
        )
        return session

    def ask_for_instructions(self) -> ToolCall:
        session = self.workspace.current_work_session
        if session is None:
            raise RuntimeError("no current work session")
        session.turn
        call = ToolCall(
            toolset=self.context_index_key,
            name="expand",
            summary="instructions expanded",
            role="expansion",
        )
        session.append_trail(call)
        return call

    def finish(self, result: str = "done") -> TurnCommit | None:
        session = self.workspace.current_work_session
        if session is None or session.open_turn is None:
            raise RuntimeError("no open turn")
        return session.open_turn.finish(result=result)


# Back-compat for specs that imported the stub name during generation.
BaseContextTool = ContextToolHost
