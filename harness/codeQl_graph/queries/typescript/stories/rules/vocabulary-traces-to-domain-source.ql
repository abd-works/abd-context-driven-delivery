/**
 * @name vocabulary-traces-to-domain-source
 * @kind problem
 * @id cdd/stories/rules/vocabulary-traces-to-domain-source
 */

import javascript
import graph_rule

from string rule, string node, string violation, CallExpr story, string title
where
  rule = "vocabulary-traces-to-domain-source" and
  story.getCalleeName() = "story" and
  title = story.getArgument(0).(StringLiteral).getValue() and
  not exists(ClassDefinition cls |
    cls.getFile() = story.getFile() and
    title.matches("%" + cls.getName() + "%")
  ) and
  node = nodeId("stories", "Story", fileOf(story), title) and
  violation = ruleViolation(rule, node, "Story '" + title + "' names no class in the file.")
select rule, node, violation
