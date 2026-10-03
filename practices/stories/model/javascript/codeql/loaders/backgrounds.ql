/**
 * @name Story backgrounds
 * @description background('each') calls in acceptance tests.
 * @kind problem
 * @id cdd/practice-graph/backgrounds
 */

import javascript

string enclosingScenario(CallExpr call) {
  exists(CallExpr scenario, StringLiteral name |
    scenario.getCalleeName() = "scenario" and
    name = scenario.getArgument(0) and
    call.getParent+() = scenario and
    result = name.getValue()
  )
}

from CallExpr call, StringLiteral scope, File file, CallExpr story, StringLiteral storyName, string scenario
where
  call.getCalleeName() = "background" and
  scope = call.getArgument(0) and
  file = call.getFile() and
  story.getCalleeName() = "story" and
  storyName = story.getArgument(0) and
  call.getParent+() = story and
  (
    scenario = enclosingScenario(call)
    or
    not exists(enclosingScenario(call)) and scenario = ""
  ) and
  (
    file.getBaseName().matches("%_story.test.js") or
    file.getBaseName().matches("%_story.spec.js")
  )
select call, scope.getValue(), storyName.getValue(), file.getRelativePath(),
  call.getLocation().getStartLine(), scenario, call.getLocation().getEndLine()
