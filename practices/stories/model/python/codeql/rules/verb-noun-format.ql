/**
 * @name verb-noun-format
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/verb-noun-format
 * CodeQL emits the story label. Python WordNet decides verb then noun.
 */

import python
import subject_filter
import model

from Call call, string label
where inSubject(call) and storyLabel(call, label)
select call, label, call
