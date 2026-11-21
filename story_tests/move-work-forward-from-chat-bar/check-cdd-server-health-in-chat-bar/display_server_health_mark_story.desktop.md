---
fidelity: [acceptance_tests]
artifact: [desktop-story-test]
format: md
---

# Desktop story test: Display Server Health Mark

Walked in the real Claude desktop app by computer control, with `/desktop-walk target="Display Server Health Mark"`; no test tier runs it. Each scenario is copied word for word from [check_cdd_server_health_in_chat_bar_story.test.md](check_cdd_server_health_in_chat_bar_story.test.md). Under each step, Do is what the walking agent does on the screen of the test chat, and See is what the step's screenshot must show. The scenario's example values stand for the test chat's live ones.

## Story: Display Server Health Mark

#### Scenario: Show the connected mark

*Given* cdd answers server-health.report with 116 tools loaded

- Do: nothing on the screen; call server-health.report yourself with project set to the test chat's folder, and keep its answer.
- See: the answer lists the registered apps, which shows cdd answered; the test chat's own count of loaded tools stands for 116.

*When* the Chat Bar draws the active session checkout-flow

- Do: wait until the CDD chat bar's line is drawn above the test chat's prompt box.
- See: one line above the prompt box that holds a session name; the test chat's session stands for checkout-flow.

*Then* a green ✓ sits left of checkout-flow

- See: a green ✓ on the chat bar's line, left of the session's name.
- See: no red ✕, amber ! or ⟳ in its place.

### Not walked on the desktop

- Show the disconnected mark: the cdd server would have to be stopped under the test chat, which also stops the walk's own cdd calls.
- Show the tools missing mark: needs a cdd server from another checkout that lacks server-health.report.
