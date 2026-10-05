/**
 * @name owns
 * @kind problem
 * @id cdd/stories/edges/owns
 */

import javascript
import stories

from string parent, string child
where
  exists(File file, string folder |
    storyFile(file) and
    folder = epicFolder(file) and
    parent = storiesPracticeId() and
    child = epicId(folder)
  )
  or
  exists(CallExpr call, string name, string file |
    storyCall(call) and
    name = call.getArgument(0).(StringLiteral).getValue() and
    file = slash(call.getFile().getRelativePath()) and
    parent = epicId(epicFolder(call.getFile())) and
    child = storyId(file, name)
  )
  or
  exists(CallExpr call, string name, string file |
    scenarioCall(call) and
    storyFile(call.getFile()) and
    name = call.getArgument(0).(StringLiteral).getValue() and
    file = slash(call.getFile().getRelativePath()) and
    parent = storyId(file, storyTitle(call)) and
    child = scenarioId(file, name)
  )
  or
  exists(CallExpr call, string file, string label |
    call.getCalleeName() = "background" and
    storyFile(call.getFile()) and
    file = slash(call.getFile().getRelativePath()) and
    label = backgroundTitle(call) and
    parent = storyId(file, storyTitle(call)) and
    child = backgroundId(file, label)
  )
  or
  exists(CallExpr call, string keyword, string text, string file, string name |
    stepCall(call, keyword) and
    text = call.getArgument(0).(StringLiteral).getValue() and
    file = slash(call.getFile().getRelativePath()) and
    name = keyword + " " + text and
    parent = scenarioId(file, scenarioTitle(call)) and
    child = stepId(file, stepLine(call), name)
  )
  or
  exists(CallExpr call, string keyword, string text, string file, string name |
    stepCall(call, keyword) and
    not exists(scenarioTitle(call)) and
    text = call.getArgument(0).(StringLiteral).getValue() and
    file = slash(call.getFile().getRelativePath()) and
    name = keyword + " " + text and
    parent = storyId(file, storyTitle(call)) and
    child = stepId(file, stepLine(call), name)
  )
select parent, child, "owns", 1, "direct"
