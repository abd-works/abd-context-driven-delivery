/**
 * @name never-swallow-exceptions
 * @kind problem
 * @id cdd/clean_engineering/rules/never-swallow-exceptions
 */

import python
import graph_rule

from string rule, string node, string violation, Function method, ExceptStmt handler
where
  rule = "never-swallow-exceptions" and
  handler.getScope() = method and
  not exists(Stmt body | body = handler.getAStmt() and not body instanceof Pass) and
  node = nodeId("clean_engineering", "Operation", functionPath(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + method.getName() + "' swallows an exception.")
select rule, node, violation
