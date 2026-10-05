/**
 * @name public-seam-only
 * @kind problem
 * @id cdd/clean_engineering/rules/public-seam-only
 */

import python
import graph_rule

from string rule, string node, string violation, StringLiteral text
where
  rule = "public-seam-only" and
  text.getS().toLowerCase().matches("%internal%") and
  node = nodeId("clean_engineering", "Module", slash(text.getLocation().getFile().getRelativePath()), text.getLocation().getFile().getStem()) and
  violation = ruleViolation(rule, node, "Module context names an internal detail.")
select rule, node, violation
