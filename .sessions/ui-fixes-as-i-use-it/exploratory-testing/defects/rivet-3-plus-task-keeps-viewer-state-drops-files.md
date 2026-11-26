# A task sent after + keeps the board viewer's state as its text and loses the images pasted with it

- **Charter:** C2
- **Tester:** Rivet
- **Story:** no scenario covers + then send. Related promises: `persons_words` in `tools/prompt_queue/prompt_queue.py` ("a step or card says what the person asked for instead of where their viewer stood"), the queue's own instruction in `prompt-queue.ts` line ~746 ("never put any of it in a title or a step"), and Attach Images To Queued Prompt (a queued draft's image is kept beside its prompt).
- **Module and class:** `tools/prompt_queue/hooks/queue/prompt-queue.ts` `takeAwaitedStep` / `appendStep` (step text is `text.trim()`); `register.tsx` `prompt.submit` passes `e.text` only, not `e.attachments`, and drops the message. Server side, `PromptSteps.plan` only strips spaces, so `set_steps` stores whatever it is given.
- **Severity:** wrong result
- **How found:** code reading (band TypeScript cannot run here); server half run for real (below).

## Steps

1. A board viewer open in the Claude app (the app prefixes each sent message with `<artifact-view-context ...>...</artifact-view-context>`).
2. Press + on a card with an empty prompt box, paste an image, type "make the header blue", send.
3. Server half, reproduced in Python in a throwaway chats folder:
   ```python
   q = PromptQueue.of_chat("lead-aaa"); q.add_all(["card"]); c = q.prompts[0].id
   q.set_steps(c, [{"text": '<artifact-view-context id="x">{"zoom":2}</artifact-view-context> make the header blue', "state": "pending"}])
   print(q.prompts[0].listed_steps)
   ```

## Expected

The step reads "make the header blue"; the image is kept with the card (as Alt+Enter's `keepQueuedAttachments` does), or the message is not dropped.

## Actual

The step text is the whole viewer block plus the words (server stores it unchanged: `[{'text': '<artifact-view-context id="x">{"zoom":2}</artifact-view-context> make the header blue', 'state': 'pending'}]`). The pasted image is in `e.attachments`, never read, and the message is dropped ("Added as a task"), so the image is lost. A message that is only a viewer block also passes `text.trim() === ''` and becomes a step.

## Tier that should catch it

Unit: a plugin test of + then send with a viewer block and an attachment; a server unit example that `set_steps`/`add_interruption` apply `persons_words` (add_interruption already does; set_steps does not).

## Also seen by

## Triage

- **Status:** confirmed: server half reproduced as a spec example on a throwaway queue (`set_steps` kept the viewer block verbatim); band half by reading `takeAwaitedStep` and `register.tsx` (`e.attachments` never read, the message dropped).
- **Severity:** wrong result.
- **Triaged by:** Cue

## Fix

- **Server:** `PromptSteps.plan` (behind `set_steps`) keeps only `persons_words` of each step, so a viewer's state is taken out and a step left with no words is left out, as `add_interruption` already did.
- **Band:** `takeAwaitedStep` takes the message's `personsWords` (new in `hooks/queue/awaited-task.ts`, the TypeScript twin of `persons_words`) as the task; a message that is only a viewer's state is no task, goes to the chat and leaves + waiting. It now takes `e.attachments` from `register.tsx` and keeps each pasted item beside the card through `attachAll`, the loop `keepQueuedAttachments` used for Alt+Enter, moved out so both paths share it.
- **Tests:**
  - `tools/prompt_queue/prompt_queue_spec.py` (unit): "keeps only the person's words of a step sent from a board viewer" and "leaves out a step that holds only a board viewer's state"; seen failing first, now pass (125 examples). The queue's story tests (23 examples) pass.
  - `tools/prompt_queue/awaited-task.spec.ts` (vitest): two `personsWords` examples, pass (8 in the file). Written with the function, so not seen failing on their own.
  - `tools/prompt_queue/hooks/register.test.tsx` (plugin): "the task sent from a board viewer is only the person's words" and "a message that is only a board viewer's state is no task, and + still waits". **Not run:** no `claude` CLI on this machine; type-checked against the claude-code stubs with no new error in the test file.
  - **The image is not tested:** `$.prompt.media` is not an event `claude-code/testing` lets a test answer (the stubs list no `prompt.media` operation), so no plugin test can hand the mod a pasted item's bytes. The Alt+Enter path that shares `attachAll` has no plugin test for the same reason.
- **Scenarios:** "Add only the person's words and pasted items of a task sent while + waits" (Edit Prompt Steps) and "Keep only the person's words of a step" (Set Steps Of Queued Prompt) in `nest_prompt_steps_in_queue_story.test.md`.
- **Commit:** (filled below)
