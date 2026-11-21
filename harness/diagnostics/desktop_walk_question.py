"""What the cadence asks the person before a timed e2e run's desktop walk. A desktop walk drives the real Claude
desktop app by computer control, so it takes the person's screen and keyboard and runs only when they say yes. The
e2e tier's own specs start at once, in the background, whatever the answer; the question is kept in the cdd home,
where every chat's health report reads it, so the first chat to answer answers for all of them."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from harness.installation.data_class import data_field
from harness.installation.json_file import JsonFile

QUESTION_FILE = "desktop-walk-question.json"
# How long the question stays on the chat bar before the run goes on without the walk.
ANSWER_WITHIN = timedelta(minutes=10)
# A desktop story test's file name ends with this (Stories acceptance tests' desktop output).
DESKTOP_STORY_TESTS = "*_story.desktop.md"
STORY_TESTS = "story_tests"
# About how long one desktop story test takes to walk: a screenshot, a judgement and a recorded verdict for each step.
MINUTES_A_STORY_TEST = 3
# The command a yes sends to the chat that asked: the desktop walk's skill, on every desktop story test.
WALK_COMMAND = "/desktop-walk"
YES, NO, NOBODY = "yes", "no", "nobody"
_NOT_RUN = {NO: "not run, the person said no", NOBODY: "not run, nobody answered the question"}


class DesktopWalkQuestion:
    """The question asked for one timed e2e run of one checkout: whether to walk its desktop story tests now, how the
    person answered, and what the run records of it."""

    def __init__(self, folder: Path, checkout: Path | None, clock: Callable[[], datetime]) -> None:
        self._file = JsonFile(Path(folder) / QUESTION_FILE)
        self._checkout = checkout
        self._clock = clock

    def ask(self, run_id: str) -> None:
        """Ask for the timed e2e run called run_id; nothing in a checkout with no desktop story test to walk."""
        if self._story_tests:
            self._file.write({"run_id": run_id, "checkout": str(self._checkout), "asked_at": self._clock().isoformat(), "answer": "",
                              "story_tests": self._story_tests})

    def answer(self, run_id: str, is_yes: bool) -> bool:
        """Take the person's answer for the run called run_id, and say whether the chat that gave it starts the walk:
        only for a yes, and only the first answer, given while the question is still open."""
        with self._file.held():
            asked = self._file.read()
            if asked.get("run_id") != run_id or not self._is_open(asked):
                return False
            self._file.write({**asked, "answer": YES if is_yes else NO})
            return is_yes

    def closed_for(self, run_id: str) -> str:
        """What the e2e run called run_id records of its desktop walk as it ends, an unanswered question closing as
        answered by nobody; nothing for a run the cadence asked no question for, such as one a person started."""
        with self._file.held():
            asked = self._file.read()
            if asked.get("run_id") != run_id:
                return ""
            answer = asked.get("answer") or NOBODY
            self._file.write({**asked, "answer": answer})
        if answer == YES:
            return f"desktop walk: the person said yes; {WALK_COMMAND} was sent to the chat that asked, which records the walk"
        return f"desktop walk: {_NOT_RUN[answer]}"

    @property
    def open(self) -> DesktopWalkQuestion | None:
        """This question while it waits for an answer, for the chats of the checkout it was asked in, whose desktop
        story tests a yes walks; none once answered, or ten minutes after it was asked."""
        return self if self._is_open(self._asked) else None

    @property
    @data_field
    def run_id(self) -> str:
        """Names the timed e2e run the question was asked for, which an answer names back."""
        return self._asked.get("run_id", "")

    @property
    @data_field
    def message(self) -> str:
        """What the dialog asks the person."""
        minutes = self._asked.get("story_tests", 0) * MINUTES_A_STORY_TEST
        return (f"An end-to-end run is due and has started in the background. The desktop walk takes over your screen and "
                f"keyboard for about {minutes} minutes. Run it now?")

    @property
    @data_field
    def command(self) -> str:
        """What the chat that asked runs when the person says yes."""
        return WALK_COMMAND

    @property
    def _asked(self) -> dict:
        return self._file.read()

    @property
    def _story_tests(self) -> int:
        """How many desktop story tests the checkout holds."""
        folder = self._checkout / STORY_TESTS if self._checkout is not None else None
        return len(list(folder.rglob(DESKTOP_STORY_TESTS))) if folder is not None and folder.is_dir() else 0

    def _is_open(self, asked: dict) -> bool:
        if not asked.get("run_id") or asked.get("answer") or asked.get("checkout") != str(self._checkout):
            return False
        return self._clock() - datetime.fromisoformat(asked["asked_at"]) < ANSWER_WITHIN
