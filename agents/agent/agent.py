"""Agent — backlog and participant orchestration (stubbed runtime hooks)."""
from __future__ import annotations

import json
import itertools
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

_ParticipantType = Literal["doer", "judge", "human"]
_ParticipantState = Literal[
    "idle",
    "sending",
    "awaiting_accept",
    "running",
    "awaiting_verdict",
    "done",
    "faulted",
]
_TaskState = Literal["Backlog", "In Progress", "Done"]
_AgentFaultKind = Literal[
    "judge_fail_limit",
    "parse_failed",
    "invariant",
    "validation_error",
]
_AIChatFaultKind = Literal["not_accepted", "stall", "send_failed", "connection"]


@dataclass
class AgentParticipant:
    """One doer, judge, or human role on a task."""

    type: _ParticipantType
    prompt: str = ""
    state: _ParticipantState = "idle"
    chat: AIChatInstance | None = None


def _default_doer() -> AgentParticipant:
    return AgentParticipant(type="doer")


@dataclass
class AgentTask:
    """One backlog item with doer and optional judge or human."""

    prompt: str
    state: _TaskState = "Backlog"
    index: int | None = None
    doer: AgentParticipant = field(default_factory=_default_doer)
    judge: AgentParticipant | None = None
    human: AgentParticipant | None = None
    tickets: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.doer.prompt:
            self.doer.prompt = self.prompt
        if self.doer.type != "doer":
            self.doer.type = "doer"


class _KindedFault(Exception):
    """Shared kind/detail/participant storage for AgentFault and AIChatFault."""

    def __init__(
        self,
        kind: str,
        detail: str = "",
        participant: Optional[AgentParticipant] = None,
    ) -> None:
        super().__init__(detail or kind)
        self._kind = kind
        self._detail = detail
        self._participant = participant

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def participant(self) -> Optional[AgentParticipant]:
        return self._participant


class AgentFault(_KindedFault):
    """Agent orchestration fault — validation_error skips; other kinds stop the run."""


class AIChatFault(_KindedFault):
    """CLI delivery fault — transcript watcher accept / stall / connection."""


@dataclass
class AgentTaskTemplate:
    """Blueprint of task prompts — not live AgentTask instances."""

    name: str
    tasks: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class AgentTaskTemplateStore:
    """Catalog of task templates outside Agent."""

    root: Path | None = None
    _by_name: dict[str, AgentTaskTemplate] = field(default_factory=dict, repr=False)

    def add(self, template: AgentTaskTemplate) -> None:
        self._by_name[template.name] = template

    def load(self, name: str) -> AgentTaskTemplate:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise KeyError(f"unknown template: {name}") from exc

    def list_all(self) -> list[AgentTaskTemplate]:
        return list(self._by_name.values())

    def find_matching(self, prompt: str) -> list[AgentTaskTemplate]:
        needle = prompt.lower()
        return [
            template
            for template in self._by_name.values()
            if needle in template.name.lower() or needle in template.description.lower()
        ]


@dataclass
class ToolCall:
    """One expand|run record on an open Turn."""

    toolset: str
    name: str
    summary: str = ""
    ok: bool = True
    error: str = ""
    role: str = "run"


@dataclass
class Turn:
    """One tools-CLI turn — opened/finished outside Agent._complete_task."""

    @dataclass
    class Guidance:
        """Fence fields handed to the AI chat runtime for a tools CLI turn."""

        session_name: str
        context_root: str
        turn_id: str
        tool_guidance: str = ""

        def as_dict(self) -> dict[str, str]:
            return {
                "sessionName": self.session_name,
                "contextRoot": self.context_root,
                "turnId": self.turn_id,
                "toolGuidance": self.tool_guidance,
            }

    session: AgentSession
    name: str
    sha: str = ""
    subject: str = ""
    hanging: bool = False
    tool_calls: list[ToolCall] = field(default_factory=list)
    guidance: Guidance | None = None
    _action: str = field(default="", repr=False)

    def open(self, *, action: str = "") -> Guidance:
        self._action = action
        self.hanging = True
        self.guidance = Turn.Guidance(
            session_name=self.session.name,
            context_root=str(self.session.context_root),
            turn_id=self.name,
            tool_guidance=action,
        )
        self.session.log.open_turn(self)
        self.session.turns.append(self)
        return self.guidance

    def append_tool(self, tool_call: ToolCall) -> None:
        self.tool_calls.append(tool_call)
        self.session.log.append_tool(tool_call)

    def finish(self, *, subject: str = "", sha: str = "stub") -> None:
        self.subject = subject or self._action or self.name
        self.sha = sha
        self.hanging = False
        self.session.log.finish_turn(self)
        if self.session.open_turn is self:
            self.session.open_turn = None

    def finish_turn(self, *, subject: str = "", sha: str = "stub") -> None:
        self.finish(subject=subject, sha=sha)

    def close(self) -> None:
        self.hanging = False


@dataclass
class _SessionLogWriter:
    path: Path | None = None
    _records: list[dict[str, Any]] = field(default_factory=list, repr=False)
    _last_ts_ms: int | None = field(default=None, repr=False)

    def open(self, *, name: str, **fields: Any) -> None:
        self._append("open", name=name, **fields)

    def close(self, *, name: str, **fields: Any) -> None:
        self._append("close", name=name, **fields)

    def _append(self, kind: str, **fields: Any) -> None:
        record = self._compose_record(kind, **fields)
        self._remember_record(record)
        self._write_record_to_disk(record)

    def _compose_record(self, kind: str, **fields: Any) -> dict[str, Any]:
        now_ms = int(time.time() * 1000)
        record: dict[str, Any] = {
            "kind": kind,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "ts_ms": now_ms,
        }
        if self._last_ts_ms is not None:
            record["since_last_s"] = round((now_ms - self._last_ts_ms) / 1000.0, 3)
        self._last_ts_ms = now_ms
        for field_name, field_value in fields.items():
            if field_value is None:
                continue
            if field_value == "":
                continue
            if isinstance(field_value, list) and not field_value:
                continue
            record[field_name] = field_value
        return record

    def _remember_record(self, record: dict[str, Any]) -> None:
        self._records.append(record)

    def _write_record_to_disk(self, record: dict[str, Any]) -> None:
        if self.path is None:
            return
        line = self._serialize_record(record)
        self._append_line_to_log(line)

    def _serialize_record(self, record: dict[str, Any]) -> str:
        return json.dumps(record, separators=(",", ":")) + "\n"

    def _append_line_to_log(self, line: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line)

    def open_turn(self, turn: Turn) -> None:
        self._append("open_turn", name=turn.name, action=turn._action or None)

    def finish_turn(self, turn: Turn) -> None:
        self._append(
            "finish_turn",
            name=turn.name,
            sha=turn.sha or None,
            subject=turn.subject or None,
        )

    def append_tool(self, tool_call: ToolCall) -> None:
        self._append(
            "append_tool",
            toolset=tool_call.toolset,
            name=tool_call.name,
            summary=tool_call.summary or None,
            ok=tool_call.ok,
            error=tool_call.error or None,
            role=tool_call.role or None,
        )

    def append_fault(self, fault: AgentFault) -> None:
        participant = fault.participant
        self._append(
            "append_fault",
            fault=fault.kind,
            detail=fault.detail or None,
            participant=participant.type if participant is not None else None,
        )

    def validation_error(self, detail: str) -> None:
        self._append("validation_error", detail=detail or None)

    def healer_eval(
        self,
        *,
        phase: str,
        trigger: str,
        journey: str,
        stop_recommended: bool = False,
        fix_recommended: bool = False,
    ) -> None:
        self._append(
            "healer_eval",
            phase=phase,
            trigger=trigger,
            journey=journey,
            stopRecommended=stop_recommended,
            fixRecommended=fix_recommended,
        )

    def healer_invoke(
        self,
        *,
        phase: str,
        trigger: str,
        journey: str,
        stop_recommended: bool = False,
    ) -> None:
        """Deprecated — use healer_eval."""
        self.healer_eval(
            phase=phase,
            trigger=trigger,
            journey=journey,
            stop_recommended=stop_recommended,
        )

    def healer_finding(self, *, finding_kind: str, detail: str, phase: str = "") -> None:
        self._append(
            "healer_finding",
            findingKind=finding_kind,
            detail=detail,
            phase=phase or None,
        )

    def healer_report(
        self,
        *,
        summary: str,
        stop_recommended: bool = False,
        fix_recommended: bool = False,
    ) -> None:
        self._append(
            "healer_report",
            summary=summary,
            stopRecommended=stop_recommended,
            fixRecommended=fix_recommended,
        )


@dataclass
class AgentSessionLog(_SessionLogWriter):
    """Append-only JSONL orchestration audit for one AgentSession."""

    def send(self, participant: AgentParticipant, *, prompt: Optional[str] = None) -> None:
        payload: dict[str, Any] = {"participant": self._participant_label(participant)}
        if prompt:
            payload["prompt"] = prompt
        self._append("send", **payload)

    def accepted(self, participant: AgentParticipant) -> None:
        self._append("accepted", participant=self._participant_label(participant))

    def done(self, participant: AgentParticipant) -> None:
        self._append("done", participant=self._participant_label(participant))

    def verdict(self, participant: AgentParticipant, result: str, **fields: Any) -> None:
        self._append(
            "verdict",
            participant=self._participant_label(participant),
            result=result,
            **fields,
        )

    def launch_next(self, task: AgentTask) -> None:
        self._append(
            "launch_next",
            prompt=task.prompt,
            hasJudge=task.judge is not None,
            hasHuman=task.human is not None,
        )

    def complete_task(self, task: AgentTask, *, outcome: str, **fields: Any) -> None:
        self._append("complete_task", prompt=task.prompt, outcome=outcome, **fields)

    def add_tasks(self, tasks: list[AgentTask]) -> None:
        self._append("add_tasks", tasks=[task.prompt for task in tasks])

    def clear_backlog(self) -> None:
        self._append("clear_backlog")

    def kick(self, participant: AgentParticipant) -> None:
        self._append("kick", participant=self._participant_label(participant))

    def human_feedback(self, feedback: str) -> None:
        self._append("human_feedback", feedback=feedback)

    @staticmethod
    def _participant_label(participant: AgentParticipant) -> str:
        return participant.type


class CliAgentSessionLog(AgentSessionLog):
    """CliAgent JSONL kinds — bind/run/judge/wait + kick with chatId."""

    def bind_chat_context(self, participant: AgentParticipant) -> None:
        chat = participant.chat
        fields: dict[str, Any] = {
            "participant": self._participant_label(participant),
        }
        if chat is not None:
            if chat.chat_id:
                fields["chatId"] = chat.chat_id
            if chat.pid is not None:
                fields["pid"] = chat.pid
            if chat.workspace_path:
                fields["workspacePath"] = chat.workspace_path
            if chat.session_name:
                fields["sessionName"] = chat.session_name
        self._append("bind_chat_context", **fields)

    def run_chat(self, chat: AIChatInstance, prompt: str) -> None:
        fields: dict[str, Any] = {"prompt": prompt}
        if chat.chat_id:
            fields["chatId"] = chat.chat_id
        if chat.pid is not None:
            fields["pid"] = chat.pid
        self._append("run", **fields)

    def launch_judge(self, participant: AgentParticipant) -> None:
        fields: dict[str, Any] = {}
        chat = participant.chat
        if chat is not None and chat.chat_id:
            fields["judgeChatId"] = chat.chat_id
        self._append("launch_judge", **fields)

    def wait_doer(self) -> None:
        self._append("wait_doer")

    def kick(self, participant: AgentParticipant) -> None:
        fields: dict[str, Any] = {
            "participant": self._participant_label(participant),
        }
        chat = participant.chat
        if chat is not None and chat.chat_id:
            fields["chatId"] = chat.chat_id
        self._append("kick", **fields)

    def _adopt_from(self, other: AgentSessionLog) -> None:
        self.path = other.path if self.path is None else self.path
        self._records = list(other._records)
        self._last_ts_ms = other._last_ts_ms


class _UnlinkedAgent:
    def close(self) -> None:
        return None


_UNLINKED = _UnlinkedAgent()


class _ParticipantOps:
    @staticmethod
    def of_task(task: AgentTask) -> list[AgentParticipant]:
        participants: list[AgentParticipant] = [task.doer]
        if task.judge is not None:
            participants.append(task.judge)
        if task.human is not None:
            participants.append(task.human)
        return participants

    @staticmethod
    def present(participant: AgentParticipant | None) -> list[AgentParticipant]:
        if participant is None:
            return []
        return [participant]

    @staticmethod
    def any_in_flight(participants: list[AgentParticipant]) -> bool:
        for participant in participants:
            if participant.state not in ("idle", "done"):
                return True
        return False

    @staticmethod
    def mark_idle(participants: list[AgentParticipant]) -> None:
        for participant in participants:
            participant.state = "idle"


class _StubSeries:
    def __init__(self, items: list[str] | None = None) -> None:
        self._items = list(items or [])

    def pop(self, default: str) -> str:
        if self._items:
            return self._items.pop(0)
        return default

    def replace(self, items: list[str]) -> None:
        self._items = list(items)


class _SlashManifest:
    """Classify slash tokens in a doer/judge prompt for the stub tools CLI."""

    _ACTIONS = frozenset({"validate", "generate", "satisfy", "scan"})
    _UTILITIES = frozenset({"echo", "diagnose", "handoff", "finish-turn"})

    @classmethod
    def tokens(cls, prompt: str) -> list[str]:
        return [part for part in prompt.split() if part.startswith("/")]

    @classmethod
    def role_for(cls, token: str) -> str:
        name = token.lstrip("/").split(".")[0].lower()
        if name in cls._ACTIONS:
            return "action"
        if name in cls._UTILITIES:
            return "utility"
        return "run"

    @classmethod
    def tool_call_for(cls, token: str) -> ToolCall:
        bare = token.lstrip("/")
        name = bare.split(".")[0] if bare else token
        role = cls.role_for(token)
        toolset = {
            "action": "actions",
            "utility": "utilities",
            "run": "context_tools",
        }[role]
        return ToolCall(toolset=toolset, name=name, summary=token, role=role)


class _ToolsCliStub:
    """Stub external tools CLI — owns Turn.open/finish (never Agent._complete_task)."""

    def run_for_prompt(self, session: AgentSession, prompt: str) -> Turn.Guidance | None:
        tokens = _SlashManifest.tokens(prompt)
        if not tokens:
            return None
        action = " ".join(tokens)
        turn = session.mint_turn(action=action)
        for token in tokens:
            turn.append_tool(_SlashManifest.tool_call_for(token))
        turn.finish(subject=action)
        return turn.guidance


@dataclass
class _SessionGate:
    is_open: bool = False


@dataclass
class _LinkedAgentSlot:
    holder: object = field(default_factory=lambda: _UNLINKED)

    def take(self):
        taken = self.holder
        self.holder = _UNLINKED
        return taken

    def bind(self, agent) -> None:
        self.holder = agent


@dataclass
class _LogPath:
    filename: str = "agent-session.jsonl"

    def under(self, folder: Path) -> Path:
        return folder / self.filename


@dataclass
class _TurnClock:
    seq: int = 0

    def next_id(self) -> str:
        self.seq += 1
        return f"turn-{self.seq}"


class _FaultPolicy:
    """validation_error skips the task; other AgentFault kinds stop the run."""

    _SKIP = frozenset({"validation_error"})

    @classmethod
    def skips_task(cls, kind: str) -> bool:
        return kind in cls._SKIP


@dataclass
class _DrainGate:
    active: bool = False


class _TemplateInstantiator:
    @staticmethod
    def tasks_from(template: AgentTaskTemplate) -> list[AgentTask]:
        return [
            _TemplateInstantiator._task_from_prompt(prompt)
            for prompt in template.tasks
        ]

    @staticmethod
    def _task_from_prompt(prompt: str) -> AgentTask:
        return AgentTask(
            prompt=prompt,
            doer=AgentParticipant(type="doer", prompt=prompt),
        )


class _CompleteOutcome:
    PASS = "PASS"
    VALIDATION_ERROR = "validation_error"


class MultiRepoSessionError(RuntimeError):
    """Raised when an AgentSession would span more than one repo."""


class _DirtyBranchSwitchError(RuntimeError):
    """Raised when checkout would move a dirty tree onto another branch."""

    def __init__(self, current: str, wanted: str) -> None:
        self._current = current
        self._wanted = wanted
        super().__init__(
            f"Working tree has uncommitted changes on {current!r}; "
            f"not switching to {wanted!r}."
        )

    @property
    def current(self) -> str:
        return self._current

    @property
    def wanted(self) -> str:
        return self._wanted


def _default_primary_worktree(
    root: Path, branch: str = "main", repo: "Repo | None" = None
) -> "Repo.Worktree":
    return Repo.Worktree(path=root, branch=branch, repo=repo)


class _WorktreeBook:
    """In-memory worktree list for a Repo."""

    def __init__(self, trees: list[Repo.Worktree]) -> None:
        self._trees = list(trees)

    def as_list(self) -> list[Repo.Worktree]:
        return list(self._trees)

    def for_branch(self, branch: str) -> Repo.Worktree | None:
        wanted = (branch or "").strip()
        for tree in self._trees:
            if tree.branch == wanted:
                return tree
        return None

    def add(self, tree: Repo.Worktree) -> Path:
        existing = self.for_branch(tree.branch)
        if existing is not None and existing.path == tree.path:
            return existing.path
        if existing is not None:
            self._trees = [row for row in self._trees if row is not existing]
        self._trees.append(tree)
        return tree.path

    def remove_path(self, path: Path) -> None:
        self._trees = [tree for tree in self._trees if tree.path != path]

    def retag_primary(self, root: Path, branch: str, repo: "Repo | None" = None) -> None:
        if not self._trees:
            self._trees = [_default_primary_worktree(root, branch, repo=repo)]
            return
        primary = self._trees[0]
        self._trees[0] = Repo.Worktree(
            path=primary.path, branch=branch, repo=repo or primary.repo
        )

    def replace_all(self, trees: list[Repo.Worktree]) -> None:
        self._trees = list(trees)

    def primary(self) -> Repo.Worktree | None:
        return self._trees[0] if self._trees else None


class _SessionRegistry:
    """Name → AgentSession index for one primary repo."""

    def __init__(self) -> None:
        self._by_name: dict[str, AgentSession] = {}

    def normalize_key(self, name: str) -> str:
        return (name or "").strip()

    def key_for(self, session: AgentSession) -> str:
        key = self.normalize_key(str(session.name or ""))
        if not key:
            raise ValueError("agent session requires a name")
        return key

    def put(self, session: AgentSession) -> None:
        self._by_name[self.key_for(session)] = session

    def all(self) -> list[AgentSession]:
        return list(self._by_name.values())

    def named(self, name: str) -> "AgentSession | None":
        return self._lookup(self.normalize_key(name))

    def _lookup(self, key: str) -> "AgentSession | None":
        if key not in self._by_name:
            return None
        return self._by_name[key]


@dataclass
class Commit:
    """One commit on a Branch — sha, subject, and note refs (stub OK)."""

    sha: str
    subject: str = ""
    notes: dict[str, str] = field(default_factory=dict)

    def note(self, ref: str, text: str) -> None:
        self.notes[ref] = _NoteBody.merge(self.read_notes(ref), text)

    def read_notes(self, ref: str) -> str:
        if ref not in self.notes:
            return ""
        return self.notes[ref]


class _NoteBody:
    """Pure merge of chat-note lines onto a prior note body."""

    @staticmethod
    def merge(prior: str, text: str) -> str:
        lines = [line for line in prior.splitlines() if line.strip()]
        cleaned = text.strip()
        if cleaned and cleaned not in lines:
            lines.append(cleaned)
        return "\n".join(lines)


class _TagKey:
    """Pure normalize for annotated-tag names."""

    @staticmethod
    def normalize(name: str) -> str:
        return (name or "").strip()


class _TagLines:
    """Pure append of a unique line onto an annotated-tag message."""

    @staticmethod
    def append_unique(existing_text: str, line: str) -> str:
        text = (line or "").strip()
        if not text:
            return existing_text
        existing = [
            row for row in existing_text.splitlines() if row.strip()
        ]
        if text not in existing:
            existing.append(text)
        return "\n".join(existing)


class AnnotatedTag:
    """Append-oriented annotated tag — chat/{branch.name} paths."""

    def __init__(self) -> None:
        self._messages: dict[str, str] = {}

    def write(self, name: str, message: str) -> None:
        key = _TagKey.normalize(name)
        if not key:
            return
        self._messages[key] = message

    def read(self, name: str) -> str:
        return self._lookup(_TagKey.normalize(name))

    def list(self, prefix: str = "") -> dict[str, str]:
        if not prefix:
            return dict(self._messages)
        return {
            key: tag_message
            for key, tag_message in self._messages.items()
            if key.startswith(prefix)
        }

    def append_line(self, name: str, line: str) -> None:
        self.write(name, _TagLines.append_unique(self.read(name), line))

    def _lookup(self, key: str) -> str:
        if key not in self._messages:
            return ""
        return self._messages[key]


class _CommitMint:
    """Stub sha sequence for in-memory Branch.commit."""

    def __init__(self) -> None:
        self._seq = 0

    def next_sha(self) -> str:
        self._seq += 1
        return f"stub-{self._seq:04d}"


class Branch:
    """Named branch — checkout, commit, chats, push/merge, worktree."""

    __slots__ = (
        "_repo",
        "_name",
        "_agent_session",
        "_chats",
        "_head",
        "_pushed",
        "_merged",
        "_mint",
    )

    def __init__(self, repo: Repo, name: str) -> None:
        self._repo = repo
        self._name = name
        self._agent_session: AgentSession | None = None
        self._chats: list[str] = []
        self._head: Commit | None = None
        self._pushed = False
        self._merged = False
        self._mint = _CommitMint()

    @property
    def name(self) -> str:
        return self._name

    @property
    def head(self) -> Commit | None:
        return self._head

    @property
    def chats(self) -> list[str]:
        return list(self._chats)

    @property
    def pushed(self) -> bool:
        return self._pushed

    def checkout_or_create(self) -> Branch:
        self._repo.checkout_or_create(self.name)
        return self

    @property
    def worktree(self) -> Repo.Worktree:
        found = self._repo._worktrees.for_branch(self.name)
        if found is not None:
            found.bind_repo(self._repo)
            return found
        return _default_primary_worktree(self._repo.root, self.name, repo=self._repo)

    @property
    def agent_session(self) -> AgentSession | None:
        return self._agent_session

    def _bind_agent_session(self, session: AgentSession) -> None:
        self._agent_session = session

    def _record_chat(self, path: str) -> None:
        text = (path or "").strip()
        if text and text not in self._chats:
            self._chats.append(text)

    def commit(
        self, paths: list[str] | None = None, message: str = ""
    ) -> Commit:
        close = Commit(sha=self._mint.next_sha(), subject=message or "commit")
        self._head = close
        self._repo.set_dirty(False)
        return close

    def push(self) -> None:
        self._pushed = True

    def merge_from(self, branch: "Branch | str | None" = None) -> None:
        self._merged = True

    def _persist_chats(self, commit: Commit) -> None:
        """Finish Work Session — note paths on commit; append chat/{branch}."""
        tag_name = f"chat/{self.name}"
        for path in self._chats:
            commit.note("refs/notes/chats", path)
            self._repo._tags.append_line(tag_name, path)


@dataclass
class Status:
    """Project board status option name."""

    name: str


@dataclass
class Issue:
    """In-memory GitHub issue — create, status, type, theme, close."""

    number: int
    title: str
    body: str
    url: str = ""
    state: "Status | None" = None
    issue_type: str = ""
    labels: list[str] = field(default_factory=list)
    closed: bool = False
    _repo: "Repo | None" = field(default=None, repr=False, compare=False)

    @property
    def repo(self) -> "Repo | None":
        return self._repo

    def close(self) -> Issue:
        shelf = self._require_shelf()
        shelf.mark_closed(self.number)
        self.closed = True
        return self

    def set_status(self, state_name: str) -> Issue:
        shelf = self._require_shelf()
        project = shelf.project
        if project is None:
            raise RuntimeError("attach_project before setting ticket status")
        status = project.state_named(state_name)
        shelf.record_status(self.number, state_name)
        self.state = status
        return self

    def set_type(self, name: str) -> Issue:
        text = (name or "").strip()
        if text:
            self.issue_type = text
        return self

    def add_label(self, name: str) -> Issue:
        label = (name or "").strip()
        if label and label not in self.labels:
            self.labels.append(label)
        return self

    def add_theme(self, theme: str) -> Issue:
        slug = (theme or "").strip()
        if slug.lower().startswith("theme:"):
            slug = slug.split(":", 1)[1].strip()
        if slug:
            self.add_label(f"theme:{slug}")
        return self

    def _require_shelf(self) -> "_IssueShelf":
        repo = self._repo
        if repo is None:
            raise RuntimeError("Issue requires a repo")
        return repo._issue_shelf


@dataclass
class Project:
    """In-memory GitHub project — status options and issues collection."""

    owner: str = "local"
    number: int = 1
    _repo: "Repo | None" = field(default=None, repr=False, compare=False)
    _statuses: tuple[str, ...] = ("Backlog", "In Progress", "Done")

    def bind_repo(self, repo: Repo) -> None:
        self._repo = repo

    @property
    def issues(self) -> dict[int, Issue]:
        if self._repo is None:
            return {}
        return self._repo._issue_shelf.as_dict()

    def state_named(self, name: str) -> Status:
        for option in self._statuses:
            if option.lower() == (name or "").strip().lower():
                return Status(name=option)
        raise ValueError(f"unknown project status {name!r}")

    def status_option_names(self) -> list[str]:
        return list(self._statuses)


class _IssueShelf:
    """Issue create/lookup and project attachment for one Repo."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo
        self._by_number: dict[int, Issue] = {}
        self._status_by_number: dict[int, str] = {}
        self._closed: set[int] = set()
        self._project: "Project | None" = None

    @property
    def project(self) -> "Project | None":
        return self._project

    def attach_project(self, project: Project) -> None:
        self._project = project
        project.bind_repo(self._repo)

    def as_dict(self) -> dict[int, Issue]:
        return dict(self._by_number)

    def status_map(self) -> dict[int, str]:
        return dict(self._status_by_number)

    def record_status(self, number: int, state_name: str) -> None:
        self._status_by_number[number] = state_name

    def mark_closed(self, number: int) -> None:
        self._closed.add(number)

    def create(self, title: str, body: str) -> Issue:
        number = self._next_number()
        issue = Issue(
            number=number,
            title=title,
            body=body,
            url=f"memory://issue/{number}",
            _repo=self._repo,
        )
        self._by_number[number] = issue
        return issue

    def lookup(self, ref: "str | int") -> Issue:
        number = self._validated_number(ref)
        if number not in self._by_number:
            raise LookupError(f"GitHub issue not found: {ref}")
        return self._by_number[number]

    def _next_number(self) -> int:
        if not self._by_number:
            return 1
        return max(self._by_number.keys()) + 1

    def _validated_number(self, ref: "str | int") -> int:
        return self._parse_issue_number(ref)

    @staticmethod
    def _parse_issue_number(ref: "str | int") -> int:
        if isinstance(ref, int):
            return ref
        text = (ref or "").strip()
        if text.startswith("#"):
            text = text[1:]
        if text.isdigit():
            return int(text)
        match = re.search(r"(\d+)$", text)
        if match is None:
            raise LookupError(f"GitHub issue not found: {ref}")
        return int(match.group(1))


class Repo:
    """Primary-repo surface for AgentSession — InMemory by default for vanilla BDD."""

    @dataclass
    class Worktree:
        """One checkout of a repository (primary clone or linked worktree)."""

        path: Path
        branch: str
        repo: Any = field(default=None, repr=False, compare=False)

        def bind_repo(self, repo: Repo) -> None:
            self.repo = repo

        def create_sibling(self, path: "str | Path") -> Repo.Worktree:
            """Sibling worktree beside primary clone — never inside primary."""
            repo = self.repo
            if repo is None:
                raise RuntimeError("Worktree.create_sibling requires a repo")
            sibling = Path(path)
            primary = Path(repo.root)
            if sibling == primary or repo._path_is_under(sibling, primary):
                raise ValueError(
                    "sibling worktree must not be inside the primary clone"
                )
            sibling.mkdir(parents=True, exist_ok=True)
            default = repo.default_branch
            repo._worktrees.retag_primary(primary, default, repo=repo)
            repo._branch = default
            tree = Repo.Worktree(path=sibling, branch=self.branch, repo=repo)
            repo._worktrees.add(tree)
            return tree

        def remove(self) -> None:
            """Teardown a linked sibling worktree — never the primary clone."""
            repo = self.repo
            if repo is None:
                return
            primary = Path(repo.root)
            target = Path(self.path)
            if target == primary:
                return
            repo._worktrees.remove_path(target)

    def __init__(
        self,
        root: Path,
        primary_worktree: Worktree,
        *,
        memory: bool = True,
        default_branch: str = "main",
        default_session_name: str = "default",
        issue_shelf: "_IssueShelf | None" = None,
    ) -> None:
        self._assign_identity(root, memory, default_branch, default_session_name)
        self._install_worktrees(primary_worktree)
        self._install_issue_shelf(issue_shelf)

    def _assign_identity(
        self,
        root: Path,
        memory: bool,
        default_branch: str,
        default_session_name: str,
    ) -> None:
        self._root = root
        self._default_branch = default_branch
        self._default_session_name = default_session_name
        self._memory = memory
        self._branch = default_branch
        self._branch_names: set[str] = {default_branch}
        self._dirty = False
        self._tags = AnnotatedTag()

    def _install_issue_shelf(
        self, issue_shelf: "_IssueShelf | None"
    ) -> None:
        self._issue_shelf = (
            issue_shelf if issue_shelf is not None else _IssueShelf(self)
        )

    def _install_worktrees(self, primary_worktree: Worktree) -> None:
        primary_worktree.bind_repo(self)
        self._worktrees = _WorktreeBook([primary_worktree])
        self._sessions = _SessionRegistry()

    @property
    def root(self) -> Path:
        return self._root

    @property
    def default_branch(self) -> str:
        return self._default_branch

    @property
    def default_session_name(self) -> str:
        return self._default_session_name

    @property
    def current_branch(self) -> str:
        return self._branch

    @property
    def agent_sessions(self) -> list[AgentSession]:
        return self._sessions.all()

    def branch_named(self, name: str) -> Branch:
        return Branch(self, name)

    def put_agent_session(self, session: AgentSession) -> None:
        self._sessions.put(session)

    def is_dirty(self) -> bool:
        return bool(self._dirty)

    def set_dirty(self, dirty: bool = True) -> None:
        self._dirty = dirty

    def checkout_or_create(self, name: str) -> str:
        if self._already_on_branch(name):
            return name
        self._refuse_dirty_switch(name)
        self._switch_to_branch(name)
        return name

    def _already_on_branch(self, name: str) -> bool:
        return self.current_branch == name

    def _refuse_dirty_switch(self, name: str) -> None:
        if self.is_dirty():
            raise _DirtyBranchSwitchError(self.current_branch, name)

    def _switch_to_branch(self, name: str) -> None:
        self._record_branch_name(name)
        self._assign_current_branch(name)
        self._retag_primary_worktree(name)

    def _record_branch_name(self, name: str) -> None:
        self._branch_names.add(name)

    def _assign_current_branch(self, name: str) -> None:
        self._branch = name

    def _retag_primary_worktree(self, name: str) -> None:
        self._worktrees.retag_primary(self.root, name, repo=self)

    def _has_branch_name(self, name: str) -> bool:
        return name in self._branch_names

    def _memory_backed(self) -> bool:
        return bool(self._memory)

    def _default_branch_name(self) -> str:
        return str(self._default_branch)

    def _session_count(self) -> int:
        return len(self._sessions.all())

    def _worktree_count(self) -> int:
        return len(self._worktrees.as_list())

    def _primary_worktree_path(self) -> Path:
        primary = self._worktrees.primary()
        if primary is None:
            return Path(self._root)
        return Path(primary.path)

    @staticmethod
    def _path_is_under(path: Path, root: Path) -> bool:
        try:
            path.resolve().relative_to(root.resolve())
            return True
        except ValueError:
            return False


class InMemoryRepo(Repo):
    """Same public API as Repo; for specs — no git/gh on PATH."""

    def __init__(
        self,
        root: Path,
        primary_worktree: Repo.Worktree,
        **_kwargs: Any,
    ) -> None:
        super().__init__(root, primary_worktree, memory=True)


class _SessionStateCodec:
    """Pure encode/extract/assign for session folder state."""

    def encode(self, session: AgentSession) -> dict[str, Any]:
        state_fields: dict[str, Any] = {
            "name": session.name,
            "contextRoot": str(session.context_root),
        }
        if session.branch is not None:
            state_fields["branch"] = session.branch.name
        return state_fields

    def extract(self, state_fields: dict[str, Any]) -> tuple[str, str]:
        root_text = ""
        if "contextRoot" in state_fields:
            root_text = str(state_fields["contextRoot"])
        branch_name = ""
        if "branch" in state_fields:
            branch_name = str(state_fields["branch"]).strip()
        return root_text, branch_name

    def assign(
        self,
        session: AgentSession,
        *,
        context_root: Path | None,
        branch_name: str,
    ) -> None:
        if context_root is not None:
            session.context_root = context_root
        if branch_name and session.repo is not None and session.branch is None:
            session.branch = session.repo.branch_named(branch_name)


class _SessionStateFile:
    filename: str = "session-state.json"

    def path_under(self, folder: Path) -> Path:
        return folder / self.filename

    def write_state(self, folder: Path, state_fields: dict[str, Any]) -> None:
        target = self.path_under(folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(state_fields, indent=2), encoding="utf-8")

    def read_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def has_state_file(self, folder: Path) -> bool:
        return self.path_under(folder).is_file()

    def read_text(self, folder: Path) -> str | None:
        if not self.has_state_file(folder):
            return None
        try:
            return self.read_file(self.path_under(folder))
        except OSError:
            return None

    def parse_state(self, text: str | None) -> dict[str, Any] | None:
        if not text:
            return None
        try:
            state_fields = json.loads(text)
        except json.JSONDecodeError:
            return None
        return state_fields if isinstance(state_fields, dict) else None


class _OpenLogFields:
    """Pure builder for AgentSessionLog open fields."""

    def build(self, session: AgentSession) -> dict[str, Any]:
        fields: dict[str, Any] = {
            "name": session.name,
            "contextRoot": str(session.context_root),
            "startedAt": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        }
        if session.branch is not None:
            fields["branch"] = session.branch.name
            fields["worktreePath"] = str(session.branch.worktree.path)
        return fields


class _SessionStore:
    """I/O collaborator for AgentSession folder, state file, and open log."""

    def __init__(
        self,
        state_file: _SessionStateFile | None = None,
        state_codec: _SessionStateCodec | None = None,
        open_fields: _OpenLogFields | None = None,
        *,
        path_type: type[Path] = Path,
    ) -> None:
        self._state_file = state_file or _SessionStateFile()
        self._state_codec = state_codec or _SessionStateCodec()
        self._open_fields = open_fields or _OpenLogFields()
        self._path_type = path_type

    def ensure_folder(self, folder: Path) -> None:
        folder.mkdir(parents=True, exist_ok=True)

    def folder_exists(self, folder: Path) -> bool:
        return folder.exists()

    def persist(self, session: AgentSession) -> None:
        self.ensure_folder(session.folder)
        self._state_file.write_state(
            session.folder, self._state_codec.encode(session)
        )

    def restore(self, session: AgentSession) -> None:
        text = self._state_file.read_text(session.folder)
        state_fields = self._state_file.parse_state(text)
        if not state_fields:
            return
        root_text, branch_name = self._state_codec.extract(state_fields)
        context_root = self._path_type(root_text) if root_text else None
        self._state_codec.assign(
            session, context_root=context_root, branch_name=branch_name
        )

    def emit_open_log(self, session: AgentSession) -> None:
        session.log.open(**self._open_fields.build(session))


@dataclass
class _BranchBinder:
    """Checkout session/{name} and attach Branch + Worktree on the session."""

    def bind(self, session: AgentSession) -> None:
        repo = session.repo
        if repo is None:
            return
        branch_name = self._branch_name_for(session)
        branch = repo.branch_named(branch_name)
        branch.checkout_or_create()
        branch._bind_agent_session(session)
        session.branch = branch
        repo.put_agent_session(session)

    @staticmethod
    def _branch_name_for(session: AgentSession) -> str:
        if session.branch is not None and session.branch.name:
            return session.branch.name
        return f"session/{session.name}"


@dataclass
class Workspace:
    """IDE entry: path + repos → pick primary Repo → AgentSessions."""

    @dataclass
    class PathOverride:
        """Workspace path override for a tool fidelity."""

        tool: str
        fidelity: str
        path: str

    path: Path
    repos: list[Repo] = field(default_factory=list)
    path_overrides: list[PathOverride] = field(default_factory=list)
    primary_repo: Repo | None = None

    def lookup_path(self, tool: str, fidelity: str) -> Path | None:
        for row in self.path_overrides:
            if row.tool == tool and row.fidelity == fidelity:
                return Path(row.path)
        return None

    def upsert_path(self, tool: str, fidelity: str, path: str | Path) -> None:
        normalized = str(path)
        self.path_overrides = [
            row
            for row in self.path_overrides
            if not (row.tool == tool and row.fidelity == fidelity)
        ]
        self.path_overrides.append(
            Workspace.PathOverride(tool=tool, fidelity=fidelity, path=normalized)
        )

    def open(
        self,
        name: str | None = None,
        *,
        context_root: Path | None = None,
        open_existing: bool = False,
    ) -> AgentSession:
        self._refuse_multi_repo_session()
        session = self._build_session(name, context_root)
        self._start_session(session, open_existing=open_existing)
        return session

    def _build_session(
        self, name: str | None, context_root: Path | None
    ) -> AgentSession:
        repo = self._require_primary_repo()
        session_name = (name or "").strip() or repo.default_session_name
        folder = Path(repo.root) / ".agent_sessions" / session_name
        root = (
            Path(context_root)
            if context_root is not None
            else self._resolve_context_root(repo)
        )
        return AgentSession(
            name=session_name,
            folder=folder,
            context_root=root,
            repo=repo,
        )

    def _start_session(self, session: AgentSession, *, open_existing: bool) -> None:
        if open_existing:
            session.open_existing()
        else:
            session.open()

    def _require_primary_repo(self) -> Repo:
        if self.primary_repo is not None:
            return self.primary_repo
        if len(self.repos) == 1:
            return self.repos[0]
        raise MultiRepoSessionError(
            "AgentSession requires one primary repo; set Workspace.primary_repo"
        )

    def _resolve_context_root(self, repo: Repo) -> Path:
        override = self.lookup_path("agent", "contextRoot")
        if override is not None:
            return override
        return Path(repo.root)

    def _refuse_multi_repo_session(self) -> None:
        if len(self.repos) <= 1:
            return
        if self.primary_repo is not None:
            return
        raise MultiRepoSessionError(
            "refuse multi-repo AgentSession span — attach to one primary repo only"
        )


@dataclass
class AgentSession:
    """Named session folder, context root, branch/worktree, and orchestration log."""

    name: str
    folder: Path
    context_root: Path = field(default_factory=Path)
    goal: str = ""
    repo: Repo | None = None
    branch: Branch | None = None
    log: AgentSessionLog = field(default_factory=AgentSessionLog)
    turns: list[Turn] = field(default_factory=list)
    open_turn: Turn | None = None
    decisions: Any = field(default=None, repr=False)
    _agent_slot: _LinkedAgentSlot = field(default_factory=_LinkedAgentSlot, repr=False)
    _gate: _SessionGate = field(default_factory=_SessionGate, repr=False)
    _log_path: _LogPath = field(default_factory=_LogPath, repr=False)
    _turn_clock: _TurnClock = field(default_factory=_TurnClock, repr=False)
    _store: _SessionStore = field(default_factory=_SessionStore, repr=False)
    _branch_binder: _BranchBinder = field(default_factory=_BranchBinder, repr=False)

    def __post_init__(self) -> None:
        if self._context_root_unset():
            self.context_root = self.folder.parent
        if self.log.path is None:
            self.log.path = self._log_path.under(self.folder)
        if self.decisions is None:
            from record_decisions.record_decisions import RecordDecisions

            self.decisions = RecordDecisions()

    def _context_root_unset(self) -> bool:
        return not self.context_root or str(self.context_root) == "."

    @property
    def path(self) -> Path:
        return self.context_root

    @property
    def eval_log_dir(self) -> Path:
        return self.folder / "logs"

    @property
    def turn(self) -> Turn:
        if self.open_turn is None or not self.open_turn.hanging:
            return self.mint_turn()
        return self.open_turn

    def mint_turn(self, *, action: str = "") -> Turn:
        turn = Turn(session=self, name=self._turn_clock.next_id())
        turn.open(action=action)
        self.open_turn = turn
        return turn

    @property
    def agent(self):
        return self._agent_slot.holder

    @agent.setter
    def agent(self, linked_agent) -> None:
        self._agent_slot.holder = linked_agent

    @property
    def worktree(self) -> Repo.Worktree | None:
        if self.branch is None:
            return None
        return self.branch.worktree

    def open(self) -> None:
        if self._session_is_open():
            return
        self._store.ensure_folder(self.folder)
        self._branch_binder.bind(self)
        self._store.persist(self)
        self._store.emit_open_log(self)
        self._gate.is_open = True

    def open_existing(self) -> None:
        """Open Existing — restore from disk; dirty worktree preserved."""
        if self._session_is_open():
            return
        if not self._store.folder_exists(self.folder):
            self._store.ensure_folder(self.folder)
        else:
            self._store.restore(self)
        self._branch_binder.bind(self)
        self._store.persist(self)
        self._store.emit_open_log(self)
        self._gate.is_open = True

    def close(self) -> None:
        if not self._session_is_open():
            return
        self._tear_down_session()

    def finish(self, outcome: str = "") -> Commit:
        """Finish work session — land close commit, persist chats, teardown."""
        chat_paths = self._gather_chat_paths()
        self._stop_agent_for_finish()
        self._finish_hanging_turns(outcome)
        close_commit = self._land_close_commit(outcome)
        self._persist_gathered_chats(close_commit, chat_paths)
        self._publish_and_teardown()
        return close_commit

    def _session_is_open(self) -> bool:
        return bool(self._gate.is_open)

    def _tear_down_session(self) -> None:
        self.log.close(name=self.name)
        self._agent_slot.take().close()
        self._gate.is_open = False

    def _stop_agent_for_finish(self) -> None:
        self._agent_slot.holder.close()

    def _finish_hanging_turns(self, outcome: str) -> None:
        subject = (outcome or "").strip() or "close"
        for turn in self.turns:
            if turn.hanging:
                turn.finish(subject=subject)

    def _land_close_commit(self, outcome: str) -> Commit:
        branch = self._require_branch()
        message = (outcome or "").strip() or f"finish {self.name}"
        return branch.commit([str(self.folder)], message)

    def _persist_gathered_chats(
        self, close_commit: Commit, chat_paths: list[str]
    ) -> None:
        branch = self._require_branch()
        for path in chat_paths:
            branch._record_chat(path)
        branch._persist_chats(close_commit)

    def _gather_chat_paths(self) -> list[str]:
        return _ChatPathGatherer().from_session(self)

    def _publish_and_teardown(self) -> None:
        branch = self._require_branch()
        branch.push()
        branch.merge_from()
        self._remove_sibling_if_ready(branch)

    def _remove_sibling_if_ready(self, branch: Branch) -> None:
        if not branch.pushed:
            return
        tree = branch.worktree
        repo = self.repo
        if repo is None:
            return
        if Path(tree.path) == Path(repo.root):
            return
        tree.remove()

    def _require_branch(self) -> Branch:
        branch = self.branch
        if branch is None:
            raise RuntimeError("AgentSession.finish requires a bound Branch")
        return branch


class _ChatPathGatherer:
    """Collect transcript paths from session participants (stub OK)."""

    def from_session(self, session: AgentSession) -> list[str]:
        paths: list[str] = []
        agent = session.agent
        if agent is _UNLINKED or agent is None:
            return paths
        for participant in self._participants_of(agent):
            path = self._path_for(participant)
            if path and path not in paths:
                paths.append(path)
        return paths

    def _participants_of(self, agent: object) -> list[AgentParticipant]:
        known = getattr(agent, "_known_tasks", None)
        tasks = known() if callable(known) else []
        if not tasks:
            current = getattr(agent, "current_task", None)
            completed = list(getattr(agent, "completed_tasks", []) or [])
            backlog = list(getattr(agent, "backlog", []) or [])
            tasks = ([current] if current is not None else []) + completed + backlog
        rows: list[AgentParticipant] = []
        for task in tasks:
            if task is None:
                continue
            rows.extend(_ParticipantOps.of_task(task))
        return rows

    def _path_for(self, participant: AgentParticipant) -> str:
        chat = participant.chat
        if chat is None or not chat.chat_id:
            return ""
        return str(_TranscriptPath().under_chat(chat))


@dataclass
class Agent:
    """Orchestrates doer → judge → human for each task on the backlog."""

    _healer_returns_handoff: bool = field(default=False, init=False, repr=False)
    session: AgentSession | None = None
    backlog: list[AgentTask] = field(default_factory=list)
    current_task: AgentTask | None = field(default=None)
    completed_tasks: list[AgentTask] = field(default_factory=list)
    template_store: AgentTaskTemplateStore = field(
        default_factory=AgentTaskTemplateStore
    )
    _stub_verdicts: _StubSeries = field(default_factory=_StubSeries, repr=False)
    _stub_human_feedback: _StubSeries = field(default_factory=_StubSeries, repr=False)
    _stub_faults: _StubSeries = field(default_factory=_StubSeries, repr=False)
    _tools_cli: _ToolsCliStub = field(default_factory=_ToolsCliStub, repr=False)
    _drain: _DrainGate = field(default_factory=_DrainGate, repr=False)
    last_guidance: Turn.Guidance | None = field(default=None, repr=False)
    healer: Any = field(default=None, repr=False)
    last_phase_name: str = field(default="", repr=False)
    last_phase_result: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if self.healer is None:
            from agent.healer import Healer

            self.healer = Healer()

    @property
    def log(self):
        if self.session is None:
            raise RuntimeError("Agent has no session")
        return self.session.log

    def add_tasks(self, tasks: list[AgentTask]) -> None:
        for task in tasks:
            task.state = "Backlog"
            self.backlog.append(task)
        self.log.add_tasks(tasks)

    def clear_backlog(self) -> None:
        self.backlog = []
        self.log.clear_backlog()

    def load_template(self, name: str) -> None:
        template = self.template_store.load(name)
        self.add_tasks(self._instantiate_tasks(template))

    def close(self) -> None:
        self.current_task = None

    def kick(self, participant: AgentParticipant | None = None) -> None:
        target = participant or self._default_kick_target()
        target.state = "idle"
        self.log.kick(target)

    def run_next_task(self) -> None:
        self._guard_phase("run_next_task", self._run_next_task_body, handoff=False)

    def _run_next_task_body(self) -> None:
        self._ensure_session()
        if self.current_task is None:
            self._launch_next()
        if self.current_task is None:
            return
        while self.current_task is not None:
            self._run_current_task_cycle()

    def run_task_queue(self) -> None:
        """Drain the backlog until empty or a workflow fault stops the process."""
        self._guard_phase("run_backlog", self._run_task_queue_body, handoff=False)

    def _run_task_queue_body(self) -> None:
        self._ensure_session()
        self._drain.active = True
        try:
            while True:
                if self.current_task is None:
                    self._launch_next()
                if self.current_task is None:
                    return
                while self.current_task is not None:
                    self._run_current_task_cycle()
        finally:
            self._drain.active = False

    def _run_current_task_cycle(self) -> None:
        if self._apply_stub_fault_if_any():
            return
        self._launch_doer()
        self._wait_doer()
        task = self._require_current_task()
        if task.judge is None:
            self._finish_task_pass()
            return
        self._launch_judge()
        result = self._wait_verdict()
        if result == "PASS":
            self._finish_task_pass()
            return
        self._retry_after_fail()

    def _apply_stub_fault_if_any(self) -> bool:
        kind = self._stub_faults.pop("")
        if not kind:
            return False
        self._raise(AgentFault(kind=self._as_fault_kind(kind), detail=kind))
        return True

    def _as_fault_kind(self, kind: str) -> _AgentFaultKind:
        if kind == "validation_error":
            return "validation_error"
        if kind == "parse_failed":
            return "parse_failed"
        if kind == "judge_fail_limit":
            return "judge_fail_limit"
        return "invariant"

    def _finish_task_pass(self) -> None:
        if self._human_requested_retry():
            return
        self._complete_task(outcome=_CompleteOutcome.PASS)
        self._healer_eval(phase="task_complete", trigger="success")

    def _retry_after_fail(self) -> None:
        task = self._require_current_task()
        self.kick(task.doer)
        self._reset_participants_for_retry(task)

    def _human_requested_retry(self) -> bool:
        task = self._require_current_task()
        if task.human is None:
            return False
        self._launch_human()
        self._wait_human()
        feedback = self._next_human_feedback()
        if not feedback:
            return False
        self.log.human_feedback(feedback)
        self.kick(task.doer)
        self._reset_participants_for_retry(task)
        return True

    def _reset_participants_for_retry(self, task: AgentTask) -> None:
        _ParticipantOps.mark_idle(_ParticipantOps.of_task(task))

    def _default_kick_target(self) -> AgentParticipant:
        task = self._require_current_task()
        return task.doer

    def _ensure_session(self) -> None:
        session = self._require_session()
        session.open()
        session.agent = self

    def _require_session(self) -> AgentSession:
        if self.session is None:
            raise RuntimeError("Agent requires an open AgentSession before run")
        return self.session

    def _instantiate_tasks(self, template: AgentTaskTemplate) -> list[AgentTask]:
        return _TemplateInstantiator.tasks_from(template)

    def _launch_next(self) -> None:
        if self._participant_in_flight():
            raise RuntimeError("refuse launch_next while participant in flight")
        if not self.backlog:
            return
        task = self.backlog.pop(0)
        task.state = "In Progress"
        task.index = len(self.completed_tasks) + 1
        self.current_task = task
        self.log.launch_next(task)

    def _launch_doer(self) -> None:
        task = self._require_current_task()
        participant = task.doer
        self._send(participant)
        self.log.send(participant, prompt=participant.prompt)
        self._await_accept(participant)
        self.log.accepted(participant)
        self._run_tools_cli_for(participant)

    def _wait_doer(self) -> None:
        task = self._require_current_task()
        participant = task.doer
        self._await_done(participant)
        self.log.done(participant)

    def _run_tools_cli_for(self, participant: AgentParticipant) -> None:
        session = self._require_session()
        self.last_guidance = self._tools_cli.run_for_prompt(
            session, participant.prompt
        )

    def _launch_judge(self) -> None:
        self._send_accepted_if_present(self._require_current_task().judge)

    def _wait_verdict(self) -> str:
        task = self._require_current_task()
        participant = task.judge
        if participant is None:
            return "PASS"
        result = self._await_verdict(participant)
        self.log.verdict(participant, result)
        return result

    def _launch_human(self) -> None:
        self._send_accepted_if_present(self._require_current_task().human)

    def _wait_human(self) -> None:
        participant = self._require_current_task().human
        for target in self._present_participants(participant):
            self._await_done(target)
            self.log.done(target)

    def _send_accepted_if_present(self, participant: AgentParticipant | None) -> None:
        for target in self._present_participants(participant):
            self._send_and_log_accept(target)

    def _present_participants(
        self, participant: AgentParticipant | None
    ) -> list[AgentParticipant]:
        return _ParticipantOps.present(participant)

    def _send_and_log_accept(self, participant: AgentParticipant) -> None:
        self._send(participant)
        self.log.send(participant, prompt=participant.prompt)
        self._await_accept(participant)
        self.log.accepted(participant)
        self._run_tools_cli_for(participant)

    def _complete_task(self, *, outcome: str) -> None:
        task = self._require_current_task()
        self.log.complete_task(task, outcome=outcome)
        task.state = "Done"
        self.completed_tasks.append(task)
        self.current_task = None
        self._advance_queue()

    def _advance_queue(self) -> None:
        if not self._drain.active:
            return
        if self.backlog:
            self._launch_next()

    def _raise(self, fault: AgentFault) -> None:
        self.log.append_fault(fault)
        self._healer_eval(
            phase="agent_fault",
            trigger="exception",
            error=RuntimeError(f"{fault.kind}: {fault.detail}"),
        )
        if _FaultPolicy.skips_task(fault.kind):
            self._skip_current_task(detail=fault.detail or fault.kind)
            return
        raise fault

    def _healer_run_context(self) -> Any:
        from agent.healer import HealerRunContext

        session = self.session
        if session is None:
            return HealerRunContext(agent_type=type(self).__name__)

        def _task_row(task: AgentTask) -> dict[str, Any]:
            row: dict[str, Any] = {
                "prompt": task.prompt,
                "state": task.state,
                "doer_prompt": task.doer.prompt,
            }
            if task.judge is not None:
                row["judge_prompt"] = task.judge.prompt
            return row

        log_path = session.log.path
        return HealerRunContext(
            agent_type=type(self).__name__,
            session_name=session.name,
            session_goal=getattr(session, "goal", "") or "",
            workspace=str(getattr(session, "context_root", "") or ""),
            context_root=str(session.context_root or ""),
            session_folder=str(session.folder or ""),
            log_path=str(log_path) if log_path else "",
            backlog_prompts=[task.prompt for task in self.backlog],
            current_task=_task_row(self.current_task) if self.current_task else {},
            completed_tasks=[_task_row(task) for task in self.completed_tasks],
        )

    def _healer_log_records(self) -> list[dict[str, Any]]:
        if self.session is None:
            return []
        return list(self.session.log._records)

    def note_phase_result(self, phase: str, result: str) -> None:
        self.last_phase_name = phase
        self.last_phase_result = str(result or "")

    def _guard_phase(self, phase: str, fn, *, handoff: bool | None = None):
        """Run *fn*; on exception forward to healer ``eval`` before re-raising."""
        from agent.healer import HealerStop, format_healer_fix_handoff

        return_handoff = (
            self._healer_returns_handoff if handoff is None else handoff
        )
        try:
            return fn()
        except HealerStop:
            raise
        except AgentFault:
            raise
        except Exception as exc:
            report = self._healer_eval(
                phase=phase,
                trigger="exception",
                error=exc,
                stop_on_exception=False,
            )
            if report.stop_recommended:
                raise HealerStop(report) from exc
            if return_handoff:
                return format_healer_fix_handoff(report)
            raise exc

    def _healer_eval(
        self,
        *,
        phase: str,
        trigger: str = "success",
        error: BaseException | None = None,
        stop_on_exception: bool = False,
    ):
        from agent.healer import HealerFailure, HealerStop, log_healer_eval

        if self.healer is None:
            raise HealerFailure(f"agent has no healer — cannot eval phase {phase!r}")
        records = self._healer_log_records()
        kinds = [row["kind"] for row in records]
        report = self.healer.eval(
            kinds,
            phase=phase,
            trigger=trigger,  # type: ignore[arg-type]
            error=error,
            backlog_remaining=len(self.backlog),
            completed_count=len(self.completed_tasks),
            log_records=records,
            run_context=self._healer_run_context(),
            last_phase_result=self.last_phase_result,
        )
        if report is None:
            raise HealerFailure(f"healer eval returned no report for phase {phase!r}")
        if self.session is not None:
            log_healer_eval(self.log, report)
        if stop_on_exception and report.stop_recommended and trigger == "exception":
            raise HealerStop(report) from error
        return report

    def eval_healer(
        self,
        *,
        phase: str = "manual",
        trigger: str = "manual",
        error: BaseException | None = None,
        stop_on_exception: bool = False,
    ):
        """Public entry — healer ``eval`` against current session log."""
        return self._healer_eval(
            phase=phase,
            trigger=trigger,
            error=error,
            stop_on_exception=stop_on_exception,
        )

    def _skip_current_task(self, *, detail: str) -> None:
        task = self._require_current_task()
        self.log.validation_error(detail)
        self.log.complete_task(
            task, outcome=_CompleteOutcome.VALIDATION_ERROR, detail=detail
        )
        task.state = "Done"
        self.completed_tasks.append(task)
        self.current_task = None
        self._advance_queue()

    def _participant_in_flight(self) -> bool:
        task = self.current_task
        if task is None:
            return False
        return _ParticipantOps.any_in_flight(_ParticipantOps.of_task(task))

    def _require_current_task(self) -> AgentTask:
        if self.current_task is None:
            raise RuntimeError("no current task")
        return self.current_task

    def _send(self, participant: AgentParticipant) -> None:
        participant.state = "sending"
        participant.state = "awaiting_accept"

    def _await_accept(self, participant: AgentParticipant) -> None:
        if participant.state != "awaiting_accept":
            raise RuntimeError(f"expected awaiting_accept, got {participant.state}")
        participant.state = "running"

    def _await_done(self, participant: AgentParticipant) -> None:
        if participant.state != "running":
            raise RuntimeError(f"expected running, got {participant.state}")
        participant.state = "done"

    def _await_verdict(self, participant: AgentParticipant) -> str:
        participant.state = "awaiting_verdict"
        result = self._next_verdict()
        participant.state = "done"
        return result

    def _next_verdict(self) -> str:
        return self._stub_verdicts.pop("PASS")

    def _next_human_feedback(self) -> str:
        return self._stub_human_feedback.pop("")


class _ChildHandle:
    """One non-blocking child runtime for a doer or judge prompt role."""

    _pids = itertools.count(10_000)

    def __init__(
        self,
        *,
        role: str,
        prompt: str,
        session_name: str,
        context_root: str,
    ) -> None:
        self._role = role
        self._prompt = prompt
        self._session_name = session_name
        self._context_root = context_root
        self._pid = next(self._pids)
        self._alive = True
        self._accepted = False
        self._finished = False

    @property
    def role(self) -> str:
        return self._role

    @property
    def session_name(self) -> str:
        return self._session_name

    @property
    def context_root(self) -> str:
        return self._context_root

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def alive(self) -> bool:
        return self._alive

    def accept(self) -> None:
        if not self._alive:
            raise RuntimeError(f"child for {self._role} already stopped")
        self._accepted = True

    def finish(self) -> None:
        if not self._alive:
            raise RuntimeError(f"child for {self._role} already stopped")
        self._finished = True

    def stop(self) -> None:
        self._alive = False
        self._finished = True


class _ChildRoster:
    """Tracks live SubAgent children keyed by participant identity."""

    def __init__(self) -> None:
        self._by_id: dict[int, _ChildHandle] = {}
        self._launch_order: list[str] = []

    def register(self, participant: AgentParticipant, handle: _ChildHandle) -> None:
        self._by_id[id(participant)] = handle
        self._launch_order.append(handle.role)

    def handle_for(self, participant: AgentParticipant) -> _ChildHandle | None:
        key = id(participant)
        if key not in self._by_id:
            return None
        return self._by_id[key]

    def launched_roles(self) -> list[str]:
        return list(self._launch_order)

    def live_handles(self) -> list[_ChildHandle]:
        return [handle for handle in self._by_id.values() if handle.alive]

    def stop_all(self) -> None:
        for handle in list(self._by_id.values()):
            handle.stop()
        self._by_id.clear()


@dataclass
class SubAgent(Agent):
    """Agent subtype — non-blocking child per doer/judge role; first two-role path."""

    _children: _ChildRoster = field(default_factory=_ChildRoster, repr=False)

    def close(self) -> None:
        self._tear_down_children()
        super().close()

    def _tear_down_children(self) -> None:
        self._children.stop_all()

    def _launch(self, participant: AgentParticipant) -> _ChildHandle:
        """Start a non-blocking child for the participant role; returns immediately."""
        session = self._require_session()
        handle = _ChildHandle(
            role=participant.type,
            prompt=participant.prompt,
            session_name=session.name,
            context_root=str(session.context_root),
        )
        self._children.register(participant, handle)
        return handle

    def _send(self, participant: AgentParticipant) -> None:
        participant.state = "sending"
        self._launch(participant)
        participant.state = "awaiting_accept"

    def _await_accept(self, participant: AgentParticipant) -> None:
        if participant.state != "awaiting_accept":
            raise RuntimeError(f"expected awaiting_accept, got {participant.state}")
        handle = self._require_child(participant)
        handle.accept()
        participant.state = "running"

    def _await_done(self, participant: AgentParticipant) -> None:
        if participant.state != "running":
            raise RuntimeError(f"expected running, got {participant.state}")
        handle = self._require_child(participant)
        handle.finish()
        participant.state = "done"

    def _await_verdict(self, participant: AgentParticipant) -> str:
        handle = self._require_child(participant)
        participant.state = "awaiting_verdict"
        result = self._next_verdict()
        handle.finish()
        participant.state = "done"
        return result

    def _require_child(self, participant: AgentParticipant) -> _ChildHandle:
        handle = self._children.handle_for(participant)
        if handle is None:
            raise RuntimeError(f"no child launched for {participant.type}")
        return handle


@dataclass
class AIChatInstance:
    """CLI chat boundary — stubbed run_prompt for CliAgent transcript-watcher specs."""

    chat_id: str = ""
    pid: Optional[int] = None
    alive: bool = True
    workspace_path: str = ""
    session_name: str = ""
    context_root: str = ""
    model: str = ""
    mode: str = ""
    _runs: list[str] = field(default_factory=list, repr=False)
    _continues: int = field(default=0, repr=False)

    @property
    def runs(self) -> list[str]:
        return list(self._runs)

    @property
    def continue_count(self) -> int:
        return self._continues

    def run_prompt(self, prompt: str) -> None:
        self._runs.append(prompt)

    def continue_chat(self) -> None:
        """Nudge a live chat after kick — not named resume (CE hard rule)."""
        self._continues += 1

    def stop(self) -> None:
        """Mark the runtime dead and clear the stub PID — no zombie chat."""
        self.alive = False
        self.pid = None


class _TranscriptPath:
    """Vendor transcript location from chat workspace + chat id."""

    def under_chat(self, chat: AIChatInstance) -> Path:
        return Path(chat.workspace_path) / "agent-transcripts" / f"{chat.chat_id}.jsonl"


class _JsonlTranscript:
    """File-backed agent-runtime transcript lines."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path

    @property
    def path(self) -> Optional[Path]:
        return self._path

    def track(self, path: Path) -> None:
        self._path = path

    def _readable(self) -> bool:
        return self._path is not None and self._path.is_file()

    def _read_raw(self) -> str:
        return self._path.read_text(encoding="utf-8", errors="replace")

    def _line_count_of(self, text: str) -> int:
        count = 0
        for _ in text.splitlines():
            count += 1
        return count

    def _parse_rows(self, text: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows

    @property
    def line_count(self) -> int:
        if not self._readable():
            return 0
        return self._line_count_of(self._read_raw())

    @property
    def user_count(self) -> int:
        count = 0
        for row in self._iter_rows():
            if "role" in row and row["role"] == "user":
                count += 1
        return count

    def rows_newest_first(self) -> list[dict[str, Any]]:
        return list(reversed(list(self._iter_rows())))

    def _iter_rows(self) -> list[dict[str, Any]]:
        if not self._readable():
            return []
        return self._parse_rows(self._read_raw())


class _PollTiming:
    """Injected clock/sleep for transcript polling."""

    def __init__(
        self,
        *,
        sleep=time.sleep,
        clock=time.time,
        poll_s: float = 0.05,
    ) -> None:
        self._sleep = sleep
        self._clock = clock
        self._poll_s = poll_s

    def clock(self) -> float:
        return self._clock()

    def sleep_poll(self) -> None:
        self._sleep(self._poll_s)

    def deadline_after(self, seconds: float) -> float:
        return self._clock() + max(0.0, seconds)


class _AssistantText:
    """Extract assistant text from flat or Cursor-nested jsonl rows."""

    def from_row(self, row: dict[str, Any]) -> str:
        content = self._content_of(row)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return self._text_blocks(content)
        if content is None:
            return ""
        return str(content)

    def _content_of(self, row: dict[str, Any]) -> Any:
        if "content" in row:
            return row["content"]
        if "message" not in row:
            return None
        message = row["message"]
        if not isinstance(message, dict):
            return None
        if "content" not in message:
            return None
        return message["content"]

    def _text_blocks(self, content: list[Any]) -> str:
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if "type" not in block or block["type"] != "text":
                continue
            if "text" not in block:
                continue
            parts.append(str(block["text"]))
        return "\n".join(parts)


class _VerdictReader:
    """PASS/FAIL from assistant rows — shape only, not LLM quality."""

    def __init__(self) -> None:
        self._text = _AssistantText()

    def from_transcript(self, transcript: _JsonlTranscript) -> str:
        for row in transcript.rows_newest_first():
            if "role" not in row or row["role"] != "assistant":
                continue
            upper = self._text.from_row(row).upper()
            if "FAIL" in upper:
                return "FAIL"
            if "PASS" in upper:
                return "PASS"
        return ""


class AgentRuntimeTranscriptWatcher:
    """Polls AIChatInstance transcripts — accept, growth-then-quiet, verdict."""

    def __init__(
        self,
        *,
        path: Optional[Path] = None,
        sleep=time.sleep,
        clock=time.time,
        poll_s: float = 0.05,
    ) -> None:
        self._file = _JsonlTranscript(path)
        self._timing = _PollTiming(sleep=sleep, clock=clock, poll_s=poll_s)
        self._verdicts = _VerdictReader()

    def track(self, path: Path) -> None:
        self._file.track(path)

    @property
    def path(self) -> Path | None:
        return self._file.path

    @property
    def user_count(self) -> int:
        return self._file.user_count

    def _await_user_turn(self, accept_seconds: float, *, alive: bool) -> None:
        before = self._file.user_count
        deadline = self._timing.deadline_after(accept_seconds)
        while self._timing.clock() < deadline:
            if self._file.user_count > before:
                return
            self._timing.sleep_poll()
        if self._file.user_count > before:
            return
        if not alive:
            raise AIChatFault(
                kind="not_accepted",
                detail="accept timeout and agent runtime process is not alive",
            )
        raise AIChatFault(
            kind="not_accepted",
            detail="accept timeout with no user turn on transcript",
        )

    def _await_growth_then_quiet(
        self, stall_seconds: float, quiet_seconds: float
    ) -> None:
        before = self._file.line_count
        deadline = self._timing.deadline_after(stall_seconds)
        while self._timing.clock() < deadline:
            if self._file.line_count > before:
                self._wait_until_quiet(quiet_seconds=quiet_seconds, deadline=deadline)
                return
            self._timing.sleep_poll()
        if self._file.line_count > before:
            self._wait_until_quiet(quiet_seconds=quiet_seconds, deadline=deadline)
            return
        raise AIChatFault(
            kind="stall",
            detail=f"transcript did not grow within {stall_seconds}s",
        )

    def _wait_until_quiet(self, *, quiet_seconds: float, deadline: float) -> None:
        last = self._file.line_count
        stable_at = self._timing.clock()
        while self._timing.clock() < deadline:
            now = self._file.line_count
            if now != last:
                last = now
                stable_at = self._timing.clock()
            elif self._timing.clock() - stable_at >= quiet_seconds:
                return
            self._timing.sleep_poll()

    def _read_verdict(self) -> str:
        return self._verdicts.from_transcript(self._file)


@dataclass
class _CliWorkspaceBind:
    """Bound worktree path for CliAgent chat/runtime fence."""

    path: str = ""
    pending: bool = False

    def clear(self) -> None:
        self.path = ""
        self.pending = False

    def bind_worktree(self, session: AgentSession) -> None:
        worktree = session.worktree
        if worktree is None:
            self.pending = True
            self.path = ""
            return
        self.pending = False
        self.path = str(worktree.path)

    def lacks_worktree(self, session: AgentSession) -> bool:
        if self.pending:
            return True
        return session.worktree is None


@dataclass
class _CliChatFactory:
    """Mint AIChatInstance per CliAgentParticipant when missing."""

    _ids: Any = field(default_factory=lambda: itertools.count(1), repr=False)

    def ensure(self, participant: AgentParticipant) -> AIChatInstance:
        if participant.chat is not None:
            return participant.chat
        chat = AIChatInstance(
            chat_id=f"{participant.type}-{next(self._ids)}",
            alive=True,
            pid=1,
        )
        participant.chat = chat
        return chat

    def bind_context(
        self,
        participant: AgentParticipant,
        *,
        session: AgentSession,
        workspace_path: str,
    ) -> AIChatInstance:
        chat = participant.chat
        if chat is None:
            raise RuntimeError(
                f"CliAgent participant {participant.type} has no chat to bind"
            )
        chat.session_name = session.name
        chat.context_root = str(session.context_root)
        if workspace_path:
            chat.workspace_path = workspace_path
        return chat

    def release(self, participant: AgentParticipant) -> None:
        chat = participant.chat
        if chat is not None:
            chat.stop()
        participant.chat = None

    def release_all(self, participants: list[AgentParticipant]) -> None:
        for participant in participants:
            self.release(participant)


_ARGV_SOFT_LIMIT = 7000


@dataclass
class _CliTaskFilePlan:
    """Pure path + body for a long-prompt task file."""

    path: Path
    body: str


class _CliTaskFile:
    """Plan (pure) and write (I/O) for CliAgent task files."""

    def plan_for(self, context_root: Path, prompt: str) -> Optional[_CliTaskFilePlan]:
        if len(prompt) < _ARGV_SOFT_LIMIT:
            return None
        path = Path(context_root) / ".context" / "cli-agent-task.txt"
        return _CliTaskFilePlan(path=path, body=prompt)

    def write(self, plan: _CliTaskFilePlan) -> Path:
        plan.path.parent.mkdir(parents=True, exist_ok=True)
        plan.path.write_text(plan.body, encoding="utf-8")
        return plan.path

    @staticmethod
    def present(plan: Optional[_CliTaskFilePlan]) -> list[_CliTaskFilePlan]:
        if plan is None:
            return []
        return [plan]


class _CliScratch:
    """Orchestration temps CliAgent wrote — never durable session artifacts."""

    _CONTEXT_TEMPS = frozenset(
        {
            "cli-agent-task.txt",
            "cli-agent-judge.txt",
            "cli-agent-put-back.txt",
        }
    )

    def wipe(self, *, context_root: Path) -> None:
        ctx = Path(context_root) / ".context"
        if not ctx.is_dir():
            return
        for name in self._CONTEXT_TEMPS:
            path = ctx / name
            if path.is_file():
                path.unlink()


@dataclass
class CliAgent(Agent):
    """CLI Agent — bind worktree/chat, launch doer/judge, transcript watcher."""

    accept_seconds: float = 30.0
    stall_seconds: float = 600.0
    quiet_seconds: float = 3.0
    max_fails: int = 2
    fail_count: int = 0
    watch: AgentRuntimeTranscriptWatcher = field(
        default_factory=AgentRuntimeTranscriptWatcher
    )
    _paths: _TranscriptPath = field(default_factory=_TranscriptPath, repr=False)
    _workspace: _CliWorkspaceBind = field(
        default_factory=_CliWorkspaceBind, repr=False
    )
    _chats: _CliChatFactory = field(default_factory=_CliChatFactory, repr=False)
    _task_files: _CliTaskFile = field(default_factory=_CliTaskFile, repr=False)
    _scratch: _CliScratch = field(default_factory=_CliScratch, repr=False)

    @property
    def workspace_root(self) -> str:
        return self._workspace.path

    @property
    def pending_session(self) -> bool:
        if self.session is None:
            return True
        return self._workspace.lacks_worktree(self.session)

    def kick(self, participant: AgentParticipant | None = None) -> None:
        target = participant or self._default_kick_target()
        chat = target.chat
        if chat is not None:
            chat.continue_chat()
        target.state = "idle"
        self.log.kick(target)

    def close_agents(self) -> None:
        """Stop live doer/judge CLI processes and clear chat bindings."""
        self._chats.release_all(self._bound_participants())
        self._workspace.clear()

    def cleanup(self) -> None:
        """Remove orchestration temps; keep durable session artifacts."""
        session = self.session
        if session is None:
            return
        self._scratch.wipe(context_root=Path(session.context_root))

    def close_cli_session(self) -> None:
        """Close Cli Agent Session — stop runtimes, wipe temps, then session.close."""
        self.close_agents()
        self.cleanup()
        self._require_session().close()

    def close(self) -> None:
        self.close_agents()
        self.cleanup()
        super().close()

    def _bound_participants(self) -> list[AgentParticipant]:
        participants: list[AgentParticipant] = []
        for task in self._known_tasks():
            participants.extend(_ParticipantOps.of_task(task))
        return participants

    def _known_tasks(self) -> list[AgentTask]:
        tasks: list[AgentTask] = []
        if self.current_task is not None:
            tasks.append(self.current_task)
        tasks.extend(self.completed_tasks)
        tasks.extend(self.backlog)
        return tasks

    def _ensure_session(self) -> None:
        session = self._require_session()
        session.open()
        session.agent = self
        self._install_cli_log(session)
        self._bind_workspace_root()

    def _install_cli_log(self, session: AgentSession) -> None:
        if isinstance(session.log, CliAgentSessionLog):
            return
        upgraded = CliAgentSessionLog()
        upgraded._adopt_from(session.log)
        session.log = upgraded

    def _bind_workspace_root(self) -> None:
        session = self._require_session()
        if session.worktree is None:
            self._workspace.bind_worktree(session)
            return
        self._workspace.bind_worktree(session)

    def _pending_session(self) -> bool:
        return self.pending_session

    def _persist_prompt_to_task_file(self, prompt: str) -> Optional[Path]:
        plan = self._task_files.plan_for(
            Path(self._require_session().context_root), prompt
        )
        return self._write_planned_task_file(plan)

    def _write_planned_task_file(
        self, plan: Optional[_CliTaskFilePlan]
    ) -> Optional[Path]:
        written = None
        for planned_file in _CliTaskFile.present(plan):
            written = self._task_files.write(planned_file)
        return written

    def _ensure_chat(self, participant: AgentParticipant) -> AIChatInstance:
        return self._chats.ensure(participant)

    def _bind_chat_context(self, participant: AgentParticipant) -> None:
        session = self._require_session()
        self._chats.bind_context(
            participant,
            session=session,
            workspace_path=self._workspace.path,
        )
        self.log.bind_chat_context(participant)

    def _launch_doer(self) -> None:
        if self._pending_session():
            raise RuntimeError(
                "refuse durable CliAgent launch on main before branch worktree exists"
            )
        task = self._require_current_task()
        participant = task.doer
        self._ensure_chat(participant)
        self._bind_chat_context(participant)
        self._persist_prompt_to_task_file(participant.prompt)
        self._send(participant)
        self.log.run_chat(self._require_chat(participant), participant.prompt)
        self.log.send(participant, prompt=participant.prompt)
        self._await_accept(participant)
        self.log.accepted(participant)
        self._run_tools_cli_for(participant)

    def _wait_doer(self) -> None:
        task = self._require_current_task()
        participant = task.doer
        self._await_done(participant)
        self.log.wait_doer()
        self.log.done(participant)

    def _launch_judge(self) -> None:
        for participant in self._present_participants(
            self._require_current_task().judge
        ):
            self._launch_bound_judge(participant)

    def _launch_bound_judge(self, participant: AgentParticipant) -> None:
        self._ensure_chat(participant)
        self._bind_chat_context(participant)
        self._send(participant)
        chat = self._require_chat(participant)
        self.log.run_chat(chat, participant.prompt)
        self.log.launch_judge(participant)
        self.log.send(participant, prompt=participant.prompt)
        self._await_accept(participant)
        self.log.accepted(participant)
        self._run_tools_cli_for(participant)

    def _finish_task_pass(self) -> None:
        self.fail_count = 0
        if self._human_requested_retry():
            return
        self._complete_task(outcome=_CompleteOutcome.PASS)

    def _retry_after_fail(self) -> None:
        self.fail_count += 1
        if self.fail_count >= self.max_fails:
            self._raise(
                AgentFault(
                    kind="judge_fail_limit",
                    detail=f"judge FAIL x{self.max_fails}",
                )
            )
            return
        task = self._require_current_task()
        self.kick(task.doer)
        self._reset_participants_for_retry(task)

    def _auto_kick_stalled_doer(self) -> None:
        task = self.current_task
        if task is None:
            return
        doer = task.doer
        if doer.state != "done":
            return
        if task.state != "In Progress":
            return
        self.kick(doer)

    def _send(self, participant: AgentParticipant) -> None:
        participant.state = "sending"
        chat = self._require_chat(participant)
        chat.run_prompt(participant.prompt)
        self.watch.track(self._paths.under_chat(chat))
        participant.state = "awaiting_accept"

    def _await_accept(self, participant: AgentParticipant) -> None:
        if participant.state != "awaiting_accept":
            raise RuntimeError(f"expected awaiting_accept, got {participant.state}")
        chat = self._require_chat(participant)
        self.watch._await_user_turn(self.accept_seconds, alive=chat.alive)
        participant.state = "running"

    def _await_done(self, participant: AgentParticipant) -> None:
        if participant.state != "running":
            raise RuntimeError(f"expected running, got {participant.state}")
        self.watch._await_growth_then_quiet(self.stall_seconds, self.quiet_seconds)
        participant.state = "done"

    def _await_verdict(self, participant: AgentParticipant) -> str:
        participant.state = "awaiting_verdict"
        self.watch._await_growth_then_quiet(self.stall_seconds, self.quiet_seconds)
        result = self.watch._read_verdict()
        participant.state = "done"
        return result

    def _require_chat(self, participant: AgentParticipant) -> AIChatInstance:
        if participant.chat is None:
            raise RuntimeError(f"CliAgent participant {participant.type} has no chat")
        return participant.chat
