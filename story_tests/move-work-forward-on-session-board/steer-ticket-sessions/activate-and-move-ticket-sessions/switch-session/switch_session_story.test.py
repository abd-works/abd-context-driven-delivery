from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Activate And Move Ticket Sessions
# Map: ../../../../.context/story-map.md#s-person----switch-session
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Switch Session
# Actor: Person
#
# Acceptance criteria:
# - A chat in a ticket's worktree works on that ticket; no chat moves. Requested 2026-11-10.
with story("Switch Session"):
    with scenario("Work on the ticket from a chat in its worktree"):
        with given("billing-report is open in its own worktree"):
            pass
        with when("a chat in that worktree asks which session it works on"):
            # Chat -> Sessions.current()
            pass
        with then("the answer is billing-report"):
            pass
