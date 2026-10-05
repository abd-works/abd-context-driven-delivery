/**
 * @name right-size-story-nodes
 * @kind problem
 * @id cdd/stories/rules/right-size-story-nodes
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr left, CallExpr right, string shorter, string longer
where
  rule = "right-size-story-nodes" and
  left.getCalleeName() = "story" and
  right.getCalleeName() = "story" and
  left.getFile() = right.getFile() and
  left != right and
  shorter = left.getArgument(0).(StringLiteral).getValue() and
  longer = right.getArgument(0).(StringLiteral).getValue() and
  shorter.length() < longer.length() and
  longer.length() - shorter.length() <= 2 and
  node = nodeId("stories", "Story", fileOf(left), shorter) and
  violation = ruleViolation(rule, node, "Story '" + shorter + "' is a near-duplicate of '" + longer + "'.")
select rule, node, violation
