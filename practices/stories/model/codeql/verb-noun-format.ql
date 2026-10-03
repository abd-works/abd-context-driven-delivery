/**
 * @name verb-noun-format
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/verb-noun-format
 * CodeQL emits the story label. Python WordNet decides verb then noun.
 */

import javascript
import subject_filter
import model

from CallExpr call, string label
where inSubject(call) and storyLabel(call, label)
select call, label, call
