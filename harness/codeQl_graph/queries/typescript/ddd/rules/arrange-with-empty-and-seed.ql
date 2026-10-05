/**
 * @name arrange-with-empty-and-seed
 * @kind problem
 * @id cdd/ddd/rules/arrange-with-empty-and-seed
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method
where
  rule = "arrange-with-empty-and-seed" and
  method.getName().matches("_empty%") and
  not method.getName() = "_empty" and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Arrange method '" + method.getName() + "' is not _empty.")
select rule, node, violation
