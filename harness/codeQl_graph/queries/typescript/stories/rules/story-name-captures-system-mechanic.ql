/**
 * @name story-name-captures-system-mechanic
 * @kind problem
 * @id cdd/stories/rules/story-name-captures-system-mechanic
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr story, string title
where
  rule = "story-name-captures-system-mechanic" and
  story.getCalleeName() = "story" and
  title = story.getArgument(0).(StringLiteral).getValue() and
  title.regexpMatch("(Handle|Process|Manage|Do|Run)( .*)?") and
  node = nodeId("stories", "Story", fileOf(story), title) and
  violation = ruleViolation(rule, node, "Story '" + title + "' names a system mechanic.")
select rule, node, violation
