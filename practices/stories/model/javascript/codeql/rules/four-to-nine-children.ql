/**
 * @name four-to-nine-children
 * @practice stories
 * @fidelity story_map
 * @node stories
 * @id stories/story_map/four-to-nine-children
 */

import javascript
import model

from CallExpr story, string name, int n
where
  storyCall(story) and
  storyLabel(story, name) and
  n = scenarioCount(story) and
  tooFewOrManyScenarios(story)
select story,
  "Story '" + name + "' has " + n.toString() + " scenarios (target 4-9).", story
