# HIERARCHY: story-graph-ops (excerpt — Story Model)

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
