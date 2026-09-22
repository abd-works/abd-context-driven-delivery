/**
 * @name plain-english-gwt-steps
 * @kind problem
 * @id cdd/practice-graph/plain-english-gwt-steps
 * @problem.severity warning
 */

import javascript
import subject_filter
import model

from CallExpr call, string keyword, string label
where
  inSubject(call) and
  stepCall(call, keyword) and
  label = call.getArgument(0).(StringLiteral).getValue() and
  identifierStep(label)
select call, "Step '" + label + "' is a code identifier, not a plain-English sentence.", call
