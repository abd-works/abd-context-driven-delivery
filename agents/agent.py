"""Agent — backlog and participant orchestration (stubbed runtime hooks)."""
from __future__ import annotations

import json
import itertools
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional, override

from harness.harness_tool import prompt
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool

_ParticipantType = Literal["doer", "judge", "human", "healer"]
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
    """One doer, judge, human, or healer role."""

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
    kit: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.doer.prompt:
            self.doer.prompt = self.prompt
        if self.doer.type != "doer":
            self.doer.type = "doer"

    @classmethod
    def from_spec(cls, spec: dict) -> AgentTask:
        """Build one backlog task from a serializable spec (tools CLI / all agent types)."""
        if not isinstance(spec, dict):
            raise TypeError("task spec must be a dict")
        doer_prompt = str(spec.get("doer_prompt") or spec.get("prompt") or "").strip()
        if not doer_prompt:
            raise ValueError("task spec requires doer_prompt or prompt")
        task = _TemplateInstantiator._task_from_prompt(doer_prompt)
        judge_prompt = str(spec.get("judge_prompt") or "").strip()
        if not judge_prompt:
            judge_val = spec.get("judge")
            if isinstance(judge_val, str) and judge_val.strip():
                judge_prompt = judge_val.strip()
        if judge_prompt:
            task.judge = AgentParticipant(type="judge", prompt=judge_prompt)
        if spec.get("human"):
            human_prompt = str(spec.get("human_prompt") or "human check").strip()
            task.human = AgentParticipant(type="human", prompt=human_prompt)
        for key in ("tools", "actions", "human", "judge", "index"):
            if key in spec and key not in task.kit:
                if key == "judge" and task.judge is not None:
                    continue
                task.kit[key] = spec[key]
        return task

    def to_spec(self) -> dict[str, Any]:
        """Round-trip spec for tools CLI and JobQueue persistence."""
        row: dict[str, Any] = {
            "doer_prompt": self.doer.prompt or self.prompt,
            "prompt": self.doer.prompt or self.prompt,
        }
        if self.judge is not None and self.judge.prompt:
            row["judge_prompt"] = self.judge.prompt
        if self.human is not None:
            row["human"] = True
            if self.human.prompt:
                row["human_prompt"] = self.human.prompt
        for key, value in self.kit.items():
            if key not in row:
                row[key] = value
        return row


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

    def run_stopped(self, reason: str) -> None:
        self._append("run_stopped", reason=reason)

    def recovery(self, **fields: Any) -> None:
        self._append("recovery", **fields)

    def error(self, detail: str, **fields: Any) -> None:
        self._append("error", detail=detail, **fields)

    @override
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
    SKIP = "skip"


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


def _default_healer():
    from agents.healer import Healer

    return Healer()


@dataclass
class Agent:
    """Orchestrates doer → judge → healer for each task on the backlog."""

    _healer_returns_handoff: bool = field(default=False, init=False, repr=False)
    session: AgentSession | None = None
    backlog: list[AgentTask] = field(default_factory=list)
    current_task: AgentTask | None = field(default=None)
    completed_tasks: list[AgentTask] = field(default_factory=list)
    template_store: AgentTaskTemplateStore = field(
        default_factory=AgentTaskTemplateStore
    )
    _tools_cli: _ToolsCliStub = field(default_factory=_ToolsCliStub, repr=False)
    _drain: _DrainGate = field(default_factory=_DrainGate, repr=False)
    last_guidance: Turn.Guidance | None = field(default=None, repr=False)
    healer: Any = field(default_factory=_default_healer, repr=False)
    last_phase_name: str = field(default="", repr=False)
    last_phase_result: str = field(default="", repr=False)
    max_fails: int = 3
    fail_count: int = 0
    _healer_tried: bool = field(default=False, init=False, repr=False)
    _last_healer_output: str = field(default="", init=False, repr=False)
    _workspace: Path = field(default_factory=Path.cwd, repr=False)
    _repo_ref: Repo | None = field(default=None, repr=False)
    _healer_role: AgentParticipant | None = field(default=None, init=False, repr=False)

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

    def add_tasks_from_specs(self, specs: list[dict]) -> list[AgentTask]:
        """Append tasks built from serializable specs — same entry point for every agent type."""
        tasks = [self._task_from_spec(spec) for spec in list(specs or [])]
        if tasks:
            self.add_tasks(tasks)
        return tasks

    def load_backlog_from_specs(self, specs: list[dict]) -> list[AgentTask]:
        """Replace backlog from specs (reload from persisted backlog)."""
        self.backlog = []
        return self.add_tasks_from_specs(specs)

    def _task_from_spec(self, spec: dict) -> AgentTask:
        ticket_number = spec.get("ticket_number")
        if ticket_number is None or not str(ticket_number).strip():
            return AgentTask.from_spec(spec)
        from agents.workflow import WorkTicket

        work = WorkTicket.from_ref(self._repo(), int(ticket_number))
        judge_prompt = str(spec.get("judge_prompt") or "").strip()
        doer_prompt = str(spec.get("doer_prompt") or spec.get("prompt") or "").strip()
        instructions = str(spec.get("instructions") or "").strip()
        prompt_text = (
            doer_prompt or _ticket_doer_prompt(work, instructions=instructions)
        ).strip()
        if not prompt_text:
            raise RuntimeError(
                "ticket task requires doer_prompt, prompt, or ticket body"
            )
        task = AgentTask.from_spec(
            {"doer_prompt": prompt_text, "judge_prompt": judge_prompt}
        )
        task.tickets = [work]
        return task

    def _bind_session(self, session: AgentSession) -> None:
        self.session = session
        session.agent = self

    def _known_tasks(self) -> list[AgentTask]:
        tasks: list[AgentTask] = []
        if self.current_task is not None:
            tasks.append(self.current_task)
        tasks.extend(self.completed_tasks)
        tasks.extend(self.backlog)
        return tasks

    def _participants_on_tasks(self) -> list[AgentParticipant]:
        participants: list[AgentParticipant] = []
        for task in self._known_tasks():
            participants.extend(_ParticipantOps.of_task(task))
        if self._healer_role is not None:
            participants.append(self._healer_role)
        return participants

    def _repo(self) -> Repo:
        if self._repo_ref is None:
            root = self._workspace.resolve()
            self._repo_ref = InMemoryRepo(root, Repo.Worktree(root, "main"))
        return self._repo_ref

    def open_session(self, name: str, *, goal: str = "") -> AgentSession:
        """Open an AgentSession — same for every agent subtype."""
        session_name = name.strip()
        repo = self._repo()
        ws = Workspace(path=self._workspace, repos=[repo], primary_repo=repo)
        folder = Path(repo.root) / ".agent_sessions" / session_name
        session = ws.open(
            name=session_name,
            context_root=self._workspace,
            open_existing=folder.is_dir(),
        )
        if goal:
            session.goal = goal
        self._bind_session(session)
        return session

    def clear_backlog(self) -> None:
        self.backlog = []
        self.log.clear_backlog()

    def load_task_backlog_template(self, name: str) -> None:
        template = self.template_store.load(name)
        self.add_tasks(_TemplateInstantiator.tasks_from(template))

    def close(self) -> None:
        """Stop owned runtimes and clear chat bindings."""
        for participant in self._participants_on_tasks():
            chat = participant.chat
            if chat is not None:
                chat.stop()
                participant.chat = None

    def kick(self, participant: AgentParticipant | None = None) -> None:
        target = participant or self._default_kick_target()
        chat = target.chat
        if chat is not None:
            chat.continue_chat()
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

    def run_backlog(self) -> None:
        """Drain the backlog until empty or a workflow fault stops the process."""
        self._guard_phase("run_backlog", self._run_backlog_body, handoff=False)

    def queue_status(self) -> str:
        """In progress / Done / Left — public readout of the Agent queue."""
        def _label(task: AgentTask) -> str:
            return (task.prompt or task.doer.prompt).strip() or "(empty)"

        lines = ["---", "In progress:"]
        current = self.current_task
        if current is None:
            lines.append("  (none)")
        else:
            role = "doer"
            if current.judge is not None and current.judge.state in (
                "sending",
                "awaiting_accept",
                "running",
                "awaiting_verdict",
            ):
                role = "judge"
            lines.append(f"  {_label(current)} [{role}]")
        lines.append("Done:")
        if not self.completed_tasks:
            lines.append("  (none)")
        else:
            for index, task in enumerate(self.completed_tasks, 1):
                lines.append(f"  {index}. {_label(task)}")
        lines.append("Left:")
        if not self.backlog:
            lines.append("  (none)")
        else:
            for index, task in enumerate(self.backlog):
                lines.append(f"  {index}. {_label(task)}")
        return "\n".join(lines)

    def _run_backlog_body(self) -> None:
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
        self._on_judge_fail()

    def _on_judge_fail(self) -> None:
        self.fail_count += 1
        if self.fail_count < self.max_fails:
            self._retry_after_fail()
            return
        if not self._healer_tried:
            self._healer_tried = True
            self._healer_eval(phase="task_complete", trigger="success")
            self._apply_healer_prompt_revisions()
            self._retry_after_fail()
            return
        self._give_up_on_judge_fail()

    def _give_up_on_judge_fail(self) -> None:
        self._skip_unhealed_task()

    def _finish_task_pass(self) -> None:
        if self._human_requested_retry():
            return
        self.fail_count = 0
        self._healer_tried = False
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
        for target in _ParticipantOps.present(participant):
            self._await_done(target)
            self.log.done(target)

    def _send_accepted_if_present(self, participant: AgentParticipant | None) -> None:
        for target in _ParticipantOps.present(participant):
            self._send_and_log_accept(target)

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
        self._advance_backlog()

    def _advance_backlog(self) -> None:
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
        from agents.healer import HealerRunContext

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
        from agents.healer import HealerStop, format_healer_fix_handoff

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
        from agents.healer import HealerFailure, HealerStop, log_healer_eval

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
            self._run_healer_runtime(report.healer_prompt)
        if stop_on_exception and report.stop_recommended and trigger == "exception":
            raise HealerStop(report) from error
        return report

    def _healer_participant(self) -> AgentParticipant:
        if self._healer_role is None:
            self._healer_role = AgentParticipant(type="healer", prompt="")
        return self._healer_role

    def _run_healer_runtime(self, prompt: str) -> None:
        """Send the healer prompt on the same runtime path as doer and judge."""
        participant = self._healer_participant()
        participant.prompt = prompt
        participant.state = "idle"
        self._send(participant)
        self.log.send(participant, prompt=prompt)
        self._await_accept(participant)
        self.log.accepted(participant)
        self._await_done(participant)
        self.log.done(participant)
        chat = participant.chat
        if isinstance(chat, SubAgentChatInstance):
            self._last_healer_output = chat._child_result

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
        self._advance_backlog()

    def _skip_unhealed_task(self) -> None:
        """Judge FAIL after retries and healer — advance backlog."""
        task = self._require_current_task()
        self.log.complete_task(
            task,
            outcome=_CompleteOutcome.SKIP,
            detail=f"judge FAIL; unhealed after {self.fail_count} try(s)",
        )
        task.state = "Done"
        self.fail_count = 0
        self._healer_tried = False
        self.completed_tasks.append(task)
        self.current_task = None
        self._advance_backlog()

    def _apply_healer_prompt_revisions(self) -> None:
        text = (self._last_healer_output or "").strip()
        if not text:
            return
        task = self.current_task
        if task is None:
            return
        doer_match = re.search(
            r"doer_prompt:\s*(.+?)(?=\njudge_prompt:|\Z)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        judge_match = re.search(
            r"judge_prompt:\s*(.+?)(?=\n(?:doer_prompt:|\d+\.|\Z))",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if doer_match:
            revised = doer_match.group(1).strip()
            if revised:
                task.doer.prompt = revised
                task.prompt = revised
        if judge_match and task.judge is not None:
            revised = judge_match.group(1).strip()
            if revised:
                task.judge.prompt = revised

    def _participant_in_flight(self) -> bool:
        task = self.current_task
        if task is None:
            return False
        return _ParticipantOps.any_in_flight(_ParticipantOps.of_task(task))

    def _require_current_task(self) -> AgentTask:
        if self.current_task is None:
            raise RuntimeError("no current task")
        return self.current_task

    def _bind_chat_context(
        self, participant: AgentParticipant, *, workspace_path: str = ""
    ) -> None:
        session = self._require_session()
        chat = self._require_runtime(participant)
        chat.session_name = session.name
        chat.context_root = str(session.context_root)
        if workspace_path:
            chat.workspace_path = workspace_path

    def _send(self, participant: AgentParticipant) -> None:
        participant.state = "sending"
        self._deliver_to_runtime(participant)
        participant.state = "awaiting_accept"

    def _await_accept(self, participant: AgentParticipant) -> None:
        if participant.state != "awaiting_accept":
            raise RuntimeError(f"expected awaiting_accept, got {participant.state}")
        self._accept_on_runtime(participant)
        participant.state = "running"

    def _await_done(self, participant: AgentParticipant) -> None:
        if participant.state != "running":
            raise RuntimeError(f"expected running, got {participant.state}")
        self._done_on_runtime(participant)
        participant.state = "done"

    def _await_verdict(self, participant: AgentParticipant) -> str:
        participant.state = "awaiting_verdict"
        result = self._require_runtime_alive(participant).verdict()
        participant.state = "done"
        return result

    def _require_runtime(self, participant: AgentParticipant) -> AIChatInstance:
        chat = participant.chat
        if chat is None:
            raise RuntimeError(
                f"participant {participant.type} has no chat runtime"
            )
        return chat

    def _require_runtime_alive(self, participant: AgentParticipant) -> AIChatInstance:
        chat = self._require_runtime(participant)
        if not chat.alive:
            raise RuntimeError(
                f"runtime for {participant.type} already stopped"
            )
        return chat

    def _runtime_class(self) -> type[AIChatInstance]:
        return AIChatInstance

    def _ensure_runtime(self, participant: AgentParticipant) -> None:
        if participant.chat is not None:
            return
        self._runtime_class().mint(participant, self._require_session())

    def _deliver_to_runtime(self, participant: AgentParticipant) -> None:
        self._ensure_runtime(participant)
        self._require_runtime(participant).run_prompt(participant.prompt)

    def _accept_on_runtime(self, participant: AgentParticipant) -> None:
        self._require_runtime_alive(participant)

    def _done_on_runtime(self, participant: AgentParticipant) -> None:
        self._require_runtime_alive(participant)

    def _next_human_feedback(self) -> str:
        return ""


@dataclass
class AIChatInstance:
    """Chat runtime boundary — one instance per participant; subtype = spawn target."""

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
    _pid_seq: ClassVar[Any] = itertools.count(1)

    @classmethod
    def mint(
        cls, participant: AgentParticipant, session: AgentSession
    ) -> AIChatInstance:
        pid = next(cls._pid_seq)
        chat = cls(
            chat_id=f"{participant.type}-{pid}",
            pid=pid,
            alive=True,
            session_name=session.name,
            context_root=str(session.context_root),
        )
        participant.chat = chat
        return chat

    @property
    def runs(self) -> list[str]:
        return list(self._runs)

    @property
    def continue_count(self) -> int:
        return self._continues

    def run_prompt(self, prompt: str) -> None:
        self._runs.append(prompt)

    def create_chat(self) -> str:
        return self.chat_id

    def list_chats(self) -> list[str]:
        root = Path(self.workspace_path or ".") / "agent-transcripts"
        if not root.is_dir():
            return []
        return sorted(path.stem for path in root.glob("*.jsonl"))

    def continue_chat(self) -> None:
        """Nudge a live chat after kick — not named resume (CE hard rule)."""
        self._continues += 1

    def stop(self) -> None:
        """Mark the runtime dead — no zombie chat."""
        self.alive = False
        self.pid = None

    def _invoke_slash(self, command: str) -> None:
        return None

    def verdict(self) -> str:
        """Judge result from this runtime — in-process child has no transcript."""
        return "PASS"


class _SubAgentMailbox:
    """Inbox/outbox files so SubAgent.run_backlog can feed Cursor Task waiters."""

    def __init__(self, root: Path) -> None:
        self._root = root
        root.mkdir(parents=True, exist_ok=True)

    def send(self, role: str, prompt: str) -> None:
        out = self._root / f"{role}.out"
        if out.is_file():
            out.write_text("", encoding="utf-8")
        (self._root / f"{role}.in").write_text(prompt.strip() + "\n", encoding="utf-8")

    def wait(self, role: str, *, timeout_s: float = 1800.0) -> str:
        path = self._root / f"{role}.out"
        inbox = self._root / f"{role}.in"
        idle_deadline = time.time() + timeout_s
        while True:
            if path.is_file():
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    path.write_text("", encoding="utf-8")
                    return text
            held = ""
            if inbox.is_file():
                held = inbox.read_text(encoding="utf-8").strip()
            if held and held != "STOP":
                idle_deadline = time.time() + timeout_s
            elif time.time() >= idle_deadline:
                raise RuntimeError(f"sub-agent {role} produced no output")
            time.sleep(0.25)

    def stop(self) -> None:
        for role in ("doer", "judge", "healer"):
            (self._root / f"{role}.in").write_text("STOP\n", encoding="utf-8")


@dataclass
class SubAgentChatInstance(AIChatInstance):
    """Sub-agent chat runtime — one long-lived child per doer/judge/healer role."""

    role: str = ""
    cursor_agent_id: str = ""
    _child_result: str = field(default="", repr=False)
    _pid_seq: ClassVar[Any] = itertools.count(10_000)

    @classmethod
    @override
    def mint(
        cls, participant: AgentParticipant, session: AgentSession
    ) -> SubAgentChatInstance:
        chat = super().mint(participant, session)
        chat.role = participant.type  # type: ignore[attr-defined]
        chat.workspace_path = str(session.context_root)
        return chat  # type: ignore[return-value]

    @override
    def run_prompt(self, prompt: str) -> None:
        super().run_prompt(prompt)

    @override
    def verdict(self) -> str:
        result = self._child_result.strip().upper()
        if "FAIL" in result:
            return "FAIL"
        if "PASS" in result:
            return "PASS"
        return "PASS"


@dataclass
class CursorChatInstance(AIChatInstance):
    """Cursor IDE chat runtime — create-chat, spawn cursor-agent, transcript verdict."""

    _pid_seq: ClassVar[Any] = itertools.count(1)
    _cli: Any = field(default=None, repr=False)
    _proc: Any = field(default=None, repr=False)
    _transcript_home: Path | None = field(default=None, repr=False)
    _vendor_chat: bool = field(default=False, repr=False)

    def create_chat(self) -> str:
        if self._vendor_chat and self.chat_id:
            return self.chat_id
        cli = self._cli
        if cli is None:
            return self.chat_id
        workspace = self.workspace_path or "."
        self.chat_id = cli.create_chat(workspace)
        self._vendor_chat = True
        return self.chat_id

    def run_prompt(self, prompt: str) -> None:
        super().run_prompt(prompt)
        self._spawn_cli(prompt)

    def continue_chat(self) -> None:
        super().continue_chat()
        self._spawn_cli("")

    def stop(self) -> None:
        proc = self._proc
        if proc is not None:
            try:
                proc.terminate()
            except OSError:
                pass
            self._proc = None
        super().stop()

    def _invoke_slash(self, command: str) -> None:
        from primitives.tools.repo_paths import pythonpath_entries, repo_python, repo_root

        root = repo_root()
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries(root))
        fence = (
            f"sessionName: {self.session_name}\n"
            f"contextRoot: {self.context_root}\n"
            f"workspacePath: {self.workspace_path}\n"
        )
        subprocess.run(
            [repo_python(root), "-m", "tools", "run", "-"],
            input=fence + command.strip() + "\n",
            cwd=self.workspace_path or str(root),
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def verdict(self) -> str:
        path = _TranscriptPath(home=self._transcript_home).under_chat(self)
        result = _VerdictReader().from_transcript(_JsonlTranscript(path))
        if result not in ("PASS", "FAIL"):
            raise AIChatFault(
                kind="connection",
                detail="judge transcript had no PASS or FAIL",
            )
        return result

    def list_chats(self) -> list[str]:
        if self.chat_id:
            return [self.chat_id]
        return super().list_chats()

    def _spawn_cli(self, prompt: str) -> None:
        cli = self._cli
        if cli is None:
            return
        self.create_chat()
        argv = self._argv(prompt)
        proc = cli.spawn(argv, cwd=self.workspace_path or ".")
        self._proc = proc
        self.pid = getattr(proc, "pid", None)
        self.alive = True

    def _argv(self, prompt: str) -> list[str]:
        exe = self._cli.launcher()
        args = [exe, "--force", "--trust"]
        if self.chat_id:
            args.extend(["--resume", self.chat_id])
        if self.workspace_path:
            args.extend(["--workspace", self.workspace_path])
        if prompt:
            args.append(prompt)
        return args


class VscodeChatInstance(CursorChatInstance):
    """VS Code chat runtime — spawn target; waits live on CliAgent."""


class CliAgentParticipant(AgentParticipant):
    """CLI participant — one CursorChatInstance or VscodeChatInstance on chat."""


class _CursorCli:
    """cursor-agent create-chat and Popen — live CLI backend."""

    _chat_id = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        re.IGNORECASE,
    )

    def launcher(self) -> str:
        exe = shutil.which("cursor-agent") or shutil.which("agent")
        if exe is None:
            raise RuntimeError("cursor-agent not found on PATH")
        return exe

    def create_chat(self, workspace: str) -> str:
        completed = subprocess.run(
            [self.launcher(), "create-chat", "--workspace", str(workspace)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "cursor-agent create-chat failed "
                f"(exit {completed.returncode}).\n"
                f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
            )
        match = self._chat_id.search(completed.stdout or "")
        if match:
            return match.group(0)
        raise RuntimeError(
            "cursor-agent create-chat returned no chat id.\n"
            f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
        )

    def spawn(self, argv: list[str], *, cwd: str):
        return subprocess.Popen(list(argv), cwd=cwd or None)


_SUB_AGENT_STATE_FILE = "sub-agent-state.json"
_SUB_AGENT_DRAIN_ENV = "SUB_AGENT_DRAIN"


@dataclass
class SubAgent(Agent):
    """Delegates participant I/O to SubAgentChatInstance — _launch spawns child cards."""

    _healer_returns_handoff: bool = field(default=True, init=False, repr=False)
    _doer_runtime: SubAgentChatInstance | None = field(default=None, init=False, repr=False)
    _judge_runtime: SubAgentChatInstance | None = field(default=None, init=False, repr=False)
    _healer_runtime: SubAgentChatInstance | None = field(default=None, init=False, repr=False)

    @override
    def _runtime_class(self) -> type[AIChatInstance]:
        return SubAgentChatInstance

    @override
    def run_backlog(self) -> None:
        try:
            super().run_backlog()
        finally:
            self.persist()
            if (
                self.session is not None
                and self._runtime_live()
                and self.current_task is None
                and not self.backlog
            ):
                self.close()

    def run(self) -> str:
        """Slash ``run`` — enqueue already done; live returns immediately."""
        self._ensure_session()
        if self._runtime_live() and os.environ.get(_SUB_AGENT_DRAIN_ENV) != "1":
            self.persist()
            note = self._spawn_live_drain()
            return f"{self.queue_status()}\n\n{note}"
        self.run_backlog()
        return self.queue_status()

    def persist(self) -> None:
        session = self.session
        if session is None:
            return
        try:
            Path(session.folder).resolve().relative_to(self._workspace.resolve())
        except ValueError:
            if not self._runtime_live():
                return
        store = _ChatAgentPersistence
        payload: dict = {
            "session_name": session.name,
            "goal": session.goal,
            "backlog": store._serialize_backlog(self.backlog),
            "current": store._serialize_task(self.current_task),
            "completed": store._serialize_backlog(self.completed_tasks),
            "doer_runtime": self._runtime_row(self._doer_runtime),
            "judge_runtime": self._runtime_row(self._judge_runtime),
            "healer_runtime": self._runtime_row(self._healer_runtime),
        }
        target = self._queue_path(self._workspace, session.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, workspace: Path, session_name: str) -> SubAgent | None:
        path = cls._queue_path(workspace, session_name)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        engine = cls(_workspace=workspace)
        name = str(payload.get("session_name") or session_name).strip()
        engine.open_session(name, goal=str(payload.get("goal") or ""))
        store = _ChatAgentPersistence
        repo = engine._repo()
        engine.backlog = store._deserialize_tasks(payload.get("backlog") or [])
        for row, task in zip(payload.get("backlog") or [], engine.backlog):
            store._link_tickets(task, row, repo=repo)
        current_row = payload.get("current")
        current = store._deserialize_task(current_row)
        store._link_tickets(current, current_row, repo=repo)
        engine.current_task = current
        completed_rows = payload.get("completed") or []
        engine.completed_tasks = store._deserialize_tasks(completed_rows)
        for row, task in zip(completed_rows, engine.completed_tasks):
            store._link_tickets(task, row, repo=repo)
        engine._doer_runtime = cls._runtime_from_row(payload.get("doer_runtime"))
        engine._judge_runtime = cls._runtime_from_row(payload.get("judge_runtime"))
        engine._healer_runtime = cls._runtime_from_row(payload.get("healer_runtime"))
        engine._bind_loaded_runtimes()
        return engine

    @classmethod
    def run_drain_worker(cls, workspace: str, session_name: str) -> None:
        os.environ[_SUB_AGENT_DRAIN_ENV] = "1"
        ws = Path(workspace)
        engine = cls.load(ws, session_name)
        if engine is None:
            engine = cls(_workspace=ws)
            engine.open_session(session_name)
        engine.run_backlog()

    @staticmethod
    def _queue_path(workspace: Path, session_name: str) -> Path:
        return workspace / ".agent_sessions" / session_name / _SUB_AGENT_STATE_FILE

    @staticmethod
    def _runtime_row(chat: SubAgentChatInstance | None) -> dict | None:
        if chat is None:
            return None
        return {
            "chat_id": chat.chat_id,
            "cursor_agent_id": chat.cursor_agent_id,
            "pid": chat.pid,
            "alive": chat.alive,
            "role": chat.role,
        }

    @staticmethod
    def _runtime_from_row(row: object) -> SubAgentChatInstance | None:
        if not isinstance(row, dict):
            return None
        return SubAgentChatInstance(
            chat_id=str(row.get("chat_id") or ""),
            pid=row.get("pid"),
            alive=bool(row.get("alive", True)),
            cursor_agent_id=str(row.get("cursor_agent_id") or ""),
            role=str(row.get("role") or ""),
        )

    def _bind_loaded_runtimes(self) -> None:
        task = self.current_task
        if task is not None:
            if self._doer_runtime is not None:
                task.doer.chat = self._doer_runtime
            if task.judge is not None and self._judge_runtime is not None:
                task.judge.chat = self._judge_runtime
        if self._healer_runtime is not None:
            healer = self._healer_participant()
            healer.chat = self._healer_runtime

    def _spawn_live_drain(self) -> str:
        from primitives.tools.repo_paths import pythonpath_entries, repo_python, repo_root

        session = self._require_session()
        runtime = self._runtime_dir()
        runtime.mkdir(parents=True, exist_ok=True)
        pid_path = runtime / "drain.pid"
        if pid_path.is_file():
            try:
                existing = int(pid_path.read_text(encoding="utf-8").strip() or "0")
            except ValueError:
                existing = 0
            if existing > 0:
                try:
                    os.kill(existing, 0)
                except OSError:
                    pass
                else:
                    return f"Drain already running (pid {existing})."
        root = repo_root()
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries(root))
        env[_SUB_AGENT_DRAIN_ENV] = "1"
        log = runtime / "drain.log"
        creationflags = 0
        if os.name == "nt":
            creationflags = (
                subprocess.CREATE_NEW_PROCESS_GROUP
                | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
                | 0x00000008
                | 0x01000000
            )
        workspace = str(self._workspace)
        name = session.name

        def _start(flags: int) -> subprocess.Popen:
            log_file = log.open("ab")
            try:
                return subprocess.Popen(
                    [
                        repo_python(root),
                        "-c",
                        (
                            "from agents.agent import SubAgent; "
                            f"SubAgent.run_drain_worker({workspace!r}, {name!r})"
                        ),
                    ],
                    cwd=str(root),
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=flags,
                )
            finally:
                log_file.close()

        try:
            proc = _start(creationflags)
        except OSError:
            fallback = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            proc = _start(fallback)
        pid_path.write_text(str(proc.pid), encoding="utf-8")
        return f"Drain running (pid {proc.pid})."

    @override
    def close(self) -> None:
        super().close()
        self._tear_down_children()

    def _tear_down_children(self) -> None:
        """Stop non-blocking doer/judge/healer children — session.close for SubAgent."""
        for chat in (self._doer_runtime, self._judge_runtime, self._healer_runtime):
            if chat is not None:
                chat.stop()
        if self.session is not None and self._runtime_live():
            self._mailbox().stop()
        self._doer_runtime = None
        self._judge_runtime = None
        self._healer_runtime = None

    @override
    def _ensure_runtime(self, participant: AgentParticipant) -> None:
        role = participant.type
        if role == "doer" and self._doer_runtime is not None:
            participant.chat = self._doer_runtime
            return
        if role == "judge" and self._judge_runtime is not None:
            participant.chat = self._judge_runtime
            return
        if role == "healer" and self._healer_runtime is not None:
            participant.chat = self._healer_runtime
            return
        super()._ensure_runtime(participant)
        chat = participant.chat
        if isinstance(chat, SubAgentChatInstance):
            chat.role = role
            if role == "doer":
                self._doer_runtime = chat
            elif role == "judge":
                self._judge_runtime = chat
            elif role == "healer":
                self._healer_runtime = chat

    def _runtime_dir(self) -> Path:
        session = self._require_session()
        return self._workspace / ".agent_sessions" / session.name / "runtime"

    def _runtime_live(self) -> bool:
        return (self._runtime_dir() / "enabled").is_file()

    def _mailbox(self) -> _SubAgentMailbox:
        return _SubAgentMailbox(self._runtime_dir())

    def _child_prompt(self, participant: AgentParticipant) -> str:
        prompt = participant.prompt
        if participant.type != "judge":
            return prompt
        answer = ""
        if self._doer_runtime is not None:
            answer = self._doer_runtime._child_result.strip()
        if not answer:
            return prompt
        return f"The doer answered: {answer}\n\n{prompt}"

    def _launch(self, participant: AgentParticipant) -> None:
        """Non-blocking child for doer, judge, or healer — same runtimes for the session."""
        self._ensure_runtime(participant)
        self._bind_chat_context(participant)
        prompt = self._child_prompt(participant)
        self._require_runtime(participant).run_prompt(prompt)
        if self._runtime_live():
            self._mailbox().send(participant.type, prompt)

    @override
    def _await_done(self, participant: AgentParticipant) -> None:
        if not self._runtime_live():
            super()._await_done(participant)
            return
        if participant.state != "running":
            raise RuntimeError(f"expected running, got {participant.state}")
        text = self._mailbox().wait(participant.type)
        chat = participant.chat
        if isinstance(chat, SubAgentChatInstance):
            chat._child_result = text
        participant.state = "done"

    @override
    def _await_verdict(self, participant: AgentParticipant) -> str:
        if not self._runtime_live():
            return super()._await_verdict(participant)
        participant.state = "awaiting_verdict"
        text = self._mailbox().wait("judge")
        chat = participant.chat
        if isinstance(chat, SubAgentChatInstance):
            chat._child_result = text
        result = self._require_runtime_alive(participant).verdict()
        participant.state = "done"
        return result

    @override
    def _deliver_to_runtime(self, participant: AgentParticipant) -> None:
        self._launch(participant)

    @override
    def _accept_on_runtime(self, participant: AgentParticipant) -> None:
        self._require_runtime_alive(participant)

    @override
    def _done_on_runtime(self, participant: AgentParticipant) -> None:
        self._require_runtime_alive(participant)


class _TranscriptPath:
    """Vendor transcript location from chat workspace + chat id."""

    def __init__(self, home: Path | None = None) -> None:
        self.home = home

    def under_chat(self, chat: AIChatInstance) -> Path:
        if self.home is not None or isinstance(chat, CursorChatInstance):
            return self._cursor_layout(chat)
        workspace = chat.workspace_path or "."
        return Path(workspace) / "agent-transcripts" / f"{chat.chat_id}.jsonl"

    def _cursor_layout(self, chat: AIChatInstance) -> Path:
        workspace = chat.workspace_path or "."
        chat_id = chat.chat_id
        home = self.home if self.home is not None else Path.home()
        return (
            home
            / ".cursor"
            / "projects"
            / _cursor_project_slug(workspace)
            / "agent-transcripts"
            / chat_id
            / f"{chat_id}.jsonl"
        )


def _cursor_project_slug(workspace: str) -> str:
    raw = str(Path(workspace).resolve())
    return (
        raw.replace(":", "")
        .replace("\\", "-")
        .replace("/", "-")
        .replace("_", "-")
    )


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
        result = self._verdicts.from_transcript(self._file)
        if result not in ("PASS", "FAIL"):
            raise AIChatFault(
                kind="connection",
                detail="judge transcript had no PASS or FAIL",
            )
        return result


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
    _worktree_bind: _CliWorkspaceBind = field(
        default_factory=_CliWorkspaceBind, repr=False
    )
    _task_files: _CliTaskFile = field(default_factory=_CliTaskFile, repr=False)
    _scratch: _CliScratch = field(default_factory=_CliScratch, repr=False)
    _log: CliAgentSessionLog = field(
        default_factory=CliAgentSessionLog, init=False, repr=False
    )
    _cli: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.session is not None:
            self._bind_session(self.session)

    @override
    def _bind_session(self, session: AgentSession) -> None:
        self._wire_session_log(session)
        super()._bind_session(session)

    def _wire_session_log(self, session: AgentSession) -> None:
        if session.log is self._log:
            return
        self._log._adopt_from(session.log)
        session.log = self._log

    @property
    def _workspace_root(self) -> str:
        return self._worktree_bind.path

    @property
    def _pending_session(self) -> bool:
        if self.session is None:
            return True
        return self._worktree_bind.lacks_worktree(self.session)

    @override
    def close(self) -> None:
        self.close_agents()
        self.cleanup()

    def close_agents(self) -> None:
        """Stop live doer/judge/healer CLI processes and clear chat bindings."""
        super().close()
        self._worktree_bind.clear()

    def cleanup(self) -> None:
        """Remove orchestration temps; never delete durable session artifacts."""
        self._wipe_scratch()

    def close_cli_session(self) -> None:
        """Stop CLI runtimes, wipe temps, then close the AgentSession."""
        self.close_agents()
        self.cleanup()
        session = self.session
        if session is not None:
            session.close()

    def run(self) -> str:
        """Slash run — drain the backlog on live CLI participants."""
        self._ensure_session()
        self.run_backlog()
        return self.queue_status()

    @override
    def run_backlog(self) -> None:
        self.log._append("run")
        try:
            super().run_backlog()
        except Exception as exc:
            self.log.error(str(exc))
            self.log.run_stopped(type(exc).__name__)
            raise
        self.log.run_stopped("complete")

    @override
    def run_next_task(self) -> None:
        self.log._append("run")
        try:
            super().run_next_task()
        except Exception as exc:
            self.log.error(str(exc))
            self.log.run_stopped(type(exc).__name__)
            raise
        self.log.run_stopped("complete")

    def _wipe_scratch(self) -> None:
        session = self.session
        if session is None:
            return
        self._scratch.wipe(context_root=Path(session.context_root))

    @override
    def _ensure_session(self) -> None:
        super()._ensure_session()
        self._bind_workspace_root()

    def _bind_workspace_root(self) -> None:
        self._worktree_bind.bind_worktree(self._require_session())

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

    @override
    def _runtime_class(self) -> type[AIChatInstance]:
        return CursorChatInstance

    @override
    def _ensure_runtime(self, participant: AgentParticipant) -> None:
        super()._ensure_runtime(participant)
        chat = participant.chat
        if isinstance(chat, CursorChatInstance):
            chat._cli = self._cli
            chat._transcript_home = self._paths.home
            if not chat.workspace_path:
                chat.workspace_path = self._worktree_bind.path
            chat.create_chat()

    @override
    def _run_tools_cli_for(self, participant: AgentParticipant) -> None:
        return None

    @override
    def _give_up_on_judge_fail(self) -> None:
        self._raise(
            AgentFault(
                kind="judge_fail_limit",
                detail=f"judge FAIL x{self.fail_count}",
            )
        )

    def _bind_chat_context(self, participant: AgentParticipant) -> None:
        super()._bind_chat_context(
            participant, workspace_path=self._worktree_bind.path
        )

    @override
    def _wait_doer(self) -> None:
        super()._wait_doer()
        self.log.wait_doer()

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

    def _child_prompt(self, participant: AgentParticipant) -> str:
        prompt = participant.prompt
        if participant.type != "judge":
            return prompt
        task = self.current_task
        if task is None:
            return prompt
        doer_chat = task.doer.chat
        if doer_chat is None:
            return prompt
        answer = self._latest_assistant_text(doer_chat)
        if not answer:
            return prompt
        return f"The doer answered: {answer}\n\n{prompt}"

    def _latest_assistant_text(self, chat: AIChatInstance) -> str:
        transcript = _JsonlTranscript(self._paths.under_chat(chat))
        text = _AssistantText()
        for row in transcript.rows_newest_first():
            if row.get("role") != "assistant":
                continue
            reply = text.from_row(row).strip()
            if reply:
                return reply
        return ""

    @override
    def _deliver_to_runtime(self, participant: AgentParticipant) -> None:
        if self._pending_session:
            raise RuntimeError(
                "refuse durable CliAgent launch on main before branch worktree exists"
            )
        self._ensure_runtime(participant)
        self._bind_chat_context(participant)
        if participant.type == "doer":
            self._persist_prompt_to_task_file(participant.prompt)
        prompt = self._child_prompt(participant)
        self._require_runtime(participant).run_prompt(prompt)
        self.log.bind_chat_context(participant)
        chat = self._require_runtime(participant)
        self.watch.track(self._paths.under_chat(chat))
        self.log.run_chat(chat, prompt)
        if participant.type == "judge":
            self.log.launch_judge(participant)

    @override
    def _accept_on_runtime(self, participant: AgentParticipant) -> None:
        if participant.type == "healer":
            Agent._accept_on_runtime(self, participant)
            return
        chat = self._require_runtime(participant)
        self.watch._await_user_turn(self.accept_seconds, alive=chat.alive)

    @override
    def _done_on_runtime(self, participant: AgentParticipant) -> None:
        if participant.type == "healer":
            Agent._done_on_runtime(self, participant)
            return
        try:
            self.watch._await_growth_then_quiet(
                self.stall_seconds, self.quiet_seconds
            )
        except AIChatFault as fault:
            if fault.kind == "stall" and participant.type == "doer":
                prior = participant.state
                participant.state = "done"
                self._auto_kick_stalled_doer()
                participant.state = prior
            raise

    @override
    def _await_verdict(self, participant: AgentParticipant) -> str:
        participant.state = "awaiting_verdict"
        self.watch._await_growth_then_quiet(self.stall_seconds, self.quiet_seconds)
        chat = self._require_runtime_alive(participant)
        if isinstance(chat, CursorChatInstance):
            result = chat.verdict()
        else:
            result = self.watch._read_verdict()
        participant.state = "done"
        return result


# ---------------------------------------------------------------------------
# ChatAgent — in-chat subtype (same loop as Agent; hooks differ)
# ---------------------------------------------------------------------------

_CHAT_STATE_FILE = "chat-agent-state.json"


def _ticket_doer_prompt(work: "WorkTicket", *, instructions: str = "") -> str:
    from agents.workflow import WorkTicket

    issue = work.issue
    number = 0 if issue is None else issue.number
    title = "" if issue is None else issue.title
    body = "" if issue is None else issue.body
    lines = [f"# Ticket #{number}: {title}", "", body.strip()]
    if instructions.strip():
        lines.extend(["", "## Start instructions", instructions.strip()])
    return "\n".join(lines).strip() + "\n"


class _ChatAgentPersistence:
    """Persist ChatAgent across separate `python -m tools run` processes (this chat based agent kit, not CliAgent)."""

    @staticmethod
    def path_for(workspace: Path, session_name: str) -> Path:
        return workspace / ".agent_sessions" / session_name / _CHAT_STATE_FILE

    @classmethod
    def save(cls, engine: "ChatAgent", *, session_name: str, goal: str = "") -> None:
        session = engine.session
        if session is None:
            return
        payload: dict = {
            "session_name": session.name,
            "goal": goal or session.goal,
            "backlog": cls._serialize_backlog(engine.backlog),
            "current": cls._serialize_task(engine.current_task),
            "completed": cls._serialize_backlog(engine.completed_tasks),
            "chat_phase": engine._chat_phase,
            "pending_verdict": engine._pending_verdict,
        }
        target = cls.path_for(engine._workspace, session.name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, workspace: Path, session_name: str) -> "ChatAgent | None":
        path = cls.path_for(workspace, session_name)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        engine = ChatAgent(_workspace=workspace)
        name = str(payload.get("session_name") or session_name).strip()
        goal = str(payload.get("goal") or "")
        engine.open_session(name, goal=goal)
        repo = engine._repo()
        engine.backlog = cls._deserialize_tasks(payload.get("backlog") or [])
        for row, task in zip(payload.get("backlog") or [], engine.backlog):
            cls._link_tickets(task, row, repo=repo)
        current_row = payload.get("current")
        current = cls._deserialize_task(current_row)
        cls._link_tickets(current, current_row, repo=repo)
        engine.current_task = current
        completed_rows = payload.get("completed") or []
        engine.completed_tasks = cls._deserialize_tasks(completed_rows)
        for row, task in zip(completed_rows, engine.completed_tasks):
            cls._link_tickets(task, row, repo=repo)
        engine._chat_phase = str(payload.get("chat_phase") or "idle")
        engine._pending_verdict = str(payload.get("pending_verdict") or "")
        return engine

    @staticmethod
    def _serialize_backlog(tasks: list[AgentTask]) -> list[dict]:
        return [_ChatAgentPersistence._task_dict(t) for t in tasks]

    @staticmethod
    def _serialize_task(task: AgentTask | None) -> dict | None:
        if task is None:
            return None
        return _ChatAgentPersistence._task_dict(task)

    @staticmethod
    def _task_dict(task: AgentTask) -> dict:
        row: dict = {
            "doer_prompt": task.doer.prompt or task.prompt,
            "state": task.state,
            "doer_state": task.doer.state,
        }
        if task.judge is not None:
            row["judge_prompt"] = task.judge.prompt
            row["judge_state"] = task.judge.state
        if task.tickets:
            snapshots = []
            for ticket in task.tickets:
                issue = getattr(ticket, "issue", None)
                if issue is None:
                    continue
                snapshots.append(
                    {
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body,
                    }
                )
            if snapshots:
                row["tickets"] = snapshots
        return row

    @classmethod
    def _deserialize_tasks(cls, rows: list) -> list[AgentTask]:
        tasks: list[AgentTask] = []
        for row in rows:
            task = cls._deserialize_task(row)
            if task is not None:
                tasks.append(task)
        return tasks

    @classmethod
    def _deserialize_task(cls, row) -> AgentTask | None:
        if not isinstance(row, dict):
            return None
        doer_prompt = str(row.get("doer_prompt") or "").strip()
        if not doer_prompt:
            return None
        task = _TemplateInstantiator._task_from_prompt(doer_prompt)
        judge_prompt = str(row.get("judge_prompt") or "").strip()
        if judge_prompt:
            task.judge = AgentParticipant(type="judge", prompt=judge_prompt)
            task.judge.state = row.get("judge_state") or "idle"
        task.state = row.get("state") or "Backlog"
        task.doer.state = row.get("doer_state") or "idle"
        return task

    @classmethod
    def _link_tickets(cls, task: AgentTask | None, row, *, repo: Repo) -> None:
        if task is None or not isinstance(row, dict):
            return
        snapshots = row.get("tickets") or []
        if not snapshots:
            return
        from agents.workflow import WorkTicket

        shelf = repo._issue_shelf
        if shelf.project is None:
            shelf.attach_project(Project())
        linked: list[WorkTicket] = []
        for snap in snapshots:
            if not isinstance(snap, dict):
                continue
            number = int(snap.get("number") or 0)
            title = str(snap.get("title") or "")
            body = str(snap.get("body") or "")
            try:
                work = WorkTicket.from_ref(repo, number)
            except Exception:
                work = WorkTicket(repo, None).create(title, body)
            else:
                if work.issue is not None and title:
                    work.issue.title = title
                    work.issue.body = body
            linked.append(work)
        task.tickets = linked


@dataclass
class ChatAgent(Agent):
    """In-chat Agent — same doer→judge loop; this window is the runtime."""

    _healer_returns_handoff: bool = field(default=True, init=False, repr=False)
    _chat_phase: str = field(default="idle", repr=False)
    _pending_verdict: str = field(default="", repr=False)

    @override
    def _deliver_to_runtime(self, participant: AgentParticipant) -> None:
        if participant.type == "healer":
            Agent._deliver_to_runtime(self, participant)
            return
        return None

    @override
    def _accept_on_runtime(self, participant: AgentParticipant) -> None:
        if participant.type == "healer":
            Agent._accept_on_runtime(self, participant)
            return
        return None

    @override
    def _done_on_runtime(self, participant: AgentParticipant) -> None:
        if participant.type == "healer":
            Agent._done_on_runtime(self, participant)
            return
        return None

    @override
    def _await_verdict(self, participant: AgentParticipant) -> str:
        participant.state = "awaiting_verdict"
        result = self._pending_verdict.strip().upper() or "PASS"
        if result not in ("PASS", "FAIL"):
            result = "PASS"
        self._pending_verdict = ""
        participant.state = "done"
        return result

    @override
    def _run_tools_cli_for(self, participant: AgentParticipant) -> None:
        """In-chat orchestration only — kit turns belong to the doer/judge runtime."""
        return None

    def _task_label(self, task: AgentTask) -> str:
        return (task.prompt or task.doer.prompt).strip() or "(empty)"

    def _chat_status_block(self) -> str:
        lines = ["---", "In progress:"]
        current = self.current_task
        if current is None:
            lines.append("  (none)")
        else:
            role = "doer"
            if self._chat_phase == "judge_out":
                role = "judge"
            elif self._chat_phase == "doer_out":
                role = "doer"
            lines.append(f"  {self._task_label(current)} [{role}]")
        lines.append("Done:")
        if not self.completed_tasks:
            lines.append("  (none)")
        else:
            for index, task in enumerate(self.completed_tasks, 1):
                lines.append(f"  {index}. {self._task_label(task)}")
        lines.append("Left:")
        if not self.backlog:
            lines.append("  (none)")
        else:
            for index, task in enumerate(self.backlog):
                lines.append(f"  {index}. {self._task_label(task)}")
        return "\n".join(lines)

    def _chat_reply(self, body: str, next_step: str) -> str:
        return f"{body}\n\n{self._chat_status_block()}\n\nNext: {next_step}"

    def step_from_chat(self, *, verdict: str = "") -> str:
        """One in-chat wait — returns the prompt for this window plus the next slash step."""
        if verdict.strip():
            self._pending_verdict = verdict.strip().upper()
        self._ensure_session()
        if self._chat_phase == "doer_out":
            return self._chat_finish_doer()
        if self._chat_phase == "judge_out":
            return self._chat_take_verdict()
        return self._chat_deliver_doer()

    def _chat_deliver_doer(self) -> str:
        if self.current_task is None:
            self._launch_next()
        if self.current_task is None:
            self._chat_phase = "idle"
            return self._chat_reply(
                "No current task.",
                "add work with /agent-backlog, or healer eval.",
            )
        self._launch_doer()
        self._chat_phase = "doer_out"
        return self._chat_reply(
            self.current_task.doer.prompt,
            "do this work, then /agent.",
        )

    def _chat_finish_doer(self) -> str:
        self._wait_doer()
        task = self._require_current_task()
        if task.judge is None:
            self._finish_task_pass()
            self._chat_phase = "idle"
            if self.backlog:
                return self._chat_deliver_doer()
            return self._chat_reply(
                "Task complete (no judge).",
                "healer eval.",
            )
        self._launch_judge()
        self._chat_phase = "judge_out"
        return self._chat_reply(
            task.judge.prompt,
            "judge PASS or FAIL, then /agent.",
        )

    def _chat_take_verdict(self) -> str:
        result = self._wait_verdict()
        if result == "PASS":
            self._finish_task_pass()
            self._chat_phase = "idle"
            if self.backlog:
                follow = self._chat_deliver_doer()
                return f"PASS.\n\n{follow}"
            return self._chat_reply(
                "PASS. Task complete.",
                "healer eval.",
            )
        self._on_judge_fail()
        self._chat_phase = "idle"
        if self.current_task is not None:
            follow = self._chat_deliver_doer()
            return f"FAIL. Retrying doer.\n\n{follow}"
        if self.backlog:
            follow = self._chat_deliver_doer()
            return f"FAIL. Skipped after judge retries.\n\n{follow}"
        return self._chat_reply(
            "FAIL. Skipped after judge retries.",
            "add work with /agent-backlog, or healer eval.",
        )


# @toolset-manifest python -m tools manifest agents.agent:ChatAgentKit
@agentic_toolset
class ChatAgentKit:
    """Slash ``/agent`` — parent orchestration in this chat window."""

    def __init__(self, workspace: str = "", session: str = "") -> None:
        self._workspace = Path((workspace or os.getcwd()).strip())
        self._session_name = (session or "agent-chat").strip()
        self._engine_ref: ChatAgent | None = None

    def _select_session(self, name: str = "") -> None:
        requested = (name or "").strip()
        if not requested:
            return
        bound_name = ""
        if self._engine_ref is not None and self._engine_ref.session is not None:
            bound_name = self._engine_ref.session.name
        if requested != self._session_name or (
            bound_name and bound_name != requested
        ):
            self._engine_ref = None
        self._session_name = requested

    def _get_engine(self) -> ChatAgent:
        if self._engine_ref is not None:
            return self._engine_ref
        loaded = _ChatAgentPersistence.load(self._workspace, self._session_name)
        if loaded is not None:
            self._engine_ref = loaded
            return loaded
        self._engine_ref = ChatAgent(_workspace=self._workspace)
        return self._engine_ref

    def _persist(self, *, goal: str = "") -> None:
        engine = self._engine_ref
        if engine is None or engine.session is None:
            return
        _ChatAgentPersistence.save(
            engine, session_name=engine.session.name, goal=goal
        )

    def _run_guarded(self, phase: str, fn):
        from agents.healer import HealerStop, format_healer_fix_handoff

        engine = self._get_engine()
        try:
            result = engine._guard_phase(phase, fn)
            engine.note_phase_result(phase, str(result))
            self._persist()
            text = str(result)
            if text.startswith("healer_fix:") or text.startswith("healer_stop:"):
                return (
                    f"{text}\n\n{engine._chat_status_block()}\n\n"
                    "Next: apply the healer fix, then /agent."
                )
            return result
        except HealerStop as stop:
            self._persist()
            return (
                f"healer_stop: {stop.report.summary()}\n{stop.report.to_json()}\n\n"
                f"{engine._chat_status_block()}\n\n"
                "Next: apply the healer fix, then /agent."
            )
        except AgentFault as fault:
            self._persist()
            report = engine.eval_healer(
                phase=phase,
                trigger="exception",
                error=fault,
                stop_on_exception=False,
            )
            return (
                f"{format_healer_fix_handoff(report)}\n\n"
                f"{engine._chat_status_block()}\n\n"
                "Next: apply the healer fix, then /agent."
            )

    def _ensure_named_session(self, name: str = "", goal: str = "") -> ChatAgent:
        self._select_session(name)
        engine = self._get_engine()
        if engine.session is None:
            engine.open_session(self._session_name, goal=goal)
        elif goal:
            engine.session.goal = goal
        return engine

    def _format_backlog(self, engine: ChatAgent) -> str:
        return engine._chat_status_block()

    @agent_tool
    def agent(
        self,
        session_name: str = "",
        goal: str = "",
        doer_prompt: str = "",
        judge_prompt: str = "",
        verdict: str = "",
        tasks: list[dict] | None = None,
    ) -> str:
        """Advance one wait. Result always includes In progress / Done / Left, then Next."""

        self._select_session(session_name)

        def _run() -> str:
            engine = self._ensure_named_session(session_name, goal)
            specs = list(tasks or [])
            if doer_prompt.strip():
                specs.append(
                    {
                        "doer_prompt": doer_prompt.strip(),
                        "judge_prompt": judge_prompt.strip(),
                    }
                )
            if (
                specs
                and engine._chat_phase == "idle"
                and engine.current_task is None
            ):
                engine.add_tasks_from_specs(specs)
            return engine.step_from_chat(verdict=verdict)

        return self._run_guarded("agent", _run)

    @agent_tool
    def backlog(
        self,
        action: str = "",
        tasks: list[dict] | None = None,
        index: int = -1,
        prompt: str = "",
    ) -> str:
        """List, add, or remove items. Result is In progress / Done / Left."""

        def _run() -> str:
            engine = self._ensure_named_session()
            hint = f"{action} {prompt}".strip().lower()
            rows = list(tasks or [])
            if hint.startswith("clear"):
                engine.clear_backlog()
                return self._format_backlog(engine)
            if rows or hint.startswith("add"):
                if rows:
                    engine.add_tasks_from_specs(rows)
                return self._format_backlog(engine)
            if hint.startswith("remove") or hint.startswith("delete") or index >= 0:
                if index >= 0 and index < len(engine.backlog):
                    engine.backlog.pop(index)
                elif prompt.strip():
                    needle = prompt.strip().lower()
                    engine.backlog = [
                        task
                        for task in engine.backlog
                        if needle not in task.prompt.lower()
                    ]
                return self._format_backlog(engine)
            return self._format_backlog(engine)

        return self._run_guarded("backlog", _run)

    @prompt(name="agent-backlog")
    @agent_instructions
    def agent_backlog(self) -> str:
        """Call tool ``backlog``. The result lists In progress, Done, and Left."""
        return (
            "Call tool backlog to list, add, or remove items. "
            "Read In progress, Done, and Left in the result. Do not drain the loop."
        )

    @prompt(name="agent")
    @agent_instructions
    def run_judged_job(
        self,
        doer_prompt: str = "",
        judge_prompt: str = "",
        session_name: str = "",
    ) -> str:
        """Call tool ``agent`` once per wait. Print In progress / Done / Left from the result."""
        return (
            "Call tool agent (session_name, doer_prompt, judge_prompt on the first call). "
            "The result is the work for this chat, then In progress, Done, and Left, then Next. "
            "Show that board in your reply. Do the work Next names. Call tool agent again. "
            "When Next says judge, pass verdict PASS or FAIL. "
            "After PASS, the board shows which tasks are Done and which are Left."
        )
