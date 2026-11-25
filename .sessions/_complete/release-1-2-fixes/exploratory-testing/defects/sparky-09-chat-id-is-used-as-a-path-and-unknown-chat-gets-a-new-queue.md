# The chat argument is used as a folder path unchecked: `..\escape-chat` writes a queue file outside the chats folder, and a mistyped chat id makes a new queue nobody reads

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** no scenario covers this. Known history: `PromptNotQueued` once did not say which chat it read; this is the same mistake on the writing side.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.load`: `CHATS_FOLDER.path / chat / QUEUE_FILE`.
- **Severity:** wrong result (a card queued for a chat is lost without a refusal; a file is written outside the chats folder)

## Steps

`C:\dev\_et\sparky\work\t\server.py`, through a real cdd server with `CDD_CHATS_FOLDER=C:\dev\_et\sparky\work\chats-server`:

1. `prompt-queue.add chat="..\escape-chat" text="written outside chats folder?"`
2. `prompt-queue.done chat="some-other-chat" prompt=<an id on the calling chat's queue>`

## Expected

1. A refusal: a chat id is not a path.
2. For a chat the server has never seen, either a refusal that says no such chat is known, or, as now, a message naming the chat that was read. For `add` the same check, since `add` cannot fail on a missing card.

## Actual

1. The call succeeds: `{"chat": "..\\escape-chat", "prompts": [{"id": "02a58296650f", ...}]}`, and `C:\dev\_et\sparky\work\escape-chat\prompt-queue.json` now exists beside `chats-server`, outside it.
2. `PromptNotQueued: no prompt 'fa77f8150e28' is on the queue of chat some-other-chat, which holds nothing`. This refusal is clear. But `prompt-queue.add chat="some-other-chat"` (or a real chat id with one wrong character) succeeds, makes the folder `some-other-chat` and a queue in it, and answers a queue holding the card, so a robot reporting a defect to a mistyped supervisor chat is told it worked.

## Tier that should catch it

Heavy: `prompt_queue_heavy_spec.py` names a chat only as `""`.

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own `s89.py` through a real cdd server with `CDD_CHATS_FOLDER=C:\dev\_et\rivet\confirm\chats-server`: `add chat="..\escape-chat"` succeeds and `C:\dev\_et\rivet\confirm\escape-chat\prompt-queue.json` exists beside the chats folder; `done chat="some-other-chat"` is refused clearly ("which holds nothing"); `add chat="some-other-chat"` succeeds and makes `chats-server\some-other-chat\prompt-queue.json`.
- Which part I ran: both steps, and the `add` on an unknown chat the report describes under Actual. Not run: an absolute path or a drive letter as the chat, nor `..` through the other chat tools.
- Cause, if you found it: `tools/prompt_queue/prompt_queue.py` `PromptQueue.load`: `CHATS_FOLDER.path / chat / QUEUE_FILE` with chat as the caller gave it.
- Shares its cause with: none among the queue's reports. gizmo-04 and gizmo-13 are the same kind of fault (a name from the caller used as a folder name unchecked) in other classes.

## Status: fixed (2026-11-23)
- Fixed before this pass (`e40748768`): a chat id that is a path, holds a separator or a drive, or is empty is refused with `ChatIdNotAnId`, so `..\escape-chat` writes nothing outside the chats folder (`prompt_queue_spec.py`, "that is asked for by a chat id"; `prompt_queue_heavy_spec.py`, "that an agent names a chat by a path out of the chats folder").
- Fixed now: `PromptQueue.load` refuses a chat other than the calling one while the chats folder keeps no folder for it, with `ChatNotKnown` ("no chat 'some-other-chat' is known: the chats folder ... keeps no folder for it; check the chat id, or name no chat to use the calling chat's own queue"), and makes no folder. A chat that has checked in or holds a queue has its folder, so a robot still reports to its supervisor's chat; the calling chat's own queue is still made on its first card.
- Covered by: `tools/prompt_queue/prompt_queue_spec.py`, "that is asked for by a chat id" (refuses a chat no chat folder is kept for; makes no folder for it; queues on another chat whose folder is kept; queues on the calling chat's own queue the first time), and `tools/prompt_queue/prompt_queue_heavy_spec.py`, "that an agent queues work on a chat the server has never seen", through a real cdd server.
