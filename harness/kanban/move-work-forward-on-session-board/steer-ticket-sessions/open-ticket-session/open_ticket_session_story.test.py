from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----open-ticket-session
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-realization.md

# Story: Open Ticket Session
# Actor: Person
#
# Acceptance criteria:
# - Choose Session Root: a person browses to the folder the ticket's work goes in, for the whole ticket or one practice, and can go back to the default. Observed.
with story("Open Ticket Session"):
    with scenario("Open a new ticket"):
        # Evidence: observed: kanban_tools_spec 'that opens a new ticket' — 'should return the new ticket in Discovery', 'should leave the current session as it is'; kanban_spec 'should name Generate on story_map as next'.
        with given("checkout-flow is the active [ticket](../../../.context/kanban-model.md#ticket--card)"):
            pass
        with when("the Person opens a new ticket titled Pet visits"):
            # Person -> Ticket.new('Pet visits', 'feature')
            # Ticket -> Session.new('pet-visits', <repo>, <repo>, {title, scope, parent}, is_current=False)
            # Ticket <- Ticket pet-visits
            pass
        with then("pet-visits is In progress in Discovery, titled Pet visits"):
            pass
        with and_("its next step is Generate on stories-story_map"):
            pass
        with and_("checkout-flow is still the active ticket"):
            pass
    with scenario("Ask a chat to open a ticket"):
        # Evidence: observed: board-page.ts openNewTicket; tests/board-surface.spec.ts 'with no chat connected' shows + Ticket off.
        with given("a chat is connected to the session board"):
            pass
        with when("the Person asks for a new ticket from the board's header"):
            # Board page -> Chat.send('fill', 'Open a new ticket with ticket.new, titled: ')
            pass
        with then("the chat's prompt holds Open a new ticket with ticket.new, titled: for the Person to finish"):
            pass
    with scenario("Keep + Ticket off with no chat"):
        # Evidence: observed: tests/board-surface.spec.ts 'with no chat connected' shows + Ticket off.
        with given("no chat is connected to the session board"):
            pass
        with when("the session board draws its header"):
            # Board page -> ChatClient.canSend <- false
            pass
        with then("+ Ticket is off"):
            pass
    with scenario("Open a ticket on a folder of the repository"):
        # Evidence: observed: kanban_tools_spec 'that opens a ticket on a folder in the repository' — 'should save that folder as the session's workpath'; 'that opens a ticket with no folder' — 'should leave the session working on the repository'.
        with given("the [repository](../../../.context/kanban-model.md#repo) has the folder src/billing"):
            pass
        with when("the Person opens a ticket titled Billing report on src/billing"):
            # Person -> Ticket.new('Billing report', 'feature', '', 'src/billing')
            # Ticket -> Session.new('billing-report', <repo>/src/billing, <repo>, fields, is_current=False)
            pass
        with then("billing-report's [session](../../../.context/kanban-model.md#session) works in src/billing"):
            pass
        with and_("the details show its root as src/billing"):
            pass
    with scenario("Choose a ticket's root"):
        # Evidence: observed: root-choice-client.spec 'that a person browses into a folder for the session root' — 'should list the folders inside it', 'should make it the ticket's root'; kanban_tools_spec 'should keep the folder as the session's work folder'.
        with given("checkout-flow works on the whole [repository](../../../.context/kanban-model.md#repo)"):
            pass
        with and_("the repository has src/billing and src/visits under src"):
            pass
        with when("the Person browses src for checkout-flow's root"):
            # Person -> Board.folders('src')
            # Board <- src/billing, src/visits
            pass
        with then("the roots dialog lists src/billing and src/visits"):
            pass
        with when("the Person chooses src/visits as checkout-flow's root"):
            # Person -> Ticket.choose_root('src/visits')
            # Ticket -> Session.change_workpath(<repo>/src/visits)
            pass
        with then("checkout-flow's root reads src/visits"):
            pass
        with and_("each practice's default root sits under src/visits"):
            pass
    with scenario("Choose one practice's root and go back to its default"):
        # Evidence: observed: root-choice-client.spec 'that a person chooses a folder for one practice's root' — 'should show it as that practice's chosen root', 'and then goes back to its default'; kanban_tools_spec 'should leave every other practice on its default root'.
        with given("checkout-flow's Stories [practice](../../../.context/kanban-model.md#practiceguidance) writes under its default root"):
            pass
        with when("the Person chooses src/billing for checkout-flow's Stories root"):
            # Person -> Ticket.choose_practice_root('stories', 'src/billing')
            # Ticket -> Session.choose_output_root('stories', <repo>/src/billing)
            pass
        with then("the Stories root reads src/billing, chosen by the Person"):
            pass
        with and_("every other practice stays on its default root"):
            pass
        with when("the Person puts Stories back on its default root"):
            # Person -> Ticket.use_default_practice_root('stories')
            # Ticket -> Session.forget_output_root('stories')
            pass
        with then("the Stories root is the default again"):
            pass
