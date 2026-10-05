/**
 * @name story-belongs-to-sub-epic
 * @kind problem
 * @id cdd/stories/edges/story-belongs-to-sub-epic
 */

import javascript
import stories

from CallExpr call, string name, string file, string parent, string child
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  parent = storyId(file, name) and
  child = storyOwner(call.getFile())
select parent, child, "belongsTo", 4, "relationship"
