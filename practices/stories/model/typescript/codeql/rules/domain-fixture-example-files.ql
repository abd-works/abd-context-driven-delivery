/**
 * @name domain-fixture-example-files
 * @kind problem
 * @id cdd/stories/rules/domain-fixture-example-files
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file
where
  rule = "domain-fixture-example-files" and
  slash(file.getRelativePath()).matches("%/examples/%") and
  file.getBaseName().matches("%cognito%") and
  node = nodeId("stories", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "Example file is named for infrastructure.")
select rule, node, violation
