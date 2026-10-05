/**
 * @name use-thorough-e2e-tests
 * @kind problem
 * @id cdd/stories/rules/use-thorough-e2e-tests
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call
where
  rule = "use-thorough-e2e-tests" and
  call.getCalleeName() = "deleteMany" and
  node = nodeId("stories", "Operation", fileOf(call), "deleteMany") and
  violation = ruleViolation(rule, node, "End-to-end test wipes the store.")
select rule, node, violation
