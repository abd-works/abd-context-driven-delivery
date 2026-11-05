# Validate report: stories-story-map

Artifacts: `story-map.md`, `story-map.drawio`. Graph rules: no violations.

| Rule | Result | Evidence |
|---|---|---|
| `vocabulary-traces-to-domain-source` | Pass | Terms come from the starting map and `claude_design.md`. |
| `read-all-source-context-in-full` | Partial | Canvas code and guidance were read. `explorer.dc.html` and `nodes.py` were read only in part, and no published canvas was walked. |
| `do-not-invent-requirements` | Pass, needs review | Model Core Domain was requested. User --> Review Domain Model rests on "Review and comment on existing artifacts" in `.context/cdd-flow-of-work.drawio`. |
| `evidence-distinguishes-observed-inferred-and-intended` | Pass | Evidence table in `story-map.md`. |
| `verb-noun-format` | Pass | Every node has a base-form verb and a noun. |
| `story-name-captures-system-mechanic` | Pass | No vague verbs. |
| `four-to-nine-children` | Warn | Both epics have 5 sub-epics and sub-epics have 4 to 9 stories. Play Canvas Story sits at the limit of 9. |
| `story-scenarios-one-to-four` | Open | This is a discovery map, so no story has scenarios yet. |
| `branch-on-mechanical-uniqueness` | Pass | Select Scenario Step and Select Outline Row stay apart because a row loads example data. |
| `right-size-story-nodes` | Pass, needs review | Render Story Map Artboard, Render Story Explorer, and Lay Out Screen Pages are one render call in code, and could merge. |
| `behaviours-not-one-time-tasks` | Pass | All are repeatable. |
| `story-map-links-to-markdown` | Pass | 69 of 69 nodes link to entries in `story-map.md`. |
