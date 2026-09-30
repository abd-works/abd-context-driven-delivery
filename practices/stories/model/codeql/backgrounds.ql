/**
 * @name Story backgrounds
 * @description background('each') calls in acceptance tests.
 * @kind problem
 * @id cdd/practice-graph/backgrounds
 */

import javascript

from CallExpr call, StringLiteral scope, File file
where
  call.getCalleeName() = "background" and
  scope = call.getArgument(0) and
  file = call.getFile() and
  (
    file.getBaseName().matches("%_story.test.ts") or
    file.getBaseName().matches("%_story.spec.ts")
  )
select call, scope.getValue(), file.getRelativePath(), call.getLocation().getStartLine()
