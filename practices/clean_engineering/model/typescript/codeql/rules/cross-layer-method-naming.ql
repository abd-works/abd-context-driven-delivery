/**
 * @name cross-layer-method-naming
 * @kind problem
 * @id cdd/clean_engineering/rules/cross-layer-method-naming
 */

import javascript
import graph_rule

from string rule, string node, string violation, Function func
where
  rule = "cross-layer-method-naming" and
  func.getName().matches("fetch%") and
  fileOf(func).matches("%-client.%") and
  node = nodeId("clean_engineering", "Operation", fileOf(func), func.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + func.getName() + "' is named for the remote layer.")
select rule, node, violation
