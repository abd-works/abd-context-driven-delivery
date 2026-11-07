---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

<!-- Discovery fidelity — every sub-epic decomposed to named stories.
     Do not wrap epic, sub-epic, story, or actor names in backticks.

     Disk layout (`artifacts-mirror-story-hierarchy` + `kebab-case-paths`):
     tests/{epic-verb-noun}/{sub_epic_verb_noun}_story.test.{ext}
     — every epic is a kebab-case folder; each sub-epic's stories share one story test file in
     it, and a sub-epic with sub-epics of its own is a folder too. An epic's own stories sit in
     {epic_verb_noun}_story.test.{ext} inside the epic's folder.

     Links (`story-map-links-to-markdown`): a Story with its own markdown file links to it
     — [Story Verb–Noun]({epic}/{sub-epic}/{story_snake}_story.test.md). A Story with no file
     stays plain text. In story-map.drawio, each epic, sub-epic, and story cell carries a `link`
     to its entry here (story-map.md#e-sub-epic-verbnoun), or to the story file when one exists.

     Story kind (`story_type`): `(S)` marks a user story. A story another system performs, with no person
     acting, is `(S:system)`; a story about the system's own technical work is `(S:technical)`. Write the
     kind only when it is not a user story, so every channel (drawio, miro, sketch, json) keeps it.

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
### (S:system) System --> Story Verb–Noun
## (E) Sub-Epic Verb–Noun
### (S) Actor --> Story Verb–Noun

---

## Scope boundary

**In scope:** what is included
**Out of scope:** what is explicitly excluded
