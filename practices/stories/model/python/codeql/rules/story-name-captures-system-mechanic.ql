/**
 * @name story-name-captures-system-mechanic
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/story-name-captures-system-mechanic
 * CodeQL emits the story label. Python WordNet decides whether the verb is a
 * vague doer word over a generic noun.
 */

import python
import subject_filter
import model

from Call call, string label
where inSubject(call) and storyLabel(call, label)
select call, label, call
