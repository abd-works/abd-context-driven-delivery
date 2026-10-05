/**
 * @name plain-english-gwt-steps
 * @kind problem
 * @id cdd/stories/rules/plain-english-gwt-steps
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr step, string label
where
  rule = "plain-english-gwt-steps" and
  step.getCalleeName() = ["given", "when", "then"] and
  label = step.getArgument(0).(StringLiteral).getValue() and
  label.regexpMatch("[A-Za-z_][A-Za-z0-9_]*") and
  node = nodeId("stories", "Step", fileOf(step), label) and
  violation = ruleViolation(rule, node, "Step '" + label + "' is not plain English.")
select rule, node, violation
