/**
 * @name prefer-class-operations
 * @kind problem
 * @id cdd/clean_engineering/rules/prefer-class-operations
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "prefer-class-operations" and
  not method.isMethod() and
  exists(method.getName()) and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' is a module function.")
select rule, node, violation
