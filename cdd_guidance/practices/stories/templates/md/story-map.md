---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story-kebab-slug}.py
     — epic/sub-epic folders kebab-case; one story file per story (no {story}/ folder).
     Exception: Python epic helper only — {epic_slug}_helper.py at epic root.

     Links (`story-map-links-to-markdown`): a Story with its own markdown file links to it
     — [Story Verb–Noun]({epic}/{sub-epic}/{story_snake}_story.test.md). A Story with no file
     stays plain text. In story-map.drawio, each epic, sub-epic, and story cell carries a `link`
     to its entry here (story-map.md#e-sub-epic-verbnoun), or to the story file when one exists.

     Headings start at column 0; the # count is the depth (epic #, sub-epic ##, its stories ###,
     a nested sub-epic ###, its stories ####). Never indent a heading: markdown reads an indented
     line as code, so it gets no anchor and links to it do not land. -->

# Story Map — Product / Feature Name

**Sources / context:** context files used

---

# (E) Epic Verb–Noun
## (E) Sub-Epic Verb–Noun
### (S) Actor --> [Story Verb–Noun]({epic}/{sub-epic}/{story_snake}_story.test.md)
### (S) Actor --> Story Verb–Noun
## (E) Sub-Epic Verb–Noun
### (S) Actor --> Story Verb–Noun

---

## Scope boundary

**In scope:** what is included
**Out of scope:** what is explicitly excluded
