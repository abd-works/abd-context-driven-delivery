/**
 * @name Story steps
 * @description given/when/then/.and/.but calls — keyword and label from the TypeScript test.
 * @kind problem
 * @id cdd/practice-graph/steps
 */

import javascript

predicate isStepName(string name) {
  name = "given" or
  name = "when" or
  name = "then" or
  name = "and" or
  name = "but"
}

string scenarioName(CallExpr call) {
  exists(CallExpr scenario, StringLiteral name |
    scenario.getCalleeName() = "scenario" and
    name = scenario.getArgument(0) and
    call.getParent+() = scenario and
    result = name.getValue()
  )
}

string backgroundName(CallExpr call) {
  exists(CallExpr background, StringLiteral name |
    background.getCalleeName() = "background" and
    name = background.getArgument(0) and
    call.getParent+() = background and
    result = name.getValue()
  )
}

from CallExpr call, string callee, StringLiteral arg, File file, CallExpr story, StringLiteral storyName, string scenario, string background
where
  callee = call.getCalleeName() and
  isStepName(callee) and
  arg = call.getArgument(0) and
  file = call.getFile() and
  story.getCalleeName() = "story" and
  storyName = story.getArgument(0) and
  call.getParent+() = story and
  (
    scenario = scenarioName(call)
    or
    not exists(scenarioName(call)) and scenario = ""
  ) and
  (
    background = backgroundName(call)
    or
    not exists(backgroundName(call)) and background = ""
  ) and
  (
    file.getBaseName().matches("%_story.test.js") or
    file.getBaseName().matches("%_story.spec.js")
  )
select call, callee, arg.getValue(), storyName.getValue(), scenario, background,
  file.getRelativePath(), call.getLocation().getStartLine(), call.getLocation().getEndLine()
