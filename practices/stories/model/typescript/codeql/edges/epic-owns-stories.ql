/**
 * @name sub-epic-owns-stories
 * @kind problem
 * @id cdd/stories/edges/sub-epic-owns-stories
 */

import javascript
import stories

from CallExpr call, string name, string file, string parent, string child
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  parent = storyOwner(call.getFile()) and
  child = storyId(file, name)
select parent, child, "owns", 1, "direct" order by parent, child
