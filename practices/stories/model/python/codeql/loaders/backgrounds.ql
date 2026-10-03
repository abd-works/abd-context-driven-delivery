/**
 * @name Story backgrounds
 * @description background('each') calls in acceptance tests.
 * @kind problem
 * @id cdd/practice-graph/backgrounds
 */

import python

string enclosingScenario(Call call) {
  exists(Call scenario, StringLiteral name |
    scenario.getFunc().(Name).getId() = "scenario" and
    name = scenario.getArg(0) and
    call.getParent+() = scenario and
    result = name.getValue()
  )
}

from Call call, StringLiteral scope, File file, Call story, StringLiteral storyName, string scenario
where
  call.getFunc().(Name).getId() = "background" and
  scope = call.getArg(0) and
  file = call.getFile() and
  story.getFunc().(Name).getId() = "story" and
  storyName = story.getArg(0) and
  call.getParent+() = story and
  (
    scenario = enclosingScenario(call)
    or
    not exists(enclosingScenario(call)) and scenario = ""
  ) and
  (
    file.getBaseName().matches("%_story.test.py") or
    file.getBaseName().matches("%_story.spec.py")
  )
select call, scope.getValue(), storyName.getValue(), file.getRelativePath(),
  call.getLocation().getStartLine(), scenario, call.getLocation().getEndLine()
