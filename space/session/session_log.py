"""SessionLog — a session's ``session.log`` and ``session.err``: what each action, tool call, note, and loop wrote."""

from __future__ import annotations

import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from space.session.chat_pointer import NO_CHAT, ChatPointer

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.guidance.rule import RulesCollection
    from space.session.session import Session

LOG_FILE = "session.log"
ERROR_FILE = "session.err"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_LOOP_MARKER = re.compile(r"---\s+(\d+)(?:\s|$)")
# Verbs older session logs wrote, by the verb that now records the same thing.
_FORMER_VERBS = {"pull": "move"}
# The actions a chat injected under a loop can be added to, when the loop's lines name one of them.
_KNOWN_ACTIONS = ("generate", "validate", "sketch", "document", "satisfy", "iterate", "createRule")
# The arguments of a tool call that name a file or folder the call worked on.
_TOOL_INPUT_PATH_KEYS = ("path", "file_path", "target_directory", "working_directory", "transcript_path", "agent_transcript_path")


class LoopNotFoundError(LookupError):
    """A loop was asked for that the session log has not marked, such as loop 4 of a log marked up to 3."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class LogEntry:
    """One line of a session log: ``<time> <verb> <words...>``, the words being the subject the verb acted on."""

    # Action lines name a practice by its folder (`clean_engineering`) and validate lines by its class
    # (`CleanEngineering`).

    def __init__(self, line: str) -> None:
        self._parts = line.split()

    @property
    def time(self) -> str:
        return self._parts[0] if self._parts else ""

    @property
    def verb(self) -> str:
        """What the line records, such as move or generate; a log written before moves were named move says pull."""
        written = self._parts[1] if len(self._parts) > 1 else ""
        return _FORMER_VERBS.get(written, written)

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

    def __init__(self, number: int, log: SessionLog, entries: list[str] | None = None) -> None:
        self.number = number
        self.entries: list[str] = list(entries or [])
        self._log = log

    def text(self) -> str:
        """Log lines for this loop plus any chat injected under them."""
        return "\n".join(self.entries)

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

    def inject(self, chat_file: Path, *, action: str | None = None) -> None:
        """Put the chat kept in chat_file under this loop, and point the log's lines for action at it: the action
        named, else the last one this loop's lines name."""
        chat, body = ChatPointer.in_chat_file(Path(chat_file))
        action_name = action or self._action_from_entries()
        if action_name:
            self._log.append_chat(action_name, chat)
        self.entries.append(str(chat))
        if body:
            self.entries.extend(body.splitlines())

    def _action_from_entries(self) -> str:
        for line in reversed(self.entries):
            for name in _KNOWN_ACTIONS:
                if f" {name} " in f" {line} " or line.endswith(f" {name}"):
                    return name
        return ""


class SessionLog:
    """The log of one session: ``session.log``, one timestamped line per action, tool call, note, and loop marker, each
    ending with a pointer to the chat that caused it, and ``session.err``, the full trace of each failure a log line
    points at. A session without a folder has a log that writes nothing."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # The rules an inject_rules hook gave the agent since the last log line, each with the edited file it matched.
        self._injected: list[tuple[RulesCollection, str]] = []
        # A chat named for the next log line only, ahead of the chat of the tool call being served.
        self._chat: ChatPointer | None = None

    @staticmethod
    def timestamp(moment: datetime) -> str:
        """A moment as session logs write it."""
        return moment.astimezone(timezone.utc).strftime(_TIMESTAMP_FORMAT)

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
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(f"{self.timestamp(datetime.now(timezone.utc))} {line}\n")

    def note_chat(self, chat: ChatPointer) -> None:
        """Point the next log line at chat, in place of the chat of the tool call being served."""
        self._chat = chat

    def note_chat_given(self, conversation_id: str, transcript_path: str, transcript_lines: str) -> None:
        """Point the next log line at the chat a call from Python names in its own arguments; an MCP call's chat is
        already being served."""
        chat = ChatPointer.of(conversation_id, transcript_path, transcript_lines)
        if chat is not None:
            self.note_chat(chat)

    def note_injected_rules(self, rules: RulesCollection, matched_path: str) -> None:
        """Note that an inject_rules hook gave the agent rules for the edited file at matched_path, so the next log line
        names each of those rules with its practice and fidelity."""
        if self.path is None or not matched_path:
            return
        entry = (rules, matched_path)
        if entry not in self._injected:
            self._injected.append(entry)

    def line(self, line: str) -> None:
        """Append line with the noted chat's pointer, such as a practice's validate line."""
        if self.path is None:
            return
        self.record(f"{line} {self._line_chat()}")
        self._injected.clear()

    def action(self, action: str, paths: list[Path]) -> None:
        """Log action with the paths it worked on and what the session's opened practices were working at."""
        if self.path is None:
            return
        self.record(self._action_line(action, paths))
        self._injected.clear()

    def guidance_action(self, action: str) -> None:
        """Log a guidance action on the practices the session has opened, with the workpath and each practice's folders
        as the paths it worked on."""
        workpath = self._session.workpath
        work = [Path(workpath).resolve()] if workpath is not None else []
        folders = [folder for practice in self._session.opened_practices for folder in practice.folders]
        self.action(action, list(dict.fromkeys([*work, *folders])))

    def tool(self, tool_name: str, tool_input: dict | None = None) -> None:
        """Append a ``tool …`` line for a tool call, with the paths its arguments name."""
        name = (tool_name or "").strip()
        if self.path is None or not name:
            return
        parts = ["tool", name]
        paths = self._paths_from_tool_input(tool_input or {})
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        rules = self._rule_text()
        if rules:
            parts.append(rules)
        # A tool line names its chat only when one is known; most tool calls come from a chat the server can name.
        chat = self._line_chat()
        if not chat.is_missing:
            parts.append(str(chat))
        self.record(" ".join(parts))
        self._injected.clear()

    def note(self, message: str, paths: list[Path] | None = None) -> None:
        """Record a correction or decision in the current loop."""
        text = (message or "").strip()
        if self.path is None or not text:
            return
        parts = ["note", text]
        if paths:
            parts.append(", ".join(str(path) for path in paths))
        parts.append(str(self._line_chat()))
        self.record(" ".join(parts))

    def failure(self, failure: BaseException, *, tool: str = "") -> None:
        """Append the full trace of failure to session.err and a line pointing at it to session.log."""
        if self.path is None:
            return
        line_number = self._append_trace(failure, tool)
        parts = ["error", *([tool.strip()] if tool.strip() else []), str(self.error_path), str(line_number)]
        parts.append(str(self._line_chat()))
        self.record(" ".join(parts))

    def _append_trace(self, failure: BaseException, tool: str) -> int:
        """Append failure's trace to session.err; the line its header is on."""
        err = self.error_path
        err.parent.mkdir(parents=True, exist_ok=True)
        line_number = len(err.read_text(encoding="utf-8").splitlines()) + 1 if err.is_file() else 1
        trace = "".join(traceback.format_exception(type(failure), failure, failure.__traceback__))
        header = f"{self.timestamp(datetime.now(timezone.utc))} {tool} {type(failure).__name__}: {failure}".strip()
        with err.open("a", encoding="utf-8") as handle:
            handle.write(f"{header}\n{trace}")
            if not trace.endswith("\n"):
                handle.write("\n")
        return line_number

    def append_chat(self, action: str, chat: ChatPointer) -> None:
        """Point action's earlier log lines at chat, and log that the chat was added."""
        lines = self._lines()
        if lines:
            pointed = [f"{line} {chat}" if f" {action} " in f" {line} " or line.endswith(f" {action}") else line for line in lines]
            self.path.write_text("\n".join(pointed) + "\n", encoding="utf-8")
        self.record(f"{action} chat {chat}")

    @property
    def last_loop_number(self) -> int:
        """The highest ``--- N`` marker in session.log; 0 before a loop is marked."""
        return max((number for number in self._loop_numbers() if number is not None), default=0)

    def _loop_numbers(self) -> list[int | None]:
        return [LogEntry(line).loop_number for line in self._lines()]

    def seed_first_loop(self) -> None:
        """Start a new session's log with ``--- 1`` before any action."""
        if self.path is not None and self.last_loop_number < 1:
            self.record("--- 1")

    def next_loop(self) -> Loop:
        """Mark the next loop, one past the highest marked, pointing at the noted chat or the chat being served."""
        number = self.last_loop_number + 1
        self.record(f"--- {number} {self._line_chat()}")
        return self.loop_at(number)

    def loop_at(self, number: int) -> Loop:
        """Loop number with its lines read from session.log; no lines when the log has not marked it."""
        return Loop(number, self, self._lines_of_loop(number))

    def _lines_of_loop(self, number: int) -> list[str]:
        lines = self._lines()
        numbers = [LogEntry(line).loop_number for line in lines]
        if number not in numbers:
            return []
        start = numbers.index(number)
        end = next((index for index in range(start + 1, len(lines)) if numbers[index] not in (None, number)), len(lines))
        return lines[start:end]

    @property
    def latest_loop_with_entries(self) -> int:
        """The highest marked loop that has lines; 0 when none has."""
        return next((number for number in range(self.last_loop_number, 0, -1) if self._lines_of_loop(number)), 0)

    def mark_loop(self) -> int:
        """Mark the next loop and answer its number."""
        return self.next_loop().number

    def read_loop(self, number: int | None = None) -> str:
        """Loop number, the latest with lines when none is named, with each line's chat transcript put under it."""
        loop_number = self.latest_loop_with_entries if number is None else number
        if loop_number < 1:
            raise LoopNotFoundError("no loops in session.log; run mark-loop first")
        opened = self.loop_at(loop_number)
        if not opened.entries:
            raise LoopNotFoundError(f"loop {loop_number} not found (missing --- {loop_number} in session.log?)")
        return f"# Loop {loop_number} ({self._session.name})\n\n" + opened.expanded_text()

    def append_note(self, note: str, loop: int | None = None, paths: list[str] | None = None) -> str:
        """Append note to loop, the latest with lines when none is named, with the paths it names."""
        text = (note or "").strip()
        if not text:
            raise ValueError("note is required")
        loop_number = self._loop_to_append_to(loop)
        body = text if text.lower().startswith(f"loop {loop_number}") else f"loop {loop_number}: {text}"
        self.note(body, [Path(item) for item in (paths or []) if str(item).strip()] or None)
        return f"appended note to {self.path or LOG_FILE} (loop {loop_number})"

    def _loop_to_append_to(self, loop: int | None) -> int:
        if loop is not None:
            if loop < 1 or self.last_loop_number < loop:
                raise LoopNotFoundError(f"loop {loop} not found in session.log (no --- {loop} marker)")
            return loop
        chosen = self.latest_loop_with_entries or self.last_loop_number
        if chosen < 1:
            raise LoopNotFoundError("no loop in session.log; run mark-loop first")
        return chosen

    def _line_chat(self) -> ChatPointer:
        """The chat the next log line points at: one noted for it, else the chat of the call being served, else
        ``no-chat``. A noted chat is used once."""
        chat = self._chat or ChatPointer.current() or NO_CHAT
        self._chat = None
        return chat

    def _action_line(self, action: str, paths: list[Path]) -> str:
        opened = self._session.opened_practices
        parts = (
            action,
            ", ".join(str(path) for path in paths),
            ", ".join(entry.name for entry in opened),
            ", ".join(entry.working_fidelity for entry in opened if entry.working_fidelity),
            ", ".join(entry.working_format for entry in opened if entry.working_format),
            " ".join(entry.root_node_name for entry in opened if entry.root_node_name),
            self._rule_text(),
            str(self._line_chat()),
        )
        return " ".join(part for part in parts if part)

    def _rule_text(self) -> str:
        named = {(rules.practice_key, rules.fidelity_name, rule.slug, path) for rules, path in self._injected for rule in rules}
        return " ".join(" ".join(part for part in entry if part) for entry in sorted(named))

    @staticmethod
    def _paths_from_tool_input(tool_input: dict) -> list[Path]:
        raw_paths = tool_input.get("paths")
        listed = raw_paths if isinstance(raw_paths, list) else []
        tokens = [str(tool_input.get(key) or "").strip() for key in _TOOL_INPUT_PATH_KEYS] + [str(item).strip() for item in listed]
        return [Path(token) for token in dict.fromkeys(token for token in tokens if token)]

    def instructions(self) -> str:
        """How an agent keeps this log: what every line points at, how loops are marked and read, and where the
        session's files go."""
        return (
            "Session owns logging once sessions.switch has run. "
            "CHAT POINTERS — required for continued conversations: every log line ends with a chat pointer, "
            "the chat id, the agent transcript JSONL path, and the transcript line range "
            "(`{id} {transcript} {lines}`), or `no-chat` when no chat can be named. "
            "MCP: pass conversation_id, transcript_path, transcript_lines on any tool call; the server takes "
            "them off the call and every line that call writes points at that chat. A Claude Code chat may "
            "pass conversation_id alone, and its transcript is found by that id. "
            "Without them the pointer comes from CDD_CONVERSATION_ID, CDD_TRANSCRIPT_PATH, CDD_TRANSCRIPT_LINES. "
            "Long threads: use an accurate slice for this turn or a cumulative range (e.g. 1-1152, "
            "then 1-1450) so read_loop can inline the full dialogue for that loop. "
            "Missing chat on an earlier line: append_chat(action, chat) or session.append_log "
            "(/append-log); never hand-edit session.log. "
            "MARK-LOOP — link the entire conversation span: call session.mark_loop (/mark-loop) only "
            "with chat fields on that MCP invoke. Dispatch writes tool session.mark_loop with a pointer; "
            "the --- N marker line records the same pointer when bound—both tie the loop to the transcript. "
            "After marking, log actions in that loop with the same thread id and growing line ranges so "
            "read_loop(number) expands every line in the loop with matching transcript slices. "
            "WHERE LINES COME FROM: every @agent_tool call the MCP host serves writes a tool line "
            "(SessionLog.tool); a guidance action writes its line through SessionLog.guidance_action "
            "(Validate writes each practice's log_validation instead); SessionLog.failure records each failed "
            "action or MCP call. Cursor hooks do not write session.log. "
            "SessionLog.action(action, paths) records an action with the paths it touched. "
            "Do not duplicate unless a line lacks detail. "
            "sessions.switch seeds --- 1 in a new session (chat on that marker when bound at open). "
            "When the user corrects ai behavior or output, session.append_log with note, optional loop, "
            "paths, and chat fields. "
            "SESSION ARTIFACTS: with session_path set, write every large/temporary agent output "
            "(graph JSON, MCP dumps, probes) under session_path—not only under Cursor agent-tools. "
            "List artifact paths on append_log. "
            "PERMANENT ARTIFACTS: fidelity outputs belong to the folder the session was opened on, its "
            "workpath, and sit at the repository root only when the session names no folder. Markdown and "
            "drawio go in that folder's .context/; code goes straight in that folder. "
            f"Log file: {self.path or LOG_FILE}. Errors: {self.error_path or ERROR_FILE}."
        )
