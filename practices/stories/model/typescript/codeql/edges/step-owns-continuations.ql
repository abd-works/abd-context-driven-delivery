/**
 * @name step-owns-continuations
 * @kind problem
 * @id cdd/stories/edges/step-owns-continuations
 */

import javascript
import stories

from CallExpr step, CallExpr prior, string keyword, string text, string file, string name, string parent, string child, int line
where
  continuesStep(step, prior) and
  keyword = step.getCalleeName() and
  text = step.getArgument(0).(StringLiteral).getValue() and
  file = slash(step.getFile().getRelativePath()) and
  name = keyword + " " + text and
  line = stepLine(step) and
  parent = stepId(file, stepLine(prior), prior.getCalleeName() + " " + prior.getArgument(0).(StringLiteral).getValue()) and
  child = stepId(file, line, name)
select parent, child, "owns", 1, "direct", file, line order by parent, file, line
