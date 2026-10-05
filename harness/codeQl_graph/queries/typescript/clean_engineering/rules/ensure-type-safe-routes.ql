/**
 * @name ensure-type-safe-routes
 * @kind problem
 * @id cdd/clean_engineering/rules/ensure-type-safe-routes
 */

import javascript
import graph_rule

from string rule, string node, string violation, Function func, TypeAssertion cast
where
  rule = "ensure-type-safe-routes" and
  cast.getEnclosingFunction() = func and
  cast.getTypeAnnotation().toString() = "any" and
  node = nodeId("clean_engineering", "Operation", fileOf(func), func.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + func.getName() + "' uses any.")
select rule, node, violation
