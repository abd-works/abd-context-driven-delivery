# Two processes changing one chat's queue at the same moment each succeed, but one change is dropped: added cards vanish, a card marked done is not done, a removed card is back on the queue while the archive says it was taken off

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Share Queue Among Robots / Send Queued Prompts To Sub-Agents / "Start one sub-agent for each robot" ("each sub-agent marks its own card done"); Build Prompt Queue / "Remove one prompt, keeping a copy in the queue archive". No scenario has two callers at once.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue._keep` and every operation that calls it: each reads the whole file, changes its copy, and writes the whole file, with nothing holding the file between the read and the write.
- **Severity:** wrong result (work is lost or done twice without any refusal)

## Steps

Sandbox scripts in `C:\dev\_et\sparky\work\t` (`common.py`, `build.py`, `race.py`, `race2.py`); environment as in sparky-01.

1. `python build.py` - a 39-card queue.
2. `python race.py` - eight processes start together, 15 calls each, every process on its own cards: three call `add`, two `done`, one `set_steps`, one `assign`, one `remove`.
3. Compare what each call answered with what the queue holds afterwards.

Simplest form: `python race2.py add` - six processes, 20 `add` calls each.

## Expected

Every call that answers without an error is kept: 45 new cards, 15 cards off the queue, each card marked done is done, each assigned card has its robot, each planned card has its steps.

## Actual

`race.py`:

```
before 39 after 49 errors 11
adds acked 45 missing 35
removes acked 15 still on queue 15
done acked but not done 5
assign acked, wrong robot 12
steps acked, not kept 15
dup ids 0
order kept True
archives 15
```

- 35 of 45 added cards are gone, though `add` answered a queue holding each.
- All 15 removed cards are still on the queue, and `queue-archive` holds 15 files saying they were taken off. A later `PromptNotQueued` for such a card cannot arise, but anything that reads the archive believes work was removed that a robot will still be sent.
- 5 cards a process marked done are not done, so the next robot to read the queue takes them again: a card worked twice.
- 12 robots and 15 step lists were dropped.

`race2.py add`: `before 39 after 59 acked adds 120 present 20` - 100 of 120 cards lost, no error.

The file always parsed, no id was duplicated, and the order of the surviving cards held. The 11 errors in the first run are sparky-01.

## Tier that should catch it

Heavy: real processes on one real queue file. The unit spec uses one `PromptQueue` object, and the heavy spec one server, so no test makes two changes overlap.
