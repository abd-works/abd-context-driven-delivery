# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""eval EvalSession domain — production from eval-ce-sketch.

Sources / context:
context_tools/actions/eval/.context/sessions/eval/eval-ce-sketch.md
context_tools/actions/eval/.context/module-context.md
"""
from __future__ import annotations

import shutil
import tempfile
import uuid
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import yaml
from primitives.actions.action import action, agentic_toolset
from scanners.scan import Scan, ScanReport
from sub_agent.sub_agent import sub_agent
from tools.tool import tool
from workspace.git_repo import (
    GitConnectError as EvalGitConnectError,
    GitRepo,
    NullGitRepo,
    _git,
    _git_executable,
    find_git_root,
)
from workspace.workspace import Workspace, WorkSession


def _mistake_slug(rule: str, wrong: str, taken: set[str]) -> str:
    raw = rule.strip()
    if raw.lower().startswith("(process)"):
        raw = raw[9:].strip()
    for sep in (" — ", " – ", " - "):
        if sep in raw:
            raw = raw.split(sep, 1)[0].strip()
            break
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", wrong.lower()).strip("-")
    slug = (slug or "mistake")[:60]
    candidate = slug
    n = 2
    while candidate in taken:
        candidate = f"{slug}-{n}"
        n += 1
    return candidate


_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without a git connection."
)


@dataclass
class ToolCall:
    """*ToolCall* is one first-order tool or action run on an open Turn."""

    _toolset: str
    _name: str
    _summary: str = ""

    @property
    def toolset(self) -> str:
        return self._toolset

    @property
    def name(self) -> str:
        return self._name

    @property
    def summary(self) -> str:
        return self._summary


@dataclass
class TurnCommit:
    """*TurnCommit* is the session-branch commit for a finished Turn."""

    turn_id: str
    session_name: str
    tool_names: list[str]
    mistake_ids: list[str]
    sha: str


@dataclass
class Correction:
    """*Correction* is the fix record linked to mistakes via their introducing commits."""

    _improved: str = ""
    _how: str = ""
    _status: str = "open"
    _fixed_in: Turn | None = None
    _mistakes: list[Mistake] = field(default_factory=list)
    _fix_commit: str = ""

    @property
    def improved(self) -> str:
        return self._improved

    @property
    def how(self) -> str:
        return self._how

    @property
    def status(self) -> str:
        return self._status

    @property
    def fixed_in(self) -> Turn | None:
        return self._fixed_in

    @property
    def mistakes(self) -> list[Mistake]:
        return self._mistakes

    @property
    def fix_commit(self) -> str:
        return self._fix_commit

    def add(self, mistake: Mistake) -> None:
        if mistake not in self._mistakes:
            self._mistakes.append(mistake)
        mistake.correct(self)

    def apply(self, mistakes: list[Mistake], turn: Turn) -> None:
        self._status = "fixed"
        self._fixed_in = turn
        for mistake in mistakes:
            self.add(mistake)
            mistake.write_files()
        self._write_improvement(mistakes)

    def link(self, git: GitRepo, fix_commit: str) -> None:
        """Record correction payload on *fix_commit* and keep Fixes-Mistake association."""
        self._fix_commit = fix_commit
        self._status = "fixed"
        entry_ids = [m.entry_id for m in self._mistakes]
        payload = {
            "improved": self._improved,
            "how": self._how,
            "status": self._status,
            "entry_ids": ",".join(entry_ids),
            "fix_commit": fix_commit,
        }
        git.note(fix_commit, payload)
        for mistake in self._mistakes:
            if not mistake.introducing_commit:
                continue
            prior = git.read_notes(mistake.introducing_commit)
            prior["fixed_by"] = fix_commit
            git.note(mistake.introducing_commit, prior)

    def correction_commit_message(self) -> str:
        entry_ids = [m.entry_id for m in self._mistakes]
        lines = [
            "correction",
            "",
            f"improved: {self._improved}",
            f"how: {self._how}",
            f"status: {self._status}",
            "",
        ]
        for entry_id in entry_ids:
            lines.append(f"Fixes-Mistake: {entry_id}")
            for mistake in self._mistakes:
                if mistake.entry_id == entry_id and mistake.introducing_commit:
                    lines.append(f"Introducing-Commit: {mistake.introducing_commit}")
        return "\n".join(lines)

    def _write_improvement(self, mistakes: list[Mistake]) -> None:
        ready = [
            mistake
            for mistake in mistakes
            if mistake.folder and mistake._session_folder
        ]
        if not ready or not self.improved:
            return
        theme_root = Path(ready[0]._session_folder) / Path(ready[0].folder).parent
        theme_root.mkdir(parents=True, exist_ok=True)
        (theme_root / "improvement.md").write_text(
            self._theme_md(ready), encoding="utf-8"
        )

    def _theme_md(self, mistakes: list[Mistake]) -> str:
        theme = Path(mistakes[0].folder).parent.name or mistakes[0].rule
        tools: list[str] = []
        rules: list[str] = []
        errors = [mistake.wrong for mistake in mistakes if mistake.wrong]
        for mistake in mistakes:
            if mistake.tool and mistake.tool not in tools:
                tools.append(mistake.tool)
            if mistake.rule and mistake.rule not in rules:
                rules.append(mistake.rule)
        lines = [f"# {theme}", "", f"- **tool:** {', '.join(tools) or '(unspecified)'}"]
        if len(errors) == 1:
            lines.append(f"- **error:** {errors[0]}")
        else:
            lines.append("- **error:**")
            lines.extend(f"  - {error}" for error in errors)
        lines.append(f"- **rule:** {'; '.join(rules)}")
        lines.append(f"- **how:** {self.how}")
        lines.append("")
        return "\n".join(lines)


@dataclass
class Mistake:
    """*Mistake* is a pointed-out error annotated on the introducing commit."""

    _entry_id: str
    _artifact: str
    _rule: str
    _wrong: str
    _original: str
    _tool: str = ""
    _fidelity: str = ""
    _introducing_commit: str = ""
    _correction: Correction = field(default_factory=Correction)
    _repair: Repair | None = None
    _folder: str = ""
    _session_folder: str = ""

    @property
    def entry_id(self) -> str:
        return self._entry_id

    @property
    def artifact(self) -> str:
        return self._artifact

    @property
    def rule(self) -> str:
        return self._rule

    @property
    def wrong(self) -> str:
        return self._wrong

    @property
    def original(self) -> str:
        return self._original

    @property
    def tool(self) -> str:
        return self._tool

    @property
    def fidelity(self) -> str:
        return self._fidelity

    @property
    def introducing_commit(self) -> str:
        return self._introducing_commit

    @property
    def correction(self) -> Correction:
        return self._correction

    @property
    def repair(self) -> Repair | None:
        return self._repair

    @repair.setter
    def repair(self, value: Repair | None) -> None:
        self._repair = value
        if value is not None and self not in value.mistakes:
            value.mistakes.append(self)
        if value is not None and value.cdd_session is not None:
            value._bring_mistakes([self])

    @property
    def folder(self) -> str:
        return self._folder

    def annotate(self, git: GitRepo) -> None:
        """Note this mistake on the introducing commit — not on the discovery turn commit."""
        if not self._introducing_commit:
            raise ValueError("Mistake.annotate requires introducing_commit")
        payload = {
            "entry_id": self._entry_id,
            "artifact": self._artifact,
            "rule": self._rule,
            "wrong": self._wrong,
            "original": self._original,
            "tool": self._tool,
            "fidelity": self._fidelity,
            "introducing_commit": self._introducing_commit,
        }
        git.note(self._introducing_commit, payload)

    def record(self, session: EvalSession) -> None:
        turn = session.begin_turn()
        if self not in session._mistakes:
            session._mistakes.append(self)
        turn.add(self)
        self._session_folder = str(session.workspace.folder)
        self.write_files()

    def copy_for(self, session: EvalSession) -> Mistake:
        replica = Mistake(
            _entry_id=self.entry_id,
            _artifact=self.artifact,
            _rule=self.rule,
            _wrong=self.wrong,
            _original=self.original,
            _tool=self.tool,
            _fidelity=self.fidelity,
            _correction=Correction(
                _improved=self.correction.improved,
                _how=self.correction.how,
                _status=self.correction.status,
            ),
            _folder=self.folder,
        )
        replica.record(session)
        return replica

    def correct(self, correction: Correction) -> None:
        self._correction = correction

    def write_files(self) -> None:
        if not self._session_folder:
            return
        session_root = Path(self._session_folder)
        previous = session_root / self._folder if self._folder else None
        dest = self._destination(session_root)
        if (
            previous is not None
            and previous.exists()
            and previous.resolve() != dest.resolve()
        ):
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(previous)
            else:
                shutil.move(str(previous), str(dest))
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "faultyAsset").write_text(self.original, encoding="utf-8")
        if self.correction.improved:
            (dest / "repairedAsset").write_text(
                self.correction.improved, encoding="utf-8"
            )
        (dest / "mistake.md").write_text(self._mistake_md(), encoding="utf-8")

    def _destination(self, session_root: Path) -> Path:
        if self.correction.improved:
            theme = _mistake_slug(self.rule, self.wrong, set())
            theme_root = session_root / "repairs" / theme
            taken = (
                {path.name for path in theme_root.iterdir() if path.is_dir()}
                if theme_root.is_dir()
                else set()
            )
            if self._folder:
                slug = Path(self._folder).name
                already_here = self._folder == f"repairs/{theme}/{slug}"
                if slug in taken and not already_here:
                    slug = _mistake_slug(self.rule, self.wrong, taken)
            else:
                slug = _mistake_slug(self.rule, self.wrong, taken)
            self._folder = f"repairs/{theme}/{slug}"
        elif not self._folder:
            root = session_root / "mistakes"
            taken = {path.name for path in root.iterdir()} if root.is_dir() else set()
            slug = _mistake_slug(self.rule, self.wrong, taken)
            self._folder = f"mistakes/{slug}"
        return session_root / self._folder

    def _mistake_md(self) -> str:
        return (
            f"# {Path(self._folder).name or self.rule}\n\n"
            f"- **entry_id:** {self.entry_id}\n"
            f"- **artifact:** {self.artifact}\n"
            f"- **rule:** {self.rule}\n"
            f"- **wrong:** {self.wrong}\n"
            f"- **status:** {self.correction.status}\n"
        )


@dataclass
class Turn:
    """*Turn* is one finished (or open) chat reply on an EvalSession."""

    _id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    _tool_calls: list[ToolCall] = field(default_factory=list)
    _context: str = ""
    _prompt: str = ""
    _result: str = ""
    _mistakes: list[Mistake] = field(default_factory=list)
    _change_commit: TurnCommit | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def tool_calls(self) -> list[ToolCall]:
        return list(self._tool_calls)

    @property
    def context(self) -> str:
        return self._context

    @property
    def prompt(self) -> str:
        return self._prompt

    @property
    def result(self) -> str:
        return self._result

    @property
    def mistakes(self) -> list[Mistake]:
        return list(self._mistakes)

    @property
    def change_commit(self) -> TurnCommit | None:
        return self._change_commit

    def add(self, item: ToolCall | Mistake) -> None:
        if isinstance(item, ToolCall):
            self._tool_calls.append(item)
        else:
            self._mistakes.append(item)


class CDDRepo(GitRepo):
    """GitRepo for the tool clone. Asset sessions link ``cddAt`` once."""

    @property
    def head_sha(self) -> str:
        return self.current_commit

    def current_branch_and_sha(self) -> tuple[str, str]:
        return self.current_branch, self.head_sha

    def link(self, session: EvalSession) -> None:
        session.cdd_at = self.head_sha

    def open_session(self, name: str) -> EvalSession:
        parent = Workspace(str(self.root))
        workspace = parent.open_work_session(name)
        return EvalSession(workspace=workspace, git=self, cdd_repo=self)


class NullCDDRepo(CDDRepo):
    """Stub CDDRepo for isolated unit tests."""

    def __init__(self, branch: str = "main", sha: str = "cddsha0") -> None:
        self.root = Path(".")
        self.commits: list[tuple[list[str], str]] = []
        self._commit = sha
        self._branch = branch
        self._sha = sha
        self._opened: list[EvalSession] = []

    def checkout_or_create(self, name: str) -> str:
        self._branch = name
        return self._branch

    def commit(self, paths: list[str], message: str) -> str:
        self.commits.append((list(paths), message))
        self._commit = f"commit-{len(self.commits)}"
        return self._commit

    @property
    def current_commit(self) -> str:
        return self._sha if not self._commit else self._commit

    @property
    def current_branch(self) -> str:
        return self._branch

    def is_dirty(self, path: str | Path | None = None) -> bool:
        return False

    @property
    def head_sha(self) -> str:
        return self._sha

    def open_session(self, name: str) -> EvalSession:
        folder = Path(tempfile.mkdtemp()) / ".context" / "sessions" / name
        folder.mkdir(parents=True)
        workspace = SimpleNamespace(path=str(folder.parents[2]), folder=folder, name=name)
        opened = EvalSession(
            workspace=workspace,
            git=NullGitRepo(),
            cdd_repo=NullCDDRepo(branch=self._branch, sha=self._sha),
        )
        self._opened.append(opened)
        return opened


def find_cdd_root() -> Path | None:
    """Git root of the running tools clone (this package)."""
    return find_git_root(Path(__file__))


def repos_for_workspace(workspace: WorkSession) -> tuple[GitRepo, CDDRepo]:
    """GitRepo at the working-area clone; CDDRepo at the tools clone.

    Share one root only when the working area sits inside the tools clone
    (e.g. ``sandbox/…``). Cannot connect → ``EvalGitConnectError`` (no Null*).
    ``Null*`` is only for tests that inject those doubles explicitly.
    """
    workspace_root = find_git_root(workspace.path)
    cdd_root = find_cdd_root()
    if workspace_root is None:
        raise EvalGitConnectError(
            "Cannot connect eval git: "
            f"{workspace.path} is not inside a git clone. {_DO_NOT_PROCEED}"
        )
    if cdd_root is None:
        raise EvalGitConnectError(
            "Cannot connect eval git: the CDD tools clone has no git root. "
            f"{_DO_NOT_PROCEED}"
        )
    git = GitRepo(workspace_root)
    if workspace_root == cdd_root:
        return git, CDDRepo(workspace_root)
    return git, CDDRepo(cdd_root)


class EvalSession:
    """*EvalSession* is the eval domain document: turns, mistakes, repairs, one YAML file."""

    def __init__(
        self,
        workspace: WorkSession,
        git: GitRepo | None = None,
        cdd_repo: CDDRepo | None = None,
        is_dirty: Callable[[], bool] | None = None,
    ) -> None:
        self._workspace = workspace
        self._turns: list[Turn] = []
        self._open_turn: Turn | None = None
        self._mistakes: list[Mistake] = []
        self._repairs: list[Repair] = []
        self._cdd_at = ""
        if git is None and cdd_repo is None:
            git, cdd_repo = repos_for_workspace(workspace)
        self._git = git or NullGitRepo()
        self._cdd_repo = cdd_repo or NullCDDRepo()
        if is_dirty is not None:
            self._is_dirty = is_dirty
        else:
            # Whole-repo scope: session path alone misses cross-cutting kit edits.
            self._is_dirty = lambda: self._git.is_dirty(None)
        session_name = str(getattr(workspace, "name", "") or "default")
        self._branch = f"session/{session_name}"
        self.load()
        if not self._cdd_at:
            self._cdd_repo.link(self)

    @property
    def workspace(self) -> WorkSession:
        return self._workspace

    @property
    def path(self) -> str:
        return str(self._workspace.path)

    @property
    def branch(self) -> str:
        return self._branch

    @property
    def turns(self) -> list[Turn]:
        return list(self._turns)

    @property
    def open_turn(self) -> Turn | None:
        return self._open_turn

    @property
    def mistakes(self) -> list[Mistake]:
        return list(self._mistakes)

    @property
    def repairs(self) -> list[Repair]:
        return list(self._repairs)

    @property
    def git(self) -> GitRepo:
        return self._git

    @property
    def cdd_repo(self) -> CDDRepo:
        return self._cdd_repo

    @property
    def cdd_at(self) -> str:
        return self._cdd_at

    @cdd_at.setter
    def cdd_at(self, value: str) -> None:
        self._cdd_at = value

    def begin_turn(self) -> Turn:
        if self._open_turn is None:
            self._open_turn = Turn()
        return self._open_turn

    def record_tool_call(self, tool_call: ToolCall) -> None:
        self.begin_turn().add(tool_call)

    def finish_turn(self, prompt: str, result: str, context: str) -> Turn | None:
        open_turn = self._open_turn
        if open_turn is None:
            open_turn = Turn()
            self._open_turn = open_turn
        dirty = self._is_dirty()
        if not dirty:
            self._open_turn = None
            return None
        open_turn._prompt = prompt
        open_turn._result = result
        open_turn._context = context
        sha = self._git.commit(
            [str(self._git.root)], f"turn {open_turn.id}"
        )
        session_name = str(getattr(self._workspace, "name", "") or "")
        open_turn._change_commit = TurnCommit(
            turn_id=open_turn.id,
            session_name=session_name,
            tool_names=[call.name for call in open_turn.tool_calls],
            mistake_ids=[mist.entry_id for mist in open_turn.mistakes],
            sha=sha,
        )
        self._turns.append(open_turn)
        self._open_turn = None
        self.save()
        return open_turn

    def save(self) -> str:
        folder = Path(self._workspace.folder)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "session.yaml"
        payload = {
            "branch": self._branch,
            "path": self.path,
            "cdd_at": self._cdd_at,
            "turns": [self._turn_dict(turn) for turn in self._turns],
        }
        path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return str(path.resolve())

    def load(self) -> None:
        path = Path(self._workspace.folder) / "session.yaml"
        if not path.is_file():
            return
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        self._branch = str(data.get("branch", self._branch))
        self._cdd_at = str(data.get("cdd_at", self._cdd_at))
        self._turns = []
        self._mistakes = []
        for raw in data.get("turns") or []:
            turn = Turn(_id=str(raw.get("id", uuid.uuid4().hex[:8])))
            turn._prompt = str(raw.get("prompt", ""))
            turn._result = str(raw.get("result", ""))
            turn._context = str(raw.get("context", ""))
            turn._change_commit = self._load_turn_commit(raw.get("change_commit"), turn.id)
            for call in raw.get("tool_calls") or []:
                turn._tool_calls.append(
                    ToolCall(
                        _toolset=str(call.get("toolset", "")),
                        _name=str(call.get("name", "")),
                        _summary=str(call.get("summary", "")),
                    )
                )
            for mist in raw.get("mistakes") or []:
                correction = Correction(
                    _improved=str((mist.get("correction") or {}).get("improved", "")),
                    _how=str((mist.get("correction") or {}).get("how", "")),
                    _status=str((mist.get("correction") or {}).get("status", "open")),
                )
                mistake = Mistake(
                    _entry_id=str(mist.get("entry_id", "")),
                    _artifact=str(mist.get("artifact", "")),
                    _rule=str(mist.get("rule", "")),
                    _wrong=str(mist.get("wrong", "")),
                    _original=str(mist.get("original", "")),
                    _tool=str(mist.get("tool", "")),
                    _fidelity=str(mist.get("fidelity", "")),
                    _correction=correction,
                    _folder=str(mist.get("folder", "")),
                    _session_folder=str(self._workspace.folder),
                )
                turn._mistakes.append(mistake)
                self._mistakes.append(mistake)
            self._turns.append(turn)

    def _find_mistake(self, mistake_id: str) -> Mistake | None:
        for mistake in self._mistakes:
            if mistake.entry_id == mistake_id:
                return mistake
        for turn in list(self._turns) + ([self._open_turn] if self._open_turn else []):
            for mistake in turn.mistakes:
                if mistake.entry_id == mistake_id:
                    return mistake
        return None

    @staticmethod
    def _load_turn_commit(raw: Any, turn_id: str) -> TurnCommit | None:
        if not raw:
            return None
        if isinstance(raw, dict):
            return TurnCommit(
                turn_id=str(raw.get("turn_id", turn_id)),
                session_name=str(raw.get("session_name", "")),
                tool_names=[str(name) for name in (raw.get("tool_names") or [])],
                mistake_ids=[str(mid) for mid in (raw.get("mistake_ids") or [])],
                sha=str(raw.get("sha", "")),
            )
        return TurnCommit(
            turn_id=turn_id,
            session_name="",
            tool_names=[],
            mistake_ids=[],
            sha=str(raw),
        )

    @staticmethod
    def _turn_dict(turn: Turn) -> dict[str, Any]:
        commit = turn.change_commit
        return {
            "id": turn.id,
            "prompt": turn.prompt,
            "result": turn.result,
            "context": turn.context,
            "change_commit": None
            if commit is None
            else {
                "turn_id": commit.turn_id,
                "session_name": commit.session_name,
                "tool_names": commit.tool_names,
                "mistake_ids": commit.mistake_ids,
                "sha": commit.sha,
            },
            "tool_calls": [
                {
                    "toolset": call.toolset,
                    "name": call.name,
                    "summary": call.summary,
                }
                for call in turn.tool_calls
            ],
            "mistakes": [
                {
                    "entry_id": mist.entry_id,
                    "artifact": mist.artifact,
                    "rule": mist.rule,
                    "wrong": mist.wrong,
                    "original": mist.original,
                    "tool": mist.tool,
                    "fidelity": mist.fidelity,
                    "folder": mist.folder,
                    "correction": {
                        "improved": mist.correction.improved,
                        "how": mist.correction.how,
                        "status": mist.correction.status,
                    },
                }
                for mist in turn.mistakes
            ],
        }



def _looks_like_asset(text: str) -> bool:
    body = text.strip()
    if not body:
        return False
    if body[0] in "<{[`#":
        return True
    if "mxfile" in body or "mxGraphModel" in body:
        return True
    if "\n" in body:
        return True
    return len(body) > 200


def _resolve_artifact_file(workspace: Any, artifact: str) -> Path | None:
    candidates = [Path(artifact)]
    root = getattr(workspace, "path", None)
    if root:
        candidates.append(Path(root) / artifact)
    folder = getattr(workspace, "folder", None)
    if folder:
        candidates.append(Path(folder) / artifact)
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


def _read_artifact_file(workspace: Any, artifact: str) -> str | None:
    path = _resolve_artifact_file(workspace, artifact)
    if path is None:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _asset_body(provided: str, disk: str | None, *, prefer_disk: bool) -> str:
    if prefer_disk and disk is not None:
        return disk
    if disk is None:
        return provided
    if _looks_like_asset(disk) and not _looks_like_asset(provided):
        return disk
    return provided if provided.strip() else disk


@agentic_toolset
class Repair:
    """Repair loop on an EvalSession. ``repair`` is atomic; ``eval`` is separate."""

    def __init__(
        self,
        session: EvalSession | None = None,
        scanner: Scan | None = None,
        host: Any | None = None,
        workspace: Any | None = None,
    ) -> None:
        self.session = session if session is not None else getattr(workspace, "eval", None)
        self.scanner = scanner or Scan()
        self.host = host
        self.cdd_session: EvalSession | None = None
        self.mistakes: list[Mistake] = []

    @sub_agent
    @tool
    def log_mistake(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        tool: str = "",
        fidelity: str = "",
    ) -> str:
        if self.session is None:
            raise ValueError("No eval session — open a named session first")
        entry_id = uuid.uuid4().hex[:8]
        original = _asset_body(
            original,
            _read_artifact_file(self.session.workspace, artifact),
            prefer_disk=False,
        )
        Mistake(
            _entry_id=entry_id,
            _artifact=artifact,
            _rule=rule,
            _wrong=wrong,
            _original=original,
            _tool=tool,
            _fidelity=fidelity,
        ).record(self.session)
        return entry_id

    @tool
    def log_correction(
        self,
        mistakes: list[Mistake] | None = None,
        correction: Correction | None = None,
        entry_id: str = "",
        improved: str = "",
        how: str = "",
        status: str = "fixed",
    ) -> str:
        if self.session is None:
            raise ValueError("No eval session — open a named session first")
        turn = self.session.begin_turn()
        if mistakes is None:
            if entry_id:
                found = self.session._find_mistake(entry_id)
                mistakes = [found] if found is not None else []
            else:
                mistakes = list(self.session.mistakes)
        provided = improved if correction is None else correction.improved
        disk = (
            _read_artifact_file(self.session.workspace, mistakes[0].artifact)
            if mistakes
            else None
        )
        body = _asset_body(provided, disk, prefer_disk=False)
        if correction is None:
            correction = Correction(_improved=body, _how=how, _status=status)
        else:
            correction._improved = body
        correction.apply(mistakes, turn)
        self._correct_cdd_copies(mistakes, correction)
        return entry_id or (mistakes[0].entry_id if mistakes else "")

    def _bring_mistakes(self, mistakes: list[Mistake]) -> None:
        cdd = self.cdd_session
        if cdd is None:
            return
        have = {item.entry_id for item in cdd.mistakes}
        for mistake in mistakes:
            if mistake.entry_id in have:
                continue
            mistake.copy_for(cdd)
            have.add(mistake.entry_id)

    def _correct_cdd_copies(
        self, mistakes: list[Mistake], correction: Correction
    ) -> None:
        cdd = self.cdd_session
        if cdd is None:
            return
        copies = []
        for mistake in mistakes:
            found = cdd._find_mistake(mistake.entry_id)
            if found is not None:
                copies.append(found)
        if not copies:
            return
        Correction(
            _improved=correction.improved,
            _how=correction.how,
            _status=correction.status,
        ).apply(copies, cdd.begin_turn())

    def _begin(self, mistakes: list[Mistake]) -> Repair:
        if self.session is None:
            raise ValueError("No eval session — open a named session first")
        if self not in self.session._repairs:
            self.session._repairs.append(self)
        for mistake in mistakes:
            mistake.repair = self
        name = str(getattr(self.session.workspace, "name", "") or "repair")
        self.cdd_session = self.session.cdd_repo.open_session(name)
        self._bring_mistakes(list(self.session.mistakes))
        return self

    def _kind(self, asset: str, violation: str) -> str:
        text = f"{asset} {violation}".lower()
        if "judgment" in text:
            return "judgment"
        return "mechanical"

    def _run(self, asset: str, violation: str) -> None:
        if self.session is None:
            raise EvalGitConnectError(
                "Cannot connect eval git: no eval session. "
                f"{_DO_NOT_PROCEED}"
            )
        if not self.session.mistakes:
            if self.host is not None:
                getattr(self.host, "contexts", None)
            self.log_mistake(
                artifact=asset,
                rule=violation,
                wrong=violation,
                original="",
            )
        self._begin(list(self.session.mistakes))
        mistake = self.mistakes[0] if self.mistakes else None
        if mistake is not None and self.scanner is not None:
            paths = [asset] if asset else []
            scan_report = ScanReport.from_scan(self.scanner.scan(paths))
            if (
                not scan_report.matches(mistake)
                and self._kind(asset, violation) == "mechanical"
                and self.host is not None
                and hasattr(self.host, "createRule")
            ):
                self.host.createRule(failed=mistake.wrong, wanted=violation)
                ScanReport.from_scan(
                    self.scanner.scan(paths, root=None, rule=mistake.rule)
                ).matches(mistake)

    def _ensure_cdd_session(self) -> None:
        if self.session is None or self.cdd_session is not None:
            return
        name = str(getattr(self.session.workspace, "name", "") or "eval")
        self.cdd_session = self.session.cdd_repo.open_session(name)
        self._bring_mistakes(list(self.session.mistakes))

    @tool
    def start(self, asset: str, violation: str) -> str:
        """Open the CDD session and copy project mistakes onto it.

        Raises EvalGitConnectError if project/CDD git cannot be connected.
        Do not proceed unless the user tells you to continue without git.
        """
        self._run(asset, violation)
        if self.cdd_session is None:
            return ""
        return str(getattr(self.cdd_session.workspace, "name", "") or "")

    @sub_agent
    @action
    def repair_session(self, asset: str, violation: str) -> str:
        """repair"""
        self.start(asset, violation)
        return (
            "Repair {{asset}} under {session.path}/ until validate passes. "
            "Fail-first: mechanical specs call expect_scan_fails / "
            "expect_scan_passes (context_tools.bdd.spec_helpers) on the fail "
            "file and the pass file; judgment specs call generate_and_judge "
            "(agent_bdd.spec_helpers) on the pass file. Do not add an "
            "eval-package spec harness. After the fix, those same helpers are "
            "the eval. If a test cannot fail, defer — do not repair."
        )

    @action
    def repair(self, tools: list, asset: str, violation: str) -> str:
        """Run repair on each passed context tool."""
        for host in self.context_tools(tools):
            host.repair(asset, violation)
        return (
            "Repair {{asset}} under {session.path}/ until validate passes. "
            "Fail-first test before any tool change. Write evals after the fix."
        )

    @sub_agent
    @action
    def eval(self) -> str:
        """eval"""
        return (
            "Eval the repair with the existing spec helpers — not a new eval "
            "package. The pair lives under {session.folder}/repairs/{theme}/ "
            "(sibling of mistakes/). Mechanical: expect_scan_fails on the "
            "before file, expect_scan_passes on the after file "
            "(context_tools.bdd.spec_helpers). Judgment: generate_and_judge "
            "on the same pass file (agent_bdd.spec_helpers); hold that "
            "generate for human review. If you need to confirm with the user, "
            "ask via AskQuestion."
        )

    @tool
    def contribute(self, before_commit: str = "", after_commit: str = "") -> str:
        self._ensure_cdd_session()
        return (
            f"Linked session-branch commits {before_commit} -> {after_commit}; ran eval."
        )
