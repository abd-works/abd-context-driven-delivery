/**
 * @name throw-typed-exception-with-message
 * @kind problem
 * @id cdd/ddd/rules/throw-typed-exception-with-message
 */

import javascript
import graph_rule

from string rule, string node, string violation, ThrowStmt thrown
where
  rule = "throw-typed-exception-with-message" and
  thrown.getExpr() instanceof ObjectExpr and
  node = nodeId("ddd", "Operation", fileOf(thrown), "throw") and
  violation = ruleViolation(rule, node, "Throw uses an object literal.")
select rule, node, violation
