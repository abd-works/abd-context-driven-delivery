/**
 * @name use-intention-revealing-names
 * @kind problem
 * @id cdd/clean_engineering/rules/use-intention-revealing-names
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Name local
where
  rule = "use-intention-revealing-names" and
  local.getScope() = method and
  local.getId().length() <= 2 and
  not local.getId() = "id" and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' uses the name '" + local.getId() + "'.")
select rule, node, violation
