from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Guide Work Through Practices
# Map: ../../../.context/story-map.md#s-person----send-next-fidelity-action
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Send Next Fidelity Action
# Actor: Person
#
# Acceptance criteria:
# - Name Next Fidelity: the button names the step that runs next. Observed: `Ticket.next_fidelity`, `Ticket.next_action`.
# - Run next steps through generate, validate, and review for each practice in order. Observed: `Ticket.next_action`.
# - Run next holds on fix violations until they are fixed, and says "fix violations". Observed.
with story("Send Next Fidelity Action"):
    with scenario("Generate the next fidelity in its default format"):
        # Evidence: observed: ticket-client.spec 'with generate next' — 'should ask for the commands of the default format', 'should send those commands in order'; 'should name the step that runs next'; kanban_tools_spec 'should name generate as the next action'.
        with given("billing-report is the active [ticket](../../../.context/kanban-model.md#ticket--card) with nothing recorded and a chat is connected"):
            pass
        with when("the Person runs billing-report's next step"):
            # Person -> Ticket.next_action <- generate on stories-story-map
            # Person -> Ticket.generate_commands(['stories-story-map'], ['markdown'])
            # Ticket <- ['/actions-generate stories-story-map format=markdown']
            # Board page -> Chat.send('command', '/actions-generate stories-story-map format=markdown')
            pass
        with then("Run next read Run next: generate before it ran"):
            pass
        with and_("the chat receives the command /actions-generate stories-story-map format=markdown"):
            pass
    with scenario("Fill the prompt to validate"):
        # Evidence: observed: ticket-client.spec 'should fill the prompt on validate'.
        with given("back-to-backlog is the active [ticket](../../../.context/kanban-model.md#ticket--card) with its story map generated and a chat is connected"):
            pass
        with when("the Person runs back-to-backlog's next step"):
            # Person -> Ticket.next_action <- validate on stories-story-map
            # Board page -> Chat.send('fill', '/actions-validate stories-story-map')
            pass
        with then("the chat's prompt holds /actions-validate stories-story-map"):
            pass
    with scenario("Open the report while violations hold the ticket"):
        # Evidence: observed: ticket-client.spec 'should say fix violations on held violations', 'with violations held and no chat connected' — 'should still offer Run next', 'should open the report'; kanban_tools_spec 'should name satisfy as the next action'; tests/board-surface.spec.ts 'should keep local actions working'.
        with given("checkout-flow's story map has a verb-noun-format violation on .context/story-map.md line 6"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the Person runs checkout-flow's next step"):
            # Person -> Ticket.next_action <- satisfy on stories-story-map
            # Person -> Ticket.report('stories-story-map')
            pass
        with then("Run next read Run next: fix violations"):
            pass
        with and_("the report panel opens on stories-story-map"):
            pass
    with scenario("Record a review with no chat"):
        # Evidence: observed: ticket-client.spec 'Review Fidelity' — 'should offer the review with no chat connected, since it is the person's own approval', 'should show the review done once Run next records it'.
        with given("billing-report's story map is generated and validated with no violations"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the Person runs billing-report's next step"):
            # Person -> Ticket.next_action <- review on stories-story-map
            # Person -> Ticket.finish_review(['stories-story-map'])
            # Ticket -> Ticket.record('review Stories story_map')
            # Board page -> Board.show()
            pass
        with then("billing-report's story_map marks Review ✓"):
            pass
    with scenario("Go back to an earlier stage's fidelity still to review"):
        # Evidence: observed: kanban_spec 'that a person has moved on with an earlier stage's fidelity still to review' — 'should name Review on that fidelity as next'.
        with given("pet-visits' story map is generated and validated with no violations"):
            pass
        with and_("a person has moved pet-visits into Specification"):
            pass
        with when("the session board reads pet-visits"):
            # Ticket -> Ticket.next_fidelity
            # Ticket <- the first fidelity not done in Specification or an earlier stage: stories-story-map
            pass
        with then("Run next reads Run next: review on stories-story-map"):
            pass
    with scenario("Keep Run next off where it cannot run"):
        # Evidence: observed: ticket-client.spec 'should stay off with no chat to send to'; ticket-client.tsx runNextHint for a locked ticket.
        with given("billing-report is the active [ticket](../../../.context/kanban-model.md#ticket--card) with generate next"):
            pass
        with but_("no chat is connected"):
            pass
        with when("the session board draws billing-report's Run next"):
            # Board page -> TicketClient.canRunNext <- false, with ChatClient.canSend false
            pass
        with then("Run next is off"):
            pass
    with scenario("Name nothing to run on a ticket done in its stage"):
        # Evidence: observed: kanban_spec 'with every required fidelity in its stage done' — 'should have no next'; ticket-client.tsx runNextHint.
        with given("every Discovery fidelity of pet-visits is reviewed"):
            pass
        with when("the session board reads pet-visits"):
            # Ticket -> Ticket.next_fidelity <- none
            pass
        with then("Run next says Nothing to run next"):
            pass
