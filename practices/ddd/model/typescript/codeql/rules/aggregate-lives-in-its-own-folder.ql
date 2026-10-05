/**
 * @name aggregate-lives-in-its-own-folder
 * @kind problem
 * @id cdd/ddd/rules/aggregate-lives-in-its-own-folder
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "aggregate-lives-in-its-own-folder" and
  slash(file.getRelativePath()).matches("%/domain/%") and
  node = nodeId("ddd", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Aggregate lives in a shared domain folder.")
select rule, node, violation
