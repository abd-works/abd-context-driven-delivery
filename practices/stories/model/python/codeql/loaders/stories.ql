/**
 * @name Story declarations
 * @description story('Name') calls in acceptance tests — epic/sub-epic from the stories/ folder path.
 * @kind problem
 * @id cdd/practice-graph/stories
 */

import python

from Call call, StringLiteral name, File file
where
  call.getFunc().(Name).getId() = "story" and
  name = call.getArg(0) and
  file = call.getFile() and
  (
    file.getBaseName().matches("%_story.test.py") or
    file.getBaseName().matches("%_story.spec.py")
  )
select call, name.getValue(), file.getRelativePath(), call.getLocation().getStartLine(),
  call.getLocation().getEndLine()
