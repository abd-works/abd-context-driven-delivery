/**
 * @name fluent-operation-returns-next-aggregate
 * @kind problem
 * @id cdd/ddd/rules/fluent-operation-returns-next-aggregate
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call
where
  rule = "fluent-operation-returns-next-aggregate" and
  call.getCalleeName() = "storeCustomerId" and
  node = nodeId("ddd", "Operation", fileOf(call), call.getCalleeName()) and
  violation = ruleViolation(rule, node, "Flow stores an id on the next aggregate.")
select rule, node, violation
