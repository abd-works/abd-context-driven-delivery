/**
 * @name Scenario declarations
 * @description scenario('Name') calls nested in a story() test.
 * @kind problem
 * @id cdd/practice-graph/scenarios
 */

import javascript

from CallExpr call, StringLiteral name, File file
where
  call.getCalleeName() = "scenario" and
  name = call.getArgument(0) and
  file = call.getFile() and
  file.getBaseName().matches("%_story.test.ts")
select call, name.getValue(), file.getRelativePath(), call.getLocation().getStartLine()
