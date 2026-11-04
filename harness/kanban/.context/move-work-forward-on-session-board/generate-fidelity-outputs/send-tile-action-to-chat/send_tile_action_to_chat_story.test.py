from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Generate Fidelity Outputs
# Map: ../../../story-map.md#s-person----send-tile-action-to-chat
# Model: ../../../kanban-model.md
# Realizations: ../../../session-board-realization.md

# Story: Send Tile Action To Chat
# Actor: Person
with story("Send Tile Action To Chat"):
    with scenario("Send sketch, iterate, or document as its own command"):
        # Evidence: observed: tile-client.spec 'Send Tile Action To Chat' — 'should send %s as its own command' for sketch, iterate, and document; story-actions.spec 'should send the chosen action on a tile'.
        with given("billing-report is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected"):
            pass
        with and_("its story_map bar is open"):
            pass
        with when("the Person runs sketch on story_map"):
            # Board page -> Chat.send('command', '/actions-sketch stories-story-map')
            pass
        with then("the chat receives the command /actions-sketch stories-story-map"):
            pass
        with when("the Person runs iterate, then document, on story_map"):
            # Board page -> Chat.send('command', '/actions-iterate stories-story-map')
            # Board page -> Chat.send('command', '/actions-document stories-story-map')
            pass
        with then("the chat receives /actions-iterate stories-story-map, then /actions-document stories-story-map"):
            pass
    with scenario("Tell the person which chat got the command"):
        # Evidence: observed: chat-client.spec 'should choose the only chat connected', 'should choose none among several', 'should send once a person picks one of several', 'should send nothing with no chat chosen', 'should show the refusal of a chat that has gone'; Chat.send raises ChatNotConnectedError.
        with given("two chats are connected and none is picked"):
            pass
        with when("the Person runs sketch on story_map"):
            pass
        with then("nothing is sent"):
            pass
        with when("the Person picks a chat and runs sketch again"):
            # Board page -> Chat.send('command', '/actions-sketch stories-story-map')
            pass
        with then("a toast says Sent to the chat: /actions-sketch stories-story-map"):
            pass
