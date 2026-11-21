"""GuidanceVersion - the version a session's guidance selection raises on every change, which waiting pages hear."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from harness.guidance.stages import STAGES
from space.session.guidance_selection import GuidanceSelection

if TYPE_CHECKING:
    from space.session.session import Session

# How long a page's waiting read of the guidance selection waits for a change before answering it unchanged, and how
# often it looks for a change another process wrote.
GUIDANCE_WAIT_SECONDS = 25
GUIDANCE_CHECK_SECONDS = 1.0
# Wakes every waiting read of a guidance selection this server changed, so none of them checks the disk in a loop.
_GUIDANCE_CHANGED = threading.Condition()


class GuidanceVersion:
    """The version of one session's guidance selection, kept in its session.json: raised once for each change, so a
    page holding a waiting read hears it at once, and once for a whole update however many practices and formats it
    changed."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # While an update changes many practices and formats, each change leaves the version alone; the update raises it once.
        self._is_batched = False

    def changed(self) -> None:
        """Raise the version, so every page waiting on it hears the change; nothing while an update is batched."""
        if self._is_batched:
            return
        version = self._on_disk() + 1
        self._session.record.update(lambda fields: setattr(fields.guidance, "version", version), f"guidance version {version}")
        with _GUIDANCE_CHANGED:
            _GUIDANCE_CHANGED.notify_all()

    @contextmanager
    def batch(self) -> Iterator[None]:
        """Leave the version alone while the block changes many practices and formats; raise it once after."""
        self._is_batched = True
        try:
            yield
        finally:
            self._is_batched = False
        self.changed()

    def select(self, stages: list[str] | None, practices: list[str] | None, formats: list[str] | None) -> None:
        """Select exactly these stages, practices, and format groups, each list in place of what was selected and a list
        left out unchanged, raising the version once for the whole update."""
        with self.batch():
            if practices is not None:
                self._select_practices(practices)
            if stages is not None:
                chosen = [stage for stage in STAGES.names if stage in stages]
                self._session.record.update(lambda fields: setattr(fields.guidance, "stages", chosen), f"stages {', '.join(chosen)}")
            if formats is not None:
                self._select_format_groups(formats)

    def _select_practices(self, practices: list[str]) -> None:
        """Turn on exactly the practices named, each changed only when it differs, so an unchanged one writes nothing."""
        for output in self._session.own_practices.values():
            if output.enabled != (output.name in practices):
                output.enable(output.name in practices)

    def _select_format_groups(self, formats: list[str]) -> None:
        """Choose exactly the format groups named for every selected fidelity offering them."""
        for group in GuidanceSelection(self._session).formats:
            if group.is_selected != (group.label in formats):
                group.select(group.label in formats)

    def wait_past(self, version: int) -> None:
        """Return once the version is past version: at once when it already is, else as soon as a change raises it, else
        after GUIDANCE_WAIT_SECONDS with it unchanged."""
        deadline = time.monotonic() + GUIDANCE_WAIT_SECONDS
        while self._on_disk() <= version and time.monotonic() < deadline:
            # Woken at once by a change this server makes; a change another process writes is seen within a check.
            with _GUIDANCE_CHANGED:
                _GUIDANCE_CHANGED.wait(min(GUIDANCE_CHECK_SECONDS, max(0.0, deadline - time.monotonic())))
        self._session.record.read_again()

    def _on_disk(self) -> int:
        """The version as session.json holds it now, read past this answer's reads: another call raises it."""
        return self._session.record.fields_on_disk.guidance.version
