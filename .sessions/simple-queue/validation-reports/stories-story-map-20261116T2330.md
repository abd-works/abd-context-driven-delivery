# Validate — stories-story-map

Scope: the epic Queue Prompts For Later, added this pass to `.context/story-map.md` (lines 937–981), with its cells in `.context/story-map.drawio` and `.context/story-map.whiteboard`. The validate call saved no graph report, so this judgment is the AI's alone.

| Rule | Verdict | Evidence |
|---|---|---|
| verb-noun-format | Pass | Epic and all nine stories open with a base-form verb and a noun. |
| story-name-captures-system-mechanic | Pass | Each story verb names the operation (Queue, Open, Edit, Reorder, Remove, Play, Pause, Send, Plan). |
| four-to-nine-children | Pass | Nine stories under the epic. |
| branch-on-mechanical-uniqueness | Fail | See judgment. |
| right-size-story-nodes | Pass | One interaction per story; the dropped desktop submission stays an outcome of Queue Draft Prompt. |
| behaviours-not-one-time-tasks | Pass | Every story repeats. |
| story-scenarios-at-most-seven | Pass | No scenarios yet. |
| kebab-case-paths | Pass | No story files yet. |
| story-map-links-to-markdown | Pass | Stories have no files, so plain text; drawio cells link to their story-map.md entries. |
| vocabulary-traces-to-domain-source | Pass | Terms are the mod's own: queue, prompt, play, pause, sub-agent. |
| read-all-source-context-in-full | Pass | The epic names its sources: the brief, the person's directions, the mod and its tests. |
| do-not-invent-requirements | Pass | Every story is in the brief or asked for by the person; Edit, Play and Pause were asked for on 2026-11-16. |

## Judgment — `.context/story-map.md`

### `branch-on-mechanical-uniqueness` — Fail
- story-map.md:957 `Remove Queued Prompts`: holds two mechanics, removing one card's prompt (`removePrompt`) and clearing the whole queue (`clearQueue`); clearing is its own operation and wants its own story, Clear Prompt Queue.
