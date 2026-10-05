/**
 * @name kebab-case-paths
 * @kind problem
 * @id cdd/stories/rules/kebab-case-paths
 */

import python
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "kebab-case-paths" and
  file.getRelativePath().regexpMatch(".*[A-Z_].*") and
  file.getRelativePath().regexpMatch(".*_story\\.test\\.py$") and
  node = nodeId("stories", "Story", slash(file.getRelativePath()), file.getRelativePath()) and
  violation = ruleViolation(rule, node, "Story file path is not kebab-case: " + slash(file.getRelativePath()))
select rule, node, violation
