/**
 * @name verb-noun-format
 * @kind problem
 * @id cdd/stories/rules/verb-noun-format
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "verb-noun-format" and
  call.getFunc().(Name).getId() = "story" and
  label = call.getArg(0).(StringLiteral).getS() and
  not label.matches("% %") and
  node = nodeId("stories", "Story", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Story '" + label + "' is not a verb then a noun.")
select rule, node, violation
