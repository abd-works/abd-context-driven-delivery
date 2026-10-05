/**
 * @name aggregate-owns-operation-repo-is-crud
 * @kind problem
 * @id cdd/ddd/rules/aggregate-owns-operation-repo-is-crud
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method
where
  rule = "aggregate-owns-operation-repo-is-crud" and
  method.getDeclaringType().getName().matches("%Repository") and
  method.getName() = "submit" and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Repository operation '" + method.getName() + "' is not CRUD.")
select rule, node, violation
