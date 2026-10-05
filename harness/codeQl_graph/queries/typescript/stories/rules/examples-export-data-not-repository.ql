/**
 * @name examples-export-data-not-repository
 * @kind problem
 * @id cdd/stories/rules/examples-export-data-not-repository
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "examples-export-data-not-repository" and
  slash(file.getRelativePath()).matches("%repository.ts") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Examples depend on a repository module.")
select rule, node, violation
