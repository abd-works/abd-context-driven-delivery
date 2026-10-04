/**
 * @name Story steps
 * @description given/when/then/.and/.but calls.
 * @kind problem
 * @id cdd/practice-graph/steps
 */

import javascript
import story_query

from CallExpr call, string callee, StringLiteral arg, File file, string storyName, string scenario, string background
where
  stepCall(call) and
  callee = call.getCalleeName() and
  arg = call.getArgument(0) and
  file = call.getFile() and
  storyName = storyTitle(call) and
  (
    scenario = scenarioTitle(call)
    or
    not exists(scenarioTitle(call)) and scenario = ""
  ) and
  (
    background = backgroundTitle(call)
    or
    not exists(backgroundTitle(call)) and background = ""
  )
select call, callee, arg.getValue(), storyName, scenario, background, file.getRelativePath(),
  stepLine(call), call.getLocation().getEndLine()
