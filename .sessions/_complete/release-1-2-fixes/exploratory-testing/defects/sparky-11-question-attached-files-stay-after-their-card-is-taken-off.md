# Question: the files attached to a card stay in the chat's attachments folder after the card is cleared or removed - is that intended?

- **Charter:** Round 1 - explore the prompt queue as several robots and a person changing one chat's queue at the same time (card 7887d9ffe762)
- **Tester:** Sparky
- **Story:** Queue Prompts For Later / Build Prompt Queue / "Keep a queued draft's image beside its prompt"; "Remove one prompt, keeping a copy in the queue archive". No scenario says what happens to a card's files when the card is taken off.
- **Module and class:** `tools/prompt_queue/prompt_queue.py` `PromptQueue.remove`, `PromptQueue.clear`, `PromptQueue._archive`.
- **Severity:** answered question

## Steps

`C:\dev\_et\sparky\work\t\clear2.py` (environment as in sparky-01), where b is a card not done:

1. `Q.attach(b, "x.exe", "", "aGk=")` - saved as `<chat folder>/attachments/<id of b>-1.exe`.
2. `Q.clear()` until the queue is empty.
3. List `<chat folder>/attachments`.

## Expected

Not known.

## Actual

`attachments left: ['<id of b>-1.exe']`. The archived copy of the card still lists the file's path, so keeping it may be meant, as the record of the work. But nothing ever removes the files, so a chat that queues screenshots grows its folder for as long as it lives, and the files of a card removed by mistake are indistinguishable from those of finished work.

Also for the answer: `attach` keeps whatever extension the file name has (`.exe` here). The name cannot leave the attachments folder.

## Tier that should catch it

Unit (`prompt_queue_spec.py`) or the story test of Attach Images To Queued Prompt, once the answer is known.

## Answer (2026-11-23)

A card's attached files are deleted with the card when it is removed or cleared, and the archived copy names them under `deleted_attachments`, no longer under `attachments`; a file the card names outside the chat's attachments folder is left alone. Built in `tools/prompt_queue/prompt_queue.py` (`QueuedPrompt.delete_attachments`, `PromptQueue._take_off`); tested by `prompt_queue_spec.py` context "whose first prompt has a file attached" (five examples) and the story test `attach_images_to_queued_prompt_story.test.py`; scenario "Delete a prompt's files when it leaves the queue" in `story_tests/queue-prompts-for-later/build-prompt-queue/build_prompt_queue_story.test.md`, story Attach Images To Queued Prompt.
