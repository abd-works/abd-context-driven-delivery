/**
 * @name pml-artifact-layout
 * @kind problem
 * @id cdd/stories/rules/pml-artifact-layout
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "pml-artifact-layout" and
  slash(file.getRelativePath()).matches("%_story.ts") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Story artifact uses an underscore name.")
select rule, node, violation
