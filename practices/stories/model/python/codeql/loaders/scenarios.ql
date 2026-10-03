/**
 * @name Scenario declarations
 * @description scenario('Name') calls nested in a story() test.
 * @kind problem
 * @id cdd/practice-graph/scenarios
 */

import python

from Call call, StringLiteral name, File file, Call story, StringLiteral storyName
where
  call.getFunc().(Name).getId() = "scenario" and
  name = call.getArg(0) and
  file = call.getFile() and
  story.getFunc().(Name).getId() = "story" and
  storyName = story.getArg(0) and
  call.getParent+() = story and
  (
    file.getBaseName().matches("%_story.test.py") or
    file.getBaseName().matches("%_story.spec.py")
  )
select call, name.getValue(), storyName.getValue(), file.getRelativePath(),
  call.getLocation().getStartLine(), call.getLocation().getEndLine()
