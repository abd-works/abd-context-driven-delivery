/**
 * @name operation-invoked-by-steps
 * @kind problem
 * @id cdd/stories/edges/operation-invoked-by-steps
 */

import javascript
import stories
import members

from CallExpr step, MethodCallExpr call, MethodDefinition callee, string parent, string child
where
  storyStep(step, ["given", "when", "then", "and", "but"], _, _, child) and
  callInsideStep(step, call) and
  callee = resolvedMethod(call) and
  parent = operationNodeId(callee)
select parent, child, "invokedBy", 6, "relationship"
