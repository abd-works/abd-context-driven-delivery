/**
 * @name Story steps
 * @description given/when/then/.and/.but calls — keyword and label from the TypeScript test.
 * @kind problem
 * @id cdd/practice-graph/steps
 */

import python

predicate isStepName(string name) {
  name = "given" or
  name = "when" or
  name = "then" or
  name = "and" or
  name = "but"
}

string scenarioName(Call call) {
  exists(Call scenario, StringLiteral name |
    scenario.getFunc().(Name).getId() = "scenario" and
    name = scenario.getArg(0) and
    call.getParent+() = scenario and
    result = name.getValue()
  )
}

string backgroundName(Call call) {
  exists(Call background, StringLiteral name |
    background.getFunc().(Name).getId() = "background" and
    name = background.getArg(0) and
    call.getParent+() = background and
    result = name.getValue()
  )
}

from Call call, string callee, StringLiteral arg, File file, Call story, StringLiteral storyName, string scenario, string background
where
  callee = call.getFunc().(Name).getId() and
  isStepName(callee) and
  arg = call.getArg(0) and
  file = call.getFile() and
  story.getFunc().(Name).getId() = "story" and
  storyName = story.getArg(0) and
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
    file.getBaseName().matches("%_story.test.py") or
    file.getBaseName().matches("%_story.spec.py")
  )
select call, callee, arg.getValue(), storyName.getValue(), scenario, background,
  file.getRelativePath(), call.getLocation().getStartLine(), call.getLocation().getEndLine()
