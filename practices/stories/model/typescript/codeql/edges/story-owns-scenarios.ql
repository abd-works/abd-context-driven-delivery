/**
 * @name story-owns-scenarios
 * @kind problem
 * @id cdd/stories/edges/story-owns-scenarios
 */

import javascript
import stories

from CallExpr call, string name, string file, string parent, string child
where
  scenarioCall(call) and
  storyFile(call.getFile()) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  parent = storyId(file, storyTitle(call)) and
  child = scenarioId(file, name)
select parent, child, "owns", 1, "direct" order by parent, child
