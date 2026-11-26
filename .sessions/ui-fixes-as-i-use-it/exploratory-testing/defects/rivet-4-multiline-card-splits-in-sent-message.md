# A card whose text holds several lines is sent to another chat as several cards, with conflicting done states

- **Charter:** C2
- **Tester:** Rivet
- **Story:** no scenario covers send_to_chat. Promise: `PromptQueue.send_to_chat` doc and `_SENT_CARDS_NOTE` ("File each card below ... check each card stands once").
- **Module and class:** `tools/prompt_queue/prompt_queue.py`, `QueuedPrompt.handed_over`: `f"{place}. {self._text}"` puts the card's whole text, newlines included, into a numbered list whose other lines (`   done:`, `   robot:`, `   - [state]`) are the card's own fields.
- **Severity:** wrong result (cards duplicated or split on the receiving chat, a not-done card read as done)

## Steps

Throwaway `CDD_CHATS_FOLDER`; chats `lead` and `other` checked in (`Chat(folder).check_in(False, name, "C:/x")`).

```python
q = PromptQueue.of_chat("lead")
q.add_all(["Do these:\n1. first thing\n2. second thing\n   done: yes"])   # a pasted list kept as one card's text
a = q.prompts[0].id
q.set_steps(a, [{"text": "s1", "state": "done"}, {"text": "s2", "state": "in_progress"}])
q.send_to_chat([a], "other")
# read other/waiting/*.json "text"
```

## Expected

One card, unambiguous: its text kept whole (indented, quoted or fenced) so the receiving agent files exactly one card, not done, with its two steps.

## Actual

```
1. Do these:
1. first thing
2. second thing
   done: yes
   done: no
   - [done] s1
   - [in_progress] s2
```

The receiver reads cards 1, 1, 2, and the first `done: yes` belongs to no clear card; the card is likely filed as three cards, one marked done. A card text is commonly multi-line: pasted lists, notes, `<pasted_content>` blocks (backlog entry "The queue band shows a pasted message as the goal's title"). The same splice happens for a step text with a newline.

## Tier that should catch it

Unit (`prompt_queue_spec.py`): its send examples use one-line texts only.

## Also seen by
