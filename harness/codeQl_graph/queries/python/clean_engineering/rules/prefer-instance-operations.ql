/**
 * @name prefer-instance-operations
 * @kind problem
 * @id cdd/clean_engineering/rules/prefer-instance-operations
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "prefer-instance-operations" and
  method.getADecorator().(Name).getId() = "classmethod" and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' is a class method.")
select rule, node, violation
