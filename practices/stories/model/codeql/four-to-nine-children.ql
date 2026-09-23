/**
 * @name four-to-nine-children
 * @kind problem
 * @id cdd/practice-graph/four-to-nine-children
 * @problem.severity warning
 */

import python
import model

from With story, string name, int n
where
  storyWith(story, name) and
  n = scenarioCount(story) and
  tooFewOrManyScenarios(story)
select story,
  "Story '" + name + "' has " + n.toString() + " scenarios (target 4-9).", story
