"""ChatInjections - the rules a hook gave each chat of one session, kept in its folder for that chat's next prompt."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload, HookResult
    from space.session.session import Session

_FOLDER = "chat-injections"
_LAST_RULES_FILE = "last-chat-injected-rules.md"


class ChatInjections:
    """The rules a hook gave each chat of one session, kept in the session's ``chat-injections`` folder so the next
    prompt in the same chat gets them again, and never another chat's."""

    _CHAT_START = "--- chat ---"
    _CHAT_END = "--- end chat ---"
    # Text that tells the person rules were injected; the model never needs it in a prompt.
    _NOTICE_LINES = frozenset(
        {
            "These rules are injected in the chat.",
            "The user sees the chat line. Do not paste the rule text into the chat.",
            "Before you continue, echo the following message to the user:",
            "The following rules need to be followed while editing this document:",
        }
    )
    # The openings of a rules dump made for one edit; replaying it into a later prompt would repeat a stale check.
    _DUMP_OPENINGS = (
        "You just edited ",
        "The following rules need to be followed",
        "Before you continue, echo the following message",
    )
    _DUMP_LINE = "The following rules need to be followed while editing this document:"

    def __init__(self, session: Session) -> None:
        self._session = session

    def path_for(self, chat_id: str) -> Path:
        """The file that keeps chat_id's injection."""
        safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in chat_id)
        return self._session.session_path / _FOLDER / f"{safe.strip('-') or 'unknown'}.md"

    def keep(self, result: HookResult, payload: HookPayload) -> None:
        """Remember result's rules for the chat the event came from, and the last rules sent in the session."""
        self._retire_shared_inject()
        body = (result.additional_context or "").strip()
        if body and payload.chat_id:
            dest = self.path_for(payload.chat_id)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8")
        folder = self._session.session_path
        folder.mkdir(parents=True, exist_ok=True)
        (folder / _LAST_RULES_FILE).write_text(result.additional_context or "", encoding="utf-8")

    def replay(self, payload: HookPayload, result: HookResult) -> HookResult:
        """result with the rules kept for the prompt's chat, when the hooks gave none of their own."""
        chat_id = payload.conversation_id.strip()
        if result.additional_context or not chat_id:
            return result
        dest = self.path_for(chat_id)
        if not dest.is_file():
            return result
        kept = dest.read_text(encoding="utf-8")
        if self.is_rules_dump(kept):
            dest.unlink(missing_ok=True)
            return result
        result.additional_context = self._model_context(kept) or None
        return result

    def is_rules_dump(self, body: str) -> bool:
        text = body.lstrip()
        return bool(text) and (text.startswith(self._DUMP_OPENINGS) or self._DUMP_LINE in text)

    def _model_context(self, body: str) -> str:
        """Rule text for the model. The injected-rules notice stays out of the prompt."""
        kept: list[str] = []
        hide = False
        for line in body.splitlines():
            stripped = line.strip()
            if stripped in (self._CHAT_START, self._CHAT_END):
                hide = stripped == self._CHAT_START
                continue
            if not hide and not stripped.startswith("rules injected") and stripped not in self._NOTICE_LINES:
                kept.append(line)
        return "\n".join(kept).strip()

    def _retire_shared_inject(self) -> None:
        """Remove the always-apply rule older installs shared between every chat."""
        shared = self._session.repo_path / ".cursor" / "rules" / "practices" / "chat-inject.mdc"
        shared.unlink(missing_ok=True)
        shared.with_suffix(".sent").unlink(missing_ok=True)
