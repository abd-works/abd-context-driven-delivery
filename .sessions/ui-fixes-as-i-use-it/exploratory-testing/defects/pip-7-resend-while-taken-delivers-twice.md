# chat.resend on a message the chat has taken but not yet confirmed delivers it twice

- **Title:** `chat.resend` moves a *taken* message back to waiting while the chat's mod is still showing it; the mod's confirm then finds no taken file and does nothing, so the next check-in hands the same message to the chat again and it is shown twice, while `chat.messages` says it waits.
- **Charter:** C1 (board sends delivered twice). **Tester:** Pip.
- **Story:** connect-chat-bar-board-and-story-ui; the backlog entry on board sends ("every press as another copy"). No scenario covers resend racing a confirm.
- **Module and class:** `harness/chat/chat.py` `ChatMailbox.resend` (takes TAKEN as well as FAILED) and `ChatMailbox.confirm` (returns silently when the taken file is gone).
- **Severity:** wrong result.

## Steps

`CDD_CHATS_FOLDER` in the sandbox, made-up chat `pip-fake-chat-0003`, `scripts/b3.py`:

1. `chat.check_in(chat, is_busy=True, ...)`; `chat.send(chat, kind="submit", text="Open the whiteboard X: https://claude.ai/artifact/B")`.
2. `chat.check_in(chat, is_busy=True, ...)` -> the mod takes message M (state `taken`). The mod's `run` holds it for up to `REFUSED_WITHIN_MILLISECONDS` (3 s) while the chat is busy before confirming.
3. In that window: `chat.resend(chat, message=M)` (an agent, or the generated chat view's Resend).
4. The mod's confirm: `chat.confirm(chat, message=M, is_shown=True)`.
5. `chat.messages(chat)`; next `chat.check_in(chat, is_busy=False, ...)`.

## Expected

A message being shown is not resent (resend only a failed one, or refuse a taken one by name), or the confirm of the first delivery wins, so the message reaches the chat once.

## Actual

After 4: states `['waiting']` - the shown message reads as still waiting. Step 5's check-in returns M again, so the chat gets it a second time. The mod's copy guard (`waitingSubmits`) only skips it while the first submit has not run; once the first ran, the copy is submitted as a new message.

## Tier that should catch it

Unit (`harness/chat/chat_spec.py`): resend between take and confirm. The specs resend only failed messages.

## Triage

- **Status:** confirmed. Throwaway `CDD_CHATS_FOLDER`: send, check-in (taken), resend, confirm(shown) left the message `waiting`, and the next check-in handed it to the chat again.
- **Severity:** wrong result (a message shown twice, and listed as waiting after it was shown).
- **Triaged by:** Relay.
- **Why:** `ChatMailbox.resend` moved a taken message back to waiting at once, while the mod still held it for up to `REFUSED_WITHIN_MILLISECONDS`; `confirm` looked only in taken, so the mod's confirm was lost. Resending a taken message is still wanted: the board offers Resend on "taken, not shown yet", for a mod that reloaded and forgot what it took.

## Fix

- **Scenarios:** "A message the chat may still be showing is not resent" and "A message taken long ago and resent is shown once" (Story: Send Command To Chat) in `story_tests/connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui/connect_chat_bar_board_and_story_ui_story.test.md`.
- **Test:** `harness/chat/chat_spec.py` (unit), "that a person resends while the chat may still be showing it" and "that a person resends once the chat has had time to show it" / "that the chat confirms it showed after all". Seen failing first: 4 examples.
- **Fix:** `harness/chat/chat.py`: `take_ready` keeps `taken_at` in the message; `resend` of a message taken less than `SHOWING_SECONDS` (10) ago raises *ChatMessageMayBeShowing*, naming the message, and leaves it taken; `confirm` also finds a message resent since (in waiting), so a late confirm still counts and the chat is not given it twice. Model (`chat-model.md`, `chat-model.drawio`) and `module-context.md` updated.
- **Not changed (outside the area):** the board's Resend button (`space/kanban/app/src/kanban/chat/chat-messages-view.tsx`) still shows on a taken message; a press within 10 seconds now gets the refusal instead of a second delivery.
- **Commit:** see below.
