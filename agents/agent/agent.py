"""Agent — backlog and participant orchestration (stubbed runtime hooks)."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

ParticipantType = Literal["doer", "judge", "human"]
ParticipantState = Literal[
    "idle",
    "sending",
    "awaiting_accept",
    "running",
    "awaiting_verdict",
    "done",
    "faulted",
]
TaskState = Literal["Backlog", "In Progress", "Done"]


@dataclass
class AgentParticipant:
    """One doer, judge, or human role on a task."""

    type: ParticipantType
    prompt: str = ""
    state: ParticipantState = "idle"


def _default_doer() -> AgentParticipant:
    return AgentParticipant(type="doer")


@dataclass
class AgentTask:
    """One backlog item with doer and optional judge or human."""

    prompt: str
    state: TaskState = "Backlog"
    index: int | None = None
    doer: AgentParticipant = field(default_factory=_default_doer)
    judge: AgentParticipant | None = None
    human: AgentParticipant | None = None

    def __post_init__(self) -> None:
        if not self.doer.prompt:
            self.doer.prompt = self.prompt
        if self.doer.type != "doer":
            self.doer.type = "doer"


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


@dataclass
class AgentSessionLog(_SessionLogWriter):
    """Append-only JSONL orchestration audit for one AgentSession."""

    def send(self, participant: AgentParticipant, *, prompt: str | None = None) -> None:
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
class AgentSession:
    """Named session folder, context root, and orchestration log."""

    name: str
    folder: Path
    context_root: Path = field(default_factory=Path)
    goal: str = ""
    log: AgentSessionLog = field(default_factory=AgentSessionLog)
    _agent_slot: _LinkedAgentSlot = field(default_factory=_LinkedAgentSlot, repr=False)
    _gate: _SessionGate = field(default_factory=_SessionGate, repr=False)
    _log_path: _LogPath = field(default_factory=_LogPath, repr=False)

    def __post_init__(self) -> None:
        if not self.context_root or str(self.context_root) == ".":
            self.context_root = self.folder.parent
        if self.log.path is None:
            self.log.path = self._log_path.under(self.folder)

    @property
    def agent(self):
        return self._agent_slot.holder

    @agent.setter
    def agent(self, linked_agent) -> None:
        self._agent_slot.holder = linked_agent

    def open(self) -> None:
        if self._session_is_open():
            return
        self.folder.mkdir(parents=True, exist_ok=True)
        self.log.open(name=self.name, contextRoot=str(self.context_root))
        self._gate.is_open = True

    def close(self) -> None:
        if not self._session_is_open():
            return
        self._tear_down_session()

    def _session_is_open(self) -> bool:
        return bool(self._gate.is_open)

    def _tear_down_session(self) -> None:
        self._emit_close_log()
        self._release_linked_agent()
        self._mark_closed()

    def _emit_close_log(self) -> None:
        self.log.close(name=self.name)

    def _release_linked_agent(self) -> None:
        self._invoke_close(self._agent_slot.take())

    def _invoke_close(self, linked) -> None:
        linked.close()

    def _mark_closed(self) -> None:
        self._gate.is_open = False


@dataclass
class Agent:
    """Orchestrates doer → judge → human for each task on the backlog."""

    session: AgentSession | None = None
    backlog: list[AgentTask] = field(default_factory=list)
    current_task: AgentTask | None = field(default=None)
    completed_tasks: list[AgentTask] = field(default_factory=list)
    _stub_verdicts: _StubSeries = field(default_factory=_StubSeries, repr=False)
    _stub_human_feedback: _StubSeries = field(default_factory=_StubSeries, repr=False)

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

    def close(self) -> None:
        self.current_task = None

    def kick(self, participant: AgentParticipant | None = None) -> None:
        target = participant or self._default_kick_target()
        target.state = "idle"
        self.log.kick(target)

    def run_next_task(self) -> None:
        self._prepare_session()
        if self.current_task is None:
            self._launch_next()
        if self.current_task is None:
            return
        while self.current_task is not None:
            self._run_current_task_cycle()

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
        self._retry_after_fail()

    def _finish_task_pass(self) -> None:
        if self._human_requested_retry():
            return
        self._complete_task(outcome="PASS")

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

    def _prepare_session(self) -> None:
        session = self._require_session()
        self._open_session(session)
        self._link_agent(session)

    def _require_session(self) -> AgentSession:
        if self.session is None:
            raise RuntimeError("Agent requires an open AgentSession before run")
        return self.session

    def _open_session(self, session: AgentSession) -> None:
        session.open()

    def _link_agent(self, session: AgentSession) -> None:
        session.agent = self

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

    def _wait_doer(self) -> None:
        task = self._require_current_task()
        participant = task.doer
        self._await_done(participant)
        self.log.done(participant)

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

    def _complete_task(self, *, outcome: str) -> None:
        task = self._require_current_task()
        self.log.complete_task(task, outcome=outcome)
        task.state = "Done"
        self.completed_tasks.append(task)
        self.current_task = None

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
