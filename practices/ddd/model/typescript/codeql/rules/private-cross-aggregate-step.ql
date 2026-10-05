/**
 * @name private-cross-aggregate-step
 * @kind problem
 * @id cdd/ddd/rules/private-cross-aggregate-step
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method
where
  rule = "private-cross-aggregate-step" and
  method.getName() = "newCustomer" and
  not method.isPrivate() and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Cross-aggregate step 'newCustomer' is public.")
select rule, node, violation
