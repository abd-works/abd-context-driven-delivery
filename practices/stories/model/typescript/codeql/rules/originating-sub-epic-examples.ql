/**
 * @name originating-sub-epic-examples
 * @kind problem
 * @id cdd/stories/rules/originating-sub-epic-examples
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "originating-sub-epic-examples" and
  slash(file.getRelativePath()).regexpMatch(".*tests/[^/]+/examples/.*") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Examples sit on the epic instead of the sub-epic.")
select rule, node, violation
