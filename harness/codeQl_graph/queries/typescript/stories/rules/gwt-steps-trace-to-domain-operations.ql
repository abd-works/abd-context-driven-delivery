/**
 * @name gwt-steps-trace-to-domain-operations
 * @kind problem
 * @id cdd/stories/rules/gwt-steps-trace-to-domain-operations
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr step, string label
where
  rule = "gwt-steps-trace-to-domain-operations" and
  step.getCalleeName() = ["given", "when", "then"] and
  label = step.getArgument(0).(StringLiteral).getValue() and
  not exists(ClassDefinition cls |
    cls.getFile() = step.getFile() and
    label.matches("%" + cls.getName() + "%")
  ) and
  node = nodeId("stories", "Step", fileOf(step), label) and
  violation = ruleViolation(rule, node, "Step '" + label + "' names no class in the file.")
select rule, node, violation
