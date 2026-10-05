/**
 * @name stories
 * @kind problem
 * @id cdd/stories/nodes/stories
 */

import javascript
import stories

from CallExpr call, string name, string file
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath())
select storyId(file, name), name, "Story", "stories", file, call.getLocation().getStartLine(),
  call.getLocation().getEndLine(), epicId(epicFolder(call.getFile())), "discovery"
