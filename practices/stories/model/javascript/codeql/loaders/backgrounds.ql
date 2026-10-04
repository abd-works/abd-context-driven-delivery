/**
 * @name Story backgrounds
 * @description background() calls. The scope each/all is a background, not its name.
 * @kind problem
 * @id cdd/practice-graph/backgrounds
 */

import javascript
import story_query

from CallExpr call, File file, string storyName, string scenario, string label
where
  call.getCalleeName() = "background" and
  storyFile(call.getFile()) and
  file = call.getFile() and
  storyName = storyTitle(call) and
  label = backgroundTitle(call) and
  (
    scenario = scenarioTitle(call)
    or
    not exists(scenarioTitle(call)) and scenario = ""
  )
select call, label, storyName, file.getRelativePath(), call.getLocation().getStartLine(),
  scenario, call.getLocation().getEndLine()
