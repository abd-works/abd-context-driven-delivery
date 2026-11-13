"""A session's file comments: what a person wrote on lines of a file in the viewer, kept in the session's folder, and
sent to a chat for the agent to act on. A comment is not sent, then sent, then processed once the chat's turn that
worked on it has ended."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.chat.chat import DONE, FAILED, Chat
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile
from harness.mcp.mcp_server import mcp

if TYPE_CHECKING:
    from space.session.session import Session

COMMENTS_FILE = "file-comments.json"
NOT_SENT = "not_sent"
SENT = "sent"
PROCESSED = "processed"
FileCommentState = Literal["not_sent", "sent", "processed"]
# A chat's message moves on once the chat is done with it; a failed one never reached the chat.
_UNDELIVERED = (FAILED,)


class FileCommentNotFoundError(LookupError):
    """A comment named by an anchor the session's file comments do not hold, such as one deleted on another page."""

    def __init__(self, anchor: str) -> None:
        super().__init__(f"no file comment at {anchor}")
        self.anchor = anchor


class FileComment:
    """One comment on lines start_line to end_line of a file, named from the project, with the text selected there; the
    chat and message it was sent in once it is sent."""

    # A comment's state is read from the chat's message, never kept twice: sent until the chat is done with the message.

    def __init__(self, path: str, start_line: int, end_line: int, selected_text: str, text: str, chat: str = "", message: str = "") -> None:
        self._path = path
        self._start_line = start_line
        self._end_line = end_line
        self._selected_text = selected_text
        self._text = text
        self._chat = chat
        self._message = message

    @classmethod
    def from_record(cls, record: dict) -> FileComment:
        return cls(record["path"], record["start_line"], record["end_line"], record["selected_text"], record["text"], record.get("chat", ""), record.get("message", ""))

    @property
    @data_field
    def anchor(self) -> str:
        """The lines the comment is on, such as src/checkout/order.py:L12-L14: one comment per selection of a file."""
        return f"{self._path}:L{self._start_line}-L{self._end_line}"

    @property
    @data_field
    def path(self) -> str:
        return self._path

    @property
    @data_field
    def start_line(self) -> int:
        return self._start_line

    @property
    @data_field
    def end_line(self) -> int:
        return self._end_line

    @property
    @data_field
    def selected_text(self) -> str:
        return self._selected_text

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def state(self) -> FileCommentState:
        """Not sent until a chat queued it; then sent, until the chat's turn that worked on it ended, or the chat forgot
        it once handled; a message the chat could not show leaves the comment not sent."""
        if not self._message:
            return NOT_SENT
        sent = Chat.load(self._chat).message(self._message)
        if sent is None or sent.state == DONE:
            return PROCESSED
        return NOT_SENT if sent.state in _UNDELIVERED else SENT

    @property
    def prompt(self) -> str:
        """What the chat reads: the file and lines with the comment, then each selected line marked >, as the report's
        Fix marks the lines it names."""
        lines = self._selected_text.splitlines()
        marked = [f"> {self._start_line + offset} | {line}" for offset, line in enumerate(lines)]
        return "\n".join([f"{self._path}:{self._start_line}-{self._end_line}: {self._text}", *marked])

    def sent_in(self, chat: str, message: str) -> FileComment:
        """This comment, sent to chat in message."""
        return FileComment(self._path, self._start_line, self._end_line, self._selected_text, self._text, chat, message)

    @property
    def record(self) -> dict:
        return {
            "path": self._path,
            "start_line": self._start_line,
            "end_line": self._end_line,
            "selected_text": self._selected_text,
            "text": self._text,
            "chat": self._chat,
            "message": self._message,
        }


@identity("session_file")
@language_adapter(language="typescript")
@agent_toolset
class FileComments:
    """Comment on lines of a session's files, send the comments to a chat, and clear the ones the chat has processed.
    The comments are kept in the session's folder, so they stay when a page reloads."""

    def __init__(self, session: Session) -> None:
        self._session = session

    @classmethod
    @tool_subject
    def load(cls, session: str, *, call: ToolCall) -> FileComments:
        """The file comments of the session whose session.json is session, a path from the project the call names."""
        return call.session_named(session).file_comments

    @property
    @data_field
    def session_file(self) -> str:
        return self._session.from_project(self._session.session_file)

    @property
    @data_field
    def comments(self) -> list[FileComment]:
        """Every comment, in the order written."""
        return [FileComment.from_record(record) for record in self._file.read().get("comments", [])]

    @mcp
    @agent_tool
    @noSessionLog
    def on(self, path: str) -> list[FileComment]:
        """List the comments on path, a file named from the project, each with the lines it is on and whether it is not sent, sent, or processed."""
        return [comment for comment in self.comments if comment.path == path]

    @mcp
    @agent_tool
    @noSessionLog
    def add(self, path: str, start_line: int, end_line: int, selected_text: str, text: str) -> FileComment:
        """Comment text on lines start_line to end_line of path, a file named from the project, whose selected_text is what those lines hold; a new comment on the same lines replaces the one there."""
        added = FileComment(path, start_line, end_line, selected_text, text)
        self._save([*(comment for comment in self.comments if comment.anchor != added.anchor), added])
        return added

    @mcp
    @agent_tool
    @noSessionLog
    def remove(self, anchor: str) -> FileComments:
        """Delete the comment at anchor, such as src/checkout/order.py:L12-L14."""
        self._save([comment for comment in self.comments if comment.anchor != self._held(anchor).anchor])
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def send(self, anchor: str, chat: str) -> FileComment:
        """Send the comment at anchor to chat, a chat's id, in its prompt for the person to review, with the file, the lines, and the session; the comment is sent once the chat has it."""
        return self._sent([self._held(anchor)], chat)[0]

    @mcp
    @agent_tool
    @noSessionLog
    def send_open(self, chat: str) -> FileComments:
        """Send every comment not yet sent to chat, a chat's id, in one prompt; the comments already sent are not sent again."""
        open_comments = [comment for comment in self.comments if comment.state == NOT_SENT]
        if open_comments:
            self._sent(open_comments, chat)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def clear_processed(self) -> FileComments:
        """Delete the comments the chat has processed, keeping the ones not sent or still sent."""
        self._save([comment for comment in self.comments if comment.state != PROCESSED])
        return self

    def _sent(self, sending: list[FileComment], chat: str) -> list[FileComment]:
        """Queue the comments for chat in one message, then keep each as sent in it; a chat that is not connected
        refuses the message, and the comments stay not sent."""
        prompt = "\n\n".join([*(comment.prompt for comment in sending), f"session={self.session_file}"])
        message = Chat.load(chat).queue("fill", prompt).message
        anchors = {comment.anchor for comment in sending}
        kept = [comment.sent_in(chat, message) if comment.anchor in anchors else comment for comment in self.comments]
        self._save(kept)
        return [comment for comment in kept if comment.anchor in anchors]

    def _held(self, anchor: str) -> FileComment:
        found = next((comment for comment in self.comments if comment.anchor == anchor), None)
        if found is None:
            raise FileCommentNotFoundError(anchor)
        return found

    def _save(self, comments: list[FileComment]) -> None:
        self._file.write({"comments": [comment.record for comment in comments]})

    @property
    def _file(self) -> JsonFile:
        return JsonFile(Path(self._session.session_path) / COMMENTS_FILE)
