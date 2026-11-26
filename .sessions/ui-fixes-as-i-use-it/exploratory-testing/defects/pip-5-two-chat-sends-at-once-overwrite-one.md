# Two chat.send calls at the same moment write one message file, so one send is lost though both answered

- **Title:** `chat.send` names each queued message from the clock (`ChatMailbox._next_file_name`) and writes it with no hold, so two sends to one chat at the same moment get the same file name and the second overwrites the first; both calls answer success.
- **Charter:** C1 (board sends). **Tester:** Pip.
- **Story:** connect-sessions-across-channels-and-apps / connect-chat-bar-board-and-story-ui (board messages reach the chat); the backlog entry "A board send says Board sent ..." (a send must reach the chat once, not twice, and never be silent). No scenario covers two senders at once. `chat.messages` promises "a message the chat could not take is never silent".
- **Module and class:** `harness/chat/chat.py`, `ChatMailbox.queue` / `_next_file_name`: the name is `max(clock_ns, latest + 1)`, read from the folder then written by `JsonFile(path).write` with no lock; `CHECK_IN_LOCKS` guards only `check_in`, not `send`.
- **Severity:** wrong result (a board message silently lost).

## Steps

`CDD_CHATS_FOLDER` set to the sandbox (`scratchpad/et/chips/sandbox/no-chats`), made-up chat id `pip-fake-chat-0002`, tools answered through `ProjectToolsets.of_repo` (`scripts/b2.py`):

1. `chat.check_in(chat="pip-fake-chat-0002", is_busy=True, name="fake", folder=<proj>)` so the chat is connected.
2. In two threads released by one barrier, at once:
   - `chat.send(chat=..., kind="refresh", text="practice ddd turned on")` (what the Files app sends when a practice or format is toggled), and
   - `chat.send(chat=..., kind="submit", text="Open the whiteboard Story Map in the artifact panel: https://claude.ai/artifact/FAKEBOARD123")` (the Files app's Open on a published board).
3. Count the files in the chat's `waiting/` folder. Repeat 20 times.

Also: 8 threads x 5 sends each.

## Expected

Two sends queue two messages, each delivered once, each followed on `chat.messages` to shown or failed.

## Actual

`20 trials ... answered 40 sends, lost 17`: in 17 of 20 trials only one file is left (on the last, only the `refresh`; the board send is gone, with no failure anywhere and no entry in `chat.messages`). 40 sends from 8 threads left 29 files. The Files app's toast says the chat opens the board when its turn ends; it never does.

## Tier that should catch it

Unit (`harness/chat/chat_spec.py`), with the spec clock frozen (`Chat.clock`) and two queues before either writes; or heavy with real threads. `chat_spec.py` covers a quick burst from one thread (the "Windows' clock repeats" comment), not two senders.
