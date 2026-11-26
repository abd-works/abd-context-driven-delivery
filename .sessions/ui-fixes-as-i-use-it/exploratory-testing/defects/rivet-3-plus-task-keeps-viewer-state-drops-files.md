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
