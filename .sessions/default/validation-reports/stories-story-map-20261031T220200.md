# Validate: stories-story-map

**Artifacts:** `harness/kanban/.context/story-map.md`, `harness/kanban/.context/story-map.drawio`
**Graph rules:** no violations reported.
**Note:** `validate.validate` returned Clean Engineering rules as its AI rubric for this guidance, so these judgments use the story_map and shared Stories rules from `cdd_guidance/practices/stories/stories.md`. No session was open, so this report is written by hand.

| Rule | Result | Evidence |
|---|---|---|
| vocabulary-traces-to-domain-source | Pass | Board, Column, Backlog, Stage, Ticket, Fidelity, Report, Help, Files come from the code and canvas. |
| read-all-source-context-in-full | Pass | The sources listed on the map were read in full; each Story cites its source. |
| do-not-invent-requirements | Pass | Every Story cites code, a spec, or a canvas operation or comment. |
| evidence-distinguishes-observed-inferred-and-intended | Pass after fix | The Open Forge Page line claimed links that the Board Pane does not have; corrected. |
| verb-noun-format | Pass | All Epics, Sub-Epics, and Stories are base-form verb and noun. |
| story-name-captures-system-mechanic | Pass after fix | Run Supporting Action was vague; renamed Send Sketch Iterate Or Document. |
| four-to-nine-children | Warn | Read Guidance Help has 3 Stories; no source supports a fourth. Three top-level Epics have no parent, so the band does not apply to them. |
| story-scenarios-one-to-four | Not applicable | Scenarios are the next fidelity. |
| branch-on-mechanical-uniqueness | Pass after fix | Fix One Violation and Fix All Rule Violations share `/actions-satisfy`, so they are one Story, Fix Report Violations. |
| right-size-story-nodes | Warn | Draw Board Columns and Draw Ticket Card are display work; kept because each has its own tests and canvas requirements. |
| behaviours-not-one-time-tasks | Pass | Removing Pull is recorded in the Scope boundary, not as a Story. |
| story-map-links-to-markdown | Pass | Every drawio node carries a link to its markdown entry; no Story has its own file, so markdown Stories stay plain text. Headings are at column 0. |
