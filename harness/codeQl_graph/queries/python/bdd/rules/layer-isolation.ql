/**
 * @name layer-isolation
 * @kind problem
 * @id cdd/bdd/rules/layer-isolation
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string target
where
  rule = "layer-isolation" and
  (
    call.getFunc().(Name).getId() = "patch" or
    call.getFunc().(Name).getId() = "mock" or
    call.getFunc().(Attribute).getName() = "patch" or
    call.getFunc().(Attribute).getName() = "mock"
  ) and
  target = call.getArg(0).(StringLiteral).getS() and
  (target.matches("./%") or target.matches("../%") or target.matches(".%")) and
  node = nodeId("bdd", "Observation", slash(call.getLocation().getFile().getRelativePath()), target) and
  violation = ruleViolation(rule, node, "Mock targets internal module '" + target + "'.")
select rule, node, violation
