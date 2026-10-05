/**
 * @name domain-core-file-matches-folder-slug
 * @kind problem
 * @id cdd/clean_engineering/rules/domain-core-file-matches-folder-slug
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "domain-core-file-matches-folder-slug" and
  file.getBaseName().regexpMatch("[A-Z].*") and
  node = nodeId("clean_engineering", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "File '" + file.getBaseName() + "' does not match its folder slug.")
select rule, node, violation
