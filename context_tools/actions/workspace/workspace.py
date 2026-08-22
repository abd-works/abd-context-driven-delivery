"""Workspace domain — from workspace-eval-oo-sketch §2 / §4."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from workspace.git_repo import GitRepo, NullGitRepo, find_git_root


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

    def open(self, host: BaseContextTool) -> Turn:
        session = host.workspace.current_work_session
        if session is None:
            raise RuntimeError("open turn requires currentWorkSession")
        if session.open_turn is None:
            session.open_turn = Turn(work_session=session)
        return session.open_turn

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

    def record_correction(
        self,
        *,
        entry_ids: list[str],
        improved: str,
        how: str,
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


class WorkSession:
    """One named work session — owns openTurn, turns, repairs, git."""

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
    ) -> None:
        self.workspace = workspace
        self.name = name
        self.goal = goal
        self.fidelities = fidelities
        self.contexts = contexts
        self.path = path or workspace.path
        self.folder = str(Path(workspace.path) / ".context" / "sessions" / name)
        self.git = git if git is not None else self._default_git()
        self.open_turn: Turn | None = None
        self.turns: list[Turn] = []
        self.repairs: list = []
        self.scope_paths: list[str] = [str(self.git.root)]
        self.trail: list[ToolCall] = []

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
            self.folder = str(
                Path(self.workspace.path) / ".context" / "sessions" / self.name
            )
        if goal:
            self.goal = goal
        if fidelities:
            self.fidelities = fidelities
        if contexts:
            self.contexts = contexts
        if path:
            self.path = path
        Path(self.folder).mkdir(parents=True, exist_ok=True)
        md = Path(self.folder) / "session.md"
        if not md.is_file():
            md.write_text(
                f"# {self.name}\n\n## Start\n- goal: {self.goal}\n",
                encoding="utf-8",
            )
        self.git.checkout_or_create(self.session_branch)
        return self.session_branch

    def close(self, outcome: str = "", handoff: str = "") -> Path:
        md = Path(self.folder) / "session.md"
        with md.open("a", encoding="utf-8") as handle:
            handle.write(f"\n## End\n- outcome: {outcome}\n- handoff: {handoff}\n")
        return md

    def save(self) -> Path:
        path = Path(self.folder) / "session.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"name: {self.name}\nbranch: {self.session_branch}\npath: {self.path}\n",
            encoding="utf-8",
        )
        return path

    def load(self) -> None:
        pass

    def append_trail(self, call: ToolCall) -> None:
        """SessionLog.append shape — events.log + openTurn.toolCalls."""
        self.trail.append(call)
        log_dir = Path(self.folder) / "logs"
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
            self.work_sessions.append(WorkSession(self, folder.name))

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

    def open_work_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
        *,
        git: GitRepo | None = None,
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


class BaseContextTool:
    """Host surface from OO — workspace direct; turn/git via currentWorkSession."""

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
