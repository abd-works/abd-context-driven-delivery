/**
 * @name use-consistent-naming
 * @kind problem
 * @id cdd/clean_engineering/rules/use-consistent-naming
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, Class owner
where
  rule = "use-consistent-naming" and
  method.isMethod() and
  owner = method.getScope() and
  method.getName().matches(owner.getName().toLowerCase() + "_%") and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' repeats its class name.")
select rule, node, violation
