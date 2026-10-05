/**
 * @name layer-separation
 * @kind problem
 * @id cdd/clean_engineering/rules/layer-separation
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Call call
where
  rule = "layer-separation" and
  call.getScope() = method and
  count(Call other | other.getScope() = method) = 1 and
  count(Stmt stmt | stmt.getScope() = method) = 1 and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' only forwards a call.")
select rule, node, violation
