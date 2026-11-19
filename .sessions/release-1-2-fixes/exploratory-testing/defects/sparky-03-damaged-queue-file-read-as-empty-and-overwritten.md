# A queue file that is truncated, empty, saved with a byte-order mark, or not a JSON object reads as an empty queue without a word, and the next add writes over it

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** no scenario covers this (Queue Prompts For Later / Build Prompt Queue is the nearest).
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue._held`, which catches `JsonFileUnreadable` and answers `{}`.
- **Severity:** wrong result (the person's queue is lost, and the refusal that follows is false). Same cause as sparky-01, reached by a damaged or hand-edited file instead of a race.

## Steps

`C:\dev\_et\sparky\work\t\edges.py`, section "damaged files" (environment as in sparky-01):

1. `Q = PromptQueue("edge", <sandbox>/chats/edge/prompt-queue.json)`; `Q.add_all(["k1", "k2", "k3"])`.
2. Replace the file's text with one of: its first half (truncated); nothing; `[1,2]`; the same good text saved with a leading byte-order mark, as Windows Notepad's "UTF-8 with BOM" does.
3. `Q.prompts`, then `Q.done(<id of k1>)`, then `Q.add("after damage")`.

## Expected

The queue says its file cannot be read and names the file, and writes nothing over it. `JsonFileUnreadable` promises this: "Nothing is written over it, so what it holds stays for a person to repair."

## Actual

For all four files:

```
show -> []
done z1 -> PromptNotQueued no prompt 'z1' is on the queue of chat edge, which holds nothing
add -> {"prompts": [{"id": "ef2ec2bd4e07", "text": "after damage"}]}
```

The byte-order-mark case is the sharpest: the file still holds all three cards, a person only opened and saved it, and the next `add` replaces them with the one new card. Nothing is archived.

## Tier that should catch it

Unit: `prompt_queue_spec.py` can write a damaged file into its temp folder. No example reads a queue whose file is not a JSON object.
