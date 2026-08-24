"""Workspace domain — from workspace-eval-oo-sketch §2 / §4."""

from __future__ import annotations

import inspect
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from primitives.instructions import Instruction
from primitives.instructions import instruction
from workspace.context_index import ContextIndex
from workspace.git_repo import GitRepo, NullGitRepo, find_git_root
from tools.tool import resource, agent_tool


@dataclass
class PathOverride:
    """Sparse override: tool + fidelity → workspace-relative path."""

    tool: str
    fidelity: str
    path: str


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
    """Session-branch commit for a finished Turn — identity is the SHA."""

    turn_id: str
    session_name: str
    tool_names: list[str]
    sha: str


class Turn:
    """Turn kit + openTurn state — finish commits/pushes via workSession.git."""

    def __init__(self, work_session: WorkSession | None = None) -> None:
        self.work_session = work_session
        self.id = uuid.uuid4().hex[:8]
        self.prompt = ""
        self.result = ""
        self.context = ""
        self.tool_calls: list[ToolCall] = []
        self.change_commit: TurnCommit | None = None
        self.commit_message = ""
        self.pending_correction: Correction | None = None
        self.artifact_path = ""

    def open(self, host: ContextToolHost) -> Turn:
        session = host.workspace.current_work_session
        if session is None:
            raise RuntimeError("open turn requires currentWorkSession")
        if session.open_turn is None:
            session.open_turn = Turn(work_session=session)
        return session.open_turn

    @agent_tool
    def finish_turn(
        self,
        tools: list[Any] | None = None,
        prompt: str = "",
        result: str = "",
        context: str = "",
    ) -> TurnCommit | None:
        """finish_turn — agent closes the open turn after work."""
        if tools:
            for host in tools:
                workspace = getattr(host, "workspace", None)
                current = getattr(workspace, "current_work_session", None)
                open_turn = getattr(current, "open_turn", None)
                if open_turn is not None:
                    return open_turn.finish(prompt=prompt, result=result, context=context)
        return self.finish(prompt=prompt, result=result, context=context)

    def finish(
        self, prompt: str = "", result: str = "", context: str = ""
    ) -> TurnCommit | None:
        session = self.work_session
        if session is None:
            raise RuntimeError("Turn.finish requires workSession")
        self.prompt = prompt
        self.result = result
        self.context = context
        run = ToolCall(
            toolset="action",
            name="action_run",
            summary=result or prompt or "action finished",
            role="run",
        )
        session.append_trail(run)
        change: TurnCommit | None = None
        if session.dirty:
            message = self.commit_message or f"turn {self.id}"
            if self.pending_correction is not None:
                message = self.pending_correction.correction_commit_message()
            sha = session.git.commit(session.scope_paths, message)
            if self.pending_correction is not None:
                self.pending_correction.link(session.git, sha)
            change = TurnCommit(
                turn_id=self.id,
                session_name=session.name,
                tool_names=[c.name for c in self.tool_calls],
                sha=sha,
            )
            self.change_commit = change
            session.turns.append(self)
        session.git.push()
        session.open_turn = None
        session.save()
        return change

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
        return mistake

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
        self.pending_correction = correction
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

    def correction_commit_message(self) -> str:
        lines = [
            "correction",
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
        if session is not None and session.open_turn is None:
            turn = getattr(host, "turn", None)
            if turn is not None:
                turn.open(host)
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


class WorkSession:
    """One named work session — owns openTurn, turns, repairs, git; session.md kit."""

    default_workspace_folder: str = "."
    context_index_key: str = ""
    _START_FIELD_KEYS = ("date", "path", "goal", "fidelities", "contexts")
    _END_FIELD_KEYS = ("ended", "outcome", "handoff")
    _END_HEADING = "## End"

    def __init__(
        self,
        workspace: Workspace,
        name: str,
        *,
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
        self.workspace = workspace
        self.name = name
        self.goal = goal
        self.fidelities = fidelities
        self.contexts = contexts
        self.path = path or workspace.path
        self.workspace_root = workspace_root if workspace_root is not None else workspace.path
        self.git = git if git is not None else self._default_git()
        self.open_turn: Turn | None = None
        self.turns: list[Turn] = []
        self.repairs = Repairs(self)
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

    def _default_git(self) -> GitRepo:
        root = find_git_root(self.workspace.path)
        if root is None:
            return NullGitRepo()
        return GitRepo(root)

    @property
    def session_branch(self) -> str:
        return f"session/{self.name}"

    @property
    def dirty(self) -> bool:
        return self.git.is_dirty()

    @property
    def folder(self) -> Path:
        if not self.name:
            raise ValueError(
                "session name is not set - confirm working path and session slug with the "
                "user, then call open before grill/sketch/handoff"
            )
        return Path(self.workspace.path) / ".context" / "sessions" / self.name

    @property
    def log(self) -> Path:
        return self.folder / "logs"

    @property
    def session_md(self) -> Path:
        return self.folder / "session.md"

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
        md = session.session_md
        if not md.is_file():
            return session
        return cls._parse(md.read_text(encoding="utf-8"), path=path, name=name)

    def ensure_started(
        self,
        *,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> Path:
        if not self.name:
            raise ValueError("session name is required to create a sprint folder")
        if goal:
            self.goal = goal
        if fidelities:
            self.fidelities = fidelities
        if contexts:
            self.contexts = contexts
        if not self.started:
            self.started = date.today().isoformat()
        self.git.checkout_or_create(self.session_branch)
        self.folder.mkdir(parents=True, exist_ok=True)
        if not self.session_md.is_file():
            self.session_md.write_text(self._render(), encoding="utf-8")
        elif goal or fidelities or contexts:
            if not self.ended:
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
        self.read_context_index()
        self.record_context_root()
        return (
            "Workspace open. "
            "durable root = path; "
            "sprint docs = folder; "
            "context index loaded when present."
        )

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
        return self.session_md

    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        md = self.close(outcome=outcome, handoff=handoff)
        return str(md.resolve())

    def save(self) -> Path:
        path = self.folder / "session.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"name: {self.name}\nbranch: {self.session_branch}\npath: {self.path}\n",
            encoding="utf-8",
        )
        return path

    def load_state(self) -> None:
        """Instance load hook — bootstrap yaml only (git-primary association elsewhere)."""
        return None

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


class Workspace:
    """Parent of `.context/` — workSessions, currentWorkSession, pathOverrides."""

    def __init__(self, path: str) -> None:
        self.path = str(Path(path))
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

    def open(
        self,
        host: Any,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> WorkSession:
        """Plain prelude — open/resume a work session for *host* (not an agent tool)."""
        effective_name = (
            name or getattr(host, "_session_name", None) or ""
        ).strip()
        if not effective_name:
            raise ValueError(
                "need session name — confirm working path and kebab slug with the user, "
                "then open before grill/sketch"
            )
        working = (
            path
            or getattr(host, "_raw_path", None)
            or self.path
            or ""
        ).strip()
        session = self.open_work_session(
            name=effective_name,
            goal=goal,
            fidelities=fidelities or getattr(host, "fidelity", "") or "",
            contexts=contexts,
            path=working or self.path,
            context_index_key=getattr(type(host), "context_index_key", ""),
            default_workspace_folder=getattr(
                type(host), "default_workspace_folder", "."
            ),
            format=getattr(host, "format", None),
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
        self.turn = Turn()
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

    def run_action(self, name: str, *, path: str = "", goal: str = "") -> WorkSession:
        session = self.workspace.open_work_session(
            name=name,
            goal=goal,
            fidelities=self.fidelity,
            path=path,
            git=self._git,
            context_index_key=self.context_index_key,
            default_workspace_folder=self.default_workspace_folder,
        )
        resolved = self.resolve_edit_path(explicit=path)
        self.artifact_path = resolved
        open_turn = self.turn.open(self)
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
        self.turn.open(self)
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
