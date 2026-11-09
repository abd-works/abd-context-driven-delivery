from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Steer Ticket Sessions
# Map: ../../../.context/story-map.md#s-person----add-backlog-item
# Model: ../../../.context/kanban-model.md
# Realizations: ../../../.context/session-board-scenario-realization.md

# Story: Add Backlog Item
# Actor: Person
#
# Acceptance criteria:
# - Start Backlog Item: the → arrow on a backlog card opens a ticket in Discovery, and a ticket that was moved to the Backlog comes back with its work. Observed: `BacklogItem.start`.
with story("Add Backlog Item"):
    with scenario("Add an idea to the Backlog"):
        # Evidence: observed: kanban_tools_spec 'that adds a backlog item' — 'should show the item in the Backlog with its text', 'should write the title and text to one markdown file'; backlog-item-client.spec 'with a title and text typed'.
        with given("the Backlog [column](../../../.context/kanban-model.md#column) has no [backlog item](../../../.context/kanban-model.md#backlogitem--card) titled Gift cards"):
            pass
        with when("the Person adds the backlog item Gift cards with the text Sell gift cards."):
            # Person -> BacklogItem.create('Gift cards', 'Sell gift cards.')
            # BacklogItem -> .sessions/_backlog/gift-cards.md: # Gift cards / Sell gift cards.
            # BacklogItem <- BacklogItem Gift cards
            # Board page -> Board.show()
            pass
        with then("the Backlog shows Gift cards with the text Sell gift cards."):
            pass
        with and_("Gift cards is selected and the form is closed"):
            pass
        with and_("a toast says Gift cards added to Backlog"):
            pass
    with scenario("Keep Add off with no title"):
        # Evidence: observed: backlog-item-client.spec 'should stay off with no title'; story-actions.spec 'should keep Add off with no title'.
        with given("the new backlog item form is open"):
            pass
        with but_("the Person has typed no title"):
            pass
        with when("the Person tries to add the item"):
            # Person -> BacklogDraftClient.add() <- nothing, with no title
            pass
        with then("Add stays off"):
            pass
        with and_("no [backlog item](../../../.context/kanban-model.md#backlogitem--card) is written"):
            pass
    with scenario("Start a backlog item in a chosen folder"):
        # Evidence: observed: root-choice-client.spec 'with a backlog item a person has asked to start' — 'should browse the top of the repository for its workpath before it starts', 'should not start it yet', 'should open its ticket with that folder as its workpath', 'should stay open on the new ticket's roots'; backlog-item-client.spec 'should say so in a toast'.
        with given("the [backlog item](../../../.context/kanban-model.md#backlogitem--card) Gift cards is in the Backlog"):
            pass
        with and_("the [repository](../../../.context/kanban-model.md#repo) has the folders src/billing and src/visits"):
            pass
        with when("the Person starts Gift cards"):
            # Person -> Board.folders('')
            # Board <- the repository's top folders
            pass
        with then("the roots dialog lists the top folders of the repository"):
            pass
        with and_("Gift cards is still in the Backlog"):
            pass
        with when("the Person chooses src/visits as its root"):
            # Person -> BacklogItem.start(path='src/visits')
            # BacklogItem -> Ticket.create('Gift cards', 'feature', '', 'src/visits')
            # Ticket -> Sessions.create('gift-cards', <repo>/src/visits, title, scope, parent)
            # BacklogItem -> TicketWork.record('backlog .sessions/_backlog/gift-cards.md')
            # BacklogItem -> Session.keep_file(gift-cards.md)
            # BacklogItem <- Ticket gift-cards
            pass
        with then("the [ticket](../../../.context/kanban-model.md#ticket--card) gift-cards is In progress in Discovery with root src/visits"):
            pass
        with and_("the roots dialog stays open on gift-cards so its practices' roots can be set"):
            pass
        with and_("a toast says Gift cards started in Discovery"):
            pass
    with scenario("Keep the idea file with the new ticket"):
        # Evidence: observed: kanban_spec 'that has been started' — 'should keep the item's file, text and all, in the new ticket's session folder', 'should open a ticket in Discovery', 'should name the item's file in the new ticket's session log'; kanban_tools_spec 'should take the item off the Backlog'.
        with given("the [backlog item](../../../.context/kanban-model.md#backlogitem--card) Returns and refunds is the file .sessions/_backlog/returns-and-refunds.md"):
            pass
        with when("the Person starts Returns and refunds on the whole repository"):
            # Person -> BacklogItem.start(scope='feature')
            # BacklogItem -> Ticket.create('Returns and refunds', 'feature', '', '')
            # BacklogItem -> TicketWork.record('backlog <path of returns-and-refunds.md>')
            # BacklogItem -> Session.keep_file(returns-and-refunds.md)
            pass
        with then("the [ticket](../../../.context/kanban-model.md#ticket--card) returns-and-refunds is In progress in Discovery"):
            pass
        with and_("its session folder holds returns-and-refunds.md, text and all"):
            pass
        with and_("its session log names the item's file"):
            pass
        with but_("the Backlog no longer shows Returns and refunds"):
            pass
    with scenario("Bring a ticket back from the Backlog with its work"):
        # Evidence: observed: kanban_tools_spec 'that starts the item again' — 'should bring the ticket back with its work'; kanban_spec 'should bring its ticket back with the history in its session log'.
        with given("the [ticket](../../../.context/kanban-model.md#ticket--card) sign-up was moved back out of Discovery and waits in the Backlog as the [backlog item](../../../.context/kanban-model.md#backlogitem--card) Sign up"):
            pass
        with and_("its folder .sessions/_backlog/sign-up/ keeps its session log"):
            pass
        with when("the Person starts Sign up"):
            # Person -> BacklogItem.start()
            # BacklogItem -> Sessions.load(.sessions/_backlog/sign-up).reopen()
            # BacklogItem <- Ticket sign-up
            pass
        with then("sign-up is back on the board with its session log and session.json"):
            pass
        with but_("no new ticket is opened"):
            pass
