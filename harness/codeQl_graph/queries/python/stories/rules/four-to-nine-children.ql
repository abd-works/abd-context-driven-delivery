/**
 * @name four-to-nine-children
 * @kind problem
 * @id cdd/stories/rules/four-to-nine-children
 */

import python
import graph_rule

from string rule, string node, string violation, With story, Call call, int n
where
  rule = "four-to-nine-children" and
  call.getFunc().(Name).getId() = "story" and
  story.getContextExpr() = call and
  n = count(With inner |
    inner.getParentNode+() = story and
    inner.getContextExpr().(Call).getFunc().(Name).getId() = "scenario"
  ) and
  (n < 4 or n > 9) and
  node = nodeId("stories", "Story", slash(call.getLocation().getFile().getRelativePath()), call.getArg(0).(StringLiteral).getS()) and
  violation = ruleViolation(rule, node, "Story '" + call.getArg(0).(StringLiteral).getS() + "' has " + n.toString() + " scenarios (target 4-9).")
select rule, node, violation
