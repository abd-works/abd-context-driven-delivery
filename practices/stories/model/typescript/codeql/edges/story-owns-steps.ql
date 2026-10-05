/**
 * @name story-owns-steps
 * @kind problem
 * @id cdd/stories/edges/story-owns-steps
 */

import javascript
import stories

from CallExpr call, string keyword, string text, string file, string name, string parent, string child
where
  stepCall(call, keyword) and
  not exists(scenarioTitle(call)) and
  text = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  name = keyword + " " + text and
  parent = storyId(file, storyTitle(call)) and
  child = stepId(file, stepLine(call), name)
select parent, child, "owns", 1, "direct" order by parent, child
