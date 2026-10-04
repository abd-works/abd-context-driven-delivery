/**
 * @name Scenario declarations
 * @description scenario() calls nested in a story.
 * @kind problem
 * @id cdd/practice-graph/scenarios
 */

import javascript
import story_query

from CallExpr call, StringLiteral name, File file, string storyName
where
  call.getCalleeName() = "scenario" and
  storyFile(call.getFile()) and
  name = call.getArgument(0) and
  file = call.getFile() and
  storyName = storyTitle(call)
select call, name.getValue(), storyName, file.getRelativePath(),
  call.getLocation().getStartLine(), call.getLocation().getEndLine()
