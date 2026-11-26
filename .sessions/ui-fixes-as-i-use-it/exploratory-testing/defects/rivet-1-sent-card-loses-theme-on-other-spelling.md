# Sending a card to another chat drops its robot's theme when the theme was set on another spelling of the robot

- **Charter:** C2 (queue band: robot rows, themes, + then send, send to another chat)
- **Tester:** Rivet
- **Story:** Queue Prompts For Later; no scenario covers send_to_chat or set_theme (no story test names either). Promised by the tools' own docs and `.sessions/_backlog/chat-ui-defects.md` "The queue band cannot hand cards to another chat" (message carries "its robot and the robot's theme").
- **Module and class:** `tools/prompt_queue/prompt_queue.py`, `PromptQueue.send_to_chat` (line ~634: `themes.get(card.robot, "")`, an exact-spelling lookup); `PromptQueue._robot_as_spelled` looks at cards only, never at the themes already kept.
- **Severity:** wrong result

## Steps

Chats folder and home of your own (`CDD_CHATS_FOLDER`, `CDD_HOME`), PYTHONPATH = the worktree:

```python
from harness.chat.chat import Chat, CHATS_FOLDER
from tools.prompt_queue.prompt_queue import PromptQueue
for c in ["lead-aaa", "other-bbb"]:
    Chat(CHATS_FOLDER.path / c).check_in(False, c, "C:/x")
lead = PromptQueue.of_chat("lead-aaa")
lead.add_all(["card three"])
card = lead.prompts[0].id
lead.set_theme("Gizmo", "files menu")   # lead names the robot's theme first...
lead.assign(card, "gizmo")              # ...then gives it its first card, spelled in lower case
print(lead.prompts[0].robot, lead.themes)   # gizmo {'Gizmo': 'files menu'}
lead.send_to_chat([card], "other-bbb")
# read other-bbb/waiting/*.json
```

## Expected

The sent card reads `robot: gizmo - files menu` (send_to_chat doc: "each card's text, robot and the robot's theme"); robots are "matched with no regard to case or outer spaces" (set_theme and assign docs), and the band's `themeOf` in `queue-view.tsx` does match them that way, so the band shows the theme beside gizmo.

## Actual

The message holds `robot: gizmo` with no theme, so the other chat never calls set_theme and the robot arrives there theme-less. The queue file also now holds two spellings of one robot (card `gizmo`, theme `Gizmo`): assign matches a robot by cards only, so the theme's spelling is not "the spelling the queue first held".

Also the reverse: set_theme on a robot whose cards were all cleared or sent stores the theme under the new spelling, while a later assign takes whatever spelling it is given.

## Tier that should catch it

Unit (`prompt_queue_spec.py`): its send_to_chat examples set the theme with the card's own spelling after assigning, so the spelling mismatch is never exercised.

## Also seen by
