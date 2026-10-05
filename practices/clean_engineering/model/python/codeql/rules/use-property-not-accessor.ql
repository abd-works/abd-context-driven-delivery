/**
 * @name use-property-not-accessor
 * @kind problem
 * @id cdd/clean_engineering/rules/use-property-not-accessor
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "use-property-not-accessor" and
  method.isMethod() and
  (method.getName().matches("get_%") or method.getName().matches("set_%")) and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' is an accessor.")
select rule, node, violation
