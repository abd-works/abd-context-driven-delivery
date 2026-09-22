/**
 * @name Story declarations
 * @description story('Name') calls in acceptance tests — epic/sub-epic from the stories/ folder path.
 * @kind problem
 * @id cdd/practice-graph/stories
 */

import javascript

from CallExpr call, StringLiteral name, File file
where
  call.getCalleeName() = "story" and
  name = call.getArgument(0) and
  file = call.getFile() and
  file.getBaseName().matches("%_story.test.ts")
select call, name.getValue(), file.getRelativePath(), call.getLocation().getStartLine()
