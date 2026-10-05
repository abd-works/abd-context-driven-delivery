/**
 * @name domain-operation-in-the-step
 * @kind problem
 * @id cdd/stories/rules/domain-operation-in-the-step
 */

import javascript
import graph_rule

from string rule, string node, string violation, Function func, MethodCallExpr call
where
  rule = "domain-operation-in-the-step" and
  func.getName() != "" and
  call.getEnclosingFunction() = func and
  not exists(CallExpr step |
    step.getCalleeName() = ["given", "when", "then", "and", "but"] and
    func = step.getArgument(1)
  ) and
  node = nodeId("stories", "Operation", fileOf(func), func.getName()) and
  violation = ruleViolation(rule, node, "Operation '" + func.getName() + "' calls the domain outside a step.")
select rule, node, violation
