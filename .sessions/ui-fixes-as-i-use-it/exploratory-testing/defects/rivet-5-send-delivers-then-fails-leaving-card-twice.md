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

## Triage

- **Status:** confirmed: reproduced with the report's archive that cannot be made (a file in its place) in a throwaway chats folder; the message waited in `chat-2`'s mailbox and the card stayed on `chat-1`.
- **Severity:** wrong result (rare trigger; a retry delivers the card twice).
- **Triaged by:** Cue

## Fix

- **Choice:** the cards leave the queue first and are sent last. `send_to_chat` now builds the message, archives the cards and keeps the queue without them, and only then hands the message to the other chat's mailbox; when that send fails (`ChatNotConnectedError` or `OSError`), `_undo_send` keeps the queue as it was and takes the archive copy off, then the failure is raised. A failure of the archive or the queue write now happens before anything is sent.
- **Code:** `tools/prompt_queue/prompt_queue.py`: `PromptQueue.send_to_chat`, new `_sent_cards_message` and `_undo_send`; `_archive` answers the copy it wrote.
- **Tests:** `tools/prompt_queue/prompt_queue_spec.py` (unit): "whose queue archive cannot be written / it sends nothing ..." (seen failing first: the message was waiting) and "it keeps every card on this queue"; "that the other chat stops being connected as the cards are sent / it keeps no copy of the cards in the queue archive" guards the undo. 118 examples pass.
- **Scenario:** "Take the sent cards off this queue only once the other chat has them", new story Send Queued Prompts To Another Chat in `story_tests/queue-prompts-for-later/share-queue-among-robots/share_queue_among_robots_story.test.md`. The story map (root `.context/story-map.md`, outside this robot's area) does not hold the story yet: for the supervisor.
- **Commit:** a91a2c5fd
