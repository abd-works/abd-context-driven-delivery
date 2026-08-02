# HIERARCHY: story-graph-ops (excerpt — Story Model)

<!--
Violates: state-oriented-hierarchy, category-headings-not-subjects.

Describes are bare class names; leaves restate operations as if the class were
the actor. No subject noun phrase, no state buildup, no observations of state.
`Story Model` is used as a describe rather than a `##` heading.
-->

Story Model
  StoryMap
    should add an Epic to a StoryMap
    should remove an Epic from a StoryMap
    should reorder Epics in a StoryMap by sequential order
    should list every Story in a StoryMap recursively across every Epic and SubEpic
  Epic
    should rename an Epic
    should add a SubEpic under an Epic
    should remove a SubEpic and its subtree from an Epic
    should reorder SubEpics under an Epic
    should move a SubEpic to a different Epic
  SubEpic
    should rename a SubEpic
    should nest a SubEpic under another SubEpic
    should add a Story under a SubEpic
    should remove a Story from a SubEpic
