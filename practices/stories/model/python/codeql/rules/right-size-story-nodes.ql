/**
 * @name right-size-story-nodes
 * @kind problem
 * @id cdd/stories/rules/right-size-story-nodes
 */

import python
import graph_rule

from string rule, string node, string violation, Call left, Call right, string leftName, string rightName
where
  rule = "right-size-story-nodes" and
  left.getFunc().(Name).getId() = "story" and
  right.getFunc().(Name).getId() = "story" and
  left != right and
  left.getLocation().getFile() = right.getLocation().getFile() and
  leftName = left.getArg(0).(StringLiteral).getS() and
  rightName = right.getArg(0).(StringLiteral).getS() and
  leftName < rightName and
  leftName.length() - rightName.length() <= 2 and
  rightName.length() - leftName.length() <= 2 and
  node = nodeId("stories", "Story", slash(left.getLocation().getFile().getRelativePath()), leftName) and
  violation = ruleViolation(rule, node, "Sibling stories '" + leftName + "' and '" + rightName + "' differ by at most two characters.")
select rule, node, violation
