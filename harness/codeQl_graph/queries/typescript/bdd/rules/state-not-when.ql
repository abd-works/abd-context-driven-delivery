/**
 * @name state-not-when
 * @kind problem
 * @id cdd/bdd/rules/state-not-when
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call, string label
where
  rule = "state-not-when" and
  (call.getCalleeName() = "context" or call.getCalleeName() = "describe") and
  label = call.getArgument(0).(StringLiteral).getValue() and
  label.toLowerCase().matches("when %") and
  node = nodeId("bdd", "Context", fileOf(call), label) and
  violation = ruleViolation(rule, node, "Nested state is named with 'when' instead of a condition.")
select rule, node, violation
