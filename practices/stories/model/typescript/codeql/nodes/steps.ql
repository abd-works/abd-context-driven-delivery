/**
 * @name steps
 * @kind problem
 * @id cdd/stories/nodes/steps
 */

import javascript
import stories

from CallExpr call, string keyword, string text, string file, string name, int line
where
  stepCall(call, keyword) and
  text = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  name = keyword + " " + text and
  line = stepLine(call)
select stepId(file, line, name), name, "Step", "stories", file, line, stepEnd(call), keyword,
  storyTitle(call), "implementation"
order by file, line
