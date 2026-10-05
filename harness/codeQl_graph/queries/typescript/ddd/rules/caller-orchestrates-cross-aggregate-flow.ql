/**
 * @name caller-orchestrates-cross-aggregate-flow
 * @kind problem
 * @id cdd/ddd/rules/caller-orchestrates-cross-aggregate-flow
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodCallExpr call
where
  rule = "caller-orchestrates-cross-aggregate-flow" and
  call.getReceiver() instanceof VarAccess and
  node = nodeId("ddd", "Operation", fileOf(call), call.getCalleeName()) and
  violation = ruleViolation(rule, node, "Caller reaches '" + call.getCalleeName() + "' through another aggregate.")
select rule, node, violation
