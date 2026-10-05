/**
 * @name step-invokes-operations
 * @kind problem
 * @id cdd/stories/edges/step-invokes-operations
 */

import javascript
import stories
import members

from CallExpr step, MethodCallExpr call, MethodDefinition callee, string parent, string child
where
  storyStep(step, ["given", "when", "then", "and", "but"], _, _, parent) and
  callInsideStep(step, call) and
  callee = resolvedMethod(call) and
  child = operationNodeId(callee)
select parent, child, "invokes", 5, "relationship"
