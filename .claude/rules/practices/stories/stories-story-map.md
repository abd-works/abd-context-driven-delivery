---
description: "Whenever you create, alter, or delete epics, sub-epics, or stories on the map, or change scenarios or acceptance work that forces a map change. Follow these rules."
paths:
  - "**/*story-map*"
  - "**/*-sketch.md"
---

#### Rules



Whenever you create, alter, or delete epics, sub-epics, or stories on the map, or change scenarios or acceptance work that forces a map change. Follow these rules.

If this change will not stay here, follow `practices/stories.mdc`.

- **`verb-noun-format`** - Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.
- **`story-name-captures-system-mechanic`** - At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.
- **`four-to-nine-children`** - Keep 4-9 direct children on an epic or sub-epic, warn at 3 or 10, and restructure at 2 or fewer or 11 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.
- **`story-scenarios-one-to-four`** - A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.
- **`branch-on-mechanical-uniqueness`** - Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.
- **`right-size-story-nodes`** - Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.
- **`behaviours-not-one-time-tasks`** - Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.
- **`story-map-links-to-markdown`** - Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

---