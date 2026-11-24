from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Check CDD Server Health On Board
# Map: ../../../.context/story-map.md#s-person----update-board-and-cdd
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Update Board And CDD
# Actor: Person
with story("Update Board And CDD"):
    with scenario("Install the board again"):
        # Evidence: observed: board-client.spec 'that a person has pressed Update'; board-page.ts update posts App.install of the Kanban app through its generated client (editor-app-client.ts kanban).
        with given("the board is open"):
            pass
        with when("the Person presses Update"):
            # Board page -> App: install (app.install, the Kanban app)
            # App -> npm install  [External: npm]
            # App -> npm run build  [External: npm]
            pass
        with then("the Kanban app is installed again through App.install, which installs its packages and rebuilds its page"):
            pass
        with and_("the page loads again from the new build"):
            pass
    with scenario("Say why the board's install failed"):
        # Evidence: observed: board-client.spec 'with an install that fails'; app.py AppNotStarted.
        with given("npm cannot install the Kanban app"):
            pass
        with when("the Person presses Update"):
            # Board page -> App: install
            # App <- AppNotStarted
            pass
        with then("a toast says the Kanban install failed, with the reason and the fix"):
            pass
        with and_("the page keeps running as it was"):
            pass
