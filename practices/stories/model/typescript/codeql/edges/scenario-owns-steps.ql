/**
 * @name scenario-owns-steps
 * @kind problem
 * @id cdd/stories/edges/scenario-owns-steps
 */

import javascript
import stories

from CallExpr call, string keyword, string text, string file, string name, string parent, string child
where
  stepCall(call, keyword) and
  text = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  name = keyword + " " + text and
  parent = scenarioId(file, scenarioTitle(call)) and
  child = stepId(file, stepLine(call), name)
select parent, child, "owns", 1, "direct" order by parent, child
