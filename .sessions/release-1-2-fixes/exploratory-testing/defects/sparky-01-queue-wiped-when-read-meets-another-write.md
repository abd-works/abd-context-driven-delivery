# A queue change made while another process is writing the queue file reads the queue as empty and saves that, so every card queued before is gone, with no archive copy

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Build Prompt Queue / "Queue the draft as it is at the bottom of the queue" (the queue holds the earlier cards, then the new one). No scenario covers two callers at once.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue._held` (catches `JsonFileUnreadable` and answers `{}`) and `PromptQueue._keep`; `harness/installation/json_file.py` `JsonFile.read` (an `OSError` while another process swaps the file in becomes `JsonFileUnreadable`).
- **Severity:** blocks work (the chat's whole queue is lost: done cards, robots, steps, and the `handoffs` list)

## Steps

Sandbox scripts: `C:\dev\_et\sparky\work\t\common.py`, `build.py`, `race2.py`, `race3.py`. Environment: `CDD_HOME=C:\dev\_et\sparky\cdd_home`, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, `PYTHONPATH=C:\dev\abd-cdd-release-1-2-fixes;C:\dev\_et\sparky\work\t`, Windows 11.

1. `python build.py` - builds one chat's queue of 39 cards with `PromptQueue("chat-sparky", <sandbox>/chats/chat-sparky/prompt-queue.json)`: 8 done, 8 given to robots, 6 with steps.
2. `python race3.py` - eight processes (multiprocessing), each its own `PromptQueue` on that file, each calls `add` 150 times, starting at the same moment.
3. Read `prompts` afterwards.

Smaller view of the cause: `python race2.py read` - three processes call `set_steps`, three only read `prompts`.

## Expected

The 39 cards queued before stay on the queue, in order, followed by the added cards. `JsonFile.write` promises "a reader, or another chat's call writing the same file at once, never meets half of it", and `JsonFileUnreadable` promises "Nothing is written over it".

## Actual

Three runs of step 2, each from a fresh 39-card queue:

```
before 39 after 105 of the 39 cards queued before the race, 0 remain; adds acked 1200, present 105
before 39 after 15 of the 39 cards queued before the race, 0 remain; adds acked 1200, present 15
before 39 after 88 of the 39 cards queued before the race, 0 remain; adds acked 1200, present 88
```

No call raised. No file was written to `queue-archive`, so nothing records the lost cards.

`race2.py read` shows the cause: readers saw the 39-card queue as 0 cards 6 to 9 times in about 9,000 reads each (`{39: 8978, 0: 6}`), and one `set_steps` was refused with `PromptNotQueued: no prompt '737e662041fb' is on the queue of chat chat-sparky, which holds nothing` while the queue held 39 cards. On Windows a read that meets another process's `os.replace` fails with `PermissionError`; `JsonFile.read` turns it into `JsonFileUnreadable`, `PromptQueue._held` turns that into an empty queue, and `add_all` then saves `[*[], *added]` over the file.

So there are two faces of the one fault: a write that wipes the queue, and a refusal ("which holds nothing") that is false about what the queue holds.

## Tier that should catch it

Heavy: it needs real processes and a real file. `prompt_queue_heavy_spec.py` drives one server; no spec has two processes change one chat's queue file.
