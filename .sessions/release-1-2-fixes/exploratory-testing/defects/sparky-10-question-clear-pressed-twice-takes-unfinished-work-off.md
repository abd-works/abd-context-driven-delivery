# Question: clear pressed a second time takes every unfinished card off the queue, including one whose steps are under way - is that intended?

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Build Prompt Queue / "Clear the done prompts first, leaving the work still to do" and "Clear every prompt when none is done".
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.clear`.
- **Severity:** question

## Steps

`C:\dev\_et\sparky\work\t\clear2.py` (environment as in sparky-01): a queue of `one` (done), `two` (a step `in_progress`), `three`, `four`.

1. `Q.clear()`
2. `Q.clear()` again.

## Expected

Not known. Both scenarios are met as written.

## Actual

1. `after first clear: ['two', 'three', 'four']`
2. `after second clear: []`. All three are taken off, the one in progress included, because none is done now. The cards are kept in the queue archive, but no operation puts an archived card back on the queue.

The same press means "tidy the finished work" the first time and "throw away what is left" the second, and a robot may be working one of those cards. Should clear with none done ask first, leave a card whose steps are under way, or stay as it is?

## Tier that should catch it

Unit (`prompt_queue_spec.py`), once the answer is known.
