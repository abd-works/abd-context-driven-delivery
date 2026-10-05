/**
 * @name one-assertion-per-test
 * @kind problem
 * @id cdd/bdd/rules/one-assertion-per-test
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr itCall, Function body, string label
where
  rule = "one-assertion-per-test" and
  itCall.getCalleeName() = "it" and
  body = itCall.getArgument(1) and
  label = itCall.getArgument(0).(StringLiteral).getValue() and
  count(CallExpr assertion | assertion.getCalleeName() = "expect" and assertion.getEnclosingFunction() = body) > 1 and
  node = nodeId("bdd", "Observation", fileOf(itCall), label) and
  violation = ruleViolation(rule, node, "Example has more than one assertion.")
select rule, node, violation
