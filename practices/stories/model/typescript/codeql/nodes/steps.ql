/**
 * @name steps
 * @kind problem
 * @id cdd/stories/nodes/steps
 */

import javascript
import stories

from CallExpr call, string keyword, string text, string file, string name
where
  stepCall(call, keyword) and
  text = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  name = keyword + " " + text
select stepId(file, stepLine(call), name), name, "Step", "stories", file, stepLine(call),
  call.getLocation().getEndLine(), keyword, storyTitle(call), "implementation"
