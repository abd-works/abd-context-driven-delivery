from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----choose-ticket-workpath-and-roots
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Choose Ticket Workpath And Roots
# Actor: Person
#
# Acceptance criteria:
# - Choose Session Root: a person browses to the folder the ticket's work goes in, for the whole ticket or one practice, and can go back to the default. Observed.
with story("Choose Ticket Workpath And Roots"):
    with scenario("Choose a ticket's workpath"):
        # Evidence: observed: root-choice-client.spec 'that a person browses into a folder for the session workpath' — 'should list the folders inside it', 'should make it the ticket's workpath'; kanban_tools_spec 'should keep the folder as the session's work folder'.
        with given("checkout-flow works on the whole [repository](../../../.context/kanban-model.md#repo)"):
            pass
        with and_("the repository has src/billing and src/visits under src"):
            pass
        with when("the Person browses src for checkout-flow's workpath"):
            # Person -> Board.folders('src')
            # Board <- src/billing, src/visits
            pass
        with then("the roots dialog lists src/billing and src/visits"):
            pass
        with when("the Person chooses src/visits as checkout-flow's workpath"):
            # Person -> Ticket.choose_workpath('src/visits')
            # Ticket -> Session.choose_workpath(<repo>/src/visits)
            pass
        with then("checkout-flow's workpath reads src/visits"):
            pass
        with and_("each practice's default practice root sits under src/visits"):
            pass
    with scenario("Choose one practice's root and go back to its default"):
        # Evidence: observed: root-choice-client.spec 'that a person chooses a folder for one practice's root' — 'should show it as that practice's chosen root', 'and then goes back to its default'; kanban_tools_spec 'should leave every other practice on its default root'.
        with given("checkout-flow's Stories [practice](../../../.context/kanban-model.md#practiceguidance) writes under its default root"):
            pass
        with when("the Person chooses src/billing for checkout-flow's Stories root"):
            # Person -> Ticket.choose_practice_root('stories', 'src/billing')
            # Ticket -> PracticeSessionOutput(stories).keep_root(<repo>/src/billing)
            pass
        with then("the Stories root reads src/billing, chosen by the Person"):
            pass
        with and_("every other practice stays on its default root"):
            pass
        with when("the Person puts Stories back on its default root"):
            # Person -> Ticket.use_default_practice_root('stories')
            # Ticket -> PracticeSessionOutput(stories).use_default_root()
            pass
        with then("the Stories root is the default again"):
            pass
