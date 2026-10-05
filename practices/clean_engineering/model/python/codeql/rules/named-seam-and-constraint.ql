/**
 * @name named-seam-and-constraint
 * @kind problem
 * @id cdd/clean_engineering/rules/named-seam-and-constraint
 */

import python
import graph_rule

from string rule, string node, string violation, StringLiteral text
where
  rule = "named-seam-and-constraint" and
  text.getS().toLowerCase().matches("%module for%") and
  node = nodeId("clean_engineering", "Module", slash(text.getLocation().getFile().getRelativePath()), text.getLocation().getFile().getStem()) and
  violation = ruleViolation(rule, node, "Module context names the seam in a docstring only.")
select rule, node, violation
