/**
 * @name four-to-nine-children
 * @kind problem
 * @id cdd/stories/rules/four-to-nine-children
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr story, string title, int children
where
  rule = "four-to-nine-children" and
  story.getCalleeName() = "story" and
  title = story.getArgument(0).(StringLiteral).getValue() and
  children = count(CallExpr scenario |
      scenario.getCalleeName() = "scenario" and
      scenario.getEnclosingFunction() = story.getArgument(1).(Function)
    ) and
  (children < 4 or children > 9) and
  node = nodeId("stories", "Story", fileOf(story), title) and
  violation = ruleViolation(rule, node, "Story '" + title + "' has " + children.toString() + " scenarios.")
select rule, node, violation
