/**
 * @name backgrounds
 * @kind problem
 * @id cdd/stories/nodes/backgrounds
 */

import javascript
import stories

from CallExpr call, string label, string file, int line
where
  call.getCalleeName() = "background" and
  storyFile(call.getFile()) and
  file = slash(call.getFile().getRelativePath()) and
  label = backgroundTitle(call) and
  line = call.getLocation().getStartLine()
select backgroundId(file, label), label, "Background", "stories", file, line,
  call.getLocation().getEndLine(), storyTitle(call), "specification"
order by file, line
