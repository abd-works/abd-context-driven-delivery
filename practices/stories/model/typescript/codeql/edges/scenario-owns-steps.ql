/**
 * @name scenario-owns-steps
 * @kind problem
 * @id cdd/stories/edges/scenario-owns-steps
 */

import javascript
import stories

from CallExpr call, string keyword, string text, string file, string name, string parent, string child, int line
where
  stepCall(call, ["given", "when", "then"]) and
  keyword = call.getCalleeName() and
  text = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  name = keyword + " " + text and
  line = stepLine(call) and
  parent = scenarioId(file, scenarioTitle(call)) and
  child = stepId(file, line, name)
select parent, child, "owns", 1, "direct", file, line order by parent, file, line
