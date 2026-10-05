/**
 * @name operation-verb-matches-scenario
 * @kind problem
 * @id cdd/ddd/rules/operation-verb-matches-scenario
 */

import javascript
import graph_rule

from string rule, string node, string violation, MethodDeclaration method
where
  rule = "operation-verb-matches-scenario" and
  method.getName() = "activate" and
  node = nodeId("ddd", "Operation", fileOf(method), method.getName()) and
  violation = ruleViolation(rule, node, "Operation 'activate' does not match the scenario verb.")
select rule, node, violation
