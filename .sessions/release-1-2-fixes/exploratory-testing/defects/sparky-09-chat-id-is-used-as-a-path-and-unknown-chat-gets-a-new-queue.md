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
