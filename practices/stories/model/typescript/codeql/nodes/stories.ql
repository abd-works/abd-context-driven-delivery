/**
 * @name stories
 * @kind problem
 * @id cdd/stories/nodes/stories
 */

import javascript
import stories

from CallExpr call, string name, string file, int line
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  line = call.getLocation().getStartLine()
select storyId(file, name), name, "Story", "stories", file, line,
  call.getLocation().getEndLine(), epicId(epicFolder(call.getFile())), "discovery"
order by file, line
