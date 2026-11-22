"""SessionLog — a session's ``session.log`` and ``session.err``: what each action, tool call, note, and loop wrote."""

from __future__ import annotations

import re
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from harness.agent_tools.chat_pointer import NO_CHAT, ChatPointer
from harness.process.capped_log_file import CappedLogFile
from harness.process.log_timestamp import LogTimestamp
from space.work_state import SESSIONS_FOLDER

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.guidance.rule import RulesCollection
    from space.session.practices.practice_session_output import FidelitySessionOutput
    from space.session.session import Session

LOG_FILE = "session.log"
ERROR_FILE = "session.err"
# How an agent keeps the log: the text sessions.switch answers with.
_INSTRUCTIONS_FILE = Path(__file__).parent / "SESSION-LOG.md"
# The rules a hook gave the agent since the last log line. The hook server notes them and the cdd server writes the next
# line, so they wait in the session's work folder rather than in either process.
_INJECTED_RULES_FILE = "injected-rules.txt"
# The verb of the line a tool call writes first, naming the tool: every line that call writes follows it.
_TOOL_VERB = "tool"
# The verb of the marker line that starts a loop: ``--- N``.
_LOOP_VERB = "---"
_LOOP_MARKER = re.compile(r"---\s+(\d+)(?:\s|$)")


class LoopNotFoundError(LookupError):
    """A loop was asked for that the session log has not marked, such as loop 4 of a log marked up to 3: it carries
    the loop asked for, none when the latest was asked for, and the highest loop the log has marked."""

    def __init__(self, detail: str, asked: int | None, highest_marked: int) -> None:
        super().__init__(detail)
        self.asked = asked
        self.highest_marked = highest_marked


class HookLog:
    """A log a hook appends to while a session is open, such as ``dispatch.debug`` or the prompt log, in the ``logs``
    folder of the session's work folder: the one place that writes such a log, so its entries are appended one way."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(self, text: str) -> None:
        """Append text, an entry that carries its own time, such as a prompt log entry under its stamped header; a log
        that reached its size starts again, its earlier entries kept in its previous file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        CappedLogFile(self.path).roll_when_full()
        with self.path.open("a", encoding="utf-8") as log:
            log.write(text if text.endswith("\n") else f"{text}\n")

    def stamped(self, line: str) -> None:
        """Append line stamped with the time it was written."""
        self.append(f"{LogTimestamp.now()} {line}")


class LogLine:
    """*LogLine* is one line of a session log: when it was written, its verb, and what the verb acted on (its subject,
    such as a tool's name, a note, a loop's number or a stage; the paths it worked on; the practices, fidelities and
    formats it names; a detail, such as a validate's findings; the rules a hook gave the agent since the last line; and
    the chat that caused it). It writes itself
    (``written``, which the log stamps with the time) and reads itself back (``LogLine.read``). A line read back keeps
    its words in order but not which part each came from, since an older log wrote some parts in another order: a
    validate line named its practice by its class (`CleanEngineering`), and ``names`` still recognises it."""

    def __init__(self, verb: str, *, subject: str = "", paths: Iterable[str | Path] = (), practices: Iterable[str] = (),
                 fidelities: Iterable[str] = (), formats: Iterable[str] = (), detail: str = "", rules: str = "",
                 chat: ChatPointer | None = None, time: str = "") -> None:
        self.verb = verb
        self.subject = (subject or "").strip()
        self.detail = (detail or "").strip()
        self.paths = [str(path) for path in paths]
        self.practices = list(practices)
        self.fidelities = list(fidelities)
        self.formats = list(formats)
        self.rules = rules
        self.chat = chat
        self.time = time

    @classmethod
    def read(cls, text: str) -> LogLine:
        """The line as the log holds it, ``<time> <verb> <words...>``: its time, its verb, and the rest of its words."""
        parts = text.split()
        return cls(parts[1] if len(parts) > 1 else "", subject=" ".join(parts[2:]), time=parts[0] if parts else "")

    @property
    def written(self) -> str:
        """The line as the log writes it after its time: its verb, its subject, the paths it worked on, the practices,
        fidelities and formats it names, its detail, the rules a hook gave, and the chat's pointer, each part left out
        when empty."""
        listed = (", ".join(names) for names in (self.paths, self.practices, self.fidelities, self.formats))
        parts = (self.verb, self.subject, *listed, self.detail, self.rules, str(self.chat) if self.chat is not None else "")
        return " ".join(part for part in parts if part)

    @property
    def text(self) -> str:
        """The line as the log holds it, its time first."""
        return " ".join(part for part in (self.time, self.written) if part)

    @property
    def words(self) -> list[str]:
        """The words after the verb, without the commas that join the paths and names a line lists."""
        return [word.rstrip(",") for word in self.written.split()[1:]]

    @property
    def stage(self) -> str:
        """The stage a move or a mark names: the first word after its verb."""
        words = self.words
        return words[0] if words else ""

    @property
    def loop_number(self) -> int | None:
        """The loop a ``--- N`` marker line starts; none for any other line."""
        match = _LOOP_MARKER.search(self.written)
        return int(match.group(1)) if match else None

    def names(self, fidelity: FidelityGuidance) -> bool:
        """Whether this line names fidelity and its practice, by its key or, in an older validate line, its class."""
        practice = fidelity.practice_guidance
        words = set(self.words)
        return fidelity.name in words and bool({practice.key, type(practice).__name__} & words)


class Loop:
    """One span of context, generation, and evaluation inside a session, read from its log: the ``--- N`` marker line
    and every line written after it until the next marker."""

    def __init__(self, number: int, entries: list[str] | None = None) -> None:
        self.number = number
        self.entries: list[str] = list(entries or [])

    def expanded_text(self) -> str:
        """Log lines for this loop, each followed by the transcript lines its chat pointer covers. A transcript range
        that an earlier line already showed is named, not repeated."""
        parts: list[str] = []
        seen: set[tuple[str, str]] = set()
        for line in self.entries:
            parts.append(line)
            chat = ChatPointer.in_log_line(line)
            if chat is None:
                continue
            transcript = chat.transcript
            key = (str(transcript.resolve()) if transcript.exists() else str(transcript), chat.lines)
            if key in seen:
                parts.append(f"    (chat {chat.id} {chat.lines} — see above)")
                continue
            seen.add(key)
            parts.append(f"--- chat {chat} ---")
            parts.extend(chat.transcript_text())
        return "\n".join(parts)


class InjectedRules:
    """The rules a hook gave the agent for the files it edited since the last log line, kept in the session folder's
    ``injected-rules.txt`` until the next line names them. The hook server notes them and the cdd server writes the
    line, so the file is how the two processes hand them over."""

    def __init__(self, log: SessionLog) -> None:
        self._log = log

    @property
    def _path(self) -> Path | None:
        """``injected-rules.txt`` beside the log, wherever the session's work folder is now; none before it has one."""
        log_path = self._log.path
        return log_path.with_name(_INJECTED_RULES_FILE) if log_path is not None else None

    def note(self, rules: RulesCollection, matched_path: str) -> None:
        """Note that rules were given for the edited file at matched_path, each named with its practice and fidelity."""
        if self._path is None or not matched_path:
            return
        named = {" ".join(part for part in (rules.practice_key, rules.fidelity_name, rule.slug, matched_path) if part) for rule in rules}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text("\n".join(sorted(named | set(self.pending))) + "\n", encoding="utf-8")

    @property
    def pending(self) -> list[str]:
        """The rules noted since the last log line; none when none were."""
        return self._path.read_text(encoding="utf-8").splitlines() if self._path is not None and self._path.is_file() else []

    @property
    def text(self) -> str:
        """The pending rules as a log line writes them."""
        return " ".join(sorted(self.pending))

    def clear(self) -> None:
        """Forget the pending rules, once a log line has named them."""
        if self._path is not None:
            self._path.unlink(missing_ok=True)


class SessionLog:
    """The log of one session: ``session.log``, one timestamped line per action, tool call, note, and loop marker, each
    ending with a pointer to the chat that caused it, and ``session.err``, the full trace of each failure a log line
    points at. A session without a folder has a log that writes nothing. A session is one object for every call made
    in it, from any chat, so a chat writes its lines through ``by(chat)``, which points each of them at that chat."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # The rules a hook gave the agent since the last line, which the next line names. The file it keeps them in is
        # shared with the hook server, so it is read on each ask.
        self.injected_rules = InjectedRules(self)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def path(self) -> Path | None:
        """The session's session.log; none before the session has a folder."""
        folder = self._session.work_folder
        return folder / LOG_FILE if folder is not None else None

    @property
    def error_path(self) -> Path | None:
        """The session's session.err, which keeps the full trace of each failure that session.log points at."""
        folder = self._session.work_folder
        return folder / ERROR_FILE if folder is not None else None

    @property
    def entries(self) -> list[LogLine]:
        """Every line of session.log, oldest first; none before anything is logged."""
        return [LogLine.read(line) for line in self._lines() if line.strip()]

    def latest(self, *verbs: str, stage: str = "") -> LogLine | None:
        """The latest line recording one of verbs, such as a ticket's latest move; with stage, the latest of them that
        names stage. None when the log has no such line."""
        return next((entry for entry in reversed(self.entries) if entry.verb in verbs and entry.stage == (stage or entry.stage)), None)

    def _lines(self) -> list[str]:
        log = self.path
        if log is None or not log.is_file():
            return []
        return log.read_text(encoding="utf-8").splitlines()

    @property
    def _is_writable(self) -> bool:
        """Whether the checkout the session works in is still there: a ticket's worktree can be removed while the cdd
        server still holds its session, and a log line making its folder again would stand where the next worktree of
        that name must be added."""
        folder = self._session.work_folder
        if folder is None:
            return False
        checkout = next((parent.parent for parent in folder.parents if parent.name == SESSIONS_FOLDER), folder.parent)
        return checkout.is_dir()

    def record(self, line: LogLine) -> None:
        """Append line to session.log, stamped with the time it was written; nothing once the session's checkout is gone."""
        if not self._is_writable:
            return
        # A project's main session has no folder until something is written in it.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._roll_when_full()
        self._append(line.written)

    def _append(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{LogTimestamp.now()} {line}\n")

    def _roll_when_full(self) -> None:
        """Move a full session.log's lines to session.log.1 and start the new one in the loop it was in, so loops number
        on and that loop's next lines are read with it."""
        capped = CappedLogFile(self.path)
        if not capped.is_full:
            return
        loop = self.last_loop_number
        capped.roll_when_full()
        if loop:
            self._append(f"--- {loop} continued from {capped.previous.name}")

    def by(self, chat: ChatPointer | None) -> ChatLog:
        """The lines chat writes in this log, each pointing at it; ``no-chat`` when no chat is known, such as for work
        run in process."""
        return ChatLog(self, chat)

    def append_trace(self, failure: BaseException, tool: str) -> int:
        """Append failure's trace to session.err; the line its header is on, 0 once the session's checkout is gone."""
        if not self._is_writable:
            return 0
        err = self.error_path
        err.parent.mkdir(parents=True, exist_ok=True)
        CappedLogFile(err).roll_when_full()
        line_number = len(err.read_text(encoding="utf-8").splitlines()) + 1 if err.is_file() else 1
        trace = "".join(traceback.format_exception(type(failure), failure, failure.__traceback__))
        header = f"{LogTimestamp.now()} {tool} {type(failure).__name__}: {failure}".strip()
        with err.open("a", encoding="utf-8") as handle:
            handle.write(f"{header}\n{trace}")
            if not trace.endswith("\n"):
                handle.write("\n")
        return line_number

    @property
    def last_loop_number(self) -> int:
        """The highest ``--- N`` marker in session.log; 0 before a loop is marked."""
        return max((number for number in self._loop_numbers() if number is not None), default=0)

    def _loop_numbers(self) -> list[int | None]:
        return [entry.loop_number for entry in self.entries]

    def seed_first_loop(self) -> None:
        """Start a new session's log with ``--- 1`` before any action."""
        if self.path is not None and self.last_loop_number < 1:
            self.record(LogLine(_LOOP_VERB, subject="1"))

    def loop_at(self, number: int) -> Loop:
        """Loop number with its lines read from session.log; no lines when the log has not marked it."""
        return Loop(number, self._lines_of_loop(number))

    def _lines_of_loop(self, number: int) -> list[str]:
        entries = self.entries
        numbers = [entry.loop_number for entry in entries]
        if number not in numbers:
            return []
        start = numbers.index(number)
        end = next((index for index in range(start + 1, len(entries)) if numbers[index] not in (None, number)), len(entries))
        return [entry.text for entry in entries[start:end]]

    @property
    def latest_loop_with_entries(self) -> int:
        """The highest marked loop that has lines; 0 when none has."""
        return next((number for number in range(self.last_loop_number, 0, -1) if self._lines_of_loop(number)), 0)

    def read_loop(self, number: int | None = None) -> str:
        """Loop number, the latest with lines when none is named, with each line's chat transcript put under it."""
        loop_number = self.latest_loop_with_entries if number is None else number
        if loop_number < 1:
            raise LoopNotFoundError("no loops in session.log; run mark-loop first", number, self.last_loop_number)
        opened = self.loop_at(loop_number)
        if not opened.entries:
            raise LoopNotFoundError(f"loop {loop_number} not found (missing --- {loop_number} in session.log?)", loop_number, self.last_loop_number)
        return f"# Loop {loop_number} ({self._session.name})\n\n" + opened.expanded_text()

    def loop_to_note(self, loop: int | None) -> int:
        """The loop a note goes in: loop, which the log must have marked, else the latest with lines, else the latest."""
        if loop is not None:
            if loop < 1 or self.last_loop_number < loop:
                raise LoopNotFoundError(f"loop {loop} not found in session.log (no --- {loop} marker)", loop, self.last_loop_number)
            return loop
        chosen = self.latest_loop_with_entries or self.last_loop_number
        if chosen < 1:
            raise LoopNotFoundError("no loop in session.log; run mark-loop first", loop, self.last_loop_number)
        return chosen

    def instructions(self) -> str:
        """How an agent keeps this log: what every line points at, how loops are marked and read, and where the
        session's files go."""
        guide = _INSTRUCTIONS_FILE.read_text(encoding="utf-8").strip()
        return f"{guide}\n\nLog file: {self.path or LOG_FILE}. Errors: {self.error_path or ERROR_FILE}."


class ChatLog:
    """The lines one chat writes in a session's log: each action, tool call, note, failure, and loop marker of a call
    from that chat, each ending with its pointer, so ``session.read_loop`` can put that chat's words back under the
    line. One session serves calls from many chats at once, so the chat is held here, by what one call writes, and
    never on the session."""

    def __init__(self, log: SessionLog, chat: ChatPointer | None) -> None:
        self._log = log
        self._chat = chat or NO_CHAT

    @property
    def chat(self) -> ChatPointer:
        return self._chat

    def _record(self, line: LogLine) -> None:
        """Write line, which this chat's operation made, and forget the rules a hook gave since the last line."""
        self._log.record(line)
        self._log.injected_rules.clear()

    def validation(self, worked: FidelitySessionOutput, violations: list[str]) -> None:
        """Log a validate of the fidelity worked, as its practice and its name, with each violation's synopsis; no
        violations is a validate that passed. A validate line names its practice by its class (`CleanEngineering`), as
        every validate line has, where an action line names it by its folder."""
        self._record(LogLine("validate", practices=[type(worked.practice.guidance).__name__], fidelities=[worked.fidelity.name], detail=" ".join(violations), chat=self._chat))

    def action(self, action: str, paths: list[Path], worked: list[FidelitySessionOutput] | None = None) -> None:
        """Log action with the paths it worked on and, for each fidelity it worked at, its practice, its name, and the
        format it worked in."""
        worked_on = list(worked or [])
        self._record(LogLine(
            action,
            paths=paths,
            practices=[entry.practice.name for entry in worked_on],
            fidelities=[entry.fidelity.name for entry in worked_on],
            formats=[entry.fidelity.format for entry in worked_on if entry.fidelity.format],
            rules=self._log.injected_rules.text,
            chat=self._chat,
        ))

    def guidance_action(self, action: str, worked: list[FidelitySessionOutput]) -> None:
        """Log a guidance action on the fidelities worked, with the session's workpath and each one's practice's folder
        as the paths it worked on."""
        workpath = self._log.session.workpath
        work = [Path(workpath).resolve()] if workpath is not None else []
        folders = [entry.practice.folder for entry in worked]
        self.action(action, list(dict.fromkeys([*work, *folders])), worked)

    def tool(self, tool_name: str, paths: list[str] | None = None) -> None:
        """Append a ``tool ...`` line for a tool call, with the paths its arguments name (``ToolCall.named_paths``)."""
        name = (tool_name or "").strip()
        if self._log.path is None or not name:
            return
        # A tool line names its chat only when one is known; most tool calls come from a chat the server can name.
        chat = None if self._chat.is_missing else self._chat
        self._record(LogLine(_TOOL_VERB, subject=name, paths=[Path(path) for path in paths or []], rules=self._log.injected_rules.text, chat=chat))

    def note(self, message: str, paths: list[Path] | None = None) -> None:
        """Record a correction or decision in the current loop."""
        text = (message or "").strip()
        if not text:
            return
        self._log.record(LogLine("note", subject=text, paths=paths or [], chat=self._chat))

    def append_note(self, note: str, loop: int | None = None, paths: list[str] | None = None) -> str:
        """Append note to loop, the latest with lines when none is named, with the paths it names."""
        text = (note or "").strip()
        if not text:
            return "nothing appended: the note is empty"
        loop_number = self._log.loop_to_note(loop)
        body = text if text.lower().startswith(f"loop {loop_number}") else f"loop {loop_number}: {text}"
        self.note(body, [Path(item) for item in (paths or []) if str(item).strip()] or None)
        return f"appended note to {self._log.path or LOG_FILE} (loop {loop_number})"

    def failure(self, failure: BaseException, *, tool: str = "") -> None:
        """Append the full trace of failure to session.err and a line pointing at it to session.log; nothing for a
        session without a folder, whose log writes nothing."""
        line_number = self._log.append_trace(failure, tool)
        named = [tool.strip()] if tool.strip() else []
        self._log.record(LogLine("error", subject=" ".join([*named, str(self._log.error_path), str(line_number)]), chat=self._chat))

    def next_loop(self) -> Loop:
        """Mark the next loop, one past the highest marked, pointing at this chat."""
        number = self._log.last_loop_number + 1
        self._log.record(LogLine(_LOOP_VERB, subject=str(number), chat=self._chat))
        return self._log.loop_at(number)
