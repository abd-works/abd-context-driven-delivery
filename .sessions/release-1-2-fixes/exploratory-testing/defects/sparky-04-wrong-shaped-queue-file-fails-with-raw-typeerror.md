# A queue file whose JSON is valid but wrongly shaped fails every call with a raw TypeError or KeyError that names neither the file nor the card

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** no scenario covers this.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.prompts` and `PromptQueue._holding`.
- **Severity:** misleading message

## Steps

`C:\dev\_et\sparky\work\t\edges.py`, section "damaged files". Write each text below as the queue file, then call `prompts`, `done("z1")`, `add("after damage")`.

| File text | show | done z1 | add |
| --- | --- | --- | --- |
| `{"prompts": null}` | `TypeError 'NoneType' object is not iterable` | same | same |
| `{"prompts": "abc"}` | `AttributeError 'str' object has no attribute 'get'` | `TypeError string indices must be integers, not 'str'` | succeeds and saves `["a", "b", "c", {new card}]` |
| `{"prompts": [{"text": "no id"}]}` | shows the card | `KeyError 'id'` | succeeds |
| `{"prompts": [{"id": "z1", "text": "A"}, {"id": "z1", "text": "B"}]}` | shows both | marks both done | succeeds |

## Expected

A refusal that says the chat's queue file does not hold a queue, naming the file and what is wrong in it, as `PromptNotQueued` now names the chat it read.

## Actual

The errors in the table. With `"prompts": null` the queue cannot be shown, added to, or cleared until a person finds and repairs the file, and the message gives no file to look in. With `"prompts": "abc"` an `add` saves the string's letters as cards. A card with no id makes every call that names any card fail with `KeyError 'id'`, including calls on healthy cards. Two cards sharing an id are both changed by one call.

## Tier that should catch it

Unit: `prompt_queue_spec.py`, with a hand-written file in its temp folder. Every example builds its queue through `add_all`, so the file is always well shaped.
