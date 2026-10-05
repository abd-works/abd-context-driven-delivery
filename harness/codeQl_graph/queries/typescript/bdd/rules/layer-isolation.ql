/**
 * @name layer-isolation
 * @kind problem
 * @id cdd/bdd/rules/layer-isolation
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr call, string target
where
  rule = "layer-isolation" and
  (call.getCalleeName() = "mock" or call.getCalleeName() = "spyOn") and
  target = call.getArgument(0).(StringLiteral).getValue() and
  (target.matches("./%") or target.matches("../%") or target.matches(".%")) and
  node = nodeId("bdd", "Observation", fileOf(call), target) and
  violation = ruleViolation(rule, node, "Mock targets internal module '" + target + "'.")
select rule, node, violation
