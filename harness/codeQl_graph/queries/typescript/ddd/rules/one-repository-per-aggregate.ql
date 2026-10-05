/**
 * @name one-repository-per-aggregate
 * @kind problem
 * @id cdd/ddd/rules/one-repository-per-aggregate
 */

import javascript
import graph_rule

from string rule, string node, string violation, File file, int repositories
where
  rule = "one-repository-per-aggregate" and
  repositories = count(ClassDefinition cls |
      cls.getFile() = file and
      cls.getName().matches("%Repository")
    ) and
  repositories > 1 and
  node = nodeId("ddd", "Module", slash(file.getRelativePath()), file.getStem()) and
  violation = ruleViolation(rule, node, "File declares " + repositories.toString() + " repositories.")
select rule, node, violation
