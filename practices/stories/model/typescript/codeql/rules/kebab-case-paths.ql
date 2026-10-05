/**
 * @name kebab-case-paths
 * @kind problem
 * @id cdd/stories/rules/kebab-case-paths
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "kebab-case-paths" and
  slash(file.getRelativePath()).regexpMatch(".*_story\\.test\\..*") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Story path uses underscores.")
select rule, node, violation
