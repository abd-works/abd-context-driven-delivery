/**
 * @name story-belongs-to-epic
 * @kind problem
 * @id cdd/stories/edges/story-belongs-to-epic
 */

import javascript
import stories.stories

from CallExpr call, string name, string file, string parent, string child
where
  storyCall(call) and
  name = call.getArgument(0).(StringLiteral).getValue() and
  file = slash(call.getFile().getRelativePath()) and
  parent = storyId(file, name) and
  child = epicId(epicFolder(call.getFile()))
select parent, child, "belongsTo", 4, "relationship"
