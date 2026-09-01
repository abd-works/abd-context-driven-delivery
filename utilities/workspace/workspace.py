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

from primitives.actions.action import agent_instructions, agentic_toolset
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


class SessionModel:
    """Persist the preferred Cursor/IDE model under ``.context/sessions/{name}/model``.

    When no work session is active, use the root-repo ``sessions/default`` folder.
    """

    DEFAULT_SESSION = "default"
    FILENAME = "model"
    # CLI doer/judge default — Composer non-fast (vast majority of jobs).
    DEFAULT_MODEL = "composer-2.5"
    DEFAULT_MODE = "medium"  # cursor-agent: model[fast=false]
    # Escalation only — long, very complex work (parent/orchestrator decides).
    COMPLEX_JOB_MODEL = "cursor-grok-4.6-medium"
    _FALLBACK_MODELS = (
        DEFAULT_MODEL,
        "composer-2.5-fast",
        COMPLEX_JOB_MODEL,
        "cursor-grok-4.5-high-fast",
        "kimi-k3-max",
        "inherit",
    )

    @classmethod
    def default_model(cls) -> str:
        return cls.DEFAULT_MODEL

    @classmethod
    def default_mode(cls) -> str:
        return cls.DEFAULT_MODE

    @classmethod
    def complex_job_model(cls) -> str:
        return cls.COMPLEX_JOB_MODEL

    @classmethod
    def resolve_for_launch(cls, workspace: str | Path, session: str = "") -> str:
        """Session file, then default session file, then DEFAULT_MODEL."""
        slug = cls.session_slug(session)
        for candidate in (slug, cls.DEFAULT_SESSION):
            text = cls.read(workspace, candidate)
            if text:
                return text
        return cls.default_model()

    @classmethod
    def session_slug(cls, name: str = "") -> str:
        slug = (name or "").strip()
        if slug.startswith("session/"):
            slug = slug[len("session/") :]
        return slug or cls.DEFAULT_SESSION

    @classmethod
    def file_path(cls, workspace: str | Path, session: str = "") -> Path:
        return SessionPaths.session_dir(workspace, cls.session_slug(session)) / cls.FILENAME

    @classmethod
    def read(cls, workspace: str | Path, session: str = "") -> str:
        path = cls.file_path(workspace, session)
        if not path.is_file():
            return ""
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError:
            return ""

    @classmethod
    def write(cls, workspace: str | Path, model: str, session: str = "") -> Path:
        value = (model or "").strip()
        if not value:
            raise ValueError("model is required")
        path = cls.file_path(workspace, session)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value + "\n", encoding="utf-8")
        return path

    @classmethod
    def copy_into(
        cls,
        dest_folder: str | Path,
        source_workspace: str | Path,
        session: str = "",
    ) -> Path | None:
        """Copy model into *dest_folder* when missing — session first, then default."""
        dest = Path(dest_folder) / cls.FILENAME
        if dest.is_file():
            return None
        slug = cls.session_slug(session)
        for candidate in (slug, cls.DEFAULT_SESSION):
            src = cls.file_path(source_workspace, candidate)
            if not src.is_file():
                continue
            try:
                text = src.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if not text:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text + "\n", encoding="utf-8")
            return dest
        return None

    @classmethod
    def list_available(cls) -> list[str]:
        """Prefer ``cursor-agent --list-models``; fall back to known Cursor model ids."""
        found: list[str] = []
        try:
            proc = subprocess.run(
                ["cursor-agent", "--list-models"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
            for line in blob.splitlines():
                token = line.strip().split()[0] if line.strip() else ""
                if not token or token.startswith("-") or ":" in token:
                    continue
                if token.lower() in {"model", "models", "name", "id"}:
                    continue
                if token not in found:
                    found.append(token)
        except (OSError, subprocess.SubprocessError, FileNotFoundError):
            pass
        if found:
            return found
        return list(cls._FALLBACK_MODELS)


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
        self._transcript_home: Path | None = None

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

    @property
    def model_file(self) -> Path:
        return self.folder / SessionModel.FILENAME

    def session_model(self) -> str:
        """Preferred IDE/CLI model for this session, or empty when unset."""
        if self.model_file.is_file():
            try:
                return self.model_file.read_text(encoding="utf-8").strip()
            except OSError:
                return ""
        return SessionModel.read(self.path or self.workspace.path, self.name)

    def set_session_model(self, model: str) -> str:
        """Persist *model* under this session folder and return the value written."""
        path = SessionModel.write(self.path or self.workspace.path, model, self.name)
        return path.read_text(encoding="utf-8").strip()

    def _inherit_session_model(self) -> None:
        """Copy model from primary (session or default) into this session folder when missing."""
        if self.model_file.is_file():
            return
        primary: Path | None = None
        git = self.git
        if git is not None and not getattr(git, "_memory", False):
            try:
                primary = Path(git.primary_root())
            except Exception:
                primary = None
        if primary is None:
            primary = Path(self.workspace.path)
        SessionModel.copy_into(self.folder, primary, self.name)

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
        from _internal_cli.cli_agent import CliAgent

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
        primary = Path(primary)
        self._retarget_git(tree)
        self.folder.mkdir(parents=True, exist_ok=True)
        SessionModel.copy_into(self.folder, primary, self.name)
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
        other.clear_stash()
        if other.is_dirty():
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
        # Shared/session stash must not keep worktrees around — drop it and remove.
        git.clear_stash()
        # Untracked .context session temps must not block removal — agent BDD and
        # finish_work_session leave disposable CliAgent files that are gitignored.
        if git.is_dirty(untracked=False) or git.has_unpushed_commits():
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


    def _session_harness_ide_type(self) -> str:
        """IDE for session deploy: saved current deploy type, else Cursor."""
        candidates: list[Path] = []
        git = self.git
        try:
            candidates.append(Path(git.primary_root()))
        except Exception:
            pass
        try:
            candidates.append(Path(git.root))
        except Exception:
            pass
        seen: set[Path] = set()
        for root in candidates:
            try:
                resolved = root.resolve()
            except OSError:
                resolved = root
            if resolved in seen:
                continue
            seen.add(resolved)
            state_path = resolved / "primitives" / "harness" / ".deploy-state.json"
            if not state_path.is_file():
                continue
            try:
                payload = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, TypeError):
                continue
            saved = str(payload.get("type") or "").strip()
            if saved in {"Cursor", "VS Code"}:
                return saved
        return "Cursor"

    def _deploy_session_harness(self) -> None:
        """Deploy all harness skills/commands into a linked session worktree.

        Uses the current deploy IDE (saved type; default Cursor). Always writes
        into this worktree's IDE folder so the session has skills/utilities even
        when the primary deploy targets an umbrella workspace.
        """
        git = self.git
        if getattr(git, "_memory", False) or not self.name:
            return
        try:
            linked = git.is_linked_worktree()
        except Exception:
            return
        if not linked:
            return
        try:
            from harness.harness import Harness
        except ImportError:
            return
        ide = self._session_harness_ide_type()
        root = Path(git.root)
        harness = Harness(ide, repo_root=root)
        deploy_path = str(root / harness._ide_folder())
        try:
            harness.write_deploy(deploy_path=deploy_path)
        except Exception:
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
        self._deploy_session_harness()
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
        self._inherit_session_model()
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

    def chat_tag_name(self) -> str:
        return f"chat/{self.session_branch}"

    def save_chat(self, message: str, *, sha: str = "") -> None:
        text = (message or "").strip()
        if not text:
            return
        target = (sha or "").strip() or self.git.current_commit
        self.git.note(target, {"chat": text}, ref="refs/notes/chats")
        existing = [
            line
            for line in self.git.read_annotated_tag(self.chat_tag_name()).splitlines()
            if line.strip()
        ]
        if text not in existing:
            existing.append(text)
        self.git.write_annotated_tag(self.chat_tag_name(), "\n".join(existing), target)

    def chats(self) -> list[str]:
        return [
            line
            for line in self.git.read_annotated_tag(self.chat_tag_name()).splitlines()
            if line.strip()
        ]

    @staticmethod
    def _session_slug(name: str) -> str:
        slug = (name or "").strip()
        if slug.startswith("session/"):
            return slug[len("session/") :]
        return slug

    @prompt(name="worksession-chat")
    @agent_tool
    def worksession_chat(
        self,
        tools: list[Any] | None = None,
        name: str = "",
    ) -> list[str]:
        """worksession-chat — list chat transcript paths attached to a work session.

        Reads the append-only annotated tag ``chat/session/{name}``. Omit ``name`` to
        use the current work session (or this session). Pass the kebab session name or
        ``session/...`` branch when looking up a closed session from another chat.
        """
        slug = self._session_slug(name)
        if tools:
            for item in tools:
                workspace = getattr(item, "workspace", None)
                if workspace is None:
                    continue
                current = getattr(workspace, "current_work_session", None)
                if not slug and current is not None:
                    return current.chats()
                if slug:
                    git = current.git if current is not None else None
                    return WorkSession(workspace, slug, git=git).chats()
        if not slug or slug == self.name:
            return self.chats()
        return WorkSession(self.workspace, slug, git=self.git).chats()

    @staticmethod
    def cursor_project_slug(workspace: str) -> str:
        raw = str(Path(workspace).resolve())
        return (
            raw.replace(":", "")
            .replace("\\", "-")
            .replace("/", "-")
            .replace("_", "-")
        )

    def cursor_chat_file(self, chat_id: str, *, workspace: str = "") -> Path:
        chat_id = (chat_id or "").strip()
        home = self._transcript_home or Path.home()
        root = workspace or self.path or self.workspace_root
        return (
            Path(home)
            / ".cursor"
            / "projects"
            / self.cursor_project_slug(root)
            / "agent-transcripts"
            / chat_id
            / f"{chat_id}.jsonl"
        )

    def current_cursor_chat_file(self) -> Path | None:
        """This chat's transcript — ``CURSOR_CONVERSATION_ID`` (per agent process, not mtime).

        Tests may set ``_conversation_id`` to a uuid, or to ``\"\"`` to ignore the process env.
        """
        if getattr(self, "_conversation_id", None) is not None:
            chat_id = (self._conversation_id or "").strip()
        else:
            chat_id = (os.environ.get("CURSOR_CONVERSATION_ID") or "").strip()
        if not chat_id:
            return None
        transcripts = (os.environ.get("AGENT_TRANSCRIPTS") or "").strip()
        if transcripts and getattr(self, "_conversation_id", None) is None:
            root = Path(transcripts)
            nested = root / chat_id / f"{chat_id}.jsonl"
            flat = root / f"{chat_id}.jsonl"
            if nested.is_file():
                return nested
            if flat.is_file():
                return flat
            return nested
        return self.cursor_chat_file(chat_id)

    def _running_chat_paths(self) -> list[str]:
        """CliAgent doer/judge chats when bound, plus this Cursor chat when present."""
        paths: list[str] = []
        seen: set[str] = set()

        def _add(path: str) -> None:
            if path and path not in seen:
                seen.add(path)
                paths.append(path)

        current = self.current_cursor_chat_file()
        if current is not None:
            _add(str(current))
        for chat_id in (self.cli_doer, self.cli_judge):
            if not chat_id:
                continue
            _add(str(self.cursor_chat_file(chat_id)))
        return paths

    def close(self, *, outcome: str = "", handoff: str = "handoff.md") -> Path:
        running_chats = self._running_chat_paths()
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
                self.git.commit(self._commit_paths(), "close")
            except (GitConnectError, ValueError):
                pass
        for path in running_chats:
            self.save_chat(path)
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
        Linked worktrees get a full harness deploy (current IDE, default Cursor)
        into that worktree so skills/commands/utilities are available immediately.

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

    def _finish_without_session(self, *, outcome: str = "") -> str:
        """No open session: finish turn, attach this chat, push — skip session/worktree."""
        git = self.git
        turn = Turn(workspace=str(self.path or self.workspace.path), session="")
        turn.work_session = None
        turn._checkout_git = git
        turn._workspace_root = str(getattr(git, "root", None) or self.path or ".")
        turn.finish(result=outcome or "finish without session")

        prior_name = self.name
        if not prior_name:
            self.name = "default"
        try:
            for path in self._running_chat_paths():
                self.save_chat(path)
        finally:
            self.name = prior_name

        try:
            git.push()
        except GitConnectError:
            pass
        return "finished without work session"

    @prompt(name="finish-work-session")
    @agent_tool
    def finish_work_session(
        self,
        tools: list[Any] | None = None,
        outcome: str = "",
        handoff: str = "handoff.md",
    ) -> str:
        """finish_work_session — close the current work session.

        Before calling: in the session worktree run ``git status``. Delete only temps
        you know are ephemeral from this session (examples: ``Harness.write_deploy``
        output under ``.cursor/commands`` and ``.cursor/skills``, agent BDD run logs
        under ``.context/.agent_bdd_sessions/`` from spec runs, ``_req*.yaml`` scratch
        files). Use session context — do not delete durable generate, product files, or
        anything you cannot attribute to disposable temps. Never ask the user whether
        to delete the worktree.

        Then: commits change-related paths (scope + session artifacts), pushes, merges onto main,
        clears any stash (stash must never keep a worktree), and removes the sibling worktree when
        the tree is clean and pushed. If untracked or dirty files remain after you removed known
        temps, leave the worktree and report what blocked removal.

        When no work session is open (e.g. work landed on main without ``start_work_session``),
        skips session.md / worktree removal and still finishes the turn (commit dirty checkout),
        attaches this chat, and pushes.
        """
        if tools:
            for item in tools:
                workspace = getattr(item, "workspace", None)
                current = getattr(workspace, "current_work_session", None)
                if current is not None:
                    return current.close_session(outcome=outcome, handoff=handoff)
        if not self.name:
            return self._finish_without_session(outcome=outcome)
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

    def _model_session_name(self, session: str = "") -> str:
        slug = (session or "").strip()
        if slug:
            return SessionModel.session_slug(slug)
        current = self.current_work_session
        if current is not None and current.name:
            return current.name
        return SessionModel.DEFAULT_SESSION

    @agent_tool
    def get_session_model(self, session: str = "", workspace: str = "") -> str:
        """Return the persisted session model id, or empty when unset."""
        root = (workspace or "").strip() or self.path
        return SessionModel.read(root, self._model_session_name(session))

    @agent_tool
    def set_session_model(
        self, model: str, session: str = "", workspace: str = ""
    ) -> str:
        """Persist {model} under ``.context/sessions/{session}/model`` (default session when none)."""
        root = (workspace or "").strip() or self.path
        slug = self._model_session_name(session)
        path = SessionModel.write(root, model, slug)
        current = self.current_work_session
        if current is not None and current.name == slug:
            current.path = current.path or root
        return path.read_text(encoding="utf-8").strip()

    @agent_tool
    def list_session_models(self) -> list[str]:
        """List available Cursor/IDE model ids for AskQuestion choices."""
        return SessionModel.list_available()

    @prompt(name="model")
    @agent_instructions
    def model(self, model: str = "", session: str = "", workspace: str = "") -> str:
        """Set the preferred IDE/CLI model for this work session (slash ``/model``).

        Persist under ``.context/sessions/{session}/model``. When no session is open,
        use the root-repo ``sessions/default`` folder. CliAgent and SubAgent read this
        value when present. Never set disable-model-invocation.

        Default for CLI launches when unset: ``composer-2.5`` (non-fast / medium mode).
        Use ``cursor-grok-4.6-medium`` only when the user confirms a long, very complex job.
        """
        """Step 1 - Resolve the model id. If {model} is already given, use it. If not, call list_session_models, then AskQuestion constrained to that list (plus Other) so the user picks one. Recommend composer-2.5 (non-fast) unless the work is long and very complex — then offer cursor-grok-4.6-medium as a rare escalation."""
        """Step 2 - Call set_session_model with the chosen model (and session/workspace when known)."""
        if model.strip():
            self.set_session_model(model, session=session, workspace=workspace)
        else:
            self.list_session_models()
            self.set_session_model
        """Step 3 - Change the IDE chat model to the chosen id now (Cursor model picker / current chat model). Confirm the switch in chat. Do not set disable-model-invocation."""
        """Step 4 - Tell the user the model is stored for this session and will be used by cli-agent and sub-agent launches when present."""
        return "Session model set."

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
