# set_theme keeps a theme for a robot with no name, and a theme of several lines that breaks the robot's row

- **Charter:** C2
- **Tester:** Rivet
- **Story:** no scenario covers set_theme. Promise: its doc ("Give the robot named robot its theme: its purpose or topic as one sentence") and backlog entry "A robot in the queue band says only its name".
- **Module and class:** `tools/prompt_queue/prompt_queue.py`, `PromptQueue.set_theme` (no check on the robot name; `theme.strip()` keeps inner newlines); band: `AgentRobotView` in `tools/prompt_queue/hooks/queue/queue-view.tsx`, whose see-through press is sized by `[...theme].length`, counting a newline as one column.
- **Severity:** cosmetic

## Steps

```python
q = PromptQueue.of_chat("t-themes"); q.add_all(["c1"]); c = q.prompts[0].id
q.set_theme("", "nobody");    q.set_theme("   ", "spaces")
q.assign(c, "Bolt"); q.set_theme("Bolt", "line one\nline two")
print(q.themes)   # {'': 'spaces', 'Bolt': 'line one\nline two'}
```

## Expected

A robot with no name is refused (as an empty chat id or prompt id is), and the theme is one line (newlines folded to spaces, or refused).

## Actual

The queue file keeps a theme under the empty robot `""`, which no robot row can show and nothing takes off except another `set_theme("", " ")`; a two-line theme is kept, and the band draws it across two lines beside the robot, its press strip sized as if it were one line.

## Tier that should catch it

Unit (`prompt_queue_spec.py`, the set_theme examples).

## Also seen by

## Triage

- **Status:** confirmed: `set_theme("   ", ...)` kept a theme under `""` and `set_theme("Bolt", "line one\nline two")` kept both lines (reproduced as spec examples on a throwaway queue).
- **Severity:** cosmetic.
- **Triaged by:** Cue

## Fix

- **Choice:** refuse a robot with no name, as an empty chat id is refused, with the new `RobotNotNamed` (it names the robot and the theme, and nothing is written); fold a theme's lines and runs of spaces into one line, so the band's row and its press strip, sized by the theme's length, stay one line. No band change: the band now only ever gets one-line themes. A queue file written before this fix keeps what it holds until its robot's theme is set again.
- **Code:** `tools/prompt_queue/prompt_queue.py`: `PromptQueue.set_theme`, new `RobotNotNamed`.
- **Tests:** `tools/prompt_queue/prompt_queue_spec.py` (unit), under "that the lead gives a robot its theme": "keeps a theme given on several lines as one line, so the robot's row stays one line" and "refuses a theme for a robot with no name, keeping every theme"; seen failing first (the refusal did not exist), now pass (127 examples).
- **Scenarios:** "Keep a robot's theme as one line" and "Refuse a theme for a robot with no name" (Assign Queued Prompt To Robot) in `share_queue_among_robots_story.test.md`.
- **Commit:** 71590096f
