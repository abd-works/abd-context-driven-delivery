/**
 * @name verb-noun-format
 * @kind problem
 * @id cdd/stories/rules/verb-noun-format
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr story, string title
where
  rule = "verb-noun-format" and
  story.getCalleeName() = "story" and
  title = story.getArgument(0).(StringLiteral).getValue() and
  not title.matches("% %") and
  node = nodeId("stories", "Story", fileOf(story), title) and
  violation = ruleViolation(rule, node, "Story '" + title + "' is not verb-noun.")
select rule, node, violation
