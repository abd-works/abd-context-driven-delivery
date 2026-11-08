"""SessionLog — a session's ``session.log`` and ``session.err``: what each action, tool call, note, and loop wrote."""

from __future__ import annotations

import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.chat_pointer import NO_CHAT, ChatPointer

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.guidance.rule import RulesCollection
    from space.session.practice_session_output import FidelitySessionOutput, PracticeSessionOutput
    from space.session.session import Session

LOG_FILE = "session.log"
ERROR_FILE = "session.err"
# How an agent keeps the log: the text sessions.switch answers with.
_INSTRUCTIONS_FILE = Path(__file__).parent / "SESSION-LOG.md"
# The rules a hook gave the agent since the last log line. The hook server notes them and the cdd server writes the next
# line, so they wait in the session's folder rather than in either process.
_INJECTED_RULES_FILE = "injected-rules.txt"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# The verb of the line a tool call writes first, naming the tool: every line that call writes follows it.
_TOOL_VERB = "tool"
_LOOP_MARKER = re.compile(r"---\s+(\d+)(?:\s|$)")
# The arguments of a tool call that name a file or folder the call worked on.
_TOOL_INPUT_PATH_KEYS = ("path", "file_path", "target_directory", "working_directory", "transcript_path", "agent_transcript_path")


class LoopNotFoundError(LookupError):
    """A loop was asked for that the session log has not marked, such as loop 4 of a log marked up to 3."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class LogTimestamp:
    """The time a session log line, a hook log entry, or a toast is stamped with: a moment in UTC, to the second, such
    as ``2026-11-07T17:30:05Z``. Every log a session keeps writes its times this one way, so their lines sort and compare
    alike."""

    def __init__(self, moment: datetime) -> None:
        self.moment = moment.astimezone(timezone.utc).replace(microsecond=0)

    @classmethod
    def now(cls) -> LogTimestamp:
        return cls(datetime.now(timezone.utc))

    @classmethod
    def read(cls, text: str) -> LogTimestamp:
        """The timestamp text names, as a log wrote it; raises ``ValueError`` for text that names no time."""
        return cls(datetime.strptime(text.strip(), _TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc))

    def __str__(self) -> str:
        return self.moment.strftime(_TIMESTAMP_FORMAT)


class HookLog:
    """A log a hook appends to while a session is open, such as ``dispatch.debug`` or the prompt log, in the ``logs``
    folder of the session's folder: the one place that writes such a log, so its entries are appended one way."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(self, text: str) -> None:
        """Append text, an entry that carries its own time, such as a prompt log entry under its stamped header."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as log:
            log.write(text if text.endswith("\n") else f"{text}\n")

    def stamped(self, line: str) -> None:
        """Append line stamped with the time it was written."""
        self.append(f"{LogTimestamp.now()} {line}")


class LogEntry:
    """One line of a session log: ``<time> <verb> <words...>``, the words being the subject the verb acted on."""

    # Action lines name a practice by its folder (`clean_engineering`) and validate lines by its class
    # (`CleanEngineering`).

    def __init__(self, line: str) -> None:
        self._parts = line.split()

    @property
    def text(self) -> str:
        """The line as the log holds it."""
        return " ".join(self._parts)

    @property
    def time(self) -> str:
        return self._parts[0] if self._parts else ""

    @property
    def verb(self) -> str:
        """What the line records, such as move or generate."""
        return self._parts[1] if len(self._parts) > 1 else ""

    @property
    def words(self) -> list[str]:
        """The words after the verb, without the commas that join the paths and names an action lists."""
        return [word.rstrip(",") for word in self._parts[2:]]

    @property
    def stage(self) -> str:
        """The stage a move or a mark names: the first word after its verb."""
        words = self.words
        return words[0] if words else ""

    @property
    def loop_number(self) -> int | None:
        """The loop a ``--- N`` marker line starts; none for any other line."""
        match = _LOOP_MARKER.search(" ".join(self._parts))
        return int(match.group(1)) if match else None

    def names(self, fidelity: FidelityGuidance) -> bool:
        """Whether this line names fidelity and its practice."""
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
        """``injected-rules.txt`` beside the log, wherever the session's folder is now; none before it has one."""
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
        folder = self._session.session_path
        return folder / LOG_FILE if folder is not None else None

    @property
    def error_path(self) -> Path | None:
        """The session's session.err, which keeps the full trace of each failure that session.log points at."""
        folder = self._session.session_path
        return folder / ERROR_FILE if folder is not None else None

    @property
    def entries(self) -> list[LogEntry]:
        """Every line of session.log, oldest first; none before anything is logged."""
        return [LogEntry(line) for line in self._lines() if line.strip()]

    def _lines(self) -> list[str]:
        log = self.path
        if log is None or not log.is_file():
            return []
        return log.read_text(encoding="utf-8").splitlines()

    def record(self, line: str) -> None:
        """Append line to session.log, stamped with the time it was written."""
        if self.path is None:
            return
        # A project's main session has no folder until something is written in it.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{LogTimestamp.now()} {line}\n")

    def by(self, chat: ChatPointer | None) -> ChatLog:
        """The lines chat writes in this log, each pointing at it; ``no-chat`` when no chat is known, such as for work
        run in process."""
        return ChatLog(self, chat)

    def append_trace(self, failure: BaseException, tool: str) -> int:
        """Append failure's trace to session.err; the line its header is on."""
        err = self.error_path
        err.parent.mkdir(parents=True, exist_ok=True)
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
            self.record("--- 1")

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
            raise LoopNotFoundError("no loops in session.log; run mark-loop first")
        opened = self.loop_at(loop_number)
        if not opened.entries:
            raise LoopNotFoundError(f"loop {loop_number} not found (missing --- {loop_number} in session.log?)")
        return f"# Loop {loop_number} ({self._session.name})\n\n" + opened.expanded_text()

    def loop_to_note(self, loop: int | None) -> int:
        """The loop a note goes in: loop, which the log must have marked, else the latest with lines, else the latest."""
        if loop is not None:
            if loop < 1 or self.last_loop_number < loop:
                raise LoopNotFoundError(f"loop {loop} not found in session.log (no --- {loop} marker)")
            return loop
        chosen = self.latest_loop_with_entries or self.last_loop_number
        if chosen < 1:
            raise LoopNotFoundError("no loop in session.log; run mark-loop first")
        return chosen

    def paths_named_by(self, tool_input: dict) -> list[Path]:
        """The files and folders the arguments of a tool call name, each once."""
        raw_paths = tool_input.get("paths")
        listed = raw_paths if isinstance(raw_paths, list) else []
        tokens = [str(tool_input.get(key) or "").strip() for key in _TOOL_INPUT_PATH_KEYS] + [str(item).strip() for item in listed]
        return [Path(token) for token in dict.fromkeys(token for token in tokens if token)]

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

    def line(self, line: str) -> None:
        """Append line with this chat's pointer, such as a practice's validate line."""
        if self._log.path is None:
            return
        self._log.record(f"{line} {self._chat}")
        self._log.injected_rules.clear()

    def validation(self, practice: PracticeSessionOutput | FidelitySessionOutput, violations: list[str]) -> None:
        """Log a validate of practice at its working fidelity, with each violation's synopsis; no violations is a
        validate that passed."""
        detail = " ".join(violations)
        self.line(f"validate {type(practice.guidance).__name__} {practice.working_fidelity} {detail}".rstrip())

    def action(self, action: str, paths: list[Path], practices: list[PracticeSessionOutput | FidelitySessionOutput] | None = None) -> None:
        """Log action with the paths it worked on and what each practice it worked on was working at."""
        if self._log.path is None:
            return
        worked_on = list(practices or [])
        parts = (
            action,
            ", ".join(str(path) for path in paths),
            ", ".join(entry.name for entry in worked_on),
            ", ".join(entry.working_fidelity for entry in worked_on if entry.working_fidelity),
            ", ".join(entry.working_format for entry in worked_on if entry.working_format),
            self._log.injected_rules.text,
            str(self._chat),
        )
        self._log.record(" ".join(part for part in parts if part))
        self._log.injected_rules.clear()

    def guidance_action(self, action: str, practices: list[PracticeSessionOutput | FidelitySessionOutput]) -> None:
        """Log a guidance action on practices, with the session's workpath and each practice's folder as the paths it
        worked on."""
        workpath = self._log.session.workpath
        work = [Path(workpath).resolve()] if workpath is not None else []
        folders = [practice.folder for practice in practices]
        self.action(action, list(dict.fromkeys([*work, *folders])), practices)

    def tool(self, tool_name: str, tool_input: dict | None = None) -> None:
        """Append a ``tool …`` line for a tool call, with the paths its arguments name."""
        name = (tool_name or "").strip()
        if self._log.path is None or not name:
            return
        parts = [_TOOL_VERB, name]
        paths = self._log.paths_named_by(tool_input or {})
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        rules = self._log.injected_rules.text
        if rules:
            parts.append(rules)
        # A tool line names its chat only when one is known; most tool calls come from a chat the server can name.
        if not self._chat.is_missing:
            parts.append(str(self._chat))
        self._log.record(" ".join(parts))
        self._log.injected_rules.clear()

    def note(self, message: str, paths: list[Path] | None = None) -> None:
        """Record a correction or decision in the current loop."""
        text = (message or "").strip()
        if self._log.path is None or not text:
            return
        parts = ["note", text]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        parts.append(str(self._chat))
        self._log.record(" ".join(parts))

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
        """Append the full trace of failure to session.err and a line pointing at it to session.log."""
        if self._log.path is None:
            return
        line_number = self._log.append_trace(failure, tool)
        named = [tool.strip()] if tool.strip() else []
        self._log.record(" ".join(["error", *named, str(self._log.error_path), str(line_number), str(self._chat)]))

    def next_loop(self) -> Loop:
        """Mark the next loop, one past the highest marked, pointing at this chat."""
        number = self._log.last_loop_number + 1
        self._log.record(f"--- {number} {self._chat}")
        return self._log.loop_at(number)

    def mark_loop(self) -> int:
        """Mark the next loop and answer its number."""
        return self.next_loop().number
