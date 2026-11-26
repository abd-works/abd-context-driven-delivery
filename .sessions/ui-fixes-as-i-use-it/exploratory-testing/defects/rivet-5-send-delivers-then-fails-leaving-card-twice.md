# send_to_chat delivers the message before archiving and saving, so a failure after delivery leaves the card on both queues

- **Charter:** C2
- **Tester:** Rivet
- **Story:** no scenario covers send_to_chat. Promise: its doc, "A card the queue does not hold, no card at all, this chat itself, or a chat not connected is refused, and nothing is sent or taken off."
- **Module and class:** `tools/prompt_queue/prompt_queue.py`, `PromptQueue.send_to_chat`: `Chat(...).send(...)` runs first, then `self._archive(sent)` and `self._keep(...)`; nothing undoes the delivered message when either raises.
- **Severity:** wrong result (rare trigger; a retry then delivers the card a second time)

## Steps

```python
bad = CHATS_FOLDER.path / "not-a-folder"; bad.write_text("x")      # archive folder cannot be made
q = PromptQueue("lead", CHATS_FOLDER.path / "lead" / "prompt-queue.json", archive=bad)
q.add_all(["card A"]); a = q.prompts[0].id
q.send_to_chat([a], "other")      # chats lead and other checked in
```

(In the server, `load` sets the archive to the calling session's work folder; any failure to make or write it, or a failed `_keep` write such as a locked file on Windows, has the same effect.)

## Expected

Either the card is sent and leaves this queue, or the call fails and nothing is sent.

## Actual

`FileExistsError [WinError 183] ...not-a-folder`; the card is still on `lead`'s queue, and `other` has the message waiting (1 message). The lead and the band are told the send failed, so the natural retry sends the card again: it ends up twice on `other` and still on `lead`.

## Tier that should catch it

Unit: a send whose archive or keep fails, checking the other chat's mailbox is empty (or the message is withdrawn).

## Also seen by
