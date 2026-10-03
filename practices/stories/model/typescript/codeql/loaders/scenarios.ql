/**
 * @name Scenario declarations
 * @description scenario('Name') calls nested in a story() test.
 * @kind problem
 * @id cdd/practice-graph/scenarios
 */

import javascript

from CallExpr call, StringLiteral name, File file, CallExpr story, StringLiteral storyName
where
  call.getCalleeName() = "scenario" and
  name = call.getArgument(0) and
  file = call.getFile() and
  story.getCalleeName() = "story" and
  storyName = story.getArgument(0) and
  call.getParent+() = story and
  (
    file.getBaseName().matches("%_story.test.ts") or
    file.getBaseName().matches("%_story.spec.ts")
  )
select call, name.getValue(), storyName.getValue(), file.getRelativePath(),
  call.getLocation().getStartLine(), call.getLocation().getEndLine()
