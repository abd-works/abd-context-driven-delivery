/**
 * @name observable-behavior
 * @kind problem
 * @id cdd/bdd/rules/observable-behavior
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call, PropAccess access
where
  rule = "observable-behavior" and
  call.getCalleeName() = "expect" and
  access = call.getArgument(0) and
  access.getPropertyName().matches("_%") and
  not access.getPropertyName().matches("__%") and
  node = nodeId("bdd", "Observation", fileOf(call), access.getPropertyName()) and
  violation = ruleViolation(rule, node, "Assertion observes a private attribute instead of stakeholder-visible behaviour.")
select rule, node, violation
