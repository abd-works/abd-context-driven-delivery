/**
 * @name keep-operations-small-focused
 * @kind problem
 * @id cdd/clean_engineering/rules/keep-operations-small-focused
 */

import python
import graph_rule

from string rule, string node, string violation, Function method
where
  rule = "keep-operations-small-focused" and
  count(Stmt stmt | stmt.getScope() = method) > 20 and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' is longer than 20 statements.")
select rule, node, violation
