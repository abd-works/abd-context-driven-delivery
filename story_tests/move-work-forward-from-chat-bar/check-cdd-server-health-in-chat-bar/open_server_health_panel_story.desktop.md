---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Open Server Health Panel

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Open Server Health Panel"`; no test tier runs it. Each scenario is copied word for word from [check_cdd_server_health_in_chat_bar_story.test.md](check_cdd_server_health_in_chat_bar_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Open Server Health Panel

#### Scenario: Show every part running on one line

*Given* cdd is connected with 116 tools loaded, the Kanban app on port 8778 and the Graph app on port 5173

- Do: call server-health.report with project set to the test chat's folder, and keep each app's label, status and port.
- See: the chat bar shows the green ✓; the test chat's tool count and the ports the report gives stand for 116, 8778 and 5173. When the report says the Kanban app or the Graph app is not running, this scenario's Given does not hold: record that and go on.

*When* the Person opens the server health panel

- Do: press the health mark, the ✓ at the left of the chat bar's line.

*Then* the session card opens with the panel on top, MCP host, Tools, Kanban app and Graph app green

- See: the session card is open above the chat bar's line, with the server health panel as its top line.
- See: the panel names MCP host, Tools, Kanban app and Graph app, each in green.

*And* Tools reads 116 loaded, Kanban app 8778 and Graph app 5173

- See: Tools reads a count followed by loaded, and the Kanban app and the Graph app each read the port the report gave.

*And* no Hook server part shows

- See: no part named Hook server on the panel.

*And* each part's name shows on hover

- Do: move the pointer over the first part's icon and wait a second.
- See: the part's name shows beside the pointer.

#### Scenario: Pin the panel open

*Given* cdd is connected and checkout-flow is the active session

- Do: close the session card if it is open, by pressing the health mark until no card shows above the line.
- See: the chat bar's line alone, with the green ✓ and the session's name.

*When* the Person presses the server health mark

- Do: press the health mark once.

*Then* the session card and its panel stay open after the pointer leaves the mark

- Do: move the pointer down into the prompt box, away from the mark, and wait two seconds.
- See: the session card and the server health panel are still open above the chat bar's line.

### Not walked on the desktop

- Say what is wrong when cdd is down: the cdd server would have to be stopped under the test chat.
