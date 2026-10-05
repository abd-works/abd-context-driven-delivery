/**
 * @name test-story-driven
 * @kind problem
 * @id cdd/stories/rules/test-story-driven
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "test-story-driven" and
  slash(file.getRelativePath()).matches("%.test.ts") and
  not slash(file.getRelativePath()).matches("%server.test.ts") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Test file is not a server story test.")
select rule, node, violation
