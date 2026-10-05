/**
 * @name story-owns-backgrounds
 * @kind problem
 * @id cdd/stories/edges/story-owns-backgrounds
 */

import javascript
import stories

from CallExpr call, string file, string label, string parent, string child, int line
where
  call.getCalleeName() = "background" and
  storyFile(call.getFile()) and
  file = slash(call.getFile().getRelativePath()) and
  label = backgroundTitle(call) and
  line = call.getLocation().getStartLine() and
  parent = storyId(file, storyTitle(call)) and
  child = backgroundId(file, label)
select parent, child, "owns", 1, "direct", file, line order by parent, file, line
