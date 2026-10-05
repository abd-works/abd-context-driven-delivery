/**
 * @name backgrounds
 * @kind problem
 * @id cdd/stories/nodes/backgrounds
 */

import javascript
import stories.stories

from CallExpr call, string label, string file
where
  call.getCalleeName() = "background" and
  storyFile(call.getFile()) and
  file = slash(call.getFile().getRelativePath()) and
  label = backgroundTitle(call)
select backgroundId(file, label), label, "Background", "stories", file,
  call.getLocation().getStartLine(), call.getLocation().getEndLine(), storyTitle(call), "specification"
