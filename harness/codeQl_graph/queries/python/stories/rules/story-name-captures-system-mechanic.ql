/**
 * @name story-name-captures-system-mechanic
 * @kind problem
 * @id cdd/stories/rules/story-name-captures-system-mechanic
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "story-name-captures-system-mechanic" and
  call.getFunc().(Name).getId() = "story" and
  label = call.getArg(0).(StringLiteral).getS() and
  label.toLowerCase().regexpMatch("(do|handle|process|manage|run)( .*)?") and
  node = nodeId("stories", "Story", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Story '" + label + "' names a vague system mechanic.")
select rule, node, violation
