/**
 * @name scenarios
 * @kind problem
 * @id cdd/stories/nodes/scenarios
 */

import javascript
import stories

from CallExpr call, string name, string file, int line
where
  scenarioCall(call) and
  storyFile(call.getFile()) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  line = call.getLocation().getStartLine()
select scenarioId(file, name), name, "Scenario", "stories", file, line,
  call.getLocation().getEndLine(), storyTitle(call), "specification"
order by file, line
