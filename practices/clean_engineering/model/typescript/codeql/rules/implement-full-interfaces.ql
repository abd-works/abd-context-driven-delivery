/**
 * @name implement-full-interfaces
 * @kind problem
 * @id cdd/clean_engineering/rules/implement-full-interfaces
 */

import javascript
import graph_rule

from string rule, string node, string violation, ThrowStmt thrown, NewExpr error
where
  rule = "implement-full-interfaces" and
  thrown.getExpr() = error and
  error.getCalleeName() = "Error" and
  error.getArgument(0).(StringLiteral).getValue() = "not implemented" and
  node = nodeId("clean_engineering", "Operation", fileOf(thrown), "not implemented") and
  violation = ruleViolation(rule, node, "Operation throws not implemented.")
select rule, node, violation
