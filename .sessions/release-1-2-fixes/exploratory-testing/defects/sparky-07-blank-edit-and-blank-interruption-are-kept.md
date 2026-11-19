# Editing a card to only spaces leaves an empty card on the queue, and a blank interruption adds an empty step and opens a done goal again, though add queues nothing for the same text

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Build Prompt Queue / "Queue nothing for an empty draft"; Edit Queued Prompt / "Put the changed text back in its place". No scenario covers a blank edit or a blank interruption.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.edit`, `PromptQueue.add_interruption`, and `PromptQueue.set_steps` (which also keeps a step whose text is empty).
- **Severity:** wrong result

## Steps

`C:\dev\_et\sparky\work\t\edges.py` (environment as in sparky-01), on a queue of `one` (a, done), `two` (b), `three` (c):

1. `Q.edit(c, "   ")`
2. `Q.add_interruption(a, "   ")`
3. `Q.set_steps(b, [{"text": "", "state": "pending"}])`

## Expected

Text that is only spaces changes nothing, as `add` promises ("Text that is only spaces queues nothing"), or is refused with a message that says the text is empty.

## Actual

1. Card c stays on the queue with text `""`: `('', False, None, [])`. Play would send an empty prompt, or the agent is told to do a card that says nothing.
2. Goal a gets the step `('[interruption] ', 'pending')` and is no longer done, so finished work is opened again for a message with no words.
3. Card b holds a step with empty text.

## Tier that should catch it

Unit: `prompt_queue_spec.py`. It checks blank text for `add` and `add_all` only.
