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

## Confirmation (Rivet, round 2)
- Result: confirmed
- What I ran and saw: my own scripts in `C:\dev\_et\rivet\confirm\t` (`s1.py`, `s1read.py`), a fresh 39-card queue, eight processes adding 150 cards each, three runs: `of the 39 before, 0 remain` every time (38, 96 and 24 cards left of 1239), no error, no archive file. Readers beside three `set_steps` writers saw the 39-card queue as 0 cards 24 to 27 times in about 23,600 reads each, and two `set_steps` calls were refused with "which holds nothing".
- Cause, if you found it: `tools/prompt_queue/prompt_queue.py` `PromptQueue._held` answers `{}` for `JsonFileUnreadable`, and `PromptQueue._keep` then writes over the file; `harness/installation/json_file.py` `JsonFile.read` raises it for the `PermissionError` a read gets while another process's `os.replace` is under way.
- Shares its cause with: sparky-03 (the same `_held`, reached by a damaged file); sparky-02 (the same `_keep`, with nothing held between read and write); rivet-06 (the same read-as-empty in `TestRunRecord._read`).
- Is the file written by more than one process in the product: yes. Every chat's queue is `~/.claude/cdd-chats/<chat>/prompt-queue.json` (`harness/chat/chat.py` `ChatsFolder.path`), whatever cdd home the server runs from, so the stable lane's server and the dev lane's server write the same file. On this machine both were running during the test: `~/.cdd/server.json` port 47800 pid 45240 and `~/.cdd/dev/server.json` port 47801 pid 41832. A chat in a dev-lane worktree holds both: the project's `.mcp.json` names `cdd` at 47801 and the cdd plugin's `.mcp.json` (`~/.claude/plugins/cache/cdd-home/cdd/1.0.0/.mcp.json`) names 47800, so its agent is offered `mcp__cdd__prompt-queue_*` and `mcp__plugin_cdd_cdd__prompt-queue_*`, one process each. The mod writes nothing itself: `hooks/queue/prompt-queue.ts` `callCddServer` calls `cdd` first, then `plugin:cdd:cdd`. `space/session/open_sessions.py` (`PromptQueue.of_chat(chat).queue_handoff`) writes it from whichever server ran `sessions.switch`. No hook writes it.
- One real run, through real cdd servers (`s89.py`, `SpecServer` on ports 8911 and 8912, two cdd homes, one chats folder): six callers adding 15 cards each to one chat's queue. One server alone: 90 adds answered, 86 on the queue. Two servers, three callers each: 90 answered, 43 on the queue. So work is lost with one server too, since it runs calls side by side, and far more with two.
