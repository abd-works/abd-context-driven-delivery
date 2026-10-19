# Stories relationships that cross a practice

Recorded when the graph working copy loads in `harness/graph/working_copy.py` (`_record_story_edges`). `owns` and `scopes` stay inside stories.

| Kind | From | To | When |
|------|------|-----|------|
| invokes | Step | Operation / Property | When step body or callee list names the member |
| invokedBy | Operation | Step | Inverse of invokes on clean engineering |
| usedBy | Module | Epic | Module home folder matches invoked operation |
| uses | Epic | Module | Inverse on stories |
| observes | Step | Example | Then step references example name |
| demonstrates | Example | OoadClass | Example source mentions class |
| demonstratedThrough | OoadClass | Example | Inverse on clean engineering |
| retrievedUsing | Example | Property | Example reads property |

The walk in `practices/stories/model/.context/story-model.md` loads the example on `Step`. Cross-practice edges attach after both stories and clean engineering practices are loaded. A transform to another channel traverses those edges on the loaded graph.
