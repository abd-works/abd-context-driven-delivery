/**
 * @name use-exceptions-properly
 * @kind problem
 * @id cdd/clean_engineering/rules/use-exceptions-properly
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, ExceptStmt handler
where
  rule = "use-exceptions-properly" and
  handler.getScope() = method and
  not exists(handler.getType()) and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' has a bare except.")
select rule, node, violation
