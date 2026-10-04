/**
 * @name Story declarations
 * @description story() and shareStory() calls in acceptance tests.
 * @kind problem
 * @id cdd/practice-graph/stories
 */

import javascript
import story_query

from CallExpr call, StringLiteral name, File file
where
  storyCall(call) and
  name = call.getArgument(0) and
  file = call.getFile()
select call, name.getValue(), file.getRelativePath(), call.getLocation().getStartLine(),
  call.getLocation().getEndLine()
