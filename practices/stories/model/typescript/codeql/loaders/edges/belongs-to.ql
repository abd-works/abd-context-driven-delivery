/**
 * @name belongs-to
 * @kind problem
 * @id cdd/stories/edges/belongs-to
 */

import javascript
import stories

from CallExpr call, string name, string file
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath())
select storyId(file, name), epicId(epicFolder(call.getFile())), "belongsTo", 4, "relationship"
