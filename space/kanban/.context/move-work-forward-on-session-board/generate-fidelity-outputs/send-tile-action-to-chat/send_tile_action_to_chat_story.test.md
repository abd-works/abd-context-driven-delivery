# (E) Move Work Forward On Session Board
## (E) Generate Fidelity Outputs
### (S) Person --> Send Tile Action To Chat

#### Scenario: Send sketch, iterate, or document as its own command

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected
*And* its story_map bar is open
*When* the Person runs sketch on story_map
*Then* the chat receives the command /actions-sketch stories-story-map
*When* the Person runs iterate on story_map
*Then* the chat receives the command /actions-iterate stories-story-map
*When* the Person runs document on story_map
*Then* the chat receives the command /actions-document stories-story-map

#### Scenario: Tell the person which chat got the command

*Given* two chats are connected and none is picked
*When* the Person runs sketch on story_map
*Then* nothing is sent
*When* the Person picks a chat and runs sketch again
*Then* a toast says Sent to the chat: /actions-sketch stories-story-map
