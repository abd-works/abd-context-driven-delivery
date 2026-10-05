/**
 * @name repository-owns-aggregate-lifecycle
 * @kind problem
 * @id cdd/ddd/rules/repository-owns-aggregate-lifecycle
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method
where
  rule = "repository-owns-aggregate-lifecycle" and
  method.getName() = "rehydrate" and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Repository rehydrates the aggregate.")
select rule, node, violation
